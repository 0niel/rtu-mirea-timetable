from pydantic import BaseModel, PositiveInt


class LessonTypeBase(BaseModel):
    name: str

class LessonTypeCreate(LessonTypeBase):
    pass


class LessonType(LessonTypeBase):
    id: PositiveInt

    class Config:
        orm_mode = True
