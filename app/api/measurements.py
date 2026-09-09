from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Measurement
from app.schemas import MeasurementCreate
from app.schemas import MeasurementResponse

router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"]
)


@router.post(
    "/",
    response_model=MeasurementResponse
)
def create_measurement(
    data: MeasurementCreate,
    db: Session = Depends(get_db)
):

    measurement = Measurement(
        metric=data.metric,
        value=data.value,
        unit=data.unit
    )

    db.add(measurement)

    db.commit()

    db.refresh(measurement)

    return measurement


@router.get("/")
def get_measurements(
    db: Session = Depends(get_db)
):

    return db.query(
        Measurement
    ).all()
    