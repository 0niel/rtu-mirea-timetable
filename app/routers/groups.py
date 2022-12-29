from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.groups as groups_service
from app import models
from app.config import config
from app.database.connection import get_session

router = APIRouter(prefix=config.BACKEND_PREFIX)
templates = Jinja2Templates(directory="app/templates")


def groupy_groups_to_response_model(groups):
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


@router.get("/", response_class=HTMLResponse)
async def groups_html(request: Request, db: AsyncSession = Depends(get_session)):
    groups = await groups_service.get_groups(db=db)

    response_model = groupy_groups_to_response_model(groups)

    return templates.TemplateResponse("groups.html", {"request": request, "groups": response_model})


@router.get("/group-schedule/{name}", response_class=HTMLResponse)
async def group_schedule_html(
    request: Request, name: str = Path(None, description="Имя группы"), 
    db: AsyncSession = Depends(get_session)
):

    group = await groups_service.get_group(db=db, name=name)
    group = models.Group.from_orm(group)

    mode = request.query_params.get("mode")
    week = request.query_params.get("week")

    if mode or week:
        if mode == "week" or week:
            week = int(week) if week else 1
            return templates.TemplateResponse("group_schedule_by_weeks.html", {"request": request, "group": group, "week": week})
        elif mode == "table":
            return templates.TemplateResponse("group_schedule.html", {"request": request, "group": group})

    return templates.TemplateResponse("group_schedule.html", {"request": request, "group": group})


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

    return groupy_groups_to_response_model(groups)


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
