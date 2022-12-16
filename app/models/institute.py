from pydantic import BaseModel, PositiveInt


class InstituteBase(BaseModel):
    name: str
    short_name: str


class InstituteCreate(InstituteBase):
    pass


class InstituteGet(InstituteBase):
    id: PositiveInt

    class Config:
        orm_mode = True
