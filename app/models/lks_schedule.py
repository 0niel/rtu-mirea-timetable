from pydantic import BaseModel


class Lesson(BaseModel):
    PROPERTY_DISCIPLINE_NAME: str
    PROPERTY_LESSON_TYPE: str
    PROPERTY_NUMBER: str
    PROPERTY_LECTOR: str
    PROPERTY_PLACE: str


class Day(BaseModel):
    DAYS: dict[int, list[Lesson]]


class Week(BaseModel):
    WEEKS: dict[int, Day]


class LksSchedule(BaseModel):
    result: Week
