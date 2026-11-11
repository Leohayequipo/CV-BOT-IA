from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.limits import Limits
from app.config import Settings, get_settings
from app.main import create_app


def chat_body(session_id: str | None = None) -> dict[str, Any]:
    return {
        "message": "Who is Leonardo?",
        "history": [],
        "locale": "en",
        "session_id": session_id or str(uuid4()),
    }


def contact_body() -> dict[str, Any]:
    return {
        "name": "Laura Gómez",
        "company": "",
        "email": "laura.gomez@example.com",
        "message": "Could we arrange an interview?",
        "session_id": str(uuid4()),
    }


def app_with(settings: Settings, **changes: Any) -> FastAPI:
    limited = settings.model_copy(update={"chat_mode": "mock"} | changes)
    app = create_app(limited)
    app.dependency_overrides[get_settings] = lambda: limited
    return app


async def post(app: FastAPI, path: str, body: dict[str, Any], **headers: str) -> Any:
    transport = ASGITransport(app=app, client=("198.51.100.7", 1234))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post(path, json=body, headers=headers)


async def test_a_session_that_asks_too_much_waits(settings: Settings) -> None:
    app = app_with(settings, chat_session_limit=2)
    session = str(uuid4())

    codes = [(await post(app, "/chat", chat_body(session))).status_code for _ in range(3)]

    assert codes == [200, 200, 429]


async def test_the_limit_answers_with_the_wait_in_a_header_and_the_error_body(
    settings: Settings,
) -> None:
    app = app_with(settings, chat_session_limit=1)
    session = str(uuid4())
    await post(app, "/chat", chat_body(session))

    refused = await post(app, "/chat", chat_body(session))

    assert refused.json()["error"]["code"] == "rate_limited"
    assert 0 < int(refused.headers["retry-after"]) <= settings.chat_session_window


async def test_another_session_is_not_held_back_by_the_first(settings: Settings) -> None:
    app = app_with(settings, chat_session_limit=1)
    await post(app, "/chat", chat_body())

    assert (await post(app, "/chat", chat_body())).status_code == 200


async def test_one_ip_cannot_get_around_the_session_limit_with_new_sessions(
    settings: Settings,
) -> None:
    app = app_with(settings, chat_ip_limit=2)

    codes = [(await post(app, "/chat", chat_body())).status_code for _ in range(3)]

    assert codes == [200, 200, 429]


async def test_a_forged_forwarded_header_does_not_buy_a_new_ip(settings: Settings) -> None:
    app = app_with(settings, chat_ip_limit=1)
    await post(app, "/chat", chat_body(), **{"x-forwarded-for": "1.1.1.1"})

    refused = await post(app, "/chat", chat_body(), **{"x-forwarded-for": "2.2.2.2"})

    assert refused.status_code == 429


async def test_behind_a_trusted_proxy_visitors_are_told_apart_by_the_forwarded_address(
    settings: Settings,
) -> None:
    app = app_with(settings, chat_ip_limit=1, trusted_proxy_hops=1)
    await post(app, "/chat", chat_body(), **{"x-forwarded-for": "1.1.1.1"})

    other = await post(app, "/chat", chat_body(), **{"x-forwarded-for": "2.2.2.2"})
    same = await post(app, "/chat", chat_body(), **{"x-forwarded-for": "1.1.1.1"})

    assert (other.status_code, same.status_code) == (200, 429)


async def test_nothing_is_answered_once_the_daily_budget_is_spent(settings: Settings) -> None:
    app = app_with(settings, daily_token_budget=100)
    limits: Limits = app.state.limits
    limits.budget.record(100)

    refused = await post(app, "/chat", chat_body())

    assert refused.status_code == 429
    assert int(refused.headers["retry-after"]) > 0


async def test_contact_has_its_own_stricter_limit(settings: Settings) -> None:
    app = app_with(settings, contact_ip_limit=1)

    codes = [(await post(app, "/contact", contact_body())).status_code for _ in range(2)]

    assert codes == [202, 429]
