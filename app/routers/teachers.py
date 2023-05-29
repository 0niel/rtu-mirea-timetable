from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import TeacherService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/teachers",
    response_model=list[models.Teacher],
    response_description="Список преподавателей успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить всех преподавателей РТУ МИРЭА",
    summary="Получение всех преподавателя РТУ МИРЭА",
)
async def get_teachers(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id преподавателей"),
    limit: int = Query(30, description="", ge=1, le=5000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Teacher]:
    return await TeacherService.get_teachers(db=db, teachers_ids=ids, limit=limit, offset=offset)


@router.get(
    "/teachers/{id}",
    response_model=models.Teacher,
    response_description="Преподаватель успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить преподавателя по id и вернуть его",
    summary="Получение преподавателя по id",
)
async def get_teacher(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id преподавателя", alias="id"),
) -> models.Teacher:
    return await TeacherService.get_teacher(db=db, id_=id_)


@router.get(
    "/teachers/search/{name}",
    response_model=list[models.Teacher],
    response_description="Преподаватели успешно получены и возвращены в ответе",
    status_code=status.HTTP_200_OK,
    description="Поиск преподавателей по имени",
    summary="Поиск преподавателей по имени",
)
async def search_teacher_by_name(
    db: AsyncSession = Depends(get_session),
    name: str = Path(..., description="Имя преподавателя"),
) -> list[models.Teacher]:
    return await TeacherService.search_teachers(db=db, name=name)
