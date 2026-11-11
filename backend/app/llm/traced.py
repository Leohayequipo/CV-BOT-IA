"""A chat model that records each call as a generation of the request's trace."""

from collections.abc import AsyncIterator

from app.llm.chat import ChatModel, Message, ModelEvent, TextDelta, ToolCalls, Usage
from app.observability.tracing import current_trace


class TracedModel:
    """Wraps a model. Put it inside MeteredModel, which swallows the Usage this one reads."""

    def __init__(self, model: ChatModel, name: str, model_id: str) -> None:
        self._model = model
        self._name = name
        self._model_id = model_id

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        trace = current_trace.get()
        if trace is None:
            async for event in self._model.stream(messages, tools):
                yield event
            return
        generation = trace.generation(self._name, self._model_id, messages)
        text, calls, tokens = "", [], 0
        try:
            async for event in self._model.stream(messages, tools):
                if isinstance(event, TextDelta):
                    text += event.text
                elif isinstance(event, ToolCalls):
                    calls = [
                        {"name": call.name, "arguments": call.arguments} for call in event.calls
                    ]
                elif isinstance(event, Usage):
                    tokens = event.tokens
                yield event
        except BaseException as error:
            generation.end(output=text, tokens=tokens, error=type(error).__name__)
            raise
        generation.end(output={"text": text, "tool_calls": calls} if calls else text, tokens=tokens)
