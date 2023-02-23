from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import InstituteDBService


class InstituteService:
    """Сервис для работы с институтами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества институтов"""
        logger.debug(f"Запрос на получение количества институтов, список институтов: {ids =}")

        institutes_count = await InstituteDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество институтов: {institutes_count}")

        return institutes_count

    @classmethod
    async def get_institutes(
        cls, db: AsyncSession, institutes_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Institute]:
        """Получение списка всех институтов"""

        logger.debug("Запрос на получение списка институтов")

        institutes = await InstituteDBService.get_institutes(
            db=db, institutes_ids=institutes_ids, limit=limit, offset=offset
        )
        logger.debug(f"Институты получены: {institutes}")

        return [models.Institute.from_orm(institute) for institute in institutes]

    @classmethod
    async def get_institute(cls, db: AsyncSession, id_: int) -> models.Institute:
        """Получение института по идентификатору"""

        logger.debug(f"Запрос на получение института: {id_ = }")

        institute = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Институт получен: {institute}")

        return models.Institute.from_orm(institute)

    @classmethod
    async def create_institute(cls, db: AsyncSession, institute: models.InstituteCreate) -> models.Institute:
        """Создание института"""

        logger.debug(f"Запрос на создание института: {institute =}")

        await cls._check_institute_existence_with_name(db=db, name=institute.name)

        db_institute = await InstituteDBService.create(db=db, institute=institute)
        await db.commit()
        await db.refresh(db_institute)

        logger.info(f"Создан новый институт: {institute = }")

        return models.Institute.from_orm(db_institute)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.Institute:
        """Получение института по идентификатору и проверка на существование"""

        institute = await InstituteDBService.get_institute(db=db, id_=id_)
        if not institute:
            logger.warning(f"Запрос несуществующуего института {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Институт {id_} не найден")
        return institute

    @classmethod
    async def _check_institute_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования института с name"""

        logger.debug(f"Проверяем существование института с {name = }")

        if await InstituteDBService.get_institute_by_name(db=db, name=name):
            logger.warning(f"Попытка создать институт с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Институт с таким названием уже существует")

        logger.debug(f"Института с {name = } ещё нет")
