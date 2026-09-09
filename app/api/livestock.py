from fastapi import APIRouter

router = APIRouter(
    prefix="/livestock",
    tags=["livestock"]
)

@router.get("/")
def get_livestock():
    return {
        "status": "ok",
        "items": []
    }