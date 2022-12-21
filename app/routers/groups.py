from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.groups as groups_service
from app import models
from app.config import config
from app.database.connection import get_session

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/groups",
    response_model=list[models.GroupTiny],
    response_description="Успешный возврат списка групп",
    status_code=status.HTTP_200_OK,
    description="Получить все учебные группы",
    summary="Получение всех учебных групп",
)
async def get(db: AsyncSession = Depends(get_session)):
    return [models.GroupTiny.from_orm(group) for group in await groups_service.get_groups(db=db)]


@router.get(
    "/groups/{name}",
    response_model=models.Group,
    status_code=200,
    description="Получить группу и её расписание по названию",
)
async def get_group_schedule(
    db: AsyncSession = Depends(get_session),
    name: str = Path(None, description="Имя группы"),
):
    return await groups_service.get_group(db=db, name=name)
