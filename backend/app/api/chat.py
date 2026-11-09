"""POST /chat: check the question, then stream the answer as Server-Sent Events."""

import logging
from collections.abc import AsyncIterator
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.agents.mock import MockChat
from app.api.errors import error_message
from app.api.limits import Limits, get_limits, visitor_ip
from app.config import Settings, get_settings
from app.content.loader import load_content
from app.content.models import Content
from app.core.errors import ApiError, InvalidRequestError, MessageTooLongError
from app.schemas.chat import ChatRequest, ErrorEvent, StreamEvent

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache
def _load_content(content_dir: Path) -> Content:
    return load_content(content_dir)


def get_mock_chat(settings: Annotated[Settings, Depends(get_settings)]) -> MockChat:
    return MockChat(_load_content(settings.content_dir))


async def accepted_question(
    request: Request,
    question: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    mock: Annotated[MockChat, Depends(get_mock_chat)],
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
    mock.check_limit(question)
    return question


@router.post("/chat", response_class=EventSourceResponse)
async def chat(
    question: Annotated[ChatRequest, Depends(accepted_question)],
    mock: Annotated[MockChat, Depends(get_mock_chat)],
) -> AsyncIterator[ServerSentEvent]:
    # Once streaming, the status is already 200: a failure becomes the stream's last event
    try:
        async for event in mock.answer(question):
            yield _to_sse(event)
    except ApiError as error:
        message = error_message(error.code, question.locale)
        yield _to_sse(ErrorEvent(code=error.code, message=message, retry_after=error.retry_after))
    except Exception:
        logger.exception("An answer failed partway")
        message = error_message("internal_error", question.locale)
        yield _to_sse(ErrorEvent(code="internal_error", message=message))


def _to_sse(event: StreamEvent) -> ServerSentEvent:
    return ServerSentEvent(event=event.name, data=event)
