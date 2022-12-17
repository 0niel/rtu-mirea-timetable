from typing import Any

from fastapi import APIRouter

from app import models
from app.config import config
from worker import app

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post("/parse-schedule/", response_model=models.Msg, status_code=201)
def parse_schedule(
    msg: models.Msg,
) -> Any:
    """
    Parse parser.
    """
    app.send_task("worker.tasks.parse_schedule")
    return {"msg": "Parsing parser"}


@router.get("/parse-schedule/", response_model=models.Msg, status_code=201)
def parse_schedule_status() -> Any:
    """
    Parse parser status.
    """
    task = app.AsyncResult("worker.tasks.parse_schedule")
    return {"msg": task.status}
