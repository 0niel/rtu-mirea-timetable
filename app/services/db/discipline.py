from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class DisciplineDBService:
    """Сервис для работы с дисциплинами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества дисциплин"""

        query = select(func.count(tables.ScheduleDiscipline.id))

        if ids:
            query = query.where(tables.ScheduleDiscipline.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_disciplines(
        cls, db: AsyncSession, disciplines_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.ScheduleDiscipline]:
        """Получение списка всех дисциплин"""

        query = select(tables.ScheduleDiscipline)

        if disciplines_ids:
            query = query.where(tables.ScheduleDiscipline.id.in_(disciplines_ids))

        disciplines = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return disciplines

    @classmethod
    async def get_discipline(cls, db: AsyncSession, id_: int) -> tables.ScheduleDiscipline:
        """Получение дисциплины по идентификатору"""

        query = select(tables.ScheduleDiscipline).where(tables.ScheduleDiscipline.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_discipline_by_name(cls, db: AsyncSession, name: str) -> tables.ScheduleDiscipline:
        """Получение дисциплины по имени"""

        query = select(tables.ScheduleDiscipline).where(tables.ScheduleDiscipline.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, discipline: models.DegreeCreate) -> tables.ScheduleDiscipline:
        """Создание дисциплины"""

        discipline = tables.ScheduleDiscipline(**discipline.dict())
        db.add(discipline)
        await db.flush()
        return discipline
