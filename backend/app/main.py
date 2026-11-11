"""Build the FastAPI app: wiring only, no logic."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, contact, health
from app.api.errors import register_error_handlers
from app.api.limits import Limits
from app.config import Settings, get_settings
from app.observability.tracing import Tracing


def create_app(settings: Settings) -> FastAPI:
    tracing = Tracing.from_settings(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        # Traces are sent in batches; this sends the last one
        tracing.shutdown()

    app = FastAPI(title="CV-BOT-IA API", lifespan=lifespan)
    app.state.tracing = tracing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        # The site reads it to say when asking works again
        expose_headers=["Retry-After"],
    )
    app.state.limits = Limits.from_settings(settings)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(contact.router)
    return app


app = create_app(get_settings())
