from fastapi import FastAPI

from app.core.events import on_startup, on_shutdown
from app.routers import main_router
from app.core.cors_middleware import init_middlewares


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(main_router)
    init_middlewares(app)
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)
    return app
