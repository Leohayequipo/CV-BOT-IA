# Backend standards (Python + FastAPI)

## Toolchain

- Latest stable Python, pinned in `backend/.python-version`.
- `uv` for dependencies and running commands. Commit `uv.lock`.
- `ruff` for formatting and linting (rules: `E, F, I, B, UP, SIM, N, S, ASYNC, RUF`).
- `mypy --strict`. A new `# type: ignore` needs an inline reason.
- `pytest`, `pytest-asyncio`, `httpx` for API tests, `respx` to mock outgoing HTTP.

## Layout

```
backend/
├── app/
│   ├── main.py            # create_app(): wiring only, no logic
│   ├── config.py          # pydantic-settings Settings, read once
│   ├── api/               # routers: HTTP concerns only (validation, status codes, SSE)
│   ├── schemas/           # Pydantic request/response and SSE event models
│   ├── agents/            # LangGraph graph, nodes, state, tools
│   ├── rag/               # ingestion, chunking, retrieval
│   ├── content/           # schema and loader for content/ (profile, case studies)
│   ├── prompts/           # prompt templates as .md files (see ai.md)
│   ├── services/          # external clients: LLM, embeddings, email, DB
│   └── core/              # errors, logging, rate limiting, security
└── tests/                 # mirrors app/ ; tests/content validates content/
```

Dependencies point inward: `api → agents/rag → services`. Routers never call an SDK directly, and nodes never import FastAPI.

## Conventions

- **Settings:** all configuration comes from environment variables through `Settings`. Never call `os.getenv` elsewhere. Provide `.env.example` with every key and fake values.
- **Dependency injection:** use FastAPI `Depends` for settings and clients, so tests can override them with `app.dependency_overrides`.
- **Pydantic at every boundary:** request bodies, SSE events, tool inputs and outputs, data loaded from `content/`. Use `extra="forbid"` on inputs.
- **Async all the way:** async endpoints and async clients. Never block the event loop (no `requests`, no `time.sleep`).
- **Small functions, descriptive names.** A function that needs a comment to explain *what* it does should be renamed or split. Comments explain *why*.

## Errors

- Define domain errors in `app/core/errors.py` (`RateLimitedError`, `UpstreamUnavailableError`, `InvalidContentError`…; ruff's N818 asks for the `Error` suffix) and map them to HTTP responses in one exception handler.
- Response errors follow one shape: `{"error": {"code": "rate_limited", "message": "..."}}`. Never leak stack traces, SDK messages or prompts.
- During streaming, a failure becomes an `error` SSE event followed by closing the stream, so the UI can show a retry button.
- Retry upstream LLM calls only on transient errors (429, 5xx, timeouts), with backoff and a cap. Always set timeouts.

## Logging

- Structured JSON logs (`structlog` or stdlib with a JSON formatter) with a `request_id` on every line.
- Log events and metadata, not content: never log full user messages, emails or names. Conversation content goes to Langfuse only, with the policy in `ai.md`.

## Security

- CORS allows only the production domain (and localhost in development).
- Validate and cap input sizes: message length, history length, request body size.
- Rate limit per IP and per session; return 429 with `Retry-After`.
- Secrets only from the environment; `.env` is git-ignored.
- Keep dependencies few and up to date; CI runs `pip-audit` (or `uv` equivalent).

## Testing patterns

```python
async def test_chat_rejects_oversized_message(client: AsyncClient) -> None:
    response = await client.post("/chat", json={"message": "x" * 5000})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "message_too_long"
```

- Shared fixtures (`client`, `settings`, `fake_llm`) live in `tests/conftest.py`.
- To test SSE, collect the parsed events and assert on their order and types, not on raw strings.
