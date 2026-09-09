from datetime import datetime, timezone

import httpx
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/ghl",
    tags=["GHL"]
)


@router.get("/status")
def get_status():

    return {
        "controller": "ProfiLux 3",
        "enabled": settings.GHL_ENABLED,
        "host": settings.GHL_HOST,
        "port": settings.GHL_PORT,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }


@router.get("/connect")
async def connect():

    try:

        async with httpx.AsyncClient(
            timeout=5
        ) as client:

            response = await client.get(
                f"http://{settings.GHL_HOST}"
            )

        return {
            "connected": True,
            "host": settings.GHL_HOST,
            "status_code": response.status_code,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

    except Exception as error:

        return {
            "connected": False,
            "host": settings.GHL_HOST,
            "error": str(error),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }


@router.get("/test-data")
def get_test_data():

    return {
        "temperature": 25.4,
        "ph": 8.12,
        "kh": 8.1,
        "salinity": 35.0,
        "orp": 380,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }


@router.get("/readings")
def get_readings():

    return {
        "controller": "ProfiLux 3",
        "temperature": 25.4,
        "ph": 8.12,
        "kh": 8.1,
        "salinity": 35.0,
        "orp": 380,
        "source": "mock",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }