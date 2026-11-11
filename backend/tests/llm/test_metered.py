from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest

from app.core.errors import RateLimitedError
from app.core.limits import DailyBudget
from app.llm.chat import Message, ModelEvent, OpenAIChatModel, TextDelta, Usage
from app.llm.metered import MeteredModel


class UsageModel:
    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        yield TextDelta("Hi")
        yield Usage(250)


async def test_the_usage_of_a_call_is_spent_from_the_budget_and_not_passed_on() -> None:
    budget = DailyBudget(tokens=1000)
    model = MeteredModel(UsageModel(), budget)

    events = [event async for event in model.stream([], [])]

    assert events == [TextDelta("Hi")]
    budget.check()
    budget.record(750)
    with pytest.raises(RateLimitedError):
        budget.check()


def chunk(content: str | None = None, usage: int | None = None) -> Any:
    choices = [SimpleNamespace(delta=SimpleNamespace(content=content, tool_calls=None))]
    return SimpleNamespace(
        choices=choices if content is not None else [],
        usage=SimpleNamespace(total_tokens=usage) if usage else None,
    )


class FakeCompletions:
    def __init__(self) -> None:
        self.arguments: dict[str, Any] = {}

    async def create(self, **arguments: Any) -> AsyncIterator[Any]:
        self.arguments = arguments

        async def chunks() -> AsyncIterator[Any]:
            yield chunk("Hel")
            yield chunk("lo")
            yield chunk(usage=321)

        return chunks()


async def test_the_openai_model_asks_for_usage_and_reports_it_last() -> None:
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    model = OpenAIChatModel(client, "model", 100, "none")  # type: ignore[arg-type]

    events = [event async for event in model.stream([], [])]

    assert events == [TextDelta("Hel"), TextDelta("lo"), Usage(321)]
    assert completions.arguments["stream_options"] == {"include_usage": True}
