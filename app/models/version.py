from pydantic import BaseModel


class VersionBase(BaseModel):
    rtu_schedule_parser: str
    rtu_mirea_timetable: str
