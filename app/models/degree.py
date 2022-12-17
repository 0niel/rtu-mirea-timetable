from pydantic import BaseModel, PositiveInt


class DegreeCreate(BaseModel):
    name: str


class Degree(DegreeCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
