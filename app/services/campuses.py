from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.table import Room, ScheduleCampus


async def get_campuses(db: AsyncSession) -> list[ScheduleCampus]:
    res = await db.execute(select(ScheduleCampus))
    return res.scalars().all()


async def get_campus_rooms(db: AsyncSession, campus_id: int) -> list[Room]:
    res = await db.execute(select(Room).where(Room.campus_id == campus_id).order_by(func.lower(Room.name).asc()))
    return res.scalars().all()
