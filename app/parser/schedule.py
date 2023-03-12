import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Generator

from loguru import logger
from rtu_schedule_parser import ExamsSchedule, ExcelScheduleParser, LessonEmpty, LessonsSchedule
from rtu_schedule_parser.constants import Degree, Institute, ScheduleType
from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser.utils import academic_calendar
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.crud_schedule as schedule_crud
from app import models
from app.services.db import (
    DegreeDBService,
    GroupDBService,
    InstituteDBService,
    LessonCallDBService,
    LessonDBService,
    PeriodDBService,
)


class ScheduleParsingService:
    @classmethod
    async def parse_schedule(cls, db: AsyncSession) -> None:
        """Парсинг расписания используя пакет rtu_schedule_parser"""

        for schedules in cls._parse():
            for schedule in schedules:
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
                        await LessonDBService.delete(
                            db,
                            models.LessonDelete(
                                group=schedule.group,
                                time_start=lesson.time_start,
                                time_end=lesson.time_end,
                                num=lesson.num,
                                weekday=lesson.weekday.value[0],
                            ),
                        )
                    else:
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

    @classmethod
    def _parse(cls) -> Generator[list[LessonsSchedule | ExamsSchedule], None, None]:
        with ThreadPoolExecutor(max_workers=4) as executor:
            # создаем список задач по загрузке и парсингу документов
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
    def _get_documents(cls) -> list:
        """Get documents for specified institute and degree"""
        docs_dir = os.path.dirname(os.path.abspath(__file__))
        docs_dir = os.path.join(docs_dir, "docs")

        downloader = ScheduleDownloader(base_file_dir=docs_dir)

        if os.path.exists(docs_dir):
            # Delete all files and dirs in folder
            for root, dirs, files in os.walk(docs_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        else:
            os.mkdir(docs_dir)

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
        documents += cls._get_documents_by_json(docs_dir)

        return documents

    @classmethod
    def _parse_document(cls, doc) -> list[LessonsSchedule | ExamsSchedule]:
        logger.info(f"Обработка документа: {doc}")
        try:
            parser = ExcelScheduleParser(doc[0], doc[1], doc[2], doc[3])
            return parser.parse(force=True).get_schedule()
        except Exception:
            logger.error(f"Парсинг завершился с ошибкой ({doc})")

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
