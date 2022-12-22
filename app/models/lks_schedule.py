from pydantic import BaseModel


class LksLesson(BaseModel):
    PROPERTY_DISCIPLINE_NAME: str
    PROPERTY_LESSON_TYPE: str
    PROPERTY_NUMBER: str
    PROPERTY_LECTOR: str
    PROPERTY_PLACE: str


class LksLessons(BaseModel):
    LESSONS: dict[int, list[LksLesson]]


class LksDay(BaseModel):
    DAYS: dict[int, LksLessons]


class LksWeeks(BaseModel):
    WEEKS: dict[int, LksDay]


class LksSchedule(BaseModel):
    result: LksWeeks
