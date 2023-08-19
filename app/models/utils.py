from pydantic import BaseModel


class CurrentWeek(BaseModel):
    week: int
