import aiofiles
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Response, UploadFile
from fastapi_cache import FastAPICache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models
from app.config import config
from app.database.connection import get_session
from app.models import SettingsCreate
from app.services.api.info import InfoService
from app.services.utils import get_week
from worker import app

router = APIRouter(prefix=config.PREFIX)


@router.post("/parse-schedule/", status_code=204)
async def parse_schedule(secret_key: str = Query(..., description="Ключ доступа")) -> Response:
    if not config.ENABLE_MANUAL_SCHEDULE_UPDATE:
        raise HTTPException(400, "Функция ручного обновления расписания отключена")
    if secret_key != config.SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")
    await FastAPICache.clear(namespace="groups")
    app.send_task("worker.tasks.parse_schedule")
    return Response(status_code=204)


@router.post("/parse-file/", status_code=204)
async def parse_file(
    secret_key: str = Query(..., description="Ключ доступа"),
    schedule: UploadFile = File(..., description="Файл с расписанием"),
    institute: str = Query(..., description="Инстиут"),
    degree: str = Query(..., description="Степень обучения"),
) -> Response:
    if secret_key != config.SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")

    async with aiofiles.open("/files", 'wb') as out_file:
        content = await schedule.read()
        await out_file.write(content)

    await FastAPICache.clear(namespace="groups")

    app.send_task(
        "worker.tasks.parse_file",
        kwargs={
            "file_path": f"",
            "institute": institute,
            "degree": degree,
        },
    )
    return Response(status_code=204)


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
    if secret_key != config.SECRET_KEY:
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
async def update_max_week_count(
    db: AsyncSession = Depends(get_session),
    settings: SettingsCreate = Body(..., description="Максимальное кол-во недель"),
    secret_key: str = Query(..., description="Ключ доступа"),
) -> models.SettingsGet:
    if secret_key != config.SECRET_KEY:
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
async def get_current_week(db: AsyncSession = Depends(get_session)) -> models.CurrentWeek:
    # TODO: Refactor, very fast solution
    current_week = get_week()
    return models.CurrentWeek(week=current_week)
