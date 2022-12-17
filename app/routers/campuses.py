from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.campuses as campuses_service
from app import models
from app.config import config
from app.database.connection import get_session

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/campuses",
    response_model=list[models.Campus],
    response_description="Успешный возврат списка кампусов",
    status_code=status.HTTP_200_OK,
    description="Получить все кампусы РТУ МИРЭА",
    summary="Получение всех кампусов РТУ МИРЭА",
)
async def get(db: AsyncSession = Depends(get_session)) -> list[models.Campus]:
    return [models.Campus.from_orm(campus) for campus in await campuses_service.get_campuses(db=db)]


@router.get("/campuses/{campus_id}/rooms", response_model=list[models.Campus], status_code=200)
async def get_rooms(
    campus_id: int = Path(None, description="Id кампуса"), db: AsyncSession = Depends(get_session)
) -> list[models.Campus]:
    return [
        models.Campus.from_orm(room) for room in await campuses_service.get_campus_rooms(db=db, campus_id=campus_id)
    ]
