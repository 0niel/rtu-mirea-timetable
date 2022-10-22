from typing import Any

from fastapi import APIRouter

import app.crud.crud_schedule as schedule_crud
from app import schemas

router = APIRouter()


@router.get("", response_model=list[schemas.CampusModel], status_code=200)
async def get_campuses() -> Any:
    """
    Get all campuses.
    """
    return [
        schemas.CampusModel.from_orm(campus)
        for campus in await schedule_crud.get_campuses()
    ]


@router.get("/{campus_id}/rooms", response_model=list[schemas.RoomModel], status_code=200)
async def get_campus_rooms(campus_id: int) -> Any:
    """
    Get all rooms for campus.
    """
    return [
        schemas.RoomModel.from_orm(room)
        for room in await schedule_crud.get_campus_rooms(campus_id)
    ]
