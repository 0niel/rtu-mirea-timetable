import hashlib
from typing import Optional

import aiohttp
from starlette.requests import Request
from starlette.responses import Response

from app import config


def key_builder_exclude_db(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
):
    from fastapi_cache import FastAPICache

    # Exclude db from cache key
    if args:
        args = args[1:]

    if kwargs:
        kwargs = kwargs.copy()
        kwargs.pop("db")

    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"

    return prefix + hashlib.md5(f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode()).hexdigest()  # nosec:B303


async def send_clear_cache_request():
    # TODO: Make api_url configurable via config.py
    api_url = f"https://timetable.mirea.ru/api"
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/clear-cache/?secret_key={config.SECRET_KEY}") as response:
            pass
