from pydantic import BaseModel, PositiveInt


class LessonTypeCreate(BaseModel):
    name: str


class LessonType(LessonTypeCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
