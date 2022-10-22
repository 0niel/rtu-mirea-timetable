from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import APIRouter, Query

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
    Get all lessons for room.
    """
    return [
        schemas.LessonModel.from_orm(room)
        for room in await schedule_crud.get_lessons_by_room(room_id)
    ]

# Moscow timezone
tz = timezone(timedelta(hours=3))

@router.get(
    "/room-lessons-date/{room_id}/{date}", response_model=list[schemas.LessonModel], status_code=200,
)
async def get_rooms_lesson_by_room_and_date(
        room_id: int,
        date: str = Query(..., description="Date in format: YYYY-MM-DD"),
) -> Any:
    """
    Get all lessons for room by date. Date must be in format YYYY-MM-DD.
    """

    # Convert date to datetime
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return {"msg": "Incorrect data format, should be YYYY-MM-DD"}

    return [
        schemas.LessonModel.from_orm(room)
        for room in await schedule_crud.get_lessons_by_room_and_date(room_id, date)
    ]


@router.get(
    "/room-lessons-week/{room_id}/{week}", response_model=list[schemas.LessonModel], status_code=200
)
async def get_rooms_lesson_by_room_and_week(
        room_id: int,
        week: int,
) -> Any:
    """
    Get all lessons for room by date. Date must be in format YYYY-MM-DD.
    """
    return [
        schemas.LessonModel.from_orm(room)
        for room in await schedule_crud.get_lessons_by_room_and_week(room_id, week)
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


@router.get("/campuses", response_model=list[schemas.CampusModel], status_code=200)
async def get_campuses() -> Any:
    """
    Get all campuses.
    """
    return [
        schemas.CampusModel.from_orm(campus)
        for campus in await schedule_crud.get_campuses()
    ]


@router.get("/campuses/{campus_id}/rooms", response_model=list[schemas.RoomModel], status_code=200)
async def get_campus_rooms(campus_id: int) -> Any:
    """
    Get all rooms for campus.
    """
    return [
        schemas.RoomModel.from_orm(room)
        for room in await schedule_crud.get_campus_rooms(campus_id)
    ]
