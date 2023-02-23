from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.services.db import CampusDBService


class CampusService:
    """Сервис для работы с кампусами."""

    @classmethod
    async def get_campuses(
        cls, db: AsyncSession, campuses_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Campus]:
        """Получение списка всех кампусов"""

        logger.debug("Запрос на получение списка кампусов")

        campuses = await CampusDBService.get_campuses(db=db, campuses_ids=campuses_ids, limit=limit, offset=offset)
        logger.debug(f"Кампусы получены: {campuses}")

        return [models.Campus.from_orm(campus) for campus in campuses]

    @classmethod
    async def get_campus(cls, db: AsyncSession, id_: int) -> models.Campus:
        """Получение кампуса по идентификатору"""

        logger.debug(f"Запрос на получение кампуса: {id_ = }")

        campus = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Кампус получен: {campus}")

        return models.Campus.from_orm(campus)

    @classmethod
    async def create_campus(cls, db: AsyncSession, campus: models.CampusCreate) -> models.Campus:
        """Создание капмуса"""

        logger.debug(f"Запрос на создание кампуса: {campus =}")

        await cls._check_campus_existence_with_name(db=db, name=campus.name)
        await cls._check_campus_existence_with_short_name(db=db, short_name=campus.short_name)

        db_campus = await CampusDBService.create(db=db, campus=campus)
        await db.commit()
        await db.refresh(db_campus)

        logger.info(f"Создан новый кампус: {campus = }")

        return models.Campus.from_orm(db_campus)

    @classmethod
    async def get_campus_rooms(cls, db: AsyncSession, campus_id: int) -> list[models.Room]:
        """Получение списка аудиторий по кампусу"""

        logger.debug(f"Запрос на получение списка аудиторий по кампусу с {campus_id = }")

        await cls._get_one(db=db, id_=campus_id)

        rooms = await CampusDBService.get_campus_rooms(db=db, campus_id=campus_id)
        logger.debug(f"Аудитории получены: {rooms}")

        return [models.Room.from_orm(room) for room in rooms]

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> models.Campus:
        """Получение кампуса по идентификатору и проверка на существование"""

        campus = await CampusDBService.get_campus(db=db, id_=id_)
        if not campus:
            logger.warning(f"Запрос несуществующуего кампуса {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Кампус {id_} не найден")
        return campus

    @classmethod
    async def _check_campus_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования кампуса с name"""

        logger.debug(f"Проверяем существование кампуса с {name = }")

        if await CampusDBService.get_campus_by_name(db=db, name=name):
            logger.warning(f"Попытка создать кампус с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Кампус с таким названием уже существует")

        logger.debug(f"Кампуса с {name = } ещё нет")

    @classmethod
    async def _check_campus_existence_with_short_name(cls, db: AsyncSession, short_name: str) -> None:
        """Проверка существования кампуса с short_name"""

        logger.debug(f"Проверяем существование кампуса с {short_name = }")

        if await CampusDBService.get_campus_by_short_name(db=db, short_name=short_name):
            logger.warning(f"Попытка создать кампус с уже существующим short name: {short_name}")
            raise HTTPException(status_code=409, detail="Кампус с таким сокращенным названием уже существует")

        logger.debug(f"Кампуса с {short_name = } ещё нет")
