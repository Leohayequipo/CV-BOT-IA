"""The profile agent: answers from the profile in its prompt and from searched case studies.

It follows the stream of docs/API.md, like the mock it replaces. The model may call `search_docs`
a few times, then it must answer; every citation it writes is checked against the sources it
was actually given (see citations.py).
"""

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Protocol

from app.agents.citations import CitationStream
from app.agents.profile_context import render_profile
from app.agents.sources import Source, chunk_source, profile_sources
from app.content.models import Profile
from app.llm.chat import ChatModel, Message, TextDelta, ToolCall
from app.prompts import render_prompt
from app.rag.retrieval import Hit
from app.schemas.chat import ChatRequest, DoneEvent, NodeEvent, StreamEvent

# A search query is a few words; a longer one is the model pasting something it shouldn't
MAX_QUERY_CHARS = 300

SEARCH_DOCS: Message = {
    "type": "function",
    "function": {
        "name": "search_docs",
        "description": (
            "Search Leonardo's case studies for details the profile doesn't give: how a project "
            "was built, why a decision was made, challenges and results. Returns the best "
            "matching sections, each with the id to cite."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to look for, in a few English words",
                }
            },
            "required": ["query"],
        },
    },
}


class DocumentSearch(Protocol):
    async def search(self, query: str, limit: int) -> list[Hit]: ...


def build_system_prompt(
    profile: Profile,
    policies: str,
    contact_email: str | None = None,
    contact_phone: str | None = None,
) -> str:
    """Everything stable goes in here, so the same text is sent, and cached, on every request."""
    profile_text = render_profile(profile, contact_email, contact_phone)
    return render_prompt("profile_agent", policies=policies, profile=profile_text)


def read_policies(content_dir: Path) -> str:
    return (content_dir / "policies.md").read_text(encoding="utf-8")


class ProfileAgent:
    def __init__(
        self,
        model: ChatModel,
        search: DocumentSearch,
        system_prompt: str,
        max_tool_rounds: int,
        search_results: int,
    ) -> None:
        self._model = model
        self._search = search
        self._system_prompt = system_prompt
        self._max_tool_rounds = max_tool_rounds
        self._search_results = search_results

    async def answer(self, request: ChatRequest) -> AsyncIterator[StreamEvent]:
        yield NodeEvent(node="profile")

        sources = profile_sources()
        citations = CitationStream(sources)
        messages: list[Message] = [
            {"role": "system", "content": self._system_prompt},
            *({"role": item.role, "content": item.content} for item in request.history),
            {"role": "user", "content": f"<user_message>\n{request.message}\n</user_message>"},
        ]

        for round_number in range(self._max_tool_rounds + 1):
            # On the last round no tool is offered, so the model has to answer
            tools = [SEARCH_DOCS] if round_number < self._max_tool_rounds else []
            text = ""
            calls: list[ToolCall] = []
            async for event in self._model.stream(messages, tools):
                if isinstance(event, TextDelta):
                    text += event.text
                    for out in citations.feed(event.text):
                        yield out
                else:
                    calls = event.calls
            if not calls:
                break
            messages.append(_assistant_turn(text, calls))
            for call in calls:
                result = await self._run_tool(call, sources)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        for out in citations.flush():
            yield out
        yield DoneEvent(suggestions=[])

    async def _run_tool(self, call: ToolCall, sources: dict[str, Source]) -> str:
        if call.name != SEARCH_DOCS["function"]["name"]:
            return f"Unknown tool: {call.name}"
        query = _query_of(call.arguments)
        if query is None:
            return f"Invalid arguments: send a 'query' of up to {MAX_QUERY_CHARS} characters."
        hits = await self._search.search(query, self._search_results)
        if not hits:
            return "No documents found."
        for hit in hits:
            sources[hit.chunk.id] = chunk_source(hit.chunk)
        return "\n\n".join(
            f'<document id="{hit.chunk.id}">\n{hit.chunk.text}\n</document>' for hit in hits
        )


def _assistant_turn(text: str, calls: list[ToolCall]) -> Message:
    return {
        "role": "assistant",
        "content": text or None,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.name, "arguments": call.arguments},
            }
            for call in calls
        ],
    }


def _query_of(arguments: str) -> str | None:
    try:
        parsed: Any = json.loads(arguments)
    except json.JSONDecodeError:
        return None
    query = parsed.get("query") if isinstance(parsed, dict) else None
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY_CHARS:
        return None
    return query.strip()
