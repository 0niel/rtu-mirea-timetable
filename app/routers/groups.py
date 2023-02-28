from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import GroupService
from app.utils.cache import key_builder_exclude_db

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/group",
    response_model=models.Groups,
    response_description="Успешный возврат списка групп",
    status_code=status.HTTP_200_OK,
    description="Получить все учебные группы",
    summary="Получение всех учебных групп",
)
@cache(namespace="groups", expire=60 * 60 * 24, key_builder=key_builder_exclude_db)
async def get_groups(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id групп"),
    limit: int = Query(30, description="", ge=1, le=5000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
):
    return await GroupService.get_groups(db=db, groups_ids=ids, limit=limit, offset=offset)


@router.get(
    "/group/{id}",
    response_model=models.Group,
    response_description="Группа успешно получена и возвращена в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить группу по id и вернуть её",
    summary="Получение группы по id",
)
async def get_group(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id института", alias="id"),
) -> models.Group:
    return await GroupService.get_group(db=db, id_=id_)


@router.get(
    "/group/name/{name}",
    response_model=models.Group,
    response_description="Группа успешно получена и возвращена в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить группу и её расписание по названию",
    summary="Получение группы и её расписания по названию",
)
@cache(namespace="group", expire=60 * 60, key_builder=key_builder_exclude_db)
async def get_group_schedule(
    db: AsyncSession = Depends(get_session),
    name: str = Path(..., description="Имя группы"),
) -> models.Group:
    return await GroupService.get_group_by_name(db=db, name=name)
