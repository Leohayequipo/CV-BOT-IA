"""The single shape of every error response: {"error": {"code": ..., "message": ...}}."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
