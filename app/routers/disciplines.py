from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import DisciplineService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/discipline",
    response_model=list[models.Discipline],
    response_description="Список дисциплин успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все дисциплины РТУ МИРЭА",
    summary="Получение всех дисциплин РТУ МИРЭА",
)
async def get_disciplines(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id дисциплин"),
    limit: int = Query(10, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Discipline]:
    return await DisciplineService.get_disciplines(db=db, disciplines_ids=ids, limit=limit, offset=offset)


@router.get(
    "/discipline/{id}",
    response_model=models.Discipline,
    response_description="Дисциплина успешно получена и возвращена в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить дисциплину по id и вернуть ее",
    summary="Получение дисциплины по id",
)
async def get_discipline(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id дисциплины", alias="id"),
) -> models.Discipline:
    return await DisciplineService.get_discipline(db=db, id_=id_)


@router.get(
    "/discipline/name/{name}",
    response_model=models.Discipline,
    response_description="Дисциплина успешно получена и возвращена в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить дисциплину по name и вернуть ее",
    summary="Получение дисциплины по name",
)
async def get_discipline_by_name(
    db: AsyncSession = Depends(get_session),
    name: str = Path(..., description="Имя дисциплины"),
):
    return await DisciplineService.get_discipline_by_name(db=db, name=name)
