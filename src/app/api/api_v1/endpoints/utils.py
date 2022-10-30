from typing import Any

from fastapi import APIRouter

from app import schemas
from app.core.celery_app import celery_app

router = APIRouter()


@router.post("/parse-schedule/", response_model=schemas.Msg, status_code=201)
def parse_schedule(
    msg: schemas.Msg,
) -> Any:
    """
    Parse schedule.
    """
    celery_app.send_task("app.worker.parse_schedule")
    return {"msg": "Parsing schedule"}



@router.get("/parse-schedule/", response_model=schemas.Msg, status_code=201)
def parse_schedule_status(
) -> Any:
    """
    Parse schedule status.
    """
    task = celery_app.AsyncResult("app.worker.parse_schedule")
    return {"msg": task.status}
