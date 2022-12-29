import datetime
import json
import logging
import os
from typing import Generator

from rtu_schedule_parser import ExcelScheduleParser, LessonEmpty, LessonsSchedule
from rtu_schedule_parser.constants import Degree, Institute, ScheduleType
from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser.utils import academic_calendar

import app.services.crud_schedule as schedule_crud
from app.database.connection import async_session
from app.models import (
    CampusCreate,
    DegreeCreate,
    DisciplineCreate,
    GroupCreate,
    InstituteCreate,
    LessonCallCreate,
    LessonCreate,
    LessonDelete,
    LessonTypeCreate,
    PeriodCreate,
    RoomCreate,
    TeacherCreate,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_by_json(docs_dir: str) -> Generator[list[LessonsSchedule], None, None]:
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

            for file in files:
                file_path = os.path.join(docs_dir, file["file"])
                logger.info(f"Parsing {file['file']} from `files.json`")

                if not os.path.exists(file_path):
                    logger.error(f"File {file['file']} not found. See `files.json` for more info. Skipping...")
                    continue

                try:
                    now_date = datetime.datetime.now()
                    parser = ExcelScheduleParser(
                        file_path,
                        academic_calendar.get_period(now_date),
                        Institute.get_by_short_name(file["institute"]),
                        Degree(file["degree"]),
                    )

                    yield parser.parse(force=True).get_schedule()
                except Exception as e:
                    logger.error(f"Error while parsing {file['file']}: {e}")
                    continue

    except FileNotFoundError:
        logger.error("File `files.json` not found. Skipping...")
        return


def parse() -> Generator[list[LessonsSchedule], None, None]:
    """Parse parser from excel file"""
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(docs_dir, "docs")

    # Initialize downloader with default directory to save files
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

    # Get documents for specified institute and degree
    all_docs = downloader.get_documents(
        specific_schedule_types={ScheduleType.SEMESTER},
        specific_degrees={Degree.BACHELOR, Degree.MASTER, Degree.PHD},
        specific_institutes={institute for institute in Institute if institute != Institute.COLLEGE},
    )

    logger.info(f"Found {len(all_docs)} documents to parse")

    # Download only if they are not downloaded yet.
    downloaded = downloader.download_all(all_docs)

    # сначала документы с Degree.PHD, потом Degree.MASTER, потом Degree.BACHELOR (то есть по убыванию)
    downloaded = sorted(downloaded, key=lambda x: x[0].degree, reverse=True)

    logger.info(f"Downloaded {len(downloaded)} files")

    for doc in downloaded:
        print(f"Processing document: {doc}")

        parser = ExcelScheduleParser(doc[1], doc[0].period, doc[0].institute, doc[0].degree)

        yield parser.parse(force=True).get_schedule()

    docs_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(docs_dir, "..", "..", "docs")

    yield from parse_by_json(docs_dir)


async def parse_schedule() -> None:  # sourcery skip: low-code-quality
    """Parse parser and save it to database"""
    async with async_session() as db:
        for schedules in parse():
            for schedule in schedules:
                try:
                    # await self.repository.clear_group_schedule(parser.group)
                    period = await schedule_crud.get_or_create_period(
                        db,
                        PeriodCreate(
                            year_start=schedule.period.year_start,
                            year_end=schedule.period.year_end,
                            semester=schedule.period.semester,
                        ),
                    )
                    degree = await schedule_crud.get_or_create_degree(
                        db,
                        DegreeCreate(
                            name=schedule.degree.name,
                        ),
                    )
                    institute = await schedule_crud.get_or_create_institute(
                        db,
                        InstituteCreate(
                            name=schedule.institute.name,
                            short_name=schedule.institute.short_name,
                        ),
                    )
                    group = await schedule_crud.get_or_create_group(
                        db,
                        GroupCreate(
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

                        lesson_call = await schedule_crud.get_or_create_lesson_call(
                            db,
                            LessonCallCreate(
                                num=lesson.num,
                                time_start=lesson.time_start,
                                time_end=lesson.time_end,
                            ),
                        )
                        if type(lesson) is LessonEmpty:
                            await schedule_crud.delete_lesson(
                                db,
                                LessonDelete(
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
                                DisciplineCreate(
                                    name=lesson.name,
                                ),
                            )
                            if lesson.room is not None:
                                campus_id = None
                                if lesson.room.campus:
                                    campus = await schedule_crud.get_or_create_campus(
                                        db,
                                        CampusCreate(
                                            name=lesson.room.campus.name,
                                            short_name=lesson.room.campus.short_name,
                                        ),
                                    )
                                    campus_id = campus.id

                                room = await schedule_crud.get_or_create_room(
                                    db,
                                    RoomCreate(
                                        name=lesson.room.name,
                                        campus_id=campus_id,
                                    ),
                                )
                            if lesson.type:
                                lesson_type = await schedule_crud.get_or_create_lesson_type(
                                    db,
                                    LessonTypeCreate(
                                        name=lesson.type.value,
                                    ),
                                )

                            teachers_id = [
                                (
                                    await schedule_crud.get_or_create_teacher(
                                        db,
                                        TeacherCreate(
                                            name=teacher,
                                        ),
                                    )
                                ).id
                                for teacher in lesson.teachers
                            ]

                            await schedule_crud.get_or_create_lesson(
                                db,
                                LessonCreate(
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

                except Exception as e:
                    logger.error(f"Error while parsing schedule: {e}")
