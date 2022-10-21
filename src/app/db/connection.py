from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.db.session import async_session


@asynccontextmanager
async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
