from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from app.config import Settings
from app.llm.chat import Message, ModelEvent, TextDelta, ToolCall, ToolCalls, Usage
from app.llm.traced import TracedModel
from app.observability import tracing as tracing_module
from app.observability.redact import redact
from app.observability.tracing import Tracing, current_trace
from app.rag.chunking import Chunk
from app.rag.retrieval import Hit
from app.rag.traced import TracedSearch
from app.schemas.chat import ChatRequest


class FakeSpan:
    """Records what a Langfuse observation was given."""

    def __init__(self, **fields: Any) -> None:
        self.fields = fields
        self.children: list[FakeSpan] = []
        self.ended = False

    def start_observation(self, **fields: Any) -> "FakeSpan":
        child = FakeSpan(**fields)
        self.children.append(child)
        return child

    def update(self, **fields: Any) -> None:
        self.fields |= fields

    def end(self) -> None:
        self.ended = True


class FakeLangfuse:
    def __init__(self) -> None:
        self.roots: list[FakeSpan] = []
        self.shut_down = False

    def start_observation(self, **fields: Any) -> FakeSpan:
        root = FakeSpan(**fields)
        self.roots.append(root)
        return root

    def shutdown(self) -> None:
        self.shut_down = True


def make_request(message: str = "Who is Leonardo?") -> ChatRequest:
    return ChatRequest(message=message, history=[], locale="en", session_id=uuid4())


def started() -> tuple[FakeLangfuse, Tracing]:
    client = FakeLangfuse()
    tracing = Tracing(client)  # type: ignore[arg-type]
    current_trace.set(tracing.start(make_request()))
    return client, tracing


@pytest.fixture(autouse=True)
def no_current_trace() -> None:
    current_trace.set(None)


def test_without_keys_nothing_is_traced(settings: Settings) -> None:
    tracing = Tracing.from_settings(settings)

    trace = tracing.start(make_request())
    trace.generation("answer", "model", []).end(output="x")
    trace.end("answer", {})
    tracing.shutdown()


def test_with_keys_the_client_masks_contact_details_and_tags_the_release(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    given: dict[str, Any] = {}

    class CapturingLangfuse:
        def __init__(self, **options: Any) -> None:
            given.update(options)

    monkeypatch.setattr(tracing_module, "Langfuse", CapturingLangfuse)
    keyed = settings.model_copy(
        update={
            "langfuse_public_key": SecretStr("pk-lf-test"),
            "langfuse_secret_key": SecretStr("sk-lf-test"),
            "langfuse_environment": "production",
        }
    )

    Tracing.from_settings(keyed)

    assert given["mask"] is redact
    assert given["release"] == "abc1234"
    assert given["environment"] == "production"
    assert given["public_key"] == "pk-lf-test"


def test_a_trace_starts_with_the_question_and_the_session_but_not_the_history() -> None:
    client, _ = started()

    root = client.roots[0]
    assert root.fields["input"] == "Who is Leonardo?"
    assert set(root.fields["metadata"]) == {"session_id", "locale", "history_messages"}


def test_ending_a_trace_adds_to_what_it_started_with() -> None:
    client, _ = started()
    trace = current_trace.get()
    assert trace is not None

    trace.end("The answer", {"nodes": ["guardrail"]})

    root = client.roots[0]
    assert root.fields["output"] == "The answer"
    assert root.fields["metadata"]["nodes"] == ["guardrail"]
    assert "session_id" in root.fields["metadata"]
    assert root.ended


def test_a_failed_trace_is_marked_as_an_error() -> None:
    client, _ = started()
    trace = current_trace.get()
    assert trace is not None

    trace.end("", {}, error="rate_limited")

    assert client.roots[0].fields["level"] == "ERROR"


def test_shutting_down_sends_what_is_queued() -> None:
    client, tracing = started()

    tracing.shutdown()

    assert client.shut_down


class StubModel:
    def __init__(self, *events: ModelEvent, fail: bool = False) -> None:
        self._events = events
        self._fail = fail

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        for event in self._events:
            yield event
        if self._fail:
            raise RuntimeError("provider down")


MESSAGES: list[Message] = [
    {"role": "system", "content": "secret policies " * 10},
    {"role": "user", "content": "<user_message>\nHi\n</user_message>"},
]


async def test_a_model_call_is_a_generation_with_its_text_and_tokens() -> None:
    client, _ = started()
    model = TracedModel(StubModel(TextDelta("Hel"), TextDelta("lo"), Usage(42)), "answer", "m-1")

    events = [event async for event in model.stream(MESSAGES, [])]

    assert events == [TextDelta("Hel"), TextDelta("lo"), Usage(42)]
    generation = client.roots[0].children[0]
    assert generation.fields["name"] == "answer"
    assert generation.fields["as_type"] == "generation"
    assert generation.fields["model"] == "m-1"
    assert generation.fields["output"] == "Hello"
    assert generation.fields["usage_details"] == {"total": 42}
    assert generation.ended


async def test_the_system_prompt_is_never_sent_only_its_size() -> None:
    client, _ = started()
    model = TracedModel(StubModel(TextDelta("Ok")), "answer", "m-1")

    _ = [event async for event in model.stream(MESSAGES, [])]

    sent = client.roots[0].children[0].fields["input"]
    assert sent[0]["content"] == "[system prompt, 160 characters]"
    assert "secret" not in str(sent)
    assert sent[1] == MESSAGES[1]


async def test_a_tool_call_is_recorded_as_the_output() -> None:
    client, _ = started()
    calls = ToolCalls([ToolCall("c1", "search_docs", '{"query": "x"}')])
    model = TracedModel(StubModel(calls), "answer", "m-1")

    _ = [event async for event in model.stream(MESSAGES, [])]

    output = client.roots[0].children[0].fields["output"]
    assert output == {
        "text": "",
        "tool_calls": [{"name": "search_docs", "arguments": '{"query": "x"}'}],
    }


async def test_a_failing_model_call_is_recorded_and_the_error_still_reaches_the_caller() -> None:
    client, _ = started()
    model = TracedModel(StubModel(TextDelta("Par"), fail=True), "answer", "m-1")

    with pytest.raises(RuntimeError):
        _ = [event async for event in model.stream(MESSAGES, [])]

    generation = client.roots[0].children[0]
    assert generation.fields["level"] == "ERROR"
    assert generation.fields["status_message"] == "RuntimeError"
    assert generation.ended


async def test_a_model_with_no_trace_in_progress_just_passes_events_through() -> None:
    model = TracedModel(StubModel(TextDelta("Hi")), "answer", "m-1")

    events = [event async for event in model.stream(MESSAGES, [])]

    assert events == [TextDelta("Hi")]


class StubSearch:
    def __init__(self, hits: list[Hit], fail: bool = False) -> None:
        self._hits = hits
        self._fail = fail

    async def search(self, query: str, limit: int) -> list[Hit]:
        if self._fail:
            raise RuntimeError("database down")
        return self._hits


CHUNK = Chunk(
    id="servime#results", source_id="servime", title="ServiME", section="Results", content="x"
)


async def test_a_search_records_the_query_and_the_ids_and_scores_it_found() -> None:
    client, _ = started()

    hits = await TracedSearch(StubSearch([Hit(CHUNK, 0.031)])).search("ServiME results", 4)

    assert len(hits) == 1
    search = client.roots[0].children[0]
    assert search.fields["as_type"] == "retriever"
    assert search.fields["input"] == "ServiME results"
    assert search.fields["output"] == [{"id": "servime#results", "score": 0.031}]
    assert "content" not in str(search.fields["output"])


async def test_a_failing_search_is_recorded_and_raised() -> None:
    client, _ = started()

    with pytest.raises(RuntimeError):
        await TracedSearch(StubSearch([], fail=True)).search("x", 4)

    assert client.roots[0].children[0].fields["level"] == "ERROR"


async def test_a_chat_request_is_traced_with_its_answer_and_nodes(app: FastAPI) -> None:
    client = FakeLangfuse()
    app.state.tracing = Tracing(client)  # type: ignore[arg-type]
    body = {
        "message": "Tell me about Leonardo",
        "history": [],
        "locale": "en",
        "session_id": str(uuid4()),
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        response = await http.post("/chat", json=body)

    root = client.roots[0]
    assert response.status_code == 200
    assert root.fields["input"] == "Tell me about Leonardo"
    assert root.fields["output"]
    assert root.fields["metadata"]["nodes"] == ["guardrail", "supervisor", "profile"]
    assert root.ended
