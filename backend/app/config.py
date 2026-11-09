"""Settings, read once from environment variables (and from backend/.env in development)."""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
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
    # Abuse and cost protection (ADR-029). A session is one page load; the limits count requests
    # in a sliding window. Contact is stricter because it sends an email.
    chat_session_limit: int = 15
    chat_session_window: int = 600
    chat_ip_limit: int = 60
    chat_ip_window: int = 3600
    contact_ip_limit: int = 3
    contact_ip_window: int = 3600
    # Tokens all the models together may use per UTC day, whatever the visitors do
    daily_token_budget: int = 2_000_000
    # Proxies of ours in front of the API. Railway's edge is one: set it to 1 there, because
    # with 0 every visitor would share the edge's IP; with too many a visitor could pick theirs.
    trusted_proxy_hops: int = 0
    # How visitors reach him. They come from the deployment, never from the repo (ADR-016, ADR-027)
    contact_email: str | None = None
    contact_phone: str | None = None
    # Secrets: SecretStr keeps them out of logs and reprs
    openai_api_key: SecretStr | None = None
    database_url: SecretStr | None = None
    # Its vector size must match rag/store.py; changing it re-embeds every chunk
    embedding_model: str = "text-embedding-3-small"
    # Chosen by Leonardo (ADR-026). The chat endpoint may not allow
    # function tools together with reasoning, so reasoning is off ("none").
    answer_model: str = "gpt-5.6-luna"
    answer_max_tokens: int = 1000
    answer_reasoning_effort: str = "none"
    # The guardrail runs on every message and answers one word, so it takes a small fast model
    guardrail_model: str = "gpt-5.6-luna"
    guardrail_max_tokens: int = 10
    guardrail_reasoning_effort: str = "none"
    # How many times the model may search before it must answer, and chunks per search
    max_tool_rounds: int = 2
    search_results: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
