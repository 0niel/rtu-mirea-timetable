from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import LessonDBService


class LessonService:
    """Сервис для работы с занятиями."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества занятий"""
        logger.debug(f"Запрос на получение количества занятий, список занятий: {ids =}")

        lessons_count = await LessonDBService.get_pagination_count(db=db, ids=ids)
        logger.debug(f"Количество занятий: {lessons_count}")

        return lessons_count

    @classmethod
    async def get_lessons(
        cls, db: AsyncSession, lessons_ids: Optional[int], limit: int, offset: int
    ) -> List[models.Lesson]:
        """Получение списка всех занятий"""

        logger.debug("Запрос на получение списка занятий")

        lessons = await LessonDBService.get_lessons(db=db, lessons_ids=lessons_ids, limit=limit, offset=offset)
        logger.debug(f"Занятия получены: {lessons}")

        return [models.Lesson.from_orm(lesson) for lesson in lessons]

    @classmethod
    async def get_lesson(cls, db: AsyncSession, id_: int) -> models.Lesson:
        """Получение занятия по идентификатору"""

        logger.debug(f"Запрос на получение занятия: {id_ = }")

        lesson = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Занятие получено: {lesson}")

        return models.Lesson.from_orm(lesson)

    @classmethod
    async def get_lessons_by_room_id(
        cls, db: AsyncSession, room_id: int, week: Optional[int], date: Optional[str]
    ) -> List[models.Lesson]:
        """Получение занятий по идентификатору аудитории"""

        logger.debug(f"Запрос на получение занятия: {room_id = }")

        lessons = await LessonDBService.get_lessons_by_room_id(db=db, room_id=room_id, week=week, date=date)
        logger.debug(f"Занятия получены: {lessons}")

        return [models.Lesson.from_orm(lesson) for lesson in lessons]

    @classmethod
    async def create_lesson(cls, db: AsyncSession, lesson: models.LessonCreate) -> models.Lesson:
        """Создание занятия"""

        logger.debug(f"Запрос на создание занятия: {lesson =}")

        await cls._check_lesson_existence(db=db, lesson=lesson)

        db_lesson = await LessonDBService.create(db=db, lesson=lesson)
        await db.commit()
        await db.refresh(db_lesson)

        logger.info(f"Создано новое занятие: {lesson = }")

        return models.Lesson.from_orm(db_lesson)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.Lesson:
        """Получение занятия по идентификатору и проверка на существование"""

        lesson = await LessonDBService.get_lesson(db=db, id_=id_)
        if not lesson:
            logger.warning(f"Запрос несуществующего занятия {id_} для взаимодейстия")
            raise HTTPException(status_code=404, detail=f"Занятие {id_} не найдено")
        return lesson

    @classmethod
    async def _check_lesson_existence(cls, db: AsyncSession, lesson: models.LessonCreate) -> None:
        """Проверка существования занятия"""

        logger.debug(
            f"Проверяем существование занятия с "
            f"{lesson.teachers_id = } {lesson.lesson_type_id = } {lesson.group_id = } "
            f"{lesson.discipline_id = } {lesson.room_id = } {lesson.weeks = } "
            f"{lesson.call_id = } {lesson.subgroup = }"
        )

        if await LessonDBService.get_lesson_by_params(
            db=db,
            teachers_id=lesson.teachers_id,
            lesson_type_id=lesson.lesson_type_id,
            group_id=lesson.group_id,
            discipline_id=lesson.discipline_id,
            room_id=lesson.room_id,
            weeks=lesson.weeks,
            call_id=lesson.call_id,
            subgroup=lesson.subgroup,
        ):
            logger.warning(
                f"Попытка создать занятия с уже существующими: "
                f"{lesson.teachers_id = } {lesson.lesson_type_id = } {lesson.group_id = } "
                f"{lesson.discipline_id = } {lesson.room_id = } {lesson.weeks = } "
                f"{lesson.call_id = } {lesson.subgroup = }"
            )
            raise HTTPException(status_code=409, detail="Занятие с такими параметрами уже существует")

        logger.debug(
            f"Занятия с {lesson.teachers_id = } {lesson.lesson_type_id = } {lesson.group_id = } "
            f"{lesson.discipline_id = } {lesson.room_id = } {lesson.weeks = } "
            f"{lesson.call_id = } {lesson.subgroup = } ещё нет"
        )
