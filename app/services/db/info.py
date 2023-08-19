from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import tables


class InfoDBService:
    """Сервис для работы с занятиями."""

    @classmethod
    async def get_max_week(cls, db: AsyncSession) -> tables.Settings:
        """Получение максимального кол-ва недель"""

        query = select(tables.Settings).limit(1)
        return (await db.execute(query)).scalar()

    @classmethod
    async def set_max_week(cls, db: AsyncSession, max_week: int) -> tables.Settings:
        """Получение максимального кол-ва недель"""

        old_settings = (await db.execute(select(tables.Settings).limit(1))).scalar()
        await db.execute(
            update(tables.Settings)
            .where(tables.Settings.id == old_settings.id)
            .values({"max_week": max_week})
        )
        await db.refresh(old_settings)
        await db.commit()
        return old_settings
