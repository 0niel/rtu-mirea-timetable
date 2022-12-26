from fastapi import APIRouter, Depends, Path
from starlette import status

from app import models
from app.config import config
from app.services.campuses import CampusesService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/campuses",
    response_model=list[models.Campus],
    response_description="Успешный возврат списка кампусов",
    status_code=status.HTTP_200_OK,
    description="Получить все кампусы РТУ МИРЭА",
    summary="Получение всех кампусов РТУ МИРЭА",
)
async def get_campuses(campuses_service: CampusesService = Depends()) -> list[models.Campus]:
    return await campuses_service.get_campuses()


@router.get(
    "/campuses/{campus_id}/rooms",
    response_model=list[models.Room],
    response_description="Успешный возврат списка аудиторий указанного кампуса",
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории по кампусу",
    summary="Получение всех аудитории по кампусу",
)
async def get_rooms(
    campus_id: int = Path(None, description="Id кампуса"), campuses_service: CampusesService = Depends()
) -> list[models.Room]:
    return await campuses_service.get_campus_rooms(campus_id=campus_id)
