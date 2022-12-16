import datetime

from pydantic import BaseModel, PositiveInt

class LessonCallBase(BaseModel):
    num: PositiveInt
    time_start: datetime.time
    time_end: datetime.time

class LessonCallCreate(LessonCallBase):
    pass


class LessonCall(LessonCallBase):
    id: PositiveInt

    class Config:
        orm_mode = True
