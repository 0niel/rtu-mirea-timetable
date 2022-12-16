from pydantic import BaseModel, PositiveInt


class DegreeBase(BaseModel):
    name: str


class DegreeCreate(DegreeBase):
    pass


class DegreeGet(DegreeBase):
    id: PositiveInt

    class Config:
        orm_mode = True
