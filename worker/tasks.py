import asyncio

from loguru import logger

from app.database.connection import async_session
from app.parser.schedule import ScheduleParsingService
from worker import app


@app.task
def parse_schedule() -> None:
    """Обновление расписания"""
    logger.debug("Запускаем задачу обновления расписания")

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(_sync_schedule())

    logger.debug("Завершена задача обновления расписания")


async def _sync_schedule() -> None:
    async with async_session() as db_session:
        logger.debug("Получена сессия БД")
        await ScheduleParsingService.parse_schedule(db=db_session)
