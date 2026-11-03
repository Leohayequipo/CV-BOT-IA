"""Settings, read once from environment variables (and from backend/.env in development)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    # The commit being served. Deploys set it, so /health shows which version is live.
    git_sha: str = "local"
    # Origins of the site; browsers block calls to the API from any other page
    cors_origins: tuple[str, ...] = ("http://localhost:5180",)
    content_dir: Path = _REPO_ROOT / "content"
    # Request limits from docs/API.md
    max_message_chars: int = 6000
    max_history_messages: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
