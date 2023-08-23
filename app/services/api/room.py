from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import RoomDBService


class RoomService:
    """Сервис для работы с аудиториями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества аудиторий"""
        logger.debug(f"Запрос на получение количества аудиторий, список аудиторий: {ids =}")

        rooms_count = await RoomDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество аудиторий: {rooms_count}")

        return rooms_count

    @classmethod
    async def get_rooms(
        cls, db: AsyncSession, rooms_ids: Optional[int], campus_id: Optional[int], limit: int, offset: int
    ) -> List[models.Room]:
        """Получение списка всех аудиторий"""

        logger.debug("Запрос на получение списка аудиторий")

        rooms = await RoomDBService.get_rooms(
            db=db, rooms_ids=rooms_ids, campus_id=campus_id, limit=limit, offset=offset
        )
        logger.debug(f"Аудитории получены: {rooms}")

        return [models.Room.from_orm(room) for room in rooms]

    @classmethod
    async def get_room(cls, db: AsyncSession, id_: int) -> models.Room:
        """Получение аудитории по идентификатору"""

        logger.debug(f"Запрос на получение аудитории: {id_ = }")

        room = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Аудитория получена: {room}")

        return models.Room.from_orm(room)

    @classmethod
    async def create_room(cls, db: AsyncSession, room: models.RoomCreate) -> models.Room:
        """Создание аудитории"""

        logger.debug(f"Запрос на создание аудитории: {room =}")

        await cls._check_room_existence_with_name(db=db, name=room.name)

        db_room = await RoomDBService.create(db=db, room=room)
        await db.commit()
        await db.refresh(db_room)

        logger.info(f"Создана новая аудитория: {room = }")

        return models.Room.from_orm(db_room)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.Room:
        """Получение аудитории по идентификатору и проверка на существование"""

        room = await RoomDBService.get_room(db=db, id_=id_)
        if not room:
            logger.warning(f"Запрос несуществующей аудитории {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Аудитория {id_} не найдена")
        return room

    @classmethod
    async def _check_room_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования аудитории с name"""

        logger.debug(f"Проверяем существование аудитории с {name = }")

        if await RoomDBService.get_room_by_name(db=db, name=name):
            logger.warning(f"Попытка создать аудиторию с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Аудитория с таким названием уже существует")

        logger.debug(f"Аудитории с {name = } ещё нет")
