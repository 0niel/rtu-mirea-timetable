from pydantic import BaseModel, PositiveInt


class TeacherBase(BaseModel):
    name: str


class TeacherCreate(TeacherBase):
    pass


class TeacherGet(TeacherBase):
    id: PositiveInt

    class Config:
        orm_mode = True
