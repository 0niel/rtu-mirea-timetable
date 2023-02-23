from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import TeacherService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/teacher",
    response_model=list[models.Teacher],
    response_description="Список преподавателей успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить всех преподавателей РТУ МИРЭА",
    summary="Получение всех преподавателя РТУ МИРЭА",
)
async def get_teachers(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id преподавателей"),
    limit: int = Query(10, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Teacher]:
    return await TeacherService.get_teachers(db=db, teachers_ids=ids, limit=limit, offset=offset)


@router.get(
    "/teacher/{id}",
    response_model=models.Teacher,
    response_description="Преподавателя успешно получен и возвращен в ответе",
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
    "/teacher/search/{name}",
    response_model=list[models.Teacher],
    status_code=200,
    description="Поиск преподавателя по имени",
    summary="Поиск преподавателя по имени",
)
async def search_teacher_by_name(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> Any:
    if len(name) < 3:
        raise HTTPException(status_code=400, detail="Имя должно быть не менее 3 символов")

    return [models.Teacher.from_orm(teacher) for teacher in await schedule_crud.search_teachers(session, name)]
