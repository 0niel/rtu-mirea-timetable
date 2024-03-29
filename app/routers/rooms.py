from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config
from app.database import tables
from app.database.connection import get_session
from app.models import RoomStatusGet, WorkloadGet
from app.services.api import RoomService
from app.utils.cache import key_builder_exclude_db

router = APIRouter(prefix=config.PREFIX)


@router.get(
    "/rooms/statuses",
    response_model=List[RoomStatusGet],
    response_description="Статусы аудиторий получены и возвращены в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить статусы аудиторий (свободна/занята) для указанного времени",
    summary="Получение статусов аудиторий",
)
async def get_statuses(
    db: AsyncSession = Depends(get_session),
    date_time: datetime = Query(
        datetime.now(),
        description="Дата и время в ISO формате. Пример: 2021-09-01T00:00:00+03:00",
    ),
    campus_id: int = Query(..., description="Id кампуса"),
) -> List[RoomStatusGet]:
    date_time = date_time.replace(tzinfo=None)
    return await schedule_crud.get_rooms_statuses(db=db, time=date_time, campus_id=campus_id)


@router.get(
    "/rooms/statuses/{id}",
    response_model=RoomStatusGet,
    response_description="Статусы аудиторий получены и возвращены в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить статусы аудиторий (свободна/занята) для указанного времени",
    summary="Получение статусов аудиторий",
)
async def get_status_by_id(
    db: AsyncSession = Depends(get_session),
    date_time: datetime = Query(
        datetime.now(),
        description="Дата и время в ISO формате. Пример: 2021-09-01T00:00:00+03:00",
    ),
    id: int = Path(..., description="Id аудитории"),
) -> RoomStatusGet:
    date_time = date_time.replace(tzinfo=None)
    return await schedule_crud.get_rooms_status(db=db, time=date_time, room_id=id)


@router.get(
    "/rooms/workload",
    status_code=status.HTTP_200_OK,
    response_model=List[WorkloadGet],
    description="Получить загруженность аудиторий",
    summary="Получение загруженности аудиторий",
)
@cache(namespace="rooms", expire=60 * 60 * 24, key_builder=key_builder_exclude_db)
async def get_rooms_workload(
    db: AsyncSession = Depends(get_session),
    campus_id: int = Query(..., description="Id кампуса"),
) -> List[WorkloadGet]:
    sttm = select(tables.Room).where(tables.Room.campus_id == campus_id)

    rows = await db.stream(sttm)

    workload = []
    async for row in rows:
        for room in row:
            workload.append(WorkloadGet(id=room.id, workload=await schedule_crud.get_room_workload(db, room.id)))

    return workload


@router.get(
    "/rooms/workload/{id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkloadGet,
    description="Получить загруженность аудиторий",
    summary="Получение загруженности аудиторий",
)
async def get_room_workload(
    db: AsyncSession = Depends(get_session),
    id: int = Path(..., description="Id аудитории"),
) -> WorkloadGet:
    room = (await db.execute(select(tables.Room).where(tables.Room.id == id))).scalar()
    return WorkloadGet(id=room.id, workload=await schedule_crud.get_room_workload(db, room.id))


@router.get(
    "/rooms",
    response_model=list[models.Room],
    response_description="Список аудиторий успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории РТУ МИРЭА",
    summary="Получение всех аудиторий РТУ МИРЭА",
)
@cache(namespace="rooms", expire=60 * 60 * 24, key_builder=key_builder_exclude_db)
async def get_rooms(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id аудиторий"),
    campus_id: Optional[int] = Query(None, description="Id кампуса"),
    limit: int = Query(30, description="", ge=1, le=5000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Room]:
    return await RoomService.get_rooms(db=db, rooms_ids=ids, campus_id=campus_id, limit=limit, offset=offset)


@router.get(
    "/rooms/{id}",
    response_model=models.Room,
    response_description="Аудитория успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить аудиторию по id и вернуть его",
    summary="Получение аудитории по id",
)
async def get_room(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id аудитории", alias="id"),
) -> models.Room:
    return await RoomService.get_room(db=db, id_=id_)


@router.get(
    "/rooms/search/{name}",
    response_model=list[models.Room],
    response_description="Аудитория найдена и возвращена в ответе",
    status_code=status.HTTP_200_OK,
    description="Поиск аудитории по названию аудитории (по подстроке)",
    summary="Поиск аудитории",
)
async def search_rooms(
    db: AsyncSession = Depends(get_session),
    name: str = Path(..., description="Номер аудитории"),
) -> list[models.Room]:
    return [models.Room.from_orm(room) for room in await schedule_crud.search_room(db, name)]


@router.get(
    "/rooms/info/{id}",
    response_model=models.RoomInfo,
    response_description="Подробная информация об аудитории получена и возвращена в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить подробную информацию об аудитории",
    summary="Получение подробной информации об аудитории",
)
async def get_info(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id аудитории", alias="id"),
) -> models.RoomInfo:
    return await schedule_crud.get_room_info(db, id_)
