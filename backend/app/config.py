"""Settings, read once from environment variables (and from backend/.env in development)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    # The commit being served. Deploys set it, so /health shows which version is live.
    git_sha: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
