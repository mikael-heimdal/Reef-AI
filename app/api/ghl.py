from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/ghl",
    tags=["GHL"]
)


@router.get("/status")
def get_status():

    return {
        "controller": "ProfiLux 3",
        "connected": False,
        "mode": "development",
        "timestamp": datetime.utcnow(),
        "message": "GHL connector not configured"
    }


@router.get("/test-data")
def get_test_data():

    return {
        "temperature": 25.4,
        "ph": 8.12,
        "kh": 8.1,
        "salinity": 35.0,
        "orp": 380,
        "timestamp": datetime.utcnow()
    }