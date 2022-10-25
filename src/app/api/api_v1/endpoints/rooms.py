import io
from datetime import datetime, timezone, timedelta
from typing import Any

import numpy as np
from fastapi.responses import StreamingResponse
import pandas as pd
from fastapi import APIRouter, Query
from starlette.responses import FileResponse

import app.crud.crud_schedule as schedule_crud
from app import schemas

router = APIRouter()


@router.get(
    "/lessons/{room_id}", response_model=list[schemas.LessonModel], status_code=200
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
    "/lessons-by-date/{room_id}/{date}", response_model=list[schemas.LessonModel], status_code=200,
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
    "/lessons-by-week/{room_id}/{week}", response_model=list[schemas.LessonModel], status_code=200
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
    "/search/{name}", response_model=list[schemas.RoomModel], status_code=200
)
async def search_rooms(
        name: str,
) -> Any:
    """
    Search rooms.
    """
    return [
        schemas.RoomModel.from_orm(room)
        for room in await schedule_crud.search_room(name)
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


@router.get("/statuses/", status_code=200)
async def get_statuses(
        date_time: datetime = Query(datetime.now(), description="Datetime in ISO format. Example: "
                                                                "2021-09-01T00:00:00+03:00"),
        *,
        rooms: list[str] = Query(..., description="List of rooms names. Example: ['А-101', 'А-102']"),
) -> Any:
    """
    Get statuses.
    """
    date_time = date_time.replace(tzinfo=None)
    return await schedule_crud.get_rooms_statuses(rooms, date_time)


@router.get("/download")
async def download_rooms_data():
    rooms = await schedule_crud.get_all_rooms()

    df = pd.DataFrame(columns=['номер комнаты', 'корпус', 'день недели', 'номер пары', 'неделя', 'дисциплина', 'группа'])

    all_rooms_data = []
    for room in rooms:
        campus = room.campus.name if room.campus else None

        for lesson in room.lessons:
            all_rooms_data.extend({'номер комнаты': room.name, 'корпус': campus, 'день недели': lesson.weekday, 'номер пары': lesson.calls.num, 'неделя': week, 'дисциплина': lesson.discipline.name, 'группа': lesson.group.name} for week in lesson.weeks)

    df = df.append(all_rooms_data, ignore_index=True)
    df.to_excel('rooms.xlsx', index=False)

    return FileResponse(path='rooms.xlsx', filename='rooms.xlsx')