import datetime
import re
from typing import Optional

from pydantic import BaseModel, PositiveInt, validator


class PeriodCreate(BaseModel):
    year_start: PositiveInt
    year_end: PositiveInt
    semester: PositiveInt


class DegreeCreate(BaseModel):
    name: str


class InstituteCreate(BaseModel):
    name: str
    short_name: str


class GroupCreate(BaseModel):
    name: str
    period_id: PositiveInt
    degree_id: PositiveInt
    institute_id: PositiveInt

    @validator("name")
    def group_name_must_be_str(cls, v):
        re_group_name = re.compile(r"([А-Яа-я]{4}-\d{2}-\d{2})")
        if not re_group_name.match(v):
            raise ValueError('Group name must be like "АААА-00-00"')
        return v


class LessonCallCreate(BaseModel):
    num: PositiveInt
    time_start: datetime.time
    time_end: datetime.time


class LessonTypeCreate(BaseModel):
    name: str


class CampusCreate(BaseModel):
    name: str
    short_name: str


class RoomCreate(BaseModel):
    name: str
    campus_id: Optional[PositiveInt] = None


class DisciplineCreate(BaseModel):
    name: str


class TeacherCreate(BaseModel):
    name: str


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


class LessonCallModel(LessonCallCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class PeriodModel(PeriodCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class DegreeModel(DegreeCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class InstituteModel(InstituteCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class LessonTypeModel(LessonTypeCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class DisciplineModel(DisciplineCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class TeacherModel(TeacherCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class CampusModel(CampusCreate):
    id: PositiveInt

    class Config:
        orm_mode = True


class RoomModel(RoomCreate):
    id: PositiveInt
    campus: Optional[CampusModel] = None

    class Config:
        orm_mode = True


class GroupInLessonModel(BaseModel):
    id: PositiveInt
    name: str

    class Config:
        orm_mode = True


class LessonModel(BaseModel):
    id: PositiveInt
    group: GroupInLessonModel
    lesson_type: Optional[LessonTypeModel] = None
    discipline: DisciplineModel
    teachers: list[TeacherModel]
    room: Optional[RoomModel] = None
    calls: LessonCallModel
    weekday: PositiveInt
    subgroup: Optional[PositiveInt] = None
    weeks: list[PositiveInt]

    class Config:
        orm_mode = True


class GroupModel(BaseModel):
    id: PositiveInt
    name: str
    period: PeriodModel
    institute: InstituteModel
    degree: DegreeModel
    lessons: list[LessonModel]

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


class RoomInfo(BaseModel):
    room: RoomModel
    purpose: str
    workload: float
    lessons: list[LessonModel]
