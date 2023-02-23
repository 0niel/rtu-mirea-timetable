from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import LessonCallDBService


class LessonCallService:
    """Сервис для работы с звонокми."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества звонков"""
        logger.debug(f"Запрос на получение количества звонков, список звонков: {ids =}")

        calls_count = await LessonCallDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество звонков: {calls_count}")

        return calls_count

    @classmethod
    async def get_calls(
        cls, db: AsyncSession, calls_ids: Optional[int], limit: int, offset: int
    ) -> List[models.LessonCall]:
        """Получение списка всех звонков"""

        logger.debug("Запрос на получение списка звонков")

        calls = await LessonCallDBService.get_calls(db=db, calls_ids=calls_ids, limit=limit, offset=offset)
        logger.debug(f"Звоноки получены: {calls}")

        return [models.LessonCall.from_orm(call) for call in calls]

    @classmethod
    async def get_call(cls, db: AsyncSession, id_: int) -> models.LessonCall:
        """Получение звонока по идентификатору"""

        logger.debug(f"Запрос на получение звонока: {id_ = }")

        call = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Звонок получен: {call}")

        return models.LessonCall.from_orm(call)

    @classmethod
    async def create_call(cls, db: AsyncSession, call: models.LessonCallCreate) -> models.LessonCall:
        """Создание звонока"""

        logger.debug(f"Запрос на создание звонока: {call =}")

        await cls._check_call_existence(db=db, call=call)

        db_call = await LessonCallDBService.create(db=db, call=call)
        await db.commit()
        await db.refresh(db_call)

        logger.info(f"Создан новый звонок: {call = }")

        return models.LessonCall.from_orm(db_call)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.LessonCall:
        """Получение звонока по идентификатору и проверка на существование"""

        call = await LessonCallDBService.get_call(db=db, id_=id_)
        if not call:
            logger.warning(f"Запрос несуществующего звонка {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Звонок {id_} не найден")
        return call

    @classmethod
    async def _check_call_existence(cls, db: AsyncSession, call: models.LessonCallCreate) -> None:
        """Проверка существования звонока"""

        logger.debug(f"Проверяем существование звонка с {call.num = } {call.time_start = } {call.time_end = }")

        if await LessonCallDBService.get_call_by_params(
            db=db, num=call.num, time_start=call.time_start, time_end=call.time_end
        ):
            logger.warning(
                f"Попытка создать звонок с уже существующими: {call.num = } {call.time_start = } {call.time_end = }"
            )
            raise HTTPException(status_code=409, detail="Звонок с такими параметрами уже существует")

        logger.debug(f"Звонока с {call.num = } {call.time_start = } {call.time_end = } ещё нет")
