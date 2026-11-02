from typing import Any

from app.content.export import SITE_PROFILE, render, site_profile
from app.content.models import Content, Profile


def test_site_copy_of_the_profile_is_up_to_date(content: Content) -> None:
    committed = SITE_PROFILE.read_text(encoding="utf-8")

    assert committed == render(content.profile), (
        "frontend/src/content/profile.json is out of date: "
        "run `uv run python -m app.content.export` in backend/ and commit the result"
    )


def test_roles_carry_their_period_in_both_languages(profile_data: dict[str, Any]) -> None:
    data = site_profile(Profile.model_validate(profile_data))

    assert data["experience"][0]["roles"][0]["period"] == {
        "en": "Jan 2022 – present",
        "es": "ene. 2022 – hoy",
    }


def test_companies_carry_their_initials(profile_data: dict[str, Any]) -> None:
    profile_data["experience"][0]["company"] = "Tres Barbas Games"

    data = site_profile(Profile.model_validate(profile_data))

    assert data["experience"][0]["initials"] == "TB"
