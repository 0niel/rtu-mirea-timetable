from typing import Any

from fastapi import APIRouter

import app.services.crud_schedule as schedule_crud
from app import schemas

router = APIRouter()

@router.get(
    "/groups",
    status_code=200,
    description="Get all groups",
)
async def get_groups(
):
    return await schedule_crud.get_groups()


@router.get(
    "/{name}",
    response_model=schemas.Group,
    status_code=200,
    description="Get schedule by group",
)
async def get_group_schedule(
    name: str,
):
    schedule = await schedule_service.get_schedule(name)
    return schedule