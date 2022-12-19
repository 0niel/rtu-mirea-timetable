from fastapi import Depends
from loguru import logger

from app import models
from app.database import DBFacadeInterface, get_db_facade


class CampusesService:
    """Сервис для работы с кампусами"""

    def __init__(self, db_facade: DBFacadeInterface = Depends(get_db_facade)) -> None:
        self._db_facade = db_facade

    async def get_campuses(self) -> list[models.Campus]:
        """Получение списка всех кампусов"""
        logger.debug("Запрос на получение списка кампусов")
        campuses = await self._db_facade.get_campuses()
        logger.debug(f"Получен список кампусов: {campuses}")
        return campuses

    async def get_campus_rooms(self, campus_id: int) -> list[models.Room]:
        """Получение списка аудиторий по кампусу"""
        logger.debug(f"Запрос на получение аудиторий кампуса с id = {campus_id}")
        rooms = await self._db_facade.get_campus_rooms(campus_id=campus_id)
        logger.debug(f"Получен список аудиторий кампуса с id = {campus_id}")
        return rooms
