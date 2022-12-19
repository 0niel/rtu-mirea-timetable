import copy

from app.database.interface import DBFacadeInterface

from app import models
from tests import data as mock_data


class MockDBFacade(DBFacadeInterface):
    """Mock фасада базы данных"""

    def __init__(self):
        self.campuses = copy.deepcopy(mock_data.CAMPUSES)
        self.rooms = copy.deepcopy(mock_data.ROOMS)

    async def commit(self) -> None:
        pass

    async def is_db_alive(self) -> bool:
        """Проверка работы БД"""
        return True

    async def get_campuses(self) -> list[models.Campus]:
        return self.campuses

    async def get_campus_rooms(self, campus_id: int) -> list[models.Room]:
        return self.rooms
