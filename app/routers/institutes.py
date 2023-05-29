from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import InstituteService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/institutes",
    response_model=list[models.Institute],
    response_description="Список институтов успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все институты РТУ МИРЭА",
    summary="Получение всех институтов РТУ МИРЭА",
)
async def get_institutes(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id институтов"),
    limit: int = Query(10, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Institute]:
    return await InstituteService.get_institutes(db=db, institutes_ids=ids, limit=limit, offset=offset)


@router.get(
    "/institutes/{id}",
    response_model=models.Institute,
    response_description="Институт успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить институт по id и вернуть его",
    summary="Получение института по id",
)
async def get_institute(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id института", alias="id"),
) -> models.Institute:
    return await InstituteService.get_institute(db=db, id_=id_)
