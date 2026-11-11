"""POST /chat: check the question, then stream the answer as Server-Sent Events."""

import logging
from collections.abc import AsyncIterator
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Protocol

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.agents.assistant import build_assistant
from app.agents.mock import MockChat
from app.api.errors import error_message
from app.api.limits import Limits, get_limits, visitor_ip
from app.config import Settings, get_settings
from app.content.loader import load_content
from app.content.models import Content
from app.core.errors import ApiError, InvalidRequestError, MessageTooLongError
from app.observability.tracing import Tracing, current_trace
from app.schemas.chat import ChatRequest, ErrorEvent, NodeEvent, StreamEvent, TokenEvent

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache
def _load_content(content_dir: Path) -> Content:
    return load_content(content_dir)


class Chat(Protocol):
    """What answers a question: the assistant, or the mock that stands in for it (ADR-032)."""

    def answer(self, question: ChatRequest) -> AsyncIterator[StreamEvent]: ...


def chat_for(app: FastAPI, settings: Settings) -> Chat:
    """The app's chat, built on first use; the app builds it at start-up to fail early."""
    if app.state.chat is None:
        content = _load_content(settings.content_dir)
        if settings.chat_mode == "mock":
            app.state.chat = MockChat(content)
        else:
            # Every model call spends from the daily budget
            app.state.chat = build_assistant(settings, content, app.state.limits.budget)
    chat: Chat = app.state.chat
    return chat


def get_chat(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> Chat:
    return chat_for(request.app, settings)


async def accepted_question(
    request: Request,
    question: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    chat: Annotated[Chat, Depends(get_chat)],
    limits: Annotated[Limits, Depends(get_limits)],
    ip: Annotated[str, Depends(visitor_ip)],
) -> ChatRequest:
    """Refuse a question with a normal error response, before any event is streamed."""
    # The error handler answers in the question's language
    request.state.locale = question.locale
    if len(question.message) > settings.max_message_chars:
        raise MessageTooLongError
    if len(question.history) > settings.max_history_messages:
        raise InvalidRequestError
    limits.budget.check()
    limits.chat_by_session.check(str(question.session_id))
    limits.chat_by_ip.check(ip)
    if isinstance(chat, MockChat):
        chat.check_limit(question)
    return question


def get_tracing(request: Request) -> Tracing:
    tracing: Tracing = request.app.state.tracing
    return tracing


@router.post("/chat", response_class=EventSourceResponse)
async def chat(
    question: Annotated[ChatRequest, Depends(accepted_question)],
    chat: Annotated[Chat, Depends(get_chat)],
    tracing: Annotated[Tracing, Depends(get_tracing)],
) -> AsyncIterator[ServerSentEvent]:
    trace = tracing.start(question)
    current_trace.set(trace)
    answer, nodes, failure = "", [], None
    # Once streaming, the status is already 200: a failure becomes the stream's last event
    try:
        async for event in chat.answer(question):
            if isinstance(event, TokenEvent):
                answer += event.text
            elif isinstance(event, NodeEvent):
                nodes.append(event.node)
            yield _to_sse(event)
    except ApiError as error:
        failure = error.code
        message = error_message(error.code, question.locale)
        yield _to_sse(ErrorEvent(code=error.code, message=message, retry_after=error.retry_after))
    except Exception:
        failure = "internal_error"
        logger.exception("An answer failed partway")
        message = error_message("internal_error", question.locale)
        yield _to_sse(ErrorEvent(code="internal_error", message=message))
    finally:
        trace.end(answer, {"nodes": nodes}, error=failure)


def _to_sse(event: StreamEvent) -> ServerSentEvent:
    return ServerSentEvent(event=event.name, data=event)
