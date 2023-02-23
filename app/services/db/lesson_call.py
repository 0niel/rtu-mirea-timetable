from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app import models
from app.database import tables


class LessonCallDBService:
    """Сервис для работы с звонками."""

    @classmethod
    async def get_pagination_count(cls, db: AsyncSession, ids: Optional[List[int]]) -> int:
        """Получение количества звонков"""

        query = select(func.count(tables.LessonCall.id))

        if ids:
            query = query.where(tables.LessonCall.id.in_(ids))

        return (await db.execute(query)).scalar()

    @classmethod
    async def get_calls(
        cls, db: AsyncSession, calls_ids: Optional[List[int]], limit: int, offset: int
    ) -> List[tables.LessonCall]:
        """Получение списка всех звонков"""

        query = select(tables.LessonCall)

        if calls_ids:
            query = query.where(tables.LessonCall.id.in_(calls_ids))

        calls = (await db.execute(query.limit(limit).offset(cast(offset, BigInteger)))).scalars()

        return calls

    @classmethod
    async def get_call(cls, db: AsyncSession, id_: int) -> tables.LessonCall:
        """Получение звонка по идентификатору"""

        query = select(tables.LessonCall).where(tables.LessonCall.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_call_by_params(
        cls, db: AsyncSession, num: int, time_start: datetime.time, time_end: datetime.time
    ) -> tables.LessonCall:
        """Получение звонка по параметрам"""

        query = select(tables.LessonCall).where(
            tables.LessonCall.num == num,
            tables.LessonCall.time_start == time_start,
            tables.LessonCall.time_end == time_end,
        )
        return (await db.execute(query)).scalar()

    @classmethod
    async def create(cls, db: AsyncSession, call: models.LessonCallCreate) -> tables.LessonCall:
        """Создание звонка"""

        call = tables.LessonCall(**call.dict())
        db.add(call)
        await db.flush()
        return call
