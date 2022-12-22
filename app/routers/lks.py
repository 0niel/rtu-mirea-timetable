import app.services.groups as groups_service
from app.config import config
from app.database.connection import get_session
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models

router = APIRouter(prefix=config.BACKEND_PREFIX)

# Расписание для ЛКс
# Возвращаемые данные:
# Json формата
# result: {
# 	WEEKS: {
# 		[номер недели]: {
# 			DAYS: {
# 				[номер дня недели]: [массив уроков]
#           }
#       }
#    }
# }
# День недели: 1 - понедельник, 7 - воскресенье
# массив уроков формата
# LESSONS: [
# 	“PROPERTY_LESSON_TYPE” => “”,
# 	“PROPERTY_NUMBER” => “”,
# 	“PROPERTY_LECTOR” => “”,
# 	“PROPERTY_PLACE” => “”
#
# ] (если группа делится на подгруппы - то LESSONS должен содержать 2 описанных выше набора данных)
# PROPERTY_LESSON_TYPE - Тип пары (Л, ЛБ, П)
# PROPERTY_NUMBER - Порядковый номер пары
# '1' => ['start' => '09:00', 'end' => '10:30'],
#     	'2' => ['start' => '10:40', 'end' => '12:10'],
#     	'3' => ['start' => '12:40', 'end' => '14:10'],
#    	 '4' => ['start' => '14:20', 'end' => '15:50'],
#     	'5' => ['start' => '16:20', 'end' => '17:50'],
#    	 '6' => ['start' => '18:00', 'end' => '19:30'],
#     	'7' => ['start' => '19:40', 'end' => '21:10']
# PROPERTY_LECTOR - преподаватель
# PROPERTY_PLACE - аудитория


def lat_to_cyr(string: str) -> str:
    """Converts latin letters to cyrillic"""
    symbols = (
        "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    )

    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    return string.translate(tr)


def get_lesson_type(lesson_type_name: str) -> str:
    """Converts lesson type name to short form"""
    if lesson_type_name == "пр":
        return "П"
    elif lesson_type_name == "лек":
        return "Л"
    elif lesson_type_name == "лаб":
        return "ЛБ"
    else:
        return ""


@router.get(
    "/lks/{group_name}",
    status_code=status.HTTP_200_OK,
    response_model=models.LksSchedule,
)
async def get_lks_schedule(
    group_name: str = Path(..., min_length=1),
    session: AsyncSession = Depends(get_session),
):
    # ivbo-01-21 -> ИВБО-01-21
    group_name = lat_to_cyr(group_name)

    group = await groups_service.get_group(session, group_name.upper())

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Группа `{group_name}` не найдена",
        )

    group = models.Group.from_orm(group)
    lessons = group.lessons  # type: list[models.Lesson]

    week = models.Week(
        WEEKS={
            week: models.Day(
                DAYS={
                    day: [
                        models.Lesson(
                            PROPERTY_DISCIPLINE_NAME=lesson.discipline.name,
                            PROPERTY_LESSON_TYPE=get_lesson_type(lesson.lesson_type.name if lesson.lesson_type else ""),
                            PROPERTY_NUMBER=str(lesson.calls.num),
                            PROPERTY_LECTOR=", ".join([teacher.name for teacher in lesson.teachers or []]),
                            PROPERTY_PLACE=lesson.room.name if lesson.room else "",
                        )
                        for lesson in lessons
                        if lesson.weekday == day and week in lesson.weeks
                    ]
                    for day in range(1, 8)
                }
            )
            for week in range(1, 18)
        }
    )

    return models.LksSchedule(result=week)
