import datetime

from pydantic import BaseModel, PositiveInt


class LessonCallCreate(BaseModel):
    num: PositiveInt
    time_start: datetime.time
    time_end: datetime.time


class LessonCall(LessonCallCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
