from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.services.db import DegreeDBService


class DegreeService:
    """Сервис для работы с степенями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества степеней"""
        logger.debug(f"Запрос на получение количества степеней, список степеней: {ids =}")

        degrees_count = await DegreeDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество степеней: {degrees_count}")

        return degrees_count

    @classmethod
    async def get_degrees(
        cls, db: AsyncSession, degrees_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Degree]:
        """Получение списка всех степеней"""

        logger.debug("Запрос на получение списка степеньов")

        degrees = await DegreeDBService.get_degrees(db=db, degrees_ids=degrees_ids, limit=limit, offset=offset)
        logger.debug(f"Степени получены: {degrees}")

        return [models.Degree.from_orm(degree) for degree in degrees]

    @classmethod
    async def get_degree(cls, db: AsyncSession, id_: int) -> models.Degree:
        """Получение степени по идентификатору"""

        logger.debug(f"Запрос на получение степени: {id_ = }")

        degree = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Степень получена: {degree}")

        return models.Degree.from_orm(degree)

    @classmethod
    async def create_degree(cls, db: AsyncSession, degree: models.DegreeCreate) -> models.Degree:
        """Создание степени"""

        logger.debug(f"Запрос на создание степени: {degree =}")

        await cls._check_degree_existence_with_name(db=db, name=degree.name)

        db_degree = await DegreeDBService.create(db=db, degree=degree)
        await db.commit()
        await db.refresh(db_degree)

        logger.info(f"Создана новая степень: {degree = }")

        return models.Degree.from_orm(db_degree)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> models.Institute:
        """Получение степени по идентификатору и проверка на существование"""

        degree = await DegreeDBService.get_degree(db=db, id_=id_)
        if not degree:
            logger.warning(f"Запрос несуществующуей степени {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Степень {id_} не найдена")
        return degree

    @classmethod
    async def _check_degree_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования степени с name"""

        logger.debug(f"Проверяем существование степени с {name = }")

        if await DegreeDBService.get_degree_by_name(db=db, name=name):
            logger.warning(f"Попытка создать степень с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Степень с таким названием уже существует")

        logger.debug(f"Степени с {name = } ещё нет")
