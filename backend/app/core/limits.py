"""Abuse and cost protection: a rate limiter, a daily token budget and the visitor's IP.

State lives in memory. That is enough while the API runs as one instance (ADR-029); a restart
forgets the counts, which only ever lets a visitor ask a little more.
"""

import math
import time
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.core.errors import RateLimitedError

# Above this many tracked visitors the limiter forgets the ones whose window has passed
MAX_TRACKED_KEYS = 10_000


class SlidingWindowLimiter:
    """At most `limit` hits per key in any `window` seconds."""

    def __init__(
        self,
        limit: int,
        window: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._limit = limit
        self._window = window
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}

    @property
    def tracked(self) -> int:
        """How many visitors are being counted."""
        return len(self._hits)

    def check(self, key: str) -> None:
        """Count a hit, or raise RateLimitedError saying when the next one is allowed."""
        now = self._clock()
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] <= now - self._window:
            hits.popleft()
        if len(hits) >= self._limit:
            raise RateLimitedError(retry_after=math.ceil(hits[0] + self._window - now))
        hits.append(now)
        if len(self._hits) > MAX_TRACKED_KEYS:
            self._forget_idle(now)

    def _forget_idle(self, now: float) -> None:
        self._hits = {
            key: hits for key, hits in self._hits.items() if hits and hits[-1] > now - self._window
        }


class DailyBudget:
    """Tokens the models may use per UTC day; asking stops for the rest of the day once spent."""

    def __init__(
        self, tokens: int, now: Callable[[], datetime] = lambda: datetime.now(UTC)
    ) -> None:
        self._tokens = tokens
        self._now = now
        self._day = now().date()
        self._used = 0

    def check(self) -> None:
        self._roll_over()
        if self._used >= self._tokens:
            raise RateLimitedError(retry_after=self._seconds_to_midnight())

    def record(self, tokens: int) -> None:
        self._roll_over()
        self._used += tokens

    def _roll_over(self) -> None:
        today = self._now().date()
        if today != self._day:
            self._day, self._used = today, 0

    def _seconds_to_midnight(self) -> int:
        now = self._now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), UTC)
        return math.ceil((midnight - now).total_seconds())


def client_ip(forwarded_for: str | None, peer: str | None, trusted_hops: int) -> str:
    """The visitor's address, taking only the proxies we run as trustworthy.

    Anyone can send an X-Forwarded-For header, and each proxy appends the address it saw. With
    `trusted_hops` proxies of ours in front (Railway's edge is one), the entry that counts is
    that many places from the right; everything to its left was written by the visitor. With 0
    the header is ignored and the socket's peer is used.
    """
    if trusted_hops > 0 and forwarded_for:
        addresses = [part.strip() for part in forwarded_for.split(",") if part.strip()]
        if len(addresses) >= trusted_hops:
            return addresses[-trusted_hops]
    return peer or "unknown"
