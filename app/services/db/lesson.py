from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import and_, cast

from app import models
from app.database import tables


class LessonDBService:
    """Сервис для работы с занятиями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества занятий"""

        query = select(func.count(tables.Lesson.id))

        if ids:
            query = query.where(tables.Lesson.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_lessons(
        cls, db: AsyncSession, lessons_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.Lesson]:
        """Получение списка всех занятий"""

        query = select(tables.Lesson)

        if lessons_ids:
            query = query.where(tables.Lesson.id.in_(lessons_ids))

        lessons = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars().unique()

        return lessons

    @classmethod
    async def get_lesson(cls, db: AsyncSession, id_: int) -> tables.Lesson:
        """Получение занятия по идентификатору"""

        query = select(tables.Lesson).where(tables.Lesson.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_lesson_by_params(
        cls,
        db: AsyncSession,
        teachers_id: List[int],
        lesson_type_id: int,
        group_id: int,
        discipline_id: int,
        room_id: int,
        weeks: List[int],
        call_id: int,
        subgroup: int,
    ) -> tables.Lesson:
        """Получение занятия по имени"""

        query = (
            select(tables.Lesson)
            .join(tables.lessons_to_teachers)
            .where(
                and_(
                    tables.lessons_to_teachers.c.teacher_id.in_(teachers_id),
                    tables.Lesson.lesson_type_id == lesson_type_id,
                    tables.Lesson.group_id == group_id,
                    tables.Lesson.discipline_id == discipline_id,
                    tables.Lesson.room_id == room_id,
                    tables.Lesson.weeks == array(weeks),
                    tables.Lesson.call_id == call_id,
                    tables.Lesson.subgroup == subgroup,
                )
            )
        )
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_lessons_by_room_id(
        cls, db: AsyncSession, room_id: int, week: Optional[int], date: Optional[str]
    ) -> List[tables.Lesson]:
        """Получение списка всех занятий"""

        query = select(tables.Lesson).where(tables.Lesson.room_id == room_id)

        if week:
            query = query.where(tables.Lesson.weeks.contains([week]))

        if date:
            # week = cls._get_current_week(date=date)
            # query = query.where(tables.Lesson.weeks.contains([week]), tables.Lesson.weekday == date.weekday() + 1)
            pass

        lessons = (await db.execute(query)).scalars().unique()

        return lessons

    @classmethod
    async def create(cls, db: AsyncSession, lesson: models.LessonCreate) -> tables.Lesson:
        """Создание занятия"""

        db_lesson = tables.Lesson(**lesson.dict(exclude={"teachers_id", "weeks"}))
        # insert list of weeks to lesson (postgres array)
        db_lesson.weeks = array(lesson.weeks)

        db.add(db_lesson)
        await db.flush()
        for teacher_id in lesson.teachers_id:
            await db.execute(tables.lessons_to_teachers.insert().values(lesson_id=db_lesson.id, teacher_id=teacher_id))
        return db_lesson

    @classmethod
    async def delete(cls, db: AsyncSession, cmd: models.LessonDelete) -> None:
        """Удаление занятия"""

        await db.execute(
            select(tables.Lesson)
            .where(
                and_(
                    tables.Lesson.group_id == select(tables.Group.id).where(tables.Group.name == cmd.group),
                    tables.Lesson.call_id
                    == select(tables.LessonCall.id).where(
                        tables.LessonCall.time_start == cmd.time_start,
                        tables.LessonCall.time_end == cmd.time_end,
                        tables.LessonCall.num == cmd.num,
                    ),
                    tables.Lesson.weekday == cmd.weekday,
                )
            )
            .execution_options(synchronize_db=False)
        )
        await db.commit()
