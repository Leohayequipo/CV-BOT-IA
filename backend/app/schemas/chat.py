"""The request and the stream events of POST /chat, as docs/API.md defines them."""

from typing import Annotated, ClassVar, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.content.models import Locale
from app.schemas.cards import Card, CardType

NodeName = Literal["guardrail", "supervisor", "profile", "job_fit", "contact"]


class HistoryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The maximum length lives in the settings, and breaking it has its own error code
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    history: list[HistoryMessage]
    locale: Locale
    session_id: UUID


class StreamEvent(BaseModel):
    """An event of the answer stream: `name` is the SSE event name, the fields its payload."""

    name: ClassVar[str]


class NodeEvent(StreamEvent):
    name: ClassVar[str] = "node"

    node: NodeName


class TokenEvent(StreamEvent):
    name: ClassVar[str] = "token"

    text: str


class CitationEvent(StreamEvent):
    name: ClassVar[str] = "citation"

    id: int
    label: str
    source: str
    section: str


class CardEvent(StreamEvent):
    name: ClassVar[str] = "card"

    type: CardType
    data: Card

    @classmethod
    def of(cls, card: Card) -> Self:
        return cls(type=card.type, data=card)


class DoneEvent(StreamEvent):
    name: ClassVar[str] = "done"

    suggestions: list[str]


class ErrorEvent(StreamEvent):
    name: ClassVar[str] = "error"

    code: str
    message: str
    retry_after: int | None = None
