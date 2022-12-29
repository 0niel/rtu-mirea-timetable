from typing import Optional

from pydantic import BaseModel, PositiveInt

from .discipline import Discipline
from .lesson import LessonType
from .lesson_call import LessonCall
from .room import Room


class TeacherCreate(BaseModel):
    name: str


class TeacherLesson(BaseModel):
    """For Teacher model"""

    id: PositiveInt
    lesson_type: Optional[LessonType] = None
    discipline: Discipline
    room: Optional[Room] = None
    calls: LessonCall
    weekday: PositiveInt
    subgroup: Optional[PositiveInt] = None
    weeks: list[PositiveInt]

    class Config:
        orm_mode = True


class Teacher(TeacherCreate):
    id: PositiveInt
    lessons: list[TeacherLesson] = []  # noqa: F821

    class Config:
        orm_mode = True
