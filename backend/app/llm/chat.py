"""The chat model behind a small interface, so the agent can be tested with a scripted one."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Protocol

import openai
from openai import AsyncOpenAI

from app.core.errors import UpstreamUnavailableError

Message = dict[str, Any]


@dataclass(frozen=True)
class TextDelta:
    text: str


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str  # JSON, as the model wrote it


@dataclass(frozen=True)
class ToolCalls:
    """The model stopped to call tools; sent once, after its text."""

    calls: list[ToolCall]


@dataclass(frozen=True)
class Usage:
    """Tokens a call used, prompt and answer together; sent once, last."""

    tokens: int


ModelEvent = TextDelta | ToolCalls | Usage


class ChatModel(Protocol):
    def stream(self, messages: list[Message], tools: list[Message]) -> AsyncIterator[ModelEvent]:
        """Answer the conversation, offering `tools` (none means the model must just answer)."""
        ...


class OpenAIChatModel:
    def __init__(
        self, client: AsyncOpenAI, model: str, max_completion_tokens: int, reasoning_effort: str
    ) -> None:
        self._client = client
        self._model = model
        self._max_completion_tokens = max_completion_tokens
        self._reasoning_effort = reasoning_effort

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        calls: dict[int, ToolCall] = {}
        tokens = 0
        try:
            # The SDK's typed message dicts are strict; ours are plain dicts in the same shape
            response = await self._client.chat.completions.create(  # type: ignore[call-overload]
                model=self._model,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
                max_completion_tokens=self._max_completion_tokens,
                reasoning_effort=self._reasoning_effort,
                tools=tools or openai.omit,
            )
            async for chunk in response:
                if chunk.usage:
                    tokens = chunk.usage.total_tokens
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    yield TextDelta(delta.content)
                for call in delta.tool_calls or []:
                    # A call arrives in pieces: its id and name first, then the arguments
                    known = calls.get(call.index, ToolCall("", "", ""))
                    function = call.function
                    name = function.name if function and function.name else ""
                    arguments = function.arguments if function and function.arguments else ""
                    calls[call.index] = ToolCall(
                        id=known.id or call.id or "",
                        name=known.name or name,
                        arguments=known.arguments + arguments,
                    )
        except openai.OpenAIError as error:
            raise UpstreamUnavailableError from error
        if calls:
            yield ToolCalls([calls[index] for index in sorted(calls)])
        if tokens:
            yield Usage(tokens)
