from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.tables import Group, SchedulePeriod
from rtu_schedule_parser.utils import academic_calendar


async def get_groups(db: AsyncSession) -> list[Group]:
    res = await db.execute(select(Group))
    return res.scalars().all()


async def get_group(db: AsyncSession, name: str, period_id: int | None = None) -> Group | None:
    if period_id:
        res = await db.execute(
            select(Group)
            .where(Group.name == name)
            .where(Group.period_id == period_id)
            .limit(1)
        )
        return res.scalar()
    
    
    current_period = academic_calendar.get_period(academic_calendar.now_date())
    
    period_id = await db.execute(
        select(SchedulePeriod.id)
        .where(SchedulePeriod.year_start == current_period.year_start)
        .where(SchedulePeriod.year_end == current_period.year_end)
        .where(SchedulePeriod.semester == current_period.semester)
        .limit(1)
    )
    
    period_id = period_id.scalar()
    
    res = await db.execute(
        select(Group)
        .where(Group.name == name)
        .where(Group.period_id == period_id)
    )
    
    return res.first()
