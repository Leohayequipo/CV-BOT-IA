"""Find contact details that must never be published (ADR-012)."""

import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Digits with the separators phone numbers use. Years and counts match too, so a candidate
# only counts as a phone number when it has enough digits.
_PHONE_CANDIDATE = re.compile(r"\+?\d[\d\s().-]{6,}\d")
_MIN_PHONE_DIGITS = 9


def find_contact_details(text: str) -> list[str]:
    """Return every email address and phone number found in `text`."""
    phones = [
        candidate
        for candidate in _PHONE_CANDIDATE.findall(text)
        if sum(char.isdigit() for char in candidate) >= _MIN_PHONE_DIGITS
    ]
    return _EMAIL.findall(text) + phones
