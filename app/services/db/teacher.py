from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class TeacherDBService:
    """Сервис для работы с преподавателями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества преподавателей"""

        query = select(func.count(tables.Teacher.id))

        if ids:
            query = query.where(tables.Teacher.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_teachers(
        cls, db: AsyncSession, teachers_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.Teacher]:
        """Получение списка всех преподавателей"""

        query = select(tables.Teacher)

        if teachers_ids:
            query = query.where(tables.Teacher.id.in_(teachers_ids))

        teacheres = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return teacheres

    @classmethod
    async def get_teacher(cls, db: AsyncSession, id_: int) -> tables.Teacher:
        """Получение преподавателя по идентификатору"""

        query = select(tables.Teacher).where(tables.Teacher.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_teacher_by_name(cls, db: AsyncSession, name: str) -> tables.Teacher:
        """Получение преподавателя по имени"""

        query = select(tables.Teacher).where(tables.Teacher.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, teacher: models.TeacherCreate) -> tables.Teacher:
        """Создание преподавателя"""

        teacher = tables.Teacher(**teacher.dict())
        db.add(teacher)
        await db.flush()
        return teacher
