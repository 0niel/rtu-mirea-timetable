from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database.connection import get_session
from app.services.api import GroupService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get(
    "/",
    response_class=HTMLResponse,
    response_description="Страница с группами успешно получена",
    status_code=status.HTTP_200_OK,
    description="Получить страницу с учебными группами",
    summary="Получение страницы с учебными группами",
)
async def groups_html(request: Request, db: AsyncSession = Depends(get_session)):
    groups = await GroupService.get_groups(db=db, groups_ids=None, limit=3000, offset=0)
    return templates.TemplateResponse("groups.html", {"request": request, "groups": groups})


@router.get(
    "/group/{name}",
    response_class=HTMLResponse,
    response_description="Страница с расписанием указанной группы успешно получена",
    status_code=status.HTTP_200_OK,
    description="Получить страницу с расписанием указанной группы",
    summary="Получение страницы с расписанием указанной группы",
)
async def group_schedule_html(
    request: Request, name: str = Path(None, description="Имя группы"), db: AsyncSession = Depends(get_session)
):
    group = await GroupService.get_group_by_name(db=db, name=name)

    mode = request.query_params.get("mode")
    week = request.query_params.get("week")

    if mode or week:
        if mode == "week" or week:
            week = int(week) if week else 1
            return templates.TemplateResponse(
                "group_schedule_by_weeks.html", {"request": request, "group": group, "week": week}
            )
        elif mode == "table":
            return templates.TemplateResponse("group_schedule.html", {"request": request, "group": group})

    return templates.TemplateResponse("group_schedule.html", {"request": request, "group": group})
