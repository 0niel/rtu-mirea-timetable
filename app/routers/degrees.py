from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import DegreeService

router = APIRouter(prefix=config.PREFIX)


@router.get(
    "/degrees",
    response_model=list[models.Degree],
    response_description="Список степеней успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все степени РТУ МИРЭА",
    summary="Получение всех степеней РТУ МИРЭА",
)
async def get_degrees(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id степеней"),
    limit: int = Query(10, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Degree]:
    return await DegreeService.get_degrees(db=db, degrees_ids=ids, limit=limit, offset=offset)


@router.get(
    "/degrees/{id}",
    response_model=models.Degree,
    response_description="Степень успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить степень по id и вернуть его",
    summary="Получение степени по id",
)
async def get_degree(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id степени", alias="id"),
) -> models.Degree:
    return await DegreeService.get_degree(db=db, id_=id_)
