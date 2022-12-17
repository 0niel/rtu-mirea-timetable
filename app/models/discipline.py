from pydantic import BaseModel, PositiveInt


class DisciplineCreate(BaseModel):
    name: str


class Discipline(DisciplineCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
