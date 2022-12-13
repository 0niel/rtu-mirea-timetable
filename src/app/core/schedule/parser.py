import logging
import os
from typing import Generator

from rtu_schedule_parser import ExcelScheduleParser, LessonEmpty, Schedule
from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser.constants import ScheduleType

import app.crud.crud_schedule as schedule_crud
from app.schemas import (
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

logger = logging.getLogger(__name__)


def parse() -> Generator[list[Schedule], None, None]:
    """Parse schedule from excel file"""
    # get current script dir
    current_dir = os.path.dirname(os.path.realpath(__file__))
    docs_dir = os.path.join(current_dir, "docs")

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
    all_docs = downloader.get_documents(specific_schedule_types={ScheduleType.SEMESTER})

    # Download only if they are not downloaded yet.
    downloaded = downloader.download_all(all_docs)

    logger.info(f"Downloaded {len(downloaded)} files")

    for doc in downloaded:
        logger.info(f"Processing document: {doc}")

        parser = ExcelScheduleParser(
            doc[1], doc[0].period, doc[0].institute, doc[0].degree
        )

        yield parser.parse(force=True).get_schedule()


async def parse_schedule() -> None:
    """Parse schedule and save it to database"""
    for schedules in parse():
        for schedule in schedules:
            # await self.repository.clear_group_schedule(schedule.group)
            period = await schedule_crud.get_or_create_period(
                PeriodCreate(
                    year_start=schedule.period.year_start,
                    year_end=schedule.period.year_end,
                    semester=schedule.period.semester,
                )
            )
            degree = await schedule_crud.get_or_create_degree(
                DegreeCreate(
                    name=schedule.degree.name,
                )
            )
            institute = await schedule_crud.get_or_create_institute(
                InstituteCreate(
                    name=schedule.institute.name,
                    short_name=schedule.institute.short_name,
                )
            )
            group = await schedule_crud.get_or_create_group(
                GroupCreate(
                    name=schedule.group,
                    period_id=period.id,
                    degree_id=degree.id,
                    institute_id=institute.id,
                )
            )

            for lesson in schedule.lessons:
                lesson_call = await schedule_crud.get_or_create_lesson_call(
                    LessonCallCreate(
                        num=lesson.num,
                        time_start=lesson.time_start,
                        time_end=lesson.time_end,
                    )
                )
                if type(lesson) is LessonEmpty:
                    await schedule_crud.delete_lesson(
                        LessonDelete(
                            group=schedule.group,
                            time_start=lesson.time_start,
                            time_end=lesson.time_end,
                            num=lesson.num,
                            weekday=lesson.weekday.value[0],
                        )
                    )
                else:
                    lesson_type = None
                    room = None
                    discipline = await schedule_crud.get_or_create_discipline(
                        DisciplineCreate(
                            name=lesson.name,
                        )
                    )
                    if lesson.room is not None:
                        campus_id = None
                        if lesson.room.campus:
                            campus = await schedule_crud.get_or_create_campus(
                                CampusCreate(
                                    name=lesson.room.campus.name,
                                    short_name=lesson.room.campus.short_name,
                                )
                            )
                            campus_id = campus.id

                        room = await schedule_crud.get_or_create_room(
                            RoomCreate(
                                name=lesson.room.name,
                                campus_id=campus_id,
                            )
                        )
                    if lesson.type:
                        lesson_type = await schedule_crud.get_or_create_lesson_type(
                            LessonTypeCreate(
                                name=lesson.type.value,
                            )
                        )

                    teachers_id = [
                        (
                            await schedule_crud.get_or_create_teacher(
                                TeacherCreate(
                                    name=teacher,
                                )
                            )
                        ).id
                        for teacher in lesson.teachers
                    ]

                    await schedule_crud.get_or_create_lesson(
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
                        )
                    )
