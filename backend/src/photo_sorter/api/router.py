from fastapi import APIRouter

from photo_sorter.api.routes import health

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
