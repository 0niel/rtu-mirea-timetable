from pydantic import BaseModel, PositiveInt


class CampusBase(BaseModel):
    name: str
    short_name: str


class CampusCreate(CampusBase):
    pass


class CampusGet(CampusBase):
    id: PositiveInt

    class Config:
        orm_mode = True
