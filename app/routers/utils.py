from typing import Any

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from fastapi_cache import FastAPICache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.models import SettingsCreate
from app.parser.schedule import ScheduleParsingService

from app.services.api import PeriodService
from app.services.api.info import InfoService
from app.services.utils import get_week
from worker import app

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post("/parse-schedule/", response_model=models.Msg, status_code=201)
async def parse_schedule(
    secret_key: str = Query(..., description="Ключ доступа"), session: AsyncSession = Depends(get_session)
) -> models.Msg:
    if config.BACKEND_DISABLE_MANUAL_SCHEDULE_UPDATE:
        raise HTTPException(400, "Функция ручного обновления расписания отключена")
    if secret_key != config.BACKEND_PARSER_SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")
    await FastAPICache.clear(namespace="groups")
    # await ScheduleParsingService.parse_schedule(db=session)
    app.send_task("worker.tasks.parse_schedule")
    return {"msg": "Parsing started"}


@router.get(
    "/versions",
    response_model=models.VersionBase,
    response_description="Системная информация успешно получена",
    status_code=status.HTTP_200_OK,
    description="Получить системную информацию",
    summary="Получение системной информации",
)
async def get_system_info() -> models.VersionBase:
    return await InfoService.get_info()


@router.get(
    "/max-week",
    response_model=models.SettingsGet,
    response_description="Максимальное кол-во недель получено",
    status_code=status.HTTP_200_OK,
    description="Получить максимальное кол-во недель в семестре",
    summary="Получить максимальное кол-во недель в семестре",
)
async def get_max_week_count(
    db: AsyncSession = Depends(get_session), secret_key: str = Query(..., description="Ключ доступа")
) -> models.SettingsGet:
    if secret_key != config.BACKEND_PARSER_SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")
    return await InfoService.get_max_week(db=db)


@router.put(
    "/max-week",
    response_model=models.SettingsGet,
    response_description="Максимальное кол-во недель установлено и возвращено",
    status_code=status.HTTP_200_OK,
    description="Установить максимальное кол-во недель в семестре",
    summary="Установить максимальное кол-во недель в семестре",
)
async def get_max_week_count(
    db: AsyncSession = Depends(get_session),
    settings: SettingsCreate = Body(..., description="Максимальное кол-во недель"),
    secret_key: str = Query(..., description="Ключ доступа"),
) -> models.SettingsGet:
    if secret_key != config.BACKEND_PARSER_SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")
    return await InfoService.set_max_week(db=db, settings=settings)

@router.get(
    "/current-week",
    response_model=models.CurrentWeek,
    response_description="Текущая неделя успешно получена",
    status_code=status.HTTP_200_OK,
    description="Получить текущую неделю",
    summary="Получить текущую неделю",
)
async def get_current_week(
    db: AsyncSession = Depends(get_session)
) -> models.CurrentWeek:
    # TODO: Refactor, very fast solution
    current_week = get_week()
    return models.CurrentWeek(week=current_week)
