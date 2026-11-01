"""Turn every error into the API's single shape, in the visitor's language, hiding internals."""

import logging
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.content.models import Locale
from app.core.errors import ApiError
from app.schemas.errors import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)

_STATUS = {
    "invalid_request": 422,
    "message_too_long": 422,
    "rate_limited": 429,
    "upstream_unavailable": 503,
}

# One sentence for what happened and one for what to do, as DESIGN.md's copy rules ask
_MESSAGES: dict[str, dict[Locale, str]] = {
    "invalid_request": {
        "en": "Your question couldn't be sent. Reload the page and try again.",
        "es": "No se pudo enviar tu pregunta. Recargá la página y volvé a intentarlo.",
    },
    "message_too_long": {
        "en": "Your message is too long. Shorten it and try again.",
        "es": "Tu mensaje es demasiado largo. Acortalo y volvé a intentarlo.",
    },
    "rate_limited": {
        "en": "You've reached the question limit for now. Try again in a few minutes.",
        "es": "Llegaste al límite de preguntas por ahora. Volvé a intentarlo en unos minutos.",
    },
    "upstream_unavailable": {
        "en": "The assistant couldn't answer right now. Try again in a moment.",
        "es": "El asistente no pudo responder en este momento. Volvé a intentarlo en un momento.",
    },
    "internal_error": {
        "en": "Something went wrong on our side. Try again in a moment.",
        "es": "Algo falló de nuestro lado. Volvé a intentarlo en un momento.",
    },
}


def error_message(code: str, locale: Locale) -> str:
    return _MESSAGES[code][locale]


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException) -> JSONResponse:
        # "Not Found" becomes "not_found"
        code = HTTPStatus(error.status_code).phrase.lower().replace(" ", "_")
        return _error_response(error.status_code, code, str(error.detail), error.headers)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError) -> JSONResponse:
        message = error_message("invalid_request", _locale_of(error.body))
        return _error_response(422, "invalid_request", message)

    @app.exception_handler(ApiError)
    async def api_error(request: Request, error: ApiError) -> JSONResponse:
        # Endpoints store the locale once the body is valid; before that, English
        locale: Locale = getattr(request.state, "locale", "en")
        headers = None if error.retry_after is None else {"Retry-After": str(error.retry_after)}
        message = error_message(error.code, locale)
        return _error_response(_STATUS[error.code], error.code, message, headers)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, error: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return _error_response(500, "internal_error", error_message("internal_error", "en"))


def _locale_of(body: Any) -> Locale:
    """The locale of a body that failed validation, when it has a valid one."""
    if isinstance(body, dict) and body.get("locale") == "es":
        return "es"
    return "en"


def _error_response(
    status_code: int, code: str, message: str, headers: Mapping[str, str] | None = None
) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(body.model_dump(), status_code=status_code, headers=headers)
