"""Build the chat cards from the profile, so everything a card shows is in content/."""

import re

from app.content.format import format_period, localize
from app.content.models import Experience, Locale, Localized, Profile
from app.schemas.cards import ProjectCard, SkillsCard, SkillsGroup, TimelineCard, TimelineItem

# Projects with their own colours in DESIGN.md
BRANDS = frozenset({"servime"})

_WORD = re.compile(r"\w+")
# "Nº" (number) is an abbreviation, not a word of the name
_ABBREVIATIONS = frozenset({"nº"})


def initials(company: str) -> str:
    """'Tres Barbas Games' becomes 'TB', 'ServiME' 'SM' and 'EEST Nº 1' 'E1'."""
    words = [
        word
        for word in _WORD.findall(company)
        if (word[0].isupper() or word[0].isdigit()) and word.casefold() not in _ABBREVIATIONS
    ]
    if len(words) == 1:
        # One word: its capitals, as in ServiME
        capitals = [letter for letter in words[0] if letter.isupper()]
        return "".join(capitals[:2]) if len(capitals) > 1 else words[0][:2].upper()
    return "".join(word[0] for word in words[:2]).upper()


def project_card(entry: Experience, highlight: Localized, locale: Locale) -> ProjectCard:
    """A company's card from its latest role, with the highlight to show as its key result."""
    role = entry.roles[0]
    return ProjectCard(
        name=entry.display_name,
        summary=localize(entry.description, locale) if entry.description else "",
        role=localize(role.title, locale),
        period=format_period(role.start, role.end, locale),
        highlight=localize(highlight, locale),
        stack=role.stack,
        url=str(entry.url) if entry.url else None,
        brand=entry.id if entry.id in BRANDS else None,
    )


def timeline_card(profile: Profile, locale: Locale) -> TimelineCard:
    """Every role, newest first; the profile lists companies by relevance instead."""
    rows = [
        (
            role.start,
            TimelineItem(
                role=localize(role.title, locale),
                company=entry.display_name,
                period=format_period(role.start, role.end, locale),
                initials=initials(entry.company),
            ),
        )
        for entry in profile.experience
        for role in entry.roles
    ]
    # Partial dates sort correctly as text: "2026-08", "2026-01", "2019-03", "2017"
    rows.sort(key=lambda row: row[0], reverse=True)
    return TimelineCard(items=[item for _, item in rows])


def skills_card(profile: Profile, group_ids: tuple[str, ...], locale: Locale) -> SkillsCard:
    """The chosen skill groups, in the order given, each with its main items."""
    groups = {group.id: group for group in profile.skills}
    return SkillsCard(
        groups=[
            SkillsGroup(
                label=localize(groups[group_id].label, locale),
                items=[
                    localize(item, locale)
                    for item in groups[group_id].items[: groups[group_id].main]
                ],
            )
            for group_id in group_ids
        ]
    )
