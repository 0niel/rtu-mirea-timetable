from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config
from app.database.connection import get_session

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/teachers/search/{name}",
    response_model=list[models.Teacher],
    status_code=200,
    description="Поиск преподавателя по имени",
    summary="Поиск преподавателя по имени",
)
async def search_teacher_by_name(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> Any:
    if len(name) < 3:
        raise HTTPException(status_code=400, detail="Имя должно быть не менее 3 символов")

    return [models.Teacher.from_orm(teacher) for teacher in await schedule_crud.search_teachers(session, name)]
