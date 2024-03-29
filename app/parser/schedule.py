import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Generator, List, Union

from loguru import logger
from rtu_schedule_parser import ExamsSchedule, ExcelScheduleParser, LessonEmpty, LessonsSchedule
from rtu_schedule_parser.constants import Degree, Institute, ScheduleType
from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser.schedule import Lesson as ParserLesson
from rtu_schedule_parser.utils import academic_calendar
from sqlalchemy.ext.asyncio import AsyncSession
from transliterate import translit

import app.services.crud_schedule as schedule_crud
from app import config, models
from app.database.connection import async_session
from app.services.api.group import GroupService
from app.services.db import DegreeDBService, GroupDBService, InstituteDBService, LessonCallDBService, PeriodDBService
from app.utils.cache import send_clear_cache_request


def _is_db_lesson_in_parsed_lessons(lessons: List[ParserLesson], lesson: models.Lesson) -> models.Lesson:
    get_room = lambda lesson: lesson.room.name if lesson.room else None
    return any(
        lesson.calls.num == lesson_.num
        and lesson.weekday == lesson_.weekday.value[0]
        and set([teacher.name for teacher in lesson.teachers]) == set(lesson_.teachers)
        and set(lesson.weeks) == set(lesson_.weeks)
        and lesson.discipline.name == lesson_.name
        and get_room(lesson) == get_room(lesson_)
        for lesson_ in lessons
    )


async def _compare_schedule_and_send_push(group: str, schedule: LessonsSchedule, lessons_in_db: List[models.Lesson]):
    try:
        from app.services.push_notifications import send_push_notification

        lessons = [lesson for lesson in schedule.lessons if type(lesson) is not LessonEmpty]
        for lesson_in_db in lessons_in_db:
            if not _is_db_lesson_in_parsed_lessons(lessons, lesson_in_db):
                logger.info(
                    f"Отправка push-уведомления о изменении расписания группы {group} [ScheduleUpdates__{translit(group, 'ru', reversed=True)}]"
                )
                await send_push_notification(
                    f"ScheduleUpdates__{translit(group, 'ru', reversed=True)}",
                    f"Обновилось расписание {group}",
                    f"В расписании вашей группы произошли изменения. Проверьте расписание в приложении.",
                )
                return

    except Exception as e:
        logger.warning(f"Не удалось отправить push-уведомление. Ошибка: {str(e)}")
        return


class ScheduleParsingService:
    @classmethod
    async def parse_schedule(
        cls, from_file: bool = False, file_path: str = None, institute: str = None, degree: int = None
    ) -> None:
        """Парсинг расписания используя пакет rtu_schedule_parser"""

        for schedules in (
            cls._parse()
            if not from_file
            else cls._parse_from_file(file_path=file_path, institute=institute, degree=degree)
        ):
            for schedule in schedules:
                async with async_session() as db:
                    try:
                        try:
                            group_schedule_in_db = await GroupService.get_group_by_name(db=db, name=schedule.group)

                            if group_schedule_in_db:
                                await _compare_schedule_and_send_push(
                                    schedule.group, schedule, group_schedule_in_db.lessons
                                )
                        except Exception as e:
                            logger.warning(
                                f"Не удалось получить расписание группы {schedule.group} для отправки пуш уведомления. "
                                f"Возможно, такой группы ещё не было Ошибка: {str(e)}"
                            )
                            pass

                        logger.info(f"Сохраняем расписание группы {schedule.group} в БД")
                        period = await PeriodDBService.get_period_by_params(
                            db,
                            year_start=schedule.period.year_start,
                            year_end=schedule.period.year_end,
                            semester=schedule.period.semester,
                        )
                        if not period:
                            period = await PeriodDBService.create(
                                db,
                                models.PeriodCreate(
                                    year_start=schedule.period.year_start,
                                    year_end=schedule.period.year_end,
                                    semester=schedule.period.semester,
                                ),
                            )
                        await schedule_crud.clear_group_schedule(db, schedule.group, period.id)
                        degree = await DegreeDBService.get_degree_by_name(db, schedule.degree.name)
                        if not degree:
                            degree = await DegreeDBService.create(db, models.DegreeCreate(name=schedule.degree.name))
                        institute = await InstituteDBService.get_institute_by_name(db, schedule.institute.name)
                        if not institute:
                            institute = await InstituteDBService.create(
                                db,
                                models.InstituteCreate(
                                    name=schedule.institute.name,
                                    short_name=schedule.institute.short_name,
                                ),
                            )
                        group = await GroupDBService.get_group_by_name(db, schedule.group, period.id)
                        if not group:
                            group = await GroupDBService.create(
                                db,
                                models.GroupCreate(
                                    name=schedule.group,
                                    period_id=period.id,
                                    degree_id=degree.id,
                                    institute_id=institute.id,
                                ),
                            )

                        for lesson in schedule.lessons:
                            if type(lesson) is not LessonEmpty:
                                if not lesson.weeks:
                                    continue

                                if not all(isinstance(week, int) for week in lesson.weeks):
                                    continue

                            lesson_call = await LessonCallDBService.get_call_by_params(
                                db, lesson.num, lesson.time_start, lesson.time_end
                            )
                            if not lesson_call:
                                lesson_call = await LessonCallDBService.create(
                                    db,
                                    models.LessonCallCreate(
                                        num=lesson.num,
                                        time_start=lesson.time_start,
                                        time_end=lesson.time_end,
                                    ),
                                )

                            if type(lesson) is LessonEmpty:
                                continue

                            lesson_type = None
                            room = None
                            discipline = await schedule_crud.get_or_create_discipline(
                                db,
                                models.DisciplineCreate(
                                    name=lesson.name,
                                ),
                            )
                            if lesson.room is not None:
                                campus_id = None
                                if lesson.room.campus:
                                    campus = await schedule_crud.get_or_create_campus(
                                        db,
                                        models.CampusCreate(
                                            name=lesson.room.campus.name,
                                            short_name=lesson.room.campus.short_name,
                                        ),
                                    )
                                    campus_id = campus.id

                                room = await schedule_crud.get_or_create_room(
                                    db,
                                    models.RoomCreate(
                                        name=lesson.room.name,
                                        campus_id=campus_id,
                                    ),
                                )
                            if lesson.type:
                                lesson_type = await schedule_crud.get_or_create_lesson_type(
                                    db,
                                    models.LessonTypeCreate(
                                        name=lesson.type.value,
                                    ),
                                )

                            teachers_id = [
                                (
                                    await schedule_crud.get_or_create_teacher(
                                        db,
                                        models.TeacherCreate(
                                            name=teacher,
                                        ),
                                    )
                                ).id
                                for teacher in lesson.teachers
                            ]
                            await schedule_crud.get_or_create_lesson(
                                db,
                                models.LessonCreate(
                                    lesson_type_id=lesson_type.id if lesson.type else None,
                                    discipline_id=discipline.id,
                                    teachers_id=teachers_id,
                                    room_id=room.id if lesson.room else None,
                                    group_id=group.id,
                                    call_id=lesson_call.id,
                                    weekday=lesson.weekday.value[0],
                                    subgroup=lesson.subgroup,
                                    weeks=lesson.weeks,
                                ),
                            )
                        logger.info(f"Сохранение группы {schedule.group} в БД завершено")
                    except Exception as e:
                        logger.error(
                            f"Неожиданная ошибка при сохранении группы {schedule.group} в БД.\n\n"
                            f"Параметры расписания:\n"
                            f"Группа: {schedule.group}\n"
                            f"Период: {schedule.period}\n"
                            f"Институт: {schedule.institute}\n"
                            f"Степень обучения: {schedule.degree}\n"
                            f"Ссылка на файл: {schedule.document_url}\n\n\n"
                            f"Расписание: {schedule.lessons}\n\n\n"
                            f"Ошибка {str(e)}\n\n"
                        )
                        await db.rollback()
                    else:
                        await db.commit()

        await send_clear_cache_request()

    @classmethod
    def _parse(cls) -> Generator[List[Union[LessonsSchedule, ExamsSchedule]], None, None]:
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = []
            for doc in cls._get_documents():
                task = executor.submit(cls._parse_document, doc)
                tasks.append(task)

            for future in as_completed(tasks):
                if schedules := future.result():  # type: list[LessonsSchedule | ExamsSchedule]
                    groups = {schedule.group for schedule in schedules}
                    logger.info(f"Получено расписание документа. Группы: {groups}")
                    yield schedules

    @classmethod
    def _parse_from_file(
        cls, file_path: str, institute: str, degree: int
    ) -> Generator[List[Union[LessonsSchedule, ExamsSchedule]], None, None]:
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = []
            for doc in cls._get_document_from_file(file_path=file_path, institute=institute, degree=degree):
                task = executor.submit(cls._parse_document, doc)
                tasks.append(task)

            for future in as_completed(tasks):
                if schedules := future.result():  # type: list[LessonsSchedule | ExamsSchedule]
                    groups = {schedule.group for schedule in schedules}
                    logger.info(f"Получено расписание документа. Группы: {groups}")
                    yield schedules

    @classmethod
    def _get_documents(cls) -> list:
        """Get documents for specified institute and degree"""
        docs_dir = f"{Path(__file__).parent.parent.parent}/docs"
        logger.info(f"{docs_dir = }")

        downloader = ScheduleDownloader(base_file_dir=docs_dir)

        # if os.path.exists(docs_dir):
        #     # Delete all files and dirs in folder
        #     for root, dirs, files in os.walk(docs_dir, topdown=False):
        #         for name in files:
        #             os.remove(os.path.join(root, name))
        #         for name in dirs:
        #             os.rmdir(os.path.join(root, name))
        # else:
        #     os.mkdir(docs_dir)

        documents = []

        if config.ENABLE_SCHEDULE_DOWNLOAD:
            all_docs = downloader.get_documents(
                specific_schedule_types={ScheduleType.SEMESTER},
                specific_degrees={Degree.BACHELOR, Degree.MASTER, Degree.PHD},
                specific_institutes={institute for institute in Institute if institute != Institute.COLLEGE},
            )

            logger.info(f"Найдено {len(all_docs)} документов для парсинга")

            # Download only if they are not downloaded yet.
            downloaded = downloader.download_all(all_docs)

            # сначала документы с Degree.PHD, потом Degree.MASTER, потом Degree.BACHELOR (то есть по убыванию)
            downloaded = sorted(downloaded, key=lambda x: x[0].degree, reverse=True)

            logger.info(f"Скачано {len(downloaded)} файлов")

            documents = [(doc[1], doc[0].period, doc[0].institute, doc[0].degree) for doc in downloaded]
        else:
            logger.warning("Функция скачивания расписания отключена")
        documents += cls._get_documents_by_json(docs_dir)

        return documents

    @classmethod
    def _get_document_from_file(cls, file_path: str, institute: str, degree: int) -> list:
        documents = [
            (
                file_path,
                academic_calendar.get_period(datetime.datetime.now()),
                Institute.get_by_short_name(institute),
                Degree(degree),
            )
        ]
        return documents

    @classmethod
    def _parse_document(cls, doc) -> List[Union[LessonsSchedule, ExamsSchedule]]:
        logger.info(f"Обработка документа: {doc}")
        try:
            parser = ExcelScheduleParser(doc[0], doc[1], doc[2], doc[3])
            return parser.parse(force=True).get_schedule()
        except Exception as e:
            logger.error(f"Парсинг документа {doc} завершился с ошибкой. Ошибка: {str(e)}")

    @classmethod
    def _get_documents_by_json(cls, docs_dir: str) -> list:
        # Формат json:
        # [
        #     {
        #         "file": "./расписание колледж.xlsx",
        #         "institute": "КПК",
        #         "type": 1,
        #         "degree": 4
        #     }
        # ]
        try:
            with open(os.path.join(docs_dir, "files.json"), "r") as f:
                files = json.load(f)
                logger.debug(f"{files = }")

                documents = []

                for file in files:
                    file_path = os.path.join(docs_dir, file["file"])
                    logger.info(f"Файл {file['file']} добавлен на парсинг из `files.json`")

                    if not os.path.exists(file_path):
                        logger.error(f"Файл {file['file']} не найден. См. `files.json`. Пропускаем...")
                        continue

                    documents.append(
                        (
                            file_path,
                            academic_calendar.get_period(datetime.datetime.now()),
                            Institute.get_by_short_name(file["institute"]),
                            Degree(file["degree"]),
                        )
                    )

                return documents

        except FileNotFoundError:
            logger.info("`files.json` не найден. Пропускаем...")
            return []
