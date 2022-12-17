from pydantic import BaseModel, PositiveInt


class CampusCreate(BaseModel):
    name: str
    short_name: str


class Campus(CampusCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
