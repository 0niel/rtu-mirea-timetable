from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class PeriodDBService:
    """Сервис для работы с периодами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества периодов"""

        query = select(func.count(tables.SchedulePeriod.id))

        if ids:
            query = query.where(tables.SchedulePeriod.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_periods(
        cls, db: AsyncSession, periods_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.SchedulePeriod]:
        """Получение списка всех периодов"""

        query = select(tables.SchedulePeriod)

        if periods_ids:
            query = query.where(tables.SchedulePeriod.id.in_(periods_ids))

        periodes = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return periodes

    @classmethod
    async def get_period(cls, db: AsyncSession, id_: int) -> tables.SchedulePeriod:
        """Получение периода по идентификатору"""

        query = select(tables.SchedulePeriod).where(tables.SchedulePeriod.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_period_by_params(
        cls, db: AsyncSession, year_start: int, year_end: int, semester: int
    ) -> tables.SchedulePeriod:
        """Получение периода по параметрам"""

        query = select(tables.SchedulePeriod).where(
            tables.SchedulePeriod.year_start == year_start,
            tables.SchedulePeriod.year_end == year_end,
            tables.SchedulePeriod.semester == semester,
        )
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, period: models.PeriodCreate) -> tables.SchedulePeriod:
        """Создание периода"""

        period = tables.SchedulePeriod(**period.dict())
        db.add(period)
        await db.flush()
        return period
