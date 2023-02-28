from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import LessonCallService, LessonService, LessonTypeService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/schedule",
    response_model=list[models.Lesson],
    response_description="Список занятий успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все занятия РТУ МИРЭА",
    summary="Получение всех занятий РТУ МИРЭА",
)
async def get_lessons(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id занятий"),
    limit: int = Query(100, description="", ge=1, le=5000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Lesson]:
    return await LessonService.get_lessons(db=db, lessons_ids=ids, limit=limit, offset=offset)


@router.get(
    "/schedule/id/{id}",
    response_model=models.Lesson,
    response_description="Занятие успешно получено и возвращено в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить занятие по id и вернуть его",
    summary="Получение занятия по id",
)
async def get_lesson(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id занятия", alias="id"),
) -> models.Lesson:
    return await LessonService.get_lesson(db=db, id_=id_)


@router.get(
    "/schedule/room/{id}",
    response_model=list[models.Lesson],
    response_description="Cписок занятий аудиторий успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все занятия аудитории по id и вернуть их",
    summary="Получение всех занятий аудитории по id",
)
async def get_lessons_by_room(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id аудитории", alias="id"),
    week: int = Query(None, description="Номер недели"),
    date: str = Query(None, description="Дата в формате: YYYY-MM-DD"),
) -> list[models.Lesson]:
    return await LessonService.get_lessons_by_room_id(db=db, room_id=id_, week=week, date=date)


@router.get(
    "/schedule/call",
    response_model=list[models.LessonCall],
    response_description="Cписок звонков успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить список звонков и вернуть его",
    summary="Получение списка звонков",
)
async def get_lessons_calls(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id звонков"),
    limit: int = Query(100, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.LessonCall]:
    return await LessonCallService.get_calls(db=db, calls_ids=ids, limit=limit, offset=offset)


@router.get(
    "/schedule/call/{id}",
    response_model=models.LessonCall,
    response_description="Тип занятия успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить звонок по id и вернуть его",
    summary="Получение звонка по id",
)
async def get_lessons_call(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id звонка", alias="id"),
) -> models.LessonCall:
    return await LessonCallService.get_call(db=db, id_=id_)


@router.get(
    "/schedule/type",
    response_model=list[models.LessonType],
    response_description="Cписок типов занятий успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все типы занятий и вернуть их",
    summary="Получение всех типов занятий",
)
async def get_lessons_types(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id типов занятий"),
    limit: int = Query(100, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.LessonType]:
    return await LessonTypeService.get_types(db=db, types_ids=ids, limit=limit, offset=offset)


@router.get(
    "/schedule/type/{id}",
    response_model=models.LessonType,
    response_description="Тип занятия успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить тип занятия по id и вернуть его",
    summary="Получение типа занятия по id",
)
async def get_lessons_type(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id типа занятия", alias="id"),
) -> models.LessonType:
    return await LessonTypeService.get_type(db=db, id_=id_)
