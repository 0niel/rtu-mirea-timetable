from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import LessonTypeDBService


class LessonTypeService:
    """Сервис для работы с звонокми."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества типов"""
        logger.debug(f"Запрос на получение количества типов занятий, список типов занятий: {ids =}")

        types_count = await LessonTypeDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество типов занятий: {types_count}")

        return types_count

    @classmethod
    async def get_types(
        cls, db: AsyncSession, types_ids: Optional[int], limit: int, offset: int
    ) -> List[models.LessonType]:
        """Получение списка всех типов"""

        logger.debug("Запрос на получение списка типов занятий")

        types = await LessonTypeDBService.get_types(db=db, types_ids=types_ids, limit=limit, offset=offset)
        logger.debug(f"Типы занятий получены: {types}")

        return [models.LessonType.from_orm(type_) for type_ in types]

    @classmethod
    async def get_type(cls, db: AsyncSession, id_: int) -> models.LessonType:
        """Получение звонока по идентификатору"""

        logger.debug(f"Запрос на получение типа занятия: {id_ = }")

        type_ = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Тип занятия получен: {type_}")

        return models.LessonType.from_orm(type_)

    @classmethod
    async def create_type(cls, db: AsyncSession, type_: models.LessonTypeCreate) -> models.LessonType:
        """Создание звонока"""

        logger.debug(f"Запрос на создание типа занятия: {type_ =}")

        await cls._check_type_existence_by_name(db=db, name=type_.name)

        db_type = await LessonTypeDBService.create(db=db, type_=type_)
        await db.commit()
        await db.refresh(db_type)

        logger.info(f"Создан новый тип занятия: {type_ = }")

        return models.LessonType.from_orm(db_type)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.LessonType:
        """Получение звонока по идентификатору и проверка на существование"""

        type = await LessonTypeDBService.get_type(db=db, id_=id_)
        if not type:
            logger.warning(f"Запрос несуществующего типа занятия {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Тип занятия {id_} не найден")
        return type

    @classmethod
    async def _check_type_existence_by_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования звонока с name"""

        logger.debug(f"Проверяем существование типа занятия с {name = }")

        if await LessonTypeDBService.get_type_by_name(db=db, name=name):
            logger.warning(f"Попытка создать тип занятия с уже существующим: {name = }")
            raise HTTPException(status_code=409, detail=f"Тип занятия с таким {name = } уже существует")

        logger.debug(f"Типа занятия с {name = } ещё нет")
