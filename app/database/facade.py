from typing import List

from app.database.connection import get_session
from app.database.dao.campuses import CampusesDAO
from app.database.interface import DBFacadeInterface
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


class DBFacade(DBFacadeInterface):
    """Фасад для работы с базой данных"""

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session
        self._campuses_dao = CampusesDAO(session=session)

    async def commit(self) -> None:
        """Commit изменений в базу"""
        await self._session.commit()

    async def is_db_alive(self) -> bool:
        """Проверка работы БД"""
        try:
            await self._session.execute("SELECT version_num FROM alembic_version")
        except Exception:
            return False
        return True

    async def get_campuses(self) -> List[models.Campus]:
        """Получение всех кампусов"""
        return await self._campuses_dao.get_campuses()

    async def get_campus_rooms(self, campus_id: int) -> List[models.Room]:
        """Получение аудиторий кампуса"""
        return await self._campuses_dao.get_campus_rooms(campus_id=campus_id)
