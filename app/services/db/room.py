from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class RoomDBService:
    """Сервис для работы с аудиториями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества аудиторий"""

        query = select(func.count(tables.Room.id))

        if ids:
            query = query.where(tables.Room.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_rooms(
        cls, db: AsyncSession, rooms_ids: Optional[List[int]], campus_id: int | None, limit: int, offset: int
    ) -> List[tables.Room]:
        """Получение списка всех аудиторий"""

        query = select(tables.Room)

        if rooms_ids:
            query = query.where(tables.Room.id.in_(rooms_ids))

        if campus_id:
            query = query.where(tables.Room.campus_id == campus_id)

        return (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

    @classmethod
    async def get_room(cls, db: AsyncSession, id_: int) -> tables.Room:
        """Получение аудитории по идентификатору"""

        query = select(tables.Room).where(tables.Room.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_room_by_name(cls, db: AsyncSession, name: str) -> tables.Room:
        """Получение аудитории по имени"""

        query = select(tables.Room).where(tables.Room.name == name)
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, room: models.RoomCreate) -> tables.Room:
        """Создание аудитории"""

        room = tables.Room(**room.dict())
        db.add(room)
        await db.flush()
        return room
