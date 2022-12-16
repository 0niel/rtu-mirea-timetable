from typing import Optional

from pydantic import BaseModel, PositiveInt

from app.models.campus import CampusGet


class RoomBase(BaseModel):
    name: str
    campus_id: Optional[PositiveInt] = None


class RoomCreate(RoomBase):
    pass


class RoomGet(RoomBase):
    id: PositiveInt
    campus: Optional[CampusGet] = None

    class Config:
        orm_mode = True


class RoomInfo(BaseModel):
    room: RoomGet
    purpose: str
    workload: float
