from typing import Any

from fastapi import APIRouter

from app import models
from app.config import config
from worker import app

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post("/parse-schedule/", response_model=models.Msg, status_code=201)
async def parse_schedule() -> Any:
    """
    Parse parser.
    """
    app.send_task("worker.tasks.parse_schedule")
    return {"msg": "Parsing parser"}
