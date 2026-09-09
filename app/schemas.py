from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    metric: str
    value: float
    unit: str


class MeasurementResponse(MeasurementCreate):
    id: int

    class Config:
        from_attributes = True