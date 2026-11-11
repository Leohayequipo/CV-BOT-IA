"""Traces of each chat request in Langfuse: the nodes, the model calls, the documents found.

Tracing is optional: without keys every call here does nothing. Everything sent passes through
`redact` first, and the system prompt is never sent, only its size (ADR-030).
"""

from contextvars import ContextVar
from typing import Any

from langfuse import Langfuse

from app.config import Settings
from app.observability.redact import redact
from app.schemas.chat import ChatRequest


class Observation:
    """One step of a trace: it ends once, with its output and what it used."""

    def __init__(self, span: Any | None) -> None:
        self._span = span

    def end(
        self,
        output: Any = None,
        tokens: int | None = None,
        error: str | None = None,
    ) -> None:
        if self._span is None:
            return
        fields: dict[str, Any] = {"output": output}
        if tokens:
            fields["usage_details"] = {"total": tokens}
        if error:
            fields.update(level="ERROR", status_message=error)
        self._span.update(**fields)
        self._span.end()


class Trace:
    """One request, from the question to the last event."""

    def __init__(self, root: Any | None, metadata: dict[str, Any] | None = None) -> None:
        self._root = root
        self._metadata = metadata or {}

    def generation(self, name: str, model: str, messages: list[dict[str, Any]]) -> Observation:
        return self._child(name, "generation", input=_without_system(messages), model=model)

    def retrieval(self, query: str) -> Observation:
        return self._child("search_docs", "retriever", input=query)

    def end(self, output: str, metadata: dict[str, Any], error: str | None = None) -> None:
        if self._root is not None:
            self._root.update(metadata={**self._metadata, **metadata})
        Observation(self._root).end(output=output, error=error)

    def _child(self, name: str, kind: str, **fields: Any) -> Observation:
        if self._root is None:
            return Observation(None)
        return Observation(self._root.start_observation(name=name, as_type=kind, **fields))


def _without_system(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The conversation as sent, with the system prompt reduced to its size."""
    return [
        {**message, "content": f"[system prompt, {len(message['content'])} characters]"}
        if message["role"] == "system"
        else message
        for message in messages
    ]


# The trace of the request being answered, so the model and the search need not be handed it
current_trace: ContextVar[Trace | None] = ContextVar("current_trace", default=None)


class Tracing:
    def __init__(self, client: Langfuse | None) -> None:
        self._client = client

    @classmethod
    def from_settings(cls, settings: Settings) -> "Tracing":
        if not (settings.langfuse_public_key and settings.langfuse_secret_key):
            return cls(None)
        client = Langfuse(
            public_key=settings.langfuse_public_key.get_secret_value(),
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            base_url=settings.langfuse_base_url,
            environment=settings.langfuse_environment,
            release=settings.git_sha,
            mask=redact,
        )
        return cls(client)

    def start(self, request: ChatRequest) -> Trace:
        if self._client is None:
            return Trace(None)
        metadata = {
            "session_id": str(request.session_id),
            "locale": request.locale,
            "history_messages": len(request.history),
        }
        root = self._client.start_observation(name="chat", input=request.message, metadata=metadata)
        return Trace(root, metadata)

    def shutdown(self) -> None:
        """Send what is still queued; the API calls it when it stops."""
        if self._client is not None:
            self._client.shutdown()
