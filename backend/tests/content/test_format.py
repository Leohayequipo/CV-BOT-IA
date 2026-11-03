import pytest

from app.content.format import format_period, localize
from app.content.models import Locale, Localized


@pytest.mark.parametrize(
    ("start", "end", "locale", "expected"),
    [
        ("2026-08", None, "en", "Aug 2026 – present"),
        ("2026-08", None, "es", "ago. 2026 – hoy"),
        ("2022-01", "2023-12", "es", "ene. 2022 – dic. 2023"),
        ("2017", "2022", "en", "2017 – 2022"),
    ],
)
def test_period_reads_as_in_the_designs(
    start: str, end: str | None, locale: Locale, expected: str
) -> None:
    assert format_period(start, end, locale) == expected


def test_localize_picks_the_visitors_language() -> None:
    text = Localized(en="queues", es="colas")

    assert (localize(text, "en"), localize(text, "es")) == ("queues", "colas")


def test_localize_keeps_a_text_shared_by_both_languages() -> None:
    assert localize("Python", "es") == "Python"
