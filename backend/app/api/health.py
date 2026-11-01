"""Health check: Railway calls it before a new version takes traffic."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas.health import Health

router = APIRouter()


@router.get("/health")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> Health:
    return Health(status="ok", git_sha=settings.git_sha)
