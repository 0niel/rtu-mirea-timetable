from typing import List, Optional

from rtu_schedule_parser.utils import academic_calendar
from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables
from app.database.tables import SchedulePeriod


class GroupDBService:
    """Сервис для работы с группами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества групп"""

        query = select(func.count(tables.Group.id))

        if ids:
            query = query.where(tables.Group.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_groups(
        cls, db: AsyncSession, groups_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.Group]:
        """Получение списка всех групп"""

        query = select(tables.Group)

        if groups_ids:
            query = query.where(tables.Group.id.in_(groups_ids))

        groups = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars().unique()

        return groups

    @classmethod
    async def get_group(cls, db: AsyncSession, id_: int) -> tables.Group:
        """Получение группы по индентификатору"""

        query = select(tables.Group).where(tables.Group.id == id_).limit(1)
        group = (await db.execute(query)).scalar()
        return group

    @classmethod
    async def get_group_by_name(cls, db: AsyncSession, name: str, period_id: Optional[int] = None) -> tables.Group:
        """Получение группы по имени"""

        query = select(tables.Group).where(tables.Group.name == name)

        if not period_id:
            period_id = await cls._get_current_period_id(db)

        query = query.where(tables.Group.period_id == period_id).limit(1)
        group = (await db.execute(query)).scalar()
        return group

    @classmethod
    async def create(cls, db: AsyncSession, group: models.GroupCreate) -> tables.Group:
        """Создание группы"""

        group = tables.Group(**group.dict())
        db.add(group)
        await db.flush()
        return group

    @classmethod
    async def _get_current_period_id(cls, db: AsyncSession) -> int:
        """Получение id текущего периода"""

        current_period = academic_calendar.get_period(academic_calendar.now_date())

        query = (
            select(SchedulePeriod.id)
            .where(
                SchedulePeriod.year_start == current_period.year_start,
                SchedulePeriod.year_end == current_period.year_end,
                SchedulePeriod.semester == current_period.semester,
            )
            .limit(1)
        )
        period_id = (await db.execute(query)).scalar()
        return period_id
