from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import PeriodService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/period",
    response_model=list[models.Period],
    response_description="Список периодов успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все периоды РТУ МИРЭА",
    summary="Получение всех периодов РТУ МИРЭА",
)
async def get_periods(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id периодов"),
    limit: int = Query(10, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Period]:
    return await PeriodService.get_periods(db=db, periods_ids=ids, limit=limit, offset=offset)


@router.get(
    "/period/{id}",
    response_model=models.Period,
    response_description="Период успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить период по id и вернуть его",
    summary="Получение периода по id",
)
async def get_period(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id периода", alias="id"),
) -> models.Period:
    return await PeriodService.get_period(db=db, id_=id_)
