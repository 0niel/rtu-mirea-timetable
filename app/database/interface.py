from abc import ABC, abstractmethod

from app import models


class DBFacadeInterface(ABC):
    """Интерфейс фасада базы данных"""

    @abstractmethod
    async def commit(self) -> None:
        """Commit изменений"""
        ...

    @abstractmethod
    async def is_db_alive(self) -> bool:
        """Проверка работы БД"""
        ...

    @abstractmethod
    async def get_campuses(self) -> list[models.Campus]:
        """Получение всех кампусов"""
        ...

    @abstractmethod
    async def get_campus_rooms(self, campus_id: int) -> list[models.Room]:
        """Получение аудиторий кампуса"""
        ...
