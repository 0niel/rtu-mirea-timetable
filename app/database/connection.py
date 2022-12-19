from app.config import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if config.DEBUG:
    engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI, future=True, echo=True)
else:
    engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI, future=True, echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
