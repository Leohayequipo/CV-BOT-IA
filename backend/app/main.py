"""Build the FastAPI app: wiring only, no logic."""

from fastapi import FastAPI

from app.api import health
from app.api.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="CV-BOT-IA API")
    register_error_handlers(app)
    app.include_router(health.router)
    return app


app = create_app()
