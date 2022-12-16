from pydantic import BaseModel, PositiveInt


class PeriodBase(BaseModel):
    year_start: PositiveInt
    year_end: PositiveInt
    semester: PositiveInt


class PeriodCreate(PeriodBase):
    pass


class PeriodGet(PeriodBase):
    id: PositiveInt

    class Config:
        orm_mode = True
