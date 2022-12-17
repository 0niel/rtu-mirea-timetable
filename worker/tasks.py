import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import app.parser.schedule as schedule_service
from worker import app


@app.task
def parse_schedule(db: AsyncSession) -> bool:
    logger.trace('Попытка выполнить задачу обновления расписания')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_service.parse_schedule(db=db))
    return True
