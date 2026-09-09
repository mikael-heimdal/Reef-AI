from datetime import datetime
from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    metric: str
    value: float
    unit: str


class MeasurementResponse(BaseModel):
    id: int
    metric: str
    value: float
    unit: str
    timestamp: datetime

    class Config:
        from_attributes = True