"""Turn content values into the text visitors read, in their language."""

from app.content.models import Locale, Localized

# Month abbreviations as the approved designs show them: "Aug 2026", "ago. 2026"
_MONTHS: dict[Locale, tuple[str, ...]] = {
    "en": ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
    "es": (
        "ene.",
        "feb.",
        "mar.",
        "abr.",
        "may.",
        "jun.",
        "jul.",
        "ago.",
        "sept.",
        "oct.",
        "nov.",
        "dic.",
    ),
}
_PRESENT: dict[Locale, str] = {"en": "present", "es": "hoy"}


def localize(text: Localized | str, locale: Locale) -> str:
    """The text in the visitor's language; plain strings read the same in both."""
    if isinstance(text, str):
        return text
    return text.en if locale == "en" else text.es


def format_date(date: str, locale: Locale) -> str:
    """'2023-10' becomes 'Oct 2023'; a year alone stays as it is."""
    year, _, month = date.partition("-")
    if not month:
        return year
    return f"{_MONTHS[locale][int(month) - 1]} {year}"


def format_period(start: str, end: str | None, locale: Locale) -> str:
    """'Oct 2023 – present', or 'oct. 2023 – hoy' in Spanish."""
    finish = _PRESENT[locale] if end is None else format_date(end, locale)
    return f"{format_date(start, locale)} – {finish}"
