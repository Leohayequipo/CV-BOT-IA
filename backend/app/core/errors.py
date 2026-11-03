"""Domain errors raised by the backend."""

from pathlib import Path
from typing import ClassVar


class InvalidContentError(Exception):
    """A file in content/ is missing, malformed or breaks the content schema."""

    def __init__(self, path: Path, problem: str) -> None:
        super().__init__(f"{path}: {problem}")
        self.path = path
        self.problem = problem


class ApiError(Exception):
    """An error the visitor is told about; `code` is one of the codes in docs/API.md."""

    code: ClassVar[str]
    # Seconds the visitor should wait before trying again, when that's known
    retry_after: int | None = None


class InvalidRequestError(ApiError):
    code = "invalid_request"


class MessageTooLongError(ApiError):
    code = "message_too_long"


class RateLimitedError(ApiError):
    code = "rate_limited"

    def __init__(self, retry_after: int) -> None:
        super().__init__(f"try again in {retry_after} seconds")
        self.retry_after = retry_after


class UpstreamUnavailableError(ApiError):
    """The model provider failed or timed out after retries."""

    code = "upstream_unavailable"
