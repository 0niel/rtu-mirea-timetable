from pydantic import BaseModel, PositiveInt


class PeriodCreate(BaseModel):
    year_start: PositiveInt
    year_end: PositiveInt
    semester: PositiveInt


class Period(PeriodCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
