from typing import Any

from fastapi import APIRouter

import app.services.crud_schedule as schedule_crud
from app import schemas

router = APIRouter()


@router.get("", response_model=list[schemas.Campus], status_code=200)
async def get_campuses() -> Any:
    """
    Get all campuses.
    """
    return [schemas.Campus.from_orm(campus) for campus in await schedule_crud.get_campuses()]


@router.get("/{campus_id}/rooms", response_model=list[schemas.Campus], status_code=200)
async def get_campus_rooms(campus_id: int) -> Any:
    """
    Get all rooms for campus.
    """
    return [schemas.Campus.from_orm(room) for room in await schedule_crud.get_campus_rooms(campus_id)]
