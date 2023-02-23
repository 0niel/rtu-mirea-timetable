from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class LessonTypeDBService:
    """Сервис для работы с типами занятий."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества типов занятий"""

        query = select(func.count(tables.LessonType.id))

        if ids:
            query = query.where(tables.LessonType.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_types(
        cls, db: AsyncSession, types_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.LessonType]:
        """Получение списка всех типов занятий"""

        query = select(tables.LessonType)

        if types_ids:
            query = query.where(tables.LessonType.id.in_(types_ids))

        types = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return types

    @classmethod
    async def get_type(cls, db: AsyncSession, id_: int) -> tables.LessonType:
        """Получение типа занятия по идентификатору"""

        query = select(tables.LessonType).where(tables.LessonType.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_type_by_name(cls, db: AsyncSession, name: str) -> tables.LessonType:
        """Получение типа занятия по параметрам"""

        query = select(tables.LessonType).where(tables.LessonType.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, type_: models.LessonTypeCreate) -> tables.LessonType:
        """Создание типа занятия"""

        type_ = tables.LessonType(**type_.dict())
        db.add(type_)
        await db.flush()
        return type_
