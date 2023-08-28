import datetime
from collections import Counter, defaultdict
from typing import List, Optional

from sqlalchemy import and_, delete, func, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app import models
from app.database import tables
from app.database.tables import (
    Group,
    Lesson,
    LessonCall,
    LessonType,
    Room,
    ScheduleCampus,
    ScheduleDiscipline,
    Teacher,
    lessons_to_teachers,
)
from app.models import RoomStatusGet
from app.services import utils


async def get_or_create_lesson_type(db: AsyncSession, cmd: models.LessonTypeCreate):
    # migrated to api v2

    res = await db.execute(select(LessonType).where(LessonType.name == cmd.name).limit(1))
    lesson_type = res.scalar()
    if not lesson_type:
        lesson_type = LessonType(**cmd.dict())
        db.add(lesson_type)
        await db.commit()
        await db.refresh(lesson_type)
    return lesson_type


async def get_or_create_campus(db: AsyncSession, cmd: models.CampusCreate):
    # migrated to api v2
    res = await db.execute(select(ScheduleCampus).where(ScheduleCampus.name == cmd.name).limit(1))
    campus = res.scalar()
    if not campus:
        campus = ScheduleCampus(**cmd.dict())
        db.add(campus)
        await db.commit()
        await db.refresh(campus)
    return campus


async def get_or_create_room(db: AsyncSession, cmd: models.RoomCreate):
    # migrated to api v2
    res = await db.execute(select(Room).where(Room.name == cmd.name).limit(1))
    room = res.scalar()
    if not room:
        room = Room(**cmd.dict())
        db.add(room)
        await db.commit()
        await db.refresh(room)
    return room


async def get_or_create_teacher(db: AsyncSession, cmd: models.TeacherCreate):
    # migrated to api v2
    res = await db.execute(select(Teacher).where(Teacher.name == cmd.name).limit(1))
    teacher = res.scalar()
    if not teacher:
        teacher = Teacher(**cmd.dict())
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
    return teacher


async def get_or_create_lesson_call(db: AsyncSession, cmd: models.LessonCallCreate):
    # migrated to api v2
    res = await db.execute(
        select(LessonCall)
        .where(
            and_(
                LessonCall.time_start == cmd.time_start,
                LessonCall.time_end == cmd.time_end,
                LessonCall.num == cmd.num,
            )
        )
        .limit(1)
    )
    lesson_call = res.scalar()
    if not lesson_call:
        lesson_call = LessonCall(**cmd.dict())
        db.add(lesson_call)
        await db.commit()
        await db.refresh(lesson_call)
    return lesson_call


async def get_or_create_discipline(db: AsyncSession, cmd: models.DisciplineCreate):
    # migrated to api v2
    res = await db.execute(select(ScheduleDiscipline).where(ScheduleDiscipline.name == cmd.name).limit(1))
    discipline = res.scalar()
    if not discipline:
        discipline = ScheduleDiscipline(**cmd.dict())
        db.add(discipline)
        await db.commit()
        await db.refresh(discipline)
    return discipline


async def get_or_create_lesson(db: AsyncSession, cmd: models.LessonCreate):
    # migrated to api v2
    res = await db.execute(
        select(Lesson)
        .join(Lesson.teachers)
        .where(
            and_(
                Lesson.discipline_id == cmd.discipline_id,
                Lesson.lesson_type_id == cmd.lesson_type_id,
                Lesson.group_id == cmd.group_id,
                Lesson.room_id == cmd.room_id,
                Lesson.weeks == array(cmd.weeks),
                Lesson.call_id == cmd.call_id,
                Lesson.subgroup == cmd.subgroup,
                Lesson.teachers.any(Teacher.id.in_(cmd.teachers_id)),
            )
        )
        .options(joinedload(Lesson.teachers))
        .limit(1)
    )
    lesson = res.scalar()
    if not lesson:
        lesson = Lesson(**cmd.dict(exclude={"weeks", "teachers_id"}))

        lesson.weeks = array(cmd.weeks)

        db.add(lesson)
        await db.flush()

        for teacher_id in cmd.teachers_id:
            lessons_to_teachers_relationship = (await db.execute(
                select(lessons_to_teachers).where(lessons_to_teachers.columns.lesson_id == lesson.id,
                                                  lessons_to_teachers.columns.teacher_id == teacher_id))).scalars()
            if not lessons_to_teachers_relationship:
                await db.execute(lessons_to_teachers.insert().values(lesson_id=lesson.id, teacher_id=teacher_id))
        await db.commit()
        await db.refresh(lesson)

    return lesson


async def clear_group_schedule(db: AsyncSession, group_name: str, period_id: int):
    res = await db.execute(
        select(Group)
        .where(
            and_(
                Group.name == group_name,
                Group.period_id == period_id,
            )
        )
        .limit(1)
    )

    if group := res.scalar():
        await db.execute(
            delete(lessons_to_teachers).where(
                lessons_to_teachers.c.lesson_id.in_(
                    select(Lesson.id).where(
                        and_(
                            Lesson.group_id == select(Group.id).where(Group.name == group_name),
                        )
                    )
                )
            )
        )

        await db.execute(
            delete(Lesson).where(
                and_(
                    Lesson.group_id == group.id,
                )
            )
        )
        await db.commit()


async def delete_lesson(db: AsyncSession, cmd: models.LessonDelete):
    await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == select(Group.id).where(Group.name == cmd.group),
                Lesson.call_id
                == select(LessonCall.id).where(
                    LessonCall.time_start == cmd.time_start,
                    LessonCall.time_end == cmd.time_end,
                    LessonCall.num == cmd.num,
                ),
                Lesson.weekday == cmd.weekday,
            )
        )
        .execution_options(synchronize_db=False)
    )
    await db.commit()


async def get_lessons_by_teacher(db: AsyncSession, teacher_id: int):
    res = await db.execute(
        select(Lesson).join(lessons_to_teachers).where(lessons_to_teachers.c.teacher_id == teacher_id)
    )
    return res.scalars().all()


async def get_lessons_by_room(db: AsyncSession, room_id: int):
    # migrated to api v2
    res = await db.execute(select(Lesson).where(Lesson.room_id == room_id))
    return res.scalars().all()


async def search_room(db: AsyncSession, name: str) -> list[Room]:
    # TODO: Refactor to better search
    name = name.replace(".", "")
    name = name.replace(" ", "")
    name = name.replace("/", "")
    res = await db.execute(select(Room).where(func.lower(Room.name).contains(name.lower())))
    return res.scalars().all()


async def get_room(db: AsyncSession, name: str, campus_short_name: Optional[str] = None):
    res = await db.execute(
        select(Room)
        .where(
            and_(
                Room.name == name,
                Room.campus_id == select(ScheduleCampus.id).where(ScheduleCampus.short_name == campus_short_name),
            )
        )
        .limit(1)
    )
    return res.scalar()


# async def get_lessons_by_room(db: AsyncSession, room_id: int) -> list[Lesson]:
#     res = await db.execute(select(Lesson).where(Lesson.room_id == room_id).order_by(Lesson.weekday, Lesson.call_id))
#     return res.scalars().all()


async def get_lessons_by_room_and_date(db: AsyncSession, room_id: int, date: datetime.date) -> list[Lesson]:
    # partially migrated to api v2
    week = utils.get_week(date=date)
    res = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.room_id == room_id,
                Lesson.weeks.contains([week]),
                Lesson.weekday == date.weekday() + 1,
            )
        )
        .order_by(Lesson.call_id)
    )
    return res.scalars().all()


async def get_lessons_by_room_and_week(db: AsyncSession, room_id: int, week: int) -> list[Lesson]:
    # migrated to api v2
    res = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.room_id == room_id,
                Lesson.weeks.contains([week]),
            )
        )
        .order_by(Lesson.weekday, Lesson.call_id)
    )
    return res.scalars().all()


async def get_room_workload(db: AsyncSession, room_id: int):
    # get all lesson for room
    res = await db.execute(select(Lesson).where(Lesson.room_id == room_id).order_by(Lesson.weekday, Lesson.call_id))
    lessons = res.scalars().unique()

    # get all calls
    res = await db.execute(select(LessonCall))
    calls = res.scalars().unique()

    checked = defaultdict(set)
    workload = 0
    for lesson in lessons:
        if call := next((c for c in calls if c.id == lesson.call_id), None):  # noqa
            for week in lesson.weeks:
                key = (lesson.weekday, lesson.call_id)
                if week not in checked[key]:
                    workload += 1
                    checked[key].add(week)

    workload = workload / (6 * 6 * 17) * 100  # 6 дней * 6 пар * 17 недель
    return round(workload, 2)


async def get_call_by_time(db: AsyncSession, time: datetime.time) -> LessonCall:
    res = await db.execute(
        select(LessonCall)
        .where(
            and_(
                LessonCall.time_start <= time,
                LessonCall.time_end > time,
            )
        )
        .limit(1)
    )
    return res.scalar()


async def get_rooms_statuses(
    db: AsyncSession, time: datetime.datetime, campus_id: Optional[int] = None, room_id: Optional[int] = None
) -> List[RoomStatusGet]:
    if campus_id:
        rooms = (await db.execute(select(tables.Room).where(tables.Room.campus_id == campus_id))).scalars()
        ids = [room.id for room in rooms]

    if room_id:
        ids = [room_id]

    res = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.room_id.in_(ids),
                Lesson.weekday == time.weekday() + 1,
                Lesson.weeks.contains([utils.get_week(date=time)]),
                Lesson.call_id
                == select(LessonCall.id)
                .where(
                    and_(
                        LessonCall.time_start <= time.time(),
                        LessonCall.time_end > time.time(),
                    )
                )
                .limit(1),
            )
        )
    )

    lessons = res.scalars().unique().all()
    return [
        RoomStatusGet(id=_id, status="free" if _id not in [lesson.room_id for lesson in lessons] else "busy")
        for _id in ids
    ]


async def get_rooms_status(db: AsyncSession, time: datetime.datetime, room_id: int) -> RoomStatusGet:
    res = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.room_id == room_id,
                Lesson.weekday == time.weekday() + 1,
                Lesson.weeks.contains([utils.get_week(date=time)]),
                Lesson.call_id
                == select(LessonCall.id)
                .where(
                    and_(
                        LessonCall.time_start <= time.time(),
                        LessonCall.time_end > time.time(),
                    )
                )
                .limit(1),
            )
        )
    )

    lessons = res.scalars().unique()
    return RoomStatusGet(id=room_id, status="free" if room_id not in [lesson.room_id for lesson in lessons] else "busy")


async def get_all_rooms(db: AsyncSession) -> list[Room]:
    # migrated to api v2
    res = await db.execute(select(Room))
    return res.scalars().all()


def get_all_rooms_sync(session) -> list[Room]:
    return session.query(Room).all()


async def get_room_info(db: AsyncSession, room_id: int) -> models.RoomInfo:
    res = await db.execute(select(Room).where(Room.id == room_id))
    room = res.scalar()

    res2 = await db.execute(select(Lesson).where(Lesson.room_id == room_id).order_by(Lesson.weekday, Lesson.call_id))
    lessons = res2.scalars().unique()

    workload = await get_room_workload(db, room_id)

    purpose = Counter([lesson.lesson_type.name for lesson in lessons]).most_common(1)[0][0]

    purpose = {
        "лек": "Лекция",
        "пр": "Практика",
        "лаб": "Лабораторная",
    }.get(purpose, "Неизвестно")

    return models.RoomInfo(
        room=room,
        lessons=lessons,
        workload=workload,
        purpose=purpose,
    )
