"""Build the FastAPI app: wiring only, no logic."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, contact, health
from app.api.errors import register_error_handlers
from app.config import Settings, get_settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="CV-BOT-IA API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        # The site reads it to say when asking works again
        expose_headers=["Retry-After"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(contact.router)
    return app


app = create_app(get_settings())
