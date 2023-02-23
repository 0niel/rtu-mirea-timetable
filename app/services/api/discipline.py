from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import DisciplineDBService


class DisciplineService:
    """Сервис для работы с дисциплинами."""

    @classmethod
    async def get_disciplines(
        cls, db: AsyncSession, disciplines_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Discipline]:
        """Получение списка всех дисциплин"""

        logger.debug("Запрос на получение списка дисциплин")

        disciplines = await DisciplineDBService.get_disciplines(
            db=db, disciplines_ids=disciplines_ids, limit=limit, offset=offset
        )
        logger.debug(f"Дисциплины получены: {disciplines}")

        return [models.Discipline.from_orm(discipline) for discipline in disciplines]

    @classmethod
    async def get_discipline(cls, db: AsyncSession, id_: int) -> models.Discipline:
        """Получение дисциплины по идентификатору"""

        logger.debug(f"Запрос на получение дисциплины с {id_ = }")

        discipline = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Дисциплина получена: {discipline}")

        return models.Discipline.from_orm(discipline)

    @classmethod
    async def get_discipline_by_name(cls, db: AsyncSession, name: str) -> models.Discipline:
        """Получение дисциплины по имени"""

        logger.debug(f"Запрос на получение дисциплины с {name = }")

        discipline = await cls._get_one_by_name(db=db, name=name)
        logger.debug(f"Дисциплина получена: {discipline}")

        return models.Discipline.from_orm(discipline)

    @classmethod
    async def create_discipline(cls, db: AsyncSession, discipline: models.DisciplineCreate) -> models.Discipline:
        """Создание дисциплины"""

        logger.debug(f"Запрос на создание дисциплины: {discipline =}")

        await cls._check_discipline_existence_with_name(db=db, name=discipline.name)

        db_discipline = await DisciplineDBService.create(db=db, discipline=discipline)
        await db.commit()
        await db.refresh(db_discipline)

        logger.info(f"Создана новая дисциплина: {discipline = }")

        return models.Discipline.from_orm(db_discipline)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.ScheduleDiscipline:
        """Получение дисциплины по идентификатору и проверка на существование"""

        discipline = await DisciplineDBService.get_discipline(db=db, id_=id_)
        if not discipline:
            logger.warning(f"Дисциплина с {id_ = } не найдена")
            raise HTTPException(status_code=404, detail=f"Дисциплина {id_} не найдена")
        return discipline

    @classmethod
    async def _get_one_by_name(cls, db: AsyncSession, name: str) -> tables.ScheduleDiscipline:
        """Получение дисциплины по имени и проверка на существование"""

        discipline = await DisciplineDBService.get_discipline_by_name(db=db, name=name)

        if not discipline:
            logger.warning(f"Дисциплина с {name = } не найдена")
            raise HTTPException(status_code=404, detail=f"Дисциплина {name} не найдена")
        return discipline

    @classmethod
    async def _check_discipline_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования дисциплины с name"""

        logger.debug(f"Проверяем существование дисциплины с {name = }")

        if await DisciplineDBService.get_discipline_by_name(db=db, name=name):
            logger.warning(f"Попытка создать дисциплину с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Дисциплина с таким названием уже существует")

        logger.debug(f"Дисциплины с {name = } ещё нет")
