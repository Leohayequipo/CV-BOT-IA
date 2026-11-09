from datetime import UTC, datetime

import pytest

from app.core.errors import RateLimitedError
from app.core.limits import MAX_TRACKED_KEYS, DailyBudget, SlidingWindowLimiter, client_ip


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_hits_up_to_the_limit_pass_and_the_next_one_says_when_to_retry() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=2, window=60, clock=clock)

    limiter.check("a")
    clock.now += 10
    limiter.check("a")
    clock.now += 5
    with pytest.raises(RateLimitedError) as refused:
        limiter.check("a")

    # The oldest hit leaves the window 60 s after it, which is 45 s from now
    assert refused.value.retry_after == 45


def test_a_hit_that_ages_out_of_the_window_frees_a_place() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=1, window=60, clock=clock)
    limiter.check("a")

    clock.now += 60
    limiter.check("a")


def test_each_key_has_its_own_count() -> None:
    limiter = SlidingWindowLimiter(limit=1, window=60, clock=Clock())
    limiter.check("a")

    limiter.check("b")


def test_a_refused_hit_does_not_extend_the_wait() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=1, window=60, clock=clock)
    limiter.check("a")
    for _ in range(5):
        clock.now += 1
        with pytest.raises(RateLimitedError):
            limiter.check("a")

    clock.now += 55
    limiter.check("a")


def test_idle_visitors_are_forgotten_so_memory_stays_bounded() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=1, window=60, clock=clock)
    for number in range(MAX_TRACKED_KEYS + 1):
        limiter.check(str(number))
    clock.now += 61

    limiter.check("new")

    # Everyone else's window has passed; only the newcomer is still counted
    with pytest.raises(RateLimitedError):
        limiter.check("new")
    assert limiter.tracked == 1


def utc(day: int, hour: int = 12) -> datetime:
    return datetime(2026, 11, day, hour, tzinfo=UTC)


def test_the_budget_refuses_once_spent_and_says_how_long_until_midnight_utc() -> None:
    now = utc(9, hour=22)
    budget = DailyBudget(tokens=100, now=lambda: now)
    budget.check()

    budget.record(60)
    budget.check()
    budget.record(40)
    with pytest.raises(RateLimitedError) as refused:
        budget.check()

    assert refused.value.retry_after == 2 * 3600


def test_the_budget_starts_again_on_the_next_utc_day() -> None:
    clock = {"now": utc(9)}
    budget = DailyBudget(tokens=100, now=lambda: clock["now"])
    budget.record(100)

    clock["now"] = utc(10, hour=0)
    budget.check()


@pytest.mark.parametrize(
    ("forwarded", "peer", "hops", "expected"),
    [
        (None, "10.0.0.1", 0, "10.0.0.1"),
        ("6.6.6.6", "10.0.0.1", 0, "10.0.0.1"),
        ("203.0.113.5", "10.0.0.1", 1, "203.0.113.5"),
        ("6.6.6.6, 203.0.113.5", "10.0.0.1", 1, "203.0.113.5"),
        ("6.6.6.6, 203.0.113.5, 10.1.1.1", "10.0.0.1", 2, "203.0.113.5"),
        (None, "10.0.0.1", 1, "10.0.0.1"),
        ("203.0.113.5", "10.0.0.1", 2, "10.0.0.1"),
        (None, None, 0, "unknown"),
    ],
    ids=[
        "no proxy",
        "header ignored without trusted proxies",
        "one proxy",
        "a forged entry on the left is ignored",
        "two proxies",
        "no header behind a proxy",
        "fewer entries than trusted proxies",
        "no peer",
    ],
)
def test_the_visitor_ip_trusts_only_the_proxies_we_run(
    forwarded: str | None, peer: str | None, hops: int, expected: str
) -> None:
    assert client_ip(forwarded, peer, hops) == expected
