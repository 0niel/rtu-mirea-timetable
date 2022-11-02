from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

from app.db.session import async_session, SessionLocal


@asynccontextmanager
async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
