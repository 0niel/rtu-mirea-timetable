from typing import Any

from fastapi import APIRouter

from app import models
from app.core.celery_app import celery_app

router = APIRouter()


@router.post("/parse-schedule/", response_model=models.Msg, status_code=201)
def parse_schedule(
    msg: models.Msg,
) -> Any:
    """
    Parse parser.
    """
    celery_app.send_task("app.worker.parse_schedule")
    return {"msg": "Parsing parser"}


@router.get("/parse-schedule/", response_model=models.Msg, status_code=201)
def parse_schedule_status() -> Any:
    """
    Parse parser status.
    """
    task = celery_app.AsyncResult("app.worker.parse_schedule")
    return {"msg": task.status}
