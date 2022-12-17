import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt

from .discipline import Discipline
from .lesson_call import LessonCall
from .lesson_type import LessonType
from .room import Room
from .teacher import Teacher


class LessonCreate(BaseModel):
    lesson_type_id: Optional[PositiveInt] = None
    discipline_id: PositiveInt
    teachers_id: list[PositiveInt]
    room_id: Optional[PositiveInt] = None
    group_id: PositiveInt
    call_id: PositiveInt
    weekday: PositiveInt
    subgroup: Optional[PositiveInt] = None
    weeks: list[PositiveInt]


class Lesson(BaseModel):
    id: PositiveInt
    lesson_type: Optional[LessonType] = None
    discipline: Discipline
    teachers: list[Teacher]
    room: Optional[Room] = None
    calls: LessonCall
    weekday: PositiveInt
    subgroup: Optional[PositiveInt] = None
    weeks: list[PositiveInt]

    class Config:
        orm_mode = True


class LessonDelete(BaseModel):
    group: str
    num: PositiveInt
    time_start: datetime.time
    time_end: datetime.time
    weekday: PositiveInt


class LessonRoomSearch(BaseModel):
    name: str
    campus_short_name: Optional[str] = None
