from pydantic import BaseModel, PositiveInt


class DisciplineBase(BaseModel):
    name: str


class DisciplineCreate(DisciplineBase):
    pass


class DisciplineGet(DisciplineBase):
    id: PositiveInt

    class Config:
        orm_mode = True
