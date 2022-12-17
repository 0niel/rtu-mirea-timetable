from pydantic import BaseModel, PositiveInt


class TeacherCreate(BaseModel):
    name: str


class Teacher(TeacherCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
