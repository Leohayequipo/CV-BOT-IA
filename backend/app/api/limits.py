"""The request limits as FastAPI dependencies: one set per app, so tests start clean."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.core.limits import DailyBudget, SlidingWindowLimiter, client_ip


@dataclass
class Limits:
    chat_by_session: SlidingWindowLimiter
    chat_by_ip: SlidingWindowLimiter
    contact_by_ip: SlidingWindowLimiter
    budget: DailyBudget

    @classmethod
    def from_settings(cls, settings: Settings) -> "Limits":
        return cls(
            chat_by_session=SlidingWindowLimiter(
                settings.chat_session_limit, settings.chat_session_window
            ),
            chat_by_ip=SlidingWindowLimiter(settings.chat_ip_limit, settings.chat_ip_window),
            contact_by_ip=SlidingWindowLimiter(
                settings.contact_ip_limit, settings.contact_ip_window
            ),
            budget=DailyBudget(settings.daily_token_budget),
        )


def get_limits(request: Request) -> Limits:
    limits: Limits = request.app.state.limits
    return limits


def visitor_ip(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> str:
    peer = request.client.host if request.client else None
    return client_ip(request.headers.get("x-forwarded-for"), peer, settings.trusted_proxy_hops)
