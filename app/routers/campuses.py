from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import CampusService

router = APIRouter(prefix=config.PREFIX)


@router.get(
    "/campuses",
    response_model=list[models.Campus],
    response_description="Список кампусов успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все кампусы РТУ МИРЭА",
    summary="Получение всех кампусов РТУ МИРЭА",
)
async def get_campuses(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id кампусов"),
    limit: int = Query(10, description="", ge=1, le=1000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Campus]:
    return await CampusService.get_campuses(db=db, campuses_ids=ids, limit=limit, offset=offset)


@router.get(
    "/campuses/{id}",
    response_model=models.Campus,
    response_description="Кампус успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить кампус по id и вернуть его",
    summary="Получение кампуса по id",
)
async def get_campus(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id кампуса", alias="id"),
) -> models.Campus:
    return await CampusService.get_campus(db=db, id_=id_)


@router.get(
    "/campuses/{id}/rooms",
    response_model=list[models.Room],
    response_description="Список аудиторий указанного кампуса успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории по кампусу",
    summary="Получение всех аудитории по кампусу",
)
async def get_rooms(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id кампуса", alias="id"),
) -> list[models.Room]:
    return await CampusService.get_campus_rooms(db=db, campus_id=id_)
