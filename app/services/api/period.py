from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.services.db import PeriodDBService


class PeriodService:
    """Сервис для работы с периодами."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества периодов"""
        logger.debug(f"Запрос на получение количества периодов, список периодов: {ids =}")

        periods_count = await PeriodDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество периодов: {periods_count}")

        return periods_count

    @classmethod
    async def get_periods(
        cls, db: AsyncSession, periods_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Period]:
        """Получение списка всех периодов"""

        logger.debug("Запрос на получение списка периодов")

        periods = await PeriodDBService.get_periods(db=db, periods_ids=periods_ids, limit=limit, offset=offset)
        logger.debug(f"Периоды получены: {periods}")

        return [models.Period.from_orm(period) for period in periods]

    @classmethod
    async def get_period(cls, db: AsyncSession, id_: int) -> models.Period:
        """Получение периода по идентификатору"""

        logger.debug(f"Запрос на получение периода: {id_ = }")

        period = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Период получен: {period}")

        return models.Period.from_orm(period)

    @classmethod
    async def create_period(cls, db: AsyncSession, period: models.PeriodCreate) -> models.Period:
        """Создание периода"""

        logger.debug(f"Запрос на создание периода: {period =}")

        await cls._check_period_existence(db=db, period=period)

        db_period = await PeriodDBService.create(db=db, period=period)
        await db.commit()
        await db.refresh(db_period)

        logger.info(f"Создан новый период: {period = }")

        return models.Period.from_orm(db_period)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> models.Period:
        """Получение периода по идентификатору и проверка на существование"""

        period = await PeriodDBService.get_period(db=db, id_=id_)
        if not period:
            logger.warning(f"Запрос несуществующуего периода {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Период {id_} не найден")
        return period

    @classmethod
    async def _check_period_existence(cls, db: AsyncSession, period: models.PeriodCreate) -> None:
        """Проверка существования периода"""

        logger.debug(
            f"Проверяем существование периода с {period.year_start = } {period.year_end = } {period.semestr = }"
        )

        if await PeriodDBService.get_period_by_params(
            db=db, year_start=period.year_start, year_end=period.year_end, semester=period.semester
        ):
            logger.warning(
                f"Попытка создать период с уже существующими: "
                f"{period.year_start = } {period.year_end = } {period.semestr = }"
            )
            raise HTTPException(status_code=409, detail="Переиод с такими параметрами уже существует")

        logger.debug(f"Периода с {period.year_start = } {period.year_end = } {period.semestr = } ещё нет")
