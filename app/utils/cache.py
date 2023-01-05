import hashlib
from typing import Optional

from starlette.requests import Request
from starlette.responses import Response


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
