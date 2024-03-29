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


@app.task
def parse_file(file_path: str, institute: str, degree: int) -> None:
    """Обновление расписания"""
    logger.debug(
        "Запускаем задачу парсинга расписания из файла. Входные параметры: " f"{file_path=} {institute = } {degree = } "
    )

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        _sync_schedule(from_file=True, file_path=file_path, institute=institute, degree=degree)
    )

    logger.debug("Завершена задача парсинга расписания из файла")


async def _sync_schedule(
    from_file: bool = False, file_path: str = None, institute: str = None, degree: int = None
) -> None:
    logger.debug("Получена сессия БД")
    await ScheduleParsingService.parse_schedule(
        from_file=from_file, file_path=file_path, institute=institute, degree=degree
    )
