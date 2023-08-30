from loguru import logger
from rtu_schedule_parser import __version__ as parser_version
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.models import SettingsCreate
from app.services.db.info import InfoDBService


class InfoService:
    """Сервис для работы с информацией о системе."""

    @classmethod
    async def get_info(cls) -> models.VersionBase:
        """Получение информации о системе"""

        logger.debug("Запрос на получение информации о системе")

        system_info = models.VersionBase(rtu_schedule_parser=parser_version, rtu_mirea_timetable="0.0.1")
        logger.debug(f"Информация о системе получения: {system_info}")

        return system_info

    @classmethod
    async def get_max_week(cls, db: AsyncSession) -> models.SettingsGet:
        """Получение максимального кол-ва недель"""

        logger.debug("Запрос на получение максимального кол-ва недель в семестре")

        max_week = await InfoDBService.get_max_week(db=db)
        logger.debug(f"Кол-во недель получено: {max_week}")

        return max_week

    @classmethod
    async def set_max_week(cls, db: AsyncSession, settings: SettingsCreate) -> models.SettingsGet:
        """Получение максимального кол-ва недель"""

        logger.debug("Запрос на установку максимального кол-ва недель в семестре")

        new_max_week = await InfoDBService.set_max_week(db=db, max_week=settings.max_week)
        logger.debug(f"Кол-во недель установлено: {settings.max_week}")

        return new_max_week
