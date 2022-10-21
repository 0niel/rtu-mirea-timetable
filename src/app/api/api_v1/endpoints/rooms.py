from typing import Any

from fastapi import APIRouter

import app.crud.crud_schedule as schedule_crud
from app import schemas

router = APIRouter()


@router.get(
    "/room-lessons/{room_id}", response_model=list[schemas.LessonModel], status_code=200
)
async def get_room_lessons(
    room_id: int,
) -> Any:
    """
    Get room lessons.
    """
    return [
        schemas.LessonModel.from_orm(room)
        for room in await schedule_crud.get_lessons_by_room(room_id)
    ]


@router.get(
    "/search-rooms/{name}", response_model=list[schemas.RoomModel], status_code=200
)
async def search_rooms(
    name: str,
) -> Any:
    """
    Search rooms.
    """
    return [
        schemas.RoomModel.from_orm(room)
        for room in await schedule_crud.search_rooms(name)
    ]


@router.get("/workload/{room_id}", response_model=schemas.Msg, status_code=200)
async def get_workload(
    room_id: int,
) -> Any:
    """
    Get workload.
    """
    workload = await schedule_crud.get_room_workload(room_id)
    return schemas.Msg(msg=workload)
