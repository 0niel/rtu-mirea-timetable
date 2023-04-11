from loguru import logger
from rtu_schedule_parser import __version__ as parser_version

from app import models


class InfoService:
    """Сервис для работы с информацией о системе."""

    @classmethod
    async def get_info(cls) -> models.VersionBase:
        """Получение информации о системе"""

        logger.debug("Запрос на получение информации о системе")

        system_info = models.VersionBase(rtu_schedule_parser=parser_version, rtu_mirea_timetable="0.0.1")
        logger.debug(f"Информация о системе получения: {system_info}")

        return system_info
