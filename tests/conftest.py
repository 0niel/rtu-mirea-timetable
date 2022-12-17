import asyncio
import warnings
from typing import Any, Generator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from alembic.command import upgrade
from alembic.config import Config
from tests.db_setup import create_test_db, drop_test_db


@pytest.fixture(scope="session")
def apply_migrations():
    from app.config import config

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    db_url = config.SQLALCHEMY_DATABASE_URI
    db_name = config.POSTGRES_DB
    db_name_test = f"{db_name.replace('-', '_')}_test"

    asyncio.run(drop_test_db(db_url, db_name_test))
    asyncio.run(create_test_db(db_url, db_name_test))

    config.SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI.replace(db_name, db_name_test)
    config = Config("alembic.ini")
    upgrade(config, "head")
    yield
    asyncio.run(drop_test_db(db_url, db_name_test))


@pytest.fixture
async def db(mocker) -> Generator[AsyncSession, Any, None]:
    from app.config import config

    engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)
    async_session = sessionmaker(engine, autoflush=False, class_=AsyncSession, autocommit=False)
    async with async_session() as session:
        mocker.patch("sqlalchemy.orm.sessionmaker.__call__", return_value=session)
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def app(apply_migrations, db) -> FastAPI:
    from app.main import app

    return app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    from app.config import config

    url = f"http://{config.BACKEND_HOST}:{config.BACKEND_PORT}"
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url=url, headers={"Content-Type": "application/json"}) as client_:
            yield client_
