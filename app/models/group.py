import re

from pydantic import BaseModel, PositiveInt, validator

from app.models.degree import DegreeGet
from app.models.institute import InstituteGet
from app.models.lesson import Lesson
from app.models.period import PeriodGet


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


class Group(BaseModel):
    id: PositiveInt
    name: str
    period: PeriodGet
    institute: InstituteGet
    degree: DegreeGet
    lessons: list[Lesson]

    class Config:
        orm_mode = True
