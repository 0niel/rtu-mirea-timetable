import asyncio

import app.core.schedule.parser as schedule_service
from app.core.celery_app import celery_app


@celery_app.task
def parse_schedule() -> str:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_service.parse_schedule())
    return "done"
