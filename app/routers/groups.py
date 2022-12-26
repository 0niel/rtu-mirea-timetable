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
    response_model=models.Groups,
    response_description="Успешный возврат списка групп",
    status_code=status.HTTP_200_OK,
    description="Получить все учебные группы",
    summary="Получение всех учебных групп",
)
async def get(db: AsyncSession = Depends(get_session)):
    groups = await groups_service.get_groups(db=db)

    groups_by_institute_and_degree = {}

    for group in groups:
        if group.institute not in groups_by_institute_and_degree:
            groups_by_institute_and_degree[group.institute] = {}
        if group.degree not in groups_by_institute_and_degree[group.institute]:
            groups_by_institute_and_degree[group.institute][group.degree] = []
        groups_by_institute_and_degree[group.institute][group.degree].append(group.name)

    groups_list = []

    for institute, degrees in groups_by_institute_and_degree.items():
        groups_list.extend(
            models.GroupList(institute=institute, degree=degree, groups=groups) for degree, groups in degrees.items()
        )

    total = sum(len(groups.groups) for groups in groups_list)

    return models.Groups(total=total, result=groups_list)


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
