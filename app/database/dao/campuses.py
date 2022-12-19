from app.database import tables
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models


class CampusesDAO:
    """DAO для работы с кампусами"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_campuses(self) -> list[models.Campus]:
        """Получение всех кампусов"""
        query = select(tables.ScheduleCampus)
        campuses = (await self._session.execute(query)).scalars().all()
        result = [models.Campus.from_orm(campus) for campus in campuses]
        return result

    async def get_campus_rooms(self, campus_id: int) -> list[models.Room]:
        """Получение аудиторий кампуса"""
        query = (
            select(tables.Room).where(tables.Room.campus_id == campus_id).order_by(func.lower(tables.Room.name).asc())
        )
        rooms = (await self._session.execute(query)).scalars().all()
        result = [models.Room.from_orm(room) for room in rooms]
        return result
