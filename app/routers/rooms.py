from datetime import datetime, timedelta, timezone
from typing import Any

import app.services.crud_schedule as schedule_crud
from app.config import config
from app.database.connection import get_session
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import models

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/lessons/{room_id}",
    response_model=list[models.Lesson],
    status_code=200,
    description="Получить расписание аудитории",
    summary="Получение расписания аудитории",
)
async def get_room_lessons(
    room_id: int,
    session: AsyncSession = Depends(get_session),
) -> Any:
    return [models.Lesson.from_orm(room) for room in await schedule_crud.get_lessons_by_room(session, room_id)]


# Moscow timezone
tz = timezone(timedelta(hours=3))


@router.get(
    "/lessons-by-date/{room_id}/{date}",
    response_model=list[models.Lesson],
    status_code=200,
    description="Получить расписание аудитории на указанную дату",
    summary="Получение расписания аудитории на указанную дату",
)
async def get_rooms_lesson_by_room_and_date(
    room_id: int,
    date: str = Query(..., description="Дата в формате: YYYY-MM-DD"),
    session: AsyncSession = Depends(get_session),
) -> Any:
    # Convert date to datetime
    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"msg": "Incorrect data format, should be YYYY-MM-DD"}

    return [
        models.Lesson.from_orm(room)
        for room in await schedule_crud.get_lessons_by_room_and_date(session, room_id, date)
    ]


@router.get(
    "/lessons-by-week/{room_id}/{week}",
    response_model=list[models.Lesson],
    status_code=200,
    description="Получить расписание аудитории на указанную неделю",
    summary="Получение расписания аудитории на указанную неделю",
)
async def get_rooms_lesson_by_room_and_week(
    room_id: int,
    week: int,
    session: AsyncSession = Depends(get_session),
) -> Any:
    return [
        models.Lesson.from_orm(room)
        for room in await schedule_crud.get_lessons_by_room_and_week(session, room_id, week)
    ]


@router.get(
    "/search/{name}",
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


@router.get(
    "/workload/{room_id}",
    response_model=models.Msg,
    status_code=200,
    description="Получить загруженность аудитории",
    summary="Получение загруженности аудитории",
)
async def get_workload(
    room_id: int,
    session: AsyncSession = Depends(get_session),
) -> Any:
    workload = await schedule_crud.get_room_workload(session, room_id)
    return models.Msg(msg=workload)


@router.get(
    "/statuses/",
    status_code=200,
    description="Получить статусы аудиторий (свободна/занята) для указанного времени",
    summary="Получение статусов аудиторий",
)
async def get_statuses(
    date_time: datetime = Query(
        datetime.now(),
        description="Дата и время в ISO формате. Пример: " "2021-09-01T00:00:00+03:00",
    ),
    *,
    rooms: list[str] = Query(..., description="Список аудиторий. Пример: ['А-101', 'А-102']"),
    session: AsyncSession = Depends(get_session),
) -> Any:
    date_time = date_time.replace(tzinfo=None)
    return await schedule_crud.get_rooms_statuses(session, rooms, date_time)


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


@router.get(
    "/workload/all/{campus_substr}",
    status_code=200,
    description="Получить загруженность всех аудиторий по корпусу (подстрока)",
    summary="Получение загруженности всех аудиторий по корпусу",
)
async def get_all_workload(
    campus_substr: str,
    session: AsyncSession = Depends(get_session),
) -> Any:
    rooms = await schedule_crud.search_room(session, campus_substr)
    workload = []
    for room in rooms:
        workload.append(
            {
                "room": room.name,
                "workload": await schedule_crud.get_room_workload(room.id),
            }
        )

    return workload


@router.get(
    "/statuses/all/{campus_substr}",
    status_code=200,
    description="Получить статусы всех аудиторий по корпусу (подстрока)",
    summary="Получение статусов всех аудиторий по корпусу",
)
async def get_all_statuses(
    campus_substr: str,
    date_time: datetime = Query(
        datetime.now(),
        description="Дата и время в ISO формате. Пример: 2021-09-01T00:00:00+03:00",
    ),
    session: AsyncSession = Depends(get_session),
) -> Any:
    rooms = await schedule_crud.search_room(session, campus_substr)
    rooms = [room.name for room in rooms]
    date_time = date_time.replace(tzinfo=None)
    return await schedule_crud.get_rooms_statuses(session, rooms, date_time)
