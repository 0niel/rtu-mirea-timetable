from pydantic import BaseModel, PositiveInt


class WorkloadGet(BaseModel):
    id: PositiveInt
    workload: float
