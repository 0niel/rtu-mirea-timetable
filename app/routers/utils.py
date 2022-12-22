from typing import Any

from app.config import config
from fastapi import APIRouter, HTTPException, Query

from app import models
from worker import app

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post("/parse-schedule/", response_model=models.Msg, status_code=201)
async def parse_schedule(secret_key: str = Query(..., description="Ключ доступа")) -> Any:
    if config.BACKEND_DISABLE_MANUAL_SCHEDULE_UPDATE:
        raise HTTPException(400, "Функция ручного обновления расписания отключена")
    if secret_key != config.BACKEND_PARSER_SECRET_KEY:
        raise HTTPException(401, "Неверный ключ доступа")
    app.send_task("worker.tasks.parse_schedule")
    return {"msg": "Parsing started"}
