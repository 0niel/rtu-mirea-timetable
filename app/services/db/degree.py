from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class DegreeDBService:
    """Сервис для работы с степенями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества степеней"""

        query = select(func.count(tables.ScheduleDegree.id))

        if ids:
            query = query.where(tables.ScheduleDegree.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_degrees(
        cls, db: AsyncSession, degrees_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.ScheduleDegree]:
        """Получение списка всех степеней"""

        query = select(tables.ScheduleDegree)

        if degrees_ids:
            query = query.where(tables.ScheduleDegree.id.in_(degrees_ids))

        degrees = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return degrees

    @classmethod
    async def get_degree(cls, db: AsyncSession, id_: int) -> tables.ScheduleDegree:
        """Получение степени по идентификатору"""

        query = select(tables.ScheduleDegree).where(tables.ScheduleDegree.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_degree_by_name(cls, db: AsyncSession, name: str) -> tables.ScheduleDegree:
        """Получение степени по имени"""

        query = select(tables.ScheduleDegree).where(tables.ScheduleDegree.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, degree: models.DegreeCreate) -> tables.ScheduleDegree:
        """Создание степени"""

        degree = tables.ScheduleDegree(**degree.dict())
        db.add(degree)
        await db.flush()
        return degree
