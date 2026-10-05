from fastapi import APIRouter

from photo_sorter.api.response import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="photo-sorter",
    )
