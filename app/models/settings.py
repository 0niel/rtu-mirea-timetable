from pydantic import BaseModel, PositiveInt


class SettingsCreate(BaseModel):
    max_week: int


class SettingsGet(SettingsCreate):
    id: PositiveInt

    class Config:
        orm_mode = True
