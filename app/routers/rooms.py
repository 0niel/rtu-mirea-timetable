from datetime import datetime
from typing import Any, List, Optional, Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import RoomService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/rooms/statuses",
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
    ids: List[int] = Query(None, description="Id аудиторий"),
) -> Any:
    date_time = date_time.replace(tzinfo=None)
    return await schedule_crud.get_rooms_statuses(db, ids, date_time)




@router.get(
    "/rooms/workload",
    status_code=status.HTTP_200_OK,
    description="Получить загруженность аудиторий",
    summary="Получение загруженности аудиторий",
)
async def get_rooms_workload(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id аудиторий"),
):
    workload = []
    for room_id in ids:
        workload.append(
            {
                "id": room_id,
                "workload": await schedule_crud.get_room_workload(db, room_id),
            }
        )

    return workload

@router.get(
    "/rooms",
    response_model=list[models.Room],
    response_description="Список аудиторий успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории РТУ МИРЭА",
    summary="Получение всех аудиторий РТУ МИРЭА",
)
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
