from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.agents.mock import MockChat, Pace
from app.api.chat import get_chat
from app.config import Settings, get_settings
from app.content.loader import load_content
from app.content.models import Content
from app.main import create_app


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def content_dir(repo_root: Path) -> Path:
    return repo_root / "content"


@pytest.fixture
def content(content_dir: Path) -> Content:
    return load_content(content_dir)


@pytest.fixture
def settings(content_dir: Path) -> Settings:
    # Ignore any developer .env, so tests see the same settings everywhere
    return Settings(git_sha="abc1234", content_dir=content_dir, _env_file=None)


@pytest.fixture
def app(settings: Settings, content: Content) -> FastAPI:
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    # Answers stream without pauses, so the tests stay fast
    app.dependency_overrides[get_chat] = lambda: MockChat(content, Pace(step=0, token=0))
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    # Unhandled errors come back as 500 responses, as a real client would see them
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
