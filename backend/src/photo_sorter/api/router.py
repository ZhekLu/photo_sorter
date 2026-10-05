from fastapi import APIRouter

from photo_sorter.api.routes import folders, health

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(folders.router)
