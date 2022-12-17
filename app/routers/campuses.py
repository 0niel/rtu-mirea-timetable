from typing import Any

from fastapi import APIRouter

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get("", response_model=list[models.Campus], status_code=200)
async def get_campuses() -> Any:
    """
    Get all campuses.
    """
    return [models.Campus.from_orm(campus) for campus in await schedule_crud.get_campuses()]


@router.get("/{campus_id}/rooms", response_model=list[models.Campus], status_code=200)
async def get_campus_rooms(campus_id: int) -> Any:
    """
    Get all rooms for campus.
    """
    return [models.Campus.from_orm(room) for room in await schedule_crud.get_campus_rooms(campus_id)]
