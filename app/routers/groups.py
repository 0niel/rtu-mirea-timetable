from fastapi import APIRouter

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/groups",
    status_code=200,
    description="Get all groups",
)
async def get_groups():
    return await schedule_crud.get_groups()


@router.get(
    "/{name}",
    response_model=models.Group,
    status_code=200,
    description="Get parser by group",
)
async def get_group_schedule(
    name: str,
):
    return await schedule_crud.get_group(name)
