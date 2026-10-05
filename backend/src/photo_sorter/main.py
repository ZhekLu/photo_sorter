from fastapi import FastAPI

from photo_sorter.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Photo Sorter API")
    app.include_router(api_router)

    return app


app = create_app()
