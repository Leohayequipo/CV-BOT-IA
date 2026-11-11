"""A chat model that reports what each call used, so the daily budget can be spent."""

from collections.abc import AsyncIterator
from typing import Protocol

from app.llm.chat import ChatModel, Message, ModelEvent, Usage


class TokenSink(Protocol):
    """Where used tokens go: the daily budget in production, a counter in the evals."""

    def record(self, tokens: int) -> None: ...


class MeteredModel:
    """Wraps a model: reports its Usage events to a sink and keeps them from the agents."""

    def __init__(self, model: ChatModel, budget: TokenSink) -> None:
        self._model = model
        self._budget = budget

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        async for event in self._model.stream(messages, tools):
            if isinstance(event, Usage):
                self._budget.record(event.tokens)
            else:
                yield event
