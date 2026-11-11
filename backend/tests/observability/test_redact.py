import pytest

from app.observability.redact import redact


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Write to laura.gomez@example.co.uk please", "Write to [email] please"),
        ("My phone is +34 600 123 456.", "My phone is [phone]."),
        ("Call (011) 4444-5555 today", "Call [phone] today"),
        ("WhatsApp +54 9 11 5555-1234", "WhatsApp [phone]"),
        ("a@b.com and c@d.org", "[email] and [email]"),
    ],
)
def test_contact_details_are_replaced(text: str, expected: str) -> None:
    assert redact(data=text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Aug 2026 - present",
        "From 2016 to 2018, then 2022-01 until 2023-12",
        "He has 10 years of experience and led 8 developers",
        "servime#results scored 0.0312",
        "the answer costs $1,250",
    ],
)
def test_ordinary_text_with_dates_and_numbers_stays(text: str) -> None:
    assert redact(data=text) == text


def test_nested_data_is_redacted_everywhere_and_other_values_are_kept() -> None:
    data = {
        "input": [{"role": "user", "content": "me@example.com"}],
        "metadata": {"turns": 2, "ok": True, "none": None, "tuple": ("+34 600 123 456",)},
    }

    assert redact(data=data) == {
        "input": [{"role": "user", "content": "[email]"}],
        "metadata": {"turns": 2, "ok": True, "none": None, "tuple": ["[phone]"]},
    }
