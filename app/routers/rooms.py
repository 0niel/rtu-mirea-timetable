from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.services.crud_schedule as schedule_crud
from app import models
from app.config import config
from app.database.connection import get_session
from app.services.api import RoomService

router = APIRouter(prefix=config.BACKEND_PREFIX)


# Moscow timezone
# tz = timezone(timedelta(hours=3))


@router.get(
    "/room",
    response_model=list[models.Room],
    response_description="Список аудиторий успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории РТУ МИРЭА",
    summary="Получение всех аудиторий РТУ МИРЭА",
)
async def get_rooms(
    db: AsyncSession = Depends(get_session),
    ids: Optional[List[int]] = Query(None, description="Id аудиторий"),
    limit: int = Query(30, description="", ge=1, le=5000),
    offset: int = Query(0, description="", ge=0, le=9000000000000000000),
) -> list[models.Room]:
    return await RoomService.get_rooms(db=db, rooms_ids=ids, limit=limit, offset=offset)


@router.get(
    "/room/{id}",
    response_model=models.Room,
    response_description="Аудитория успешно получен и возвращен в ответе",
    status_code=status.HTTP_200_OK,
    description="Получить аудиторию по id и вернуть его",
    summary="Получение аудитории по id",
)
async def get_room(
    db: AsyncSession = Depends(get_session),
    id_: int = Path(..., description="Id аудитории", alias="id"),
) -> models.Room:
    return await RoomService.get_room(db=db, id_=id_)


@router.get(
    "/room/search/{name}",
    response_model=list[models.Room],
    status_code=200,
    description="Поиск аудитории по названию аудитории (по подстроке)",
    summary="Поиск аудитории",
)
async def search_rooms(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> Any:
    return [models.Room.from_orm(room) for room in await schedule_crud.search_room(session, name)]


# @router.get(
#     "/workload/{room_id}",
#     response_model=models.Msg,
#     status_code=200,
#     description="Получить загруженность аудитории",
#     summary="Получение загруженности аудитории",
# )
# async def get_workload(
#     room_id: int,
#     session: AsyncSession = Depends(get_session),
# ) -> Any:
#     workload = await schedule_crud.get_room_workload(session, room_id)
#     return models.Msg(msg=workload)


# @router.get(
#     "/statuses/",
#     status_code=200,
#     description="Получить статусы аудиторий (свободна/занята) для указанного времени",
#     summary="Получение статусов аудиторий",
# )
# async def get_statuses(
#     date_time: datetime = Query(
#         datetime.now(),
#         description="Дата и время в ISO формате. Пример: " "2021-09-01T00:00:00+03:00",
#     ),
#     *,
#     rooms: list[str] = Query(..., description="Список аудиторий. Пример: ['А-101', 'А-102']"),
#     session: AsyncSession = Depends(get_session),
# ) -> Any:
#     date_time = date_time.replace(tzinfo=None)
#     return await schedule_crud.get_rooms_statuses(session, rooms, date_time)


# @router.get("/export-create/", status_code=200)
# def export_create(db: Session = Depends(get_db)):
#     if os.path.exists("rooms.xslx"):
#         os.remove("rooms.xslx")
#
#     # rooms = await schedule_crud.get_all_rooms()
#
#     rooms = schedule_crud.get_all_rooms_sync(db)
#
#     df = pd.DataFrame(
#         columns=[
#             "номер комнаты",
#             "корпус",
#             "день недели",
#             "номер пары",
#             "неделя",
#             "дисциплина",
#             "группа",
#         ]
#     )
#
#     all_rooms_data = []
#     for room in rooms:
#         campus = room.campus.name if room.campus else None
#
#         for lesson in room.lessons:
#             all_rooms_data.extend(
#                 {
#                     "номер комнаты": room.name,
#                     "корпус": campus,
#                     "день недели": lesson.weekday,
#                     "номер пары": lesson.calls.num,
#                     "неделя": week,
#                     "дисциплина": lesson.discipline.name,
#                     "группа": lesson.group.name,
#                 }
#                 for week in lesson.weeks
#             )
#
#     df = df.append(all_rooms_data, ignore_index=True)
#     df.to_excel("rooms.xlsx", index=False)
#
#     return


# @router.get("/download")
# def download_rooms_data():
#     try:
#         return FileResponse(
#             "rooms.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#     except Exception:
#         return Response(status_code=404)
#

# @router.get("/report-status")
# def report_status():
#     if os.path.exists("rooms.xlsx") and os.stat("rooms.xlsx").st_size > 1000000:
#         return {"status": "ready"}
#     return {"status": "not ready"}
#

# @router.get("/info/{room_id}", response_model=models.RoomInfo, status_code=200)
# async def get_info(room_id: int) -> Any:
#     """
#     Get info.
#     """
#     return await schedule_crud.get_room_info(room_id)


# @router.get(
#     "/workload/all/{campus_substr}",
#     status_code=200,
#     description="Получить загруженность всех аудиторий по корпусу (подстрока)",
#     summary="Получение загруженности всех аудиторий по корпусу",
# )
# async def get_all_workload(
#     campus_substr: str,
#     session: AsyncSession = Depends(get_session),
# ) -> Any:
#     rooms = await schedule_crud.search_room(session, campus_substr)
#     workload = []
#     for room in rooms:
#         workload.append(
#             {
#                 "room": room.name,
#                 "workload": await schedule_crud.get_room_workload(room.id),
#             }
#         )
#
#     return workload
#
#
# @router.get(
#     "/statuses/all/{campus_substr}",
#     status_code=200,
#     description="Получить статусы всех аудиторий по корпусу (подстрока)",
#     summary="Получение статусов всех аудиторий по корпусу",
# )
# async def get_all_statuses(
#     campus_substr: str,
#     date_time: datetime = Query(
#         datetime.now(),
#         description="Дата и время в ISO формате. Пример: 2021-09-01T00:00:00+03:00",
#     ),
#     session: AsyncSession = Depends(get_session),
# ) -> Any:
#     rooms = await schedule_crud.search_room(session, campus_substr)
#     rooms = [room.name for room in rooms]
#     date_time = date_time.replace(tzinfo=None)
#     return await schedule_crud.get_rooms_statuses(session, rooms, date_time)
