from fastapi import APIRouter
from app.services.ghl_service import GHLService

router = APIRouter(
    prefix="/ghl",
    tags=["GHL"]
)

@router.get("/status")
def get_status():
    return GHLService.get_current_values()
``