"""A chat model that reports what each call used, so the daily budget can be spent."""

from collections.abc import AsyncIterator

from app.core.limits import DailyBudget
from app.llm.chat import ChatModel, Message, ModelEvent, Usage


class MeteredModel:
    """Wraps a model: spends its Usage events from the budget and keeps them from the agents."""

    def __init__(self, model: ChatModel, budget: DailyBudget) -> None:
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
