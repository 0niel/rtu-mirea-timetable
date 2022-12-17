from pydantic import BaseModel, PositiveInt


class InstituteCreate(BaseModel):
    name: str
    short_name: str


class Institute(InstituteCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
