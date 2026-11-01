from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.agents.mock import LIMIT_RETRY_AFTER


def contact(**fields: Any) -> dict[str, Any]:
    body = {
        "name": "Laura Gómez",
        "company": "Example Ltd",
        "email": "laura.gomez@example.com",
        "message": "I'd like to arrange an interview.",
        "session_id": str(uuid4()),
    }
    return body | fields


async def test_confirmed_message_is_accepted_with_its_time(client: AsyncClient) -> None:
    response = await client.post("/contact", json=contact())

    assert response.status_code == 202
    assert datetime.fromisoformat(response.json()["sent_at"]).tzinfo is not None


async def test_company_may_be_empty(client: AsyncClient) -> None:
    response = await client.post("/contact", json=contact(company=""))

    assert response.status_code == 202


@pytest.mark.parametrize(
    "change",
    [
        {"name": " "},
        {"email": "laura.gomez@"},
        {"message": "x" * 2001},
        {"company": "x" * 101},
        {"phone": "+00 000"},
    ],
    ids=["blank-name", "bad-email", "long-message", "long-company", "unknown-field"],
)
async def test_invalid_message_is_refused(client: AsyncClient, change: dict[str, Any]) -> None:
    response = await client.post("/contact", json=contact(**change))

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


async def test_email_provider_failure_answers_503(client: AsyncClient) -> None:
    response = await client.post("/contact", json=contact(message="mock: fail"))

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "upstream_unavailable"


async def test_too_many_messages_answer_429(client: AsyncClient) -> None:
    response = await client.post("/contact", json=contact(message="mock: limit"))

    assert response.status_code == 429
    assert response.headers["retry-after"] == str(LIMIT_RETRY_AFTER)
