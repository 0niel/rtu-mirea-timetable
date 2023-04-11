from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi_cache import FastAPICache
from starlette import status

from app import models
from app.config import config
from app.services.api.info import InfoService
from worker import app

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post("/parse-schedule/", response_model=models.Msg, status_code=201)
async def parse_schedule(secret_key: str = Query(..., description="Ключ доступа")) -> Any:
    if config.BACKEND_DISABLE_MANUAL_SCHEDULE_UPDATE:
        raise HTTPException(400, "Функция ручного обновления расписания отключена")
    if secret_key != config.BACKEND_PARSER_SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")
    await FastAPICache.clear(namespace="groups")
    app.send_task("worker.tasks.parse_schedule")
    return {"msg": "Parsing started"}


@router.get(
    "/version",
    response_model=models.VersionBase,
    response_description="Системная информация успешно получена",
    status_code=status.HTTP_200_OK,
    description="Получить системную информацию",
    summary="Получение системной информации",
)
async def get_system_info() -> models.VersionBase:
    return await InfoService.get_info()
