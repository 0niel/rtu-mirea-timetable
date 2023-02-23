from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class CampusDBService:
    """Сервис для работы с кампусами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества кампусов"""

        query = select(func.count(tables.ScheduleCampus.id))

        if ids:
            query = query.where(tables.ScheduleCampus.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_campuses(
        cls, db: AsyncSession, campuses_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.ScheduleCampus]:
        """Получение списка всех кампусов"""

        query = select(tables.ScheduleCampus)

        if campuses_ids:
            query = query.where(tables.ScheduleCampus.id.in_(campuses_ids))

        campuses = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return campuses

    @classmethod
    async def get_campus(cls, db: AsyncSession, id_: int) -> tables.ScheduleCampus:
        """Получение кампуса по идентификатору"""

        query = select(tables.ScheduleCampus).where(tables.ScheduleCampus.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_campus_by_name(cls, db: AsyncSession, name: str) -> tables.ScheduleCampus:
        """Получение кампуса по имени"""

        query = select(tables.ScheduleCampus).where(tables.ScheduleCampus.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_campus_by_short_name(cls, db: AsyncSession, short_name: str) -> tables.ScheduleCampus:
        """Получение кампуса по короткому имени"""

        query = select(tables.ScheduleCampus).where(tables.ScheduleCampus.short_name == short_name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_campus_rooms(cls, db: AsyncSession, campus_id: int) -> list[tables.Room]:
        """Получение списка аудиторий по кампусу"""

        query = (
            select(tables.Room).where(tables.Room.campus_id == campus_id).order_by(func.lower(tables.Room.name).asc())
        )
        rooms = (await db.execute(query)).scalars().all()
        return rooms

    @classmethod
    async def create(cls, db: AsyncSession, campus: models.CampusCreate) -> tables.ScheduleCampus:
        """Создание кампуса"""

        campus = tables.ScheduleCampus(**campus.dict())
        db.add(campus)
        await db.flush()
        return campus
