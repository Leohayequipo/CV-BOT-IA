import json
from collections.abc import AsyncIterator
from uuid import uuid4

from app.agents.profile_agent import SEARCH_DOCS, ProfileAgent
from app.llm.chat import Message, ModelEvent, TextDelta, ToolCall, ToolCalls
from app.rag.chunking import Chunk
from app.rag.retrieval import Hit
from app.schemas.chat import (
    ChatRequest,
    CitationEvent,
    DoneEvent,
    HistoryMessage,
    NodeEvent,
    StreamEvent,
    TokenEvent,
)

SYSTEM = "system prompt"
RESULTS = Chunk(
    id="servime#results",
    source_id="servime",
    title="ServiME",
    section="Results",
    content="It is in production.",
)


class ScriptedModel:
    """Plays one scripted turn per call and records what it was sent."""

    def __init__(self, *turns: list[ModelEvent]) -> None:
        self._turns = list(turns)
        self.requests: list[tuple[list[Message], list[Message]]] = []

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        self.requests.append((list(messages), tools))
        for event in self._turns.pop(0):
            yield event


class FakeSearch:
    def __init__(self, *hits: Hit) -> None:
        self._hits = list(hits)
        self.queries: list[tuple[str, int]] = []

    async def search(self, query: str, limit: int) -> list[Hit]:
        self.queries.append((query, limit))
        return self._hits


def request(
    message: str = "What did he build?", history: list[HistoryMessage] | None = None
) -> ChatRequest:
    return ChatRequest(message=message, history=history or [], locale="en", session_id=uuid4())


def search_call(arguments: dict[str, str] | str, call_id: str = "call-1") -> ToolCalls:
    text = arguments if isinstance(arguments, str) else json.dumps(arguments)
    return ToolCalls([ToolCall(call_id, "search_docs", text)])


async def collect(agent: ProfileAgent, chat_request: ChatRequest) -> list[StreamEvent]:
    return [event async for event in agent.answer(chat_request)]


def make_agent(model: ScriptedModel, search: FakeSearch, rounds: int = 2) -> ProfileAgent:
    return ProfileAgent(model, search, SYSTEM, max_tool_rounds=rounds, search_results=3)


def text_of(events: list[StreamEvent]) -> str:
    return "".join(event.text for event in events if isinstance(event, TokenEvent))


async def test_a_plain_answer_streams_between_the_node_and_done() -> None:
    model = ScriptedModel([TextDelta("He is an AI engineer "), TextDelta("[profile:summary].")])

    events = await collect(make_agent(model, FakeSearch()), request())

    assert [type(event) for event in events] == [
        NodeEvent,
        TokenEvent,
        CitationEvent,
        TokenEvent,
        TokenEvent,
        DoneEvent,
    ]
    assert text_of(events) == "He is an AI engineer [1]."


async def test_the_model_gets_the_system_prompt_the_history_and_the_wrapped_question() -> None:
    model = ScriptedModel([TextDelta("Ok.")])
    history = [HistoryMessage(role="assistant", content="Hi!")]

    await collect(make_agent(model, FakeSearch()), request("Tell me more", history))

    messages, tools = model.requests[0]
    assert messages == [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": "Hi!"},
        {"role": "user", "content": "<user_message>\nTell me more\n</user_message>"},
    ]
    assert tools == [SEARCH_DOCS]


async def test_a_search_result_can_be_cited_and_is_sent_back_to_the_model() -> None:
    search = FakeSearch(Hit(RESULTS, 0.03))
    model = ScriptedModel(
        [search_call({"query": "ServiME results"})],
        [TextDelta("It runs in production [servime#results].")],
    )

    events = await collect(make_agent(model, search), request())

    assert search.queries == [("ServiME results", 3)]
    citation = next(event for event in events if isinstance(event, CitationEvent))
    assert (citation.label, citation.source, citation.section) == (
        "ServiME · Results",
        "case-studies/servime.md",
        "Results",
    )
    assert text_of(events) == "It runs in production [1]."
    follow_up = model.requests[1][0]
    assert follow_up[-2]["tool_calls"][0]["function"]["arguments"] == '{"query": "ServiME results"}'
    assert follow_up[-1] == {
        "role": "tool",
        "tool_call_id": "call-1",
        "content": (
            '<document id="servime#results">\n'
            "ServiME - Results\n\nIt is in production.\n"
            "</document>"
        ),
    }


async def test_a_chunk_that_was_never_retrieved_cannot_be_cited() -> None:
    model = ScriptedModel([TextDelta("It is great [servime#results].")])

    events = await collect(make_agent(model, FakeSearch(Hit(RESULTS, 0.03))), request())

    assert not [event for event in events if isinstance(event, CitationEvent)]
    assert text_of(events) == "It is great ."


async def test_the_model_must_answer_after_the_allowed_number_of_searches() -> None:
    search = FakeSearch()
    model = ScriptedModel(
        [search_call({"query": "a"})],
        [search_call({"query": "b"}, "call-2")],
        [TextDelta("I couldn't find it.")],
    )

    events = await collect(make_agent(model, search, rounds=2), request())

    assert [tools for _, tools in model.requests] == [[SEARCH_DOCS], [SEARCH_DOCS], []]
    assert text_of(events) == "I couldn't find it."
    assert isinstance(events[-1], DoneEvent)


async def test_no_documents_found_is_told_to_the_model() -> None:
    model = ScriptedModel([search_call({"query": "nothing"})], [TextDelta("Not covered.")])

    await collect(make_agent(model, FakeSearch()), request())

    assert model.requests[1][0][-1]["content"] == "No documents found."


async def test_bad_tool_arguments_are_reported_to_the_model_without_searching() -> None:
    search = FakeSearch()
    model = ScriptedModel(
        [search_call("not json")],
        [search_call({"query": "x" * 301}, "call-2")],
        [TextDelta("Ok.")],
    )

    await collect(make_agent(model, search), request())

    assert search.queries == []
    assert model.requests[1][0][-1]["content"].startswith("Invalid arguments")
    assert model.requests[2][0][-1]["content"].startswith("Invalid arguments")


async def test_an_unknown_tool_is_refused() -> None:
    model = ScriptedModel([ToolCalls([ToolCall("call-1", "send_email", "{}")])], [TextDelta("Ok.")])

    await collect(make_agent(model, FakeSearch()), request())

    assert model.requests[1][0][-1]["content"] == "Unknown tool: send_email"
