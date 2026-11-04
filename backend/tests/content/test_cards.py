from typing import Any

import pytest

from app.content.cards import initials, project_card, skills_card, timeline_card
from app.content.models import Content, Profile


@pytest.mark.parametrize(
    ("company", "expected"),
    [
        ("ServiME", "SM"),
        ("Simbel IA Studio", "SI"),
        ("Universidad Tecnológica Nacional, Facultad Regional Morón", "UT"),
        ('EEST Nº 1 "Raúl Scalabrini Ortiz"', "E1"),
        ("Tres Barbas Games", "TB"),
    ],
)
def test_initials_match_the_approved_design(company: str, expected: str) -> None:
    assert initials(company) == expected


def test_timeline_lists_every_role_newest_first(profile_data: dict[str, Any]) -> None:
    # The profile lists companies by relevance: Acme first, though Beta's role is newer
    profile_data["experience"].append(
        {
            "id": "beta",
            "company": "Beta Labs",
            "roles": [
                {
                    "title": {"en": "Advisor", "es": "Asesor"},
                    "start": "2023-05",
                    "end": "2023-12",
                    "highlights": [{"en": "Advised.", "es": "Asesoró."}],
                }
            ],
        }
    )

    card = timeline_card(Profile.model_validate(profile_data), "en")

    assert [(item.company, item.period) for item in card.items] == [
        ("Beta Labs", "May 2023 – Dec 2023"),
        ("Acme", "Jan 2022 – present"),
        ("Acme", "2019 – Dec 2021"),
    ]


def test_project_card_shows_the_brand_only_for_projects_with_their_own_colours(
    content: Content,
) -> None:
    servime, other = (
        next(entry for entry in content.profile.experience if entry.id == entry_id)
        for entry_id in ("servime", "simbel")
    )

    assert project_card(servime, servime.roles[0].highlights[-1], "en").brand == "servime"
    assert project_card(other, other.roles[0].highlights[0], "en").brand is None


def test_skills_card_keeps_the_requested_groups_in_order(content: Content) -> None:
    card = skills_card(content.profile, ("frontend", "ai"), "es")

    groups = {group.id: group for group in content.profile.skills}
    assert [group.label for group in card.groups] == [
        groups["frontend"].label.es,
        groups["ai"].label.es,
    ]


def test_timeline_uses_the_short_name_and_keeps_the_initials(
    profile_data: dict[str, Any],
) -> None:
    profile_data["experience"][0]["company"] = "Universidad Tecnológica Nacional"
    profile_data["experience"][0]["short_name"] = "UTN"

    card = timeline_card(Profile.model_validate(profile_data), "en")

    assert {(item.company, item.initials) for item in card.items} == {("UTN", "UT")}
