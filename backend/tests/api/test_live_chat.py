import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api import chat as chat_module
from app.config import Settings, get_settings
from app.core.errors import UpstreamUnavailableError
from app.core.limits import DailyBudget
from app.main import create_app
from app.schemas.chat import ChatRequest, DoneEvent, NodeEvent, StreamEvent, TokenEvent


class ScriptedAssistant:
    """Stands in for the real assistant: plays its events, then fails if told to."""

    def __init__(self, fail: bool = False) -> None:
        self._fail = fail
        self.questions: list[str] = []

    async def answer(self, question: ChatRequest) -> AsyncIterator[StreamEvent]:
        self.questions.append(question.message)
        yield NodeEvent(node="guardrail")
        yield TokenEvent(text="He builds ")
        if self._fail:
            raise UpstreamUnavailableError
        yield TokenEvent(text="AI products.")
        yield DoneEvent(suggestions=[])


def body(message: str = "Who is Leonardo?") -> dict[str, Any]:
    return {"message": message, "history": [], "locale": "en", "session_id": str(uuid4())}


def events_of(text: str) -> list[tuple[str, dict[str, Any]]]:
    found = []
    for block in text.split("\n\n"):
        fields = dict(line.partition(": ")[::2] for line in block.splitlines())
        if "event" in fields:
            found.append((fields["event"], json.loads(fields["data"])))
    return found


@pytest.fixture
def built(monkeypatch: pytest.MonkeyPatch) -> list[Any]:
    """Replaces the real assistant's builder, and records what it was built with."""
    calls: list[Any] = []
    assistant = ScriptedAssistant()

    def fake_build(settings: Settings, content: object, usage: object) -> ScriptedAssistant:
        calls.append(usage)
        return assistant

    monkeypatch.setattr(chat_module, "build_assistant", fake_build)
    calls.append(assistant)
    return calls


def live_app(settings: Settings, **changes: Any) -> FastAPI:
    changed = settings.model_copy(update=changes)
    app = create_app(changed)
    app.dependency_overrides[get_settings] = lambda: changed
    return app


async def post(app: FastAPI, message: str = "Who is Leonardo?") -> Any:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await client.post("/chat", json=body(message))


async def test_a_question_is_answered_by_the_assistant(
    settings: Settings, built: list[Any]
) -> None:
    app = live_app(settings)

    response = await post(app)

    events = events_of(response.text)
    assert [name for name, _ in events] == ["node", "token", "token", "done"]
    assert "".join(e["text"] for name, e in events if name == "token") == "He builds AI products."
    assert built[0].questions == ["Who is Leonardo?"]


async def test_the_assistant_spends_from_the_daily_budget_and_is_built_once(
    settings: Settings, built: list[Any]
) -> None:
    app = live_app(settings)

    await post(app)
    await post(app)

    builds = [call for call in built if isinstance(call, DailyBudget)]
    assert builds == [app.state.limits.budget]


async def test_a_failure_in_the_assistant_ends_the_stream_with_an_error_event(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(chat_module, "build_assistant", lambda *_: ScriptedAssistant(fail=True))
    app = live_app(settings)

    response = await post(app)

    names = [name for name, _ in events_of(response.text)]
    assert names == ["node", "token", "error"]
    assert events_of(response.text)[-1][1]["code"] == "upstream_unavailable"


async def test_the_mock_commands_are_ordinary_questions_in_live_mode(
    settings: Settings, built: list[Any]
) -> None:
    response = await post(live_app(settings), "mock: limit")

    assert response.status_code == 200


async def test_mock_mode_answers_with_the_scripted_answers(settings: Settings) -> None:
    app = live_app(settings, chat_mode="mock")

    response = await post(app, "mock: limit")

    assert response.status_code == 429


async def test_starting_without_keys_in_live_mode_fails_instead_of_serving_errors(
    settings: Settings,
) -> None:
    app = live_app(settings)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        async with app.router.lifespan_context(app):
            pass


async def test_starting_in_mock_mode_needs_no_keys(settings: Settings) -> None:
    app = live_app(settings, chat_mode="mock")

    async with app.router.lifespan_context(app):
        pass
