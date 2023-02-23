from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import TeacherDBService


class TeacherService:
    """Сервис для работы с преподавателями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества преподавателей"""
        logger.debug(f"Запрос на получение количества преподавателей, список преподавателей: {ids =}")

        teachers_count = await TeacherDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество преподавателей: {teachers_count}")

        return teachers_count

    @classmethod
    async def get_teachers(
        cls, db: AsyncSession, teachers_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Teacher]:
        """Получение списка всех преподавателей"""

        logger.debug("Запрос на получение списка преподавателей")

        teachers = await TeacherDBService.get_teachers(db=db, teachers_ids=teachers_ids, limit=limit, offset=offset)
        logger.debug(f"Преподавательы получены: {teachers}")

        return [models.Teacher.from_orm(teacher) for teacher in teachers]

    @classmethod
    async def get_teacher(cls, db: AsyncSession, id_: int) -> models.Teacher:
        """Получение преподавателя по идентификатору"""

        logger.debug(f"Запрос на получение преподавателя: {id_ = }")

        teacher = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Преподаватель получен: {teacher}")

        return models.Teacher.from_orm(teacher)

    @classmethod
    async def get_teacher_by_name(cls, db: AsyncSession, name: str) -> models.Teacher:
        """Получение дисциплины по имени"""

        logger.debug(f"Запрос на получение преподавателя с {name = }")

        teacher = await cls._get_one_by_name(db=db, name=name)
        logger.debug(f"Преподаватель получен: {teacher}")

        return models.Teacher.from_orm(teacher)

    @classmethod
    async def create_teacher(cls, db: AsyncSession, teacher: models.TeacherCreate) -> models.Teacher:
        """Создание преподавателя"""

        logger.debug(f"Запрос на создание преподавателя: {teacher =}")

        await cls._check_teacher_existence_with_name(db=db, name=teacher.name)

        db_teacher = await TeacherDBService.create(db=db, teacher=teacher)
        await db.commit()
        await db.refresh(db_teacher)

        logger.info(f"Создан новый преподаватель: {teacher = }")

        return models.Teacher.from_orm(db_teacher)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.Teacher:
        """Получение преподавателя по идентификатору и проверка на существование"""

        teacher = await TeacherDBService.get_teacher(db=db, id_=id_)
        if not teacher:
            logger.warning(f"Запрос несуществующуего преподавателя {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Преподаватель {id_} не найден")
        return teacher

    @classmethod
    async def _get_one_by_name(cls, db: AsyncSession, name: str) -> tables.Teacher:
        """Получение преподавателя по имени и проверка на существование"""

        teacher = await TeacherDBService.get_teacher_by_name(db=db, name=name)

        if not teacher:
            logger.warning(f"Преподаватель с {name = } не найден")
            raise HTTPException(status_code=404, detail=f"Преподаватель {name} не найден")
        return teacher

    @classmethod
    async def _check_teacher_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования преподавателя с name"""

        logger.debug(f"Проверяем существование преподавателя с {name = }")

        if await TeacherDBService.get_teacher_by_name(db=db, name=name):
            logger.warning(f"Попытка создать преподавателя с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Преподаватель с таким названием уже существует")

        logger.debug(f"Преподавательа с {name = } ещё нет")
