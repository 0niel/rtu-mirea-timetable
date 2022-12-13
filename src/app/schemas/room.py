from typing import Optional

from pydantic import BaseModel, PositiveInt


class RoomCreate(BaseModel):
    name: str
    campus_id: Optional[PositiveInt] = None


class Room(RoomCreate):
    id: PositiveInt
    campus: Optional[CampusModel] = None

    class Config:
        orm_mode = True


class RoomInfo(BaseModel):
    room: RoomModel
    purpose: str
    workload: float
    lessons: list[LessonModel]
