from app.database.tables import Group
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_groups(db: AsyncSession) -> list[Group]:
    res = await db.execute(select(Group))
    return res.scalars().all()


async def get_group(db: AsyncSession, name: str) -> Group:
    res = await db.execute(select(Group).where(Group.name == name).limit(1))
    return res.scalar()
