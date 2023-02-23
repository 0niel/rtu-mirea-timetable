from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class InstituteDBService:
    """Сервис для работы с институтами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества институтов"""

        query = select(func.count(tables.Institute.id))

        if ids:
            query = query.where(tables.Institute.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_institutes(
        cls, db: AsyncSession, institutes_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.Institute]:
        """Получение списка всех институтов"""

        query = select(tables.Institute)

        if institutes_ids:
            query = query.where(tables.Institute.id.in_(institutes_ids))

        institutes = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return institutes

    @classmethod
    async def get_institute(cls, db: AsyncSession, id_: int) -> tables.Institute:
        """Получение института по идентификатору"""

        query = select(tables.Institute).where(tables.Institute.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_institute_by_name(cls, db: AsyncSession, name: str) -> tables.Institute:
        """Получение института по имени"""

        query = select(tables.Institute).where(tables.Institute.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, institute: models.InstituteCreate) -> tables.Institute:
        """Создание института"""

        institute = tables.Institute(**institute.dict())
        db.add(institute)
        await db.flush()
        return institute
