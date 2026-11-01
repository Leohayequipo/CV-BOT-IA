from typing import Any

import pytest
from pydantic import ValidationError

from app.content.models import Profile


def test_minimal_profile_is_valid(profile_data: dict[str, Any]) -> None:
    profile = Profile.model_validate(profile_data)

    assert profile.entry_ids == {"acme", "demo"}


def test_text_without_spanish_version_is_rejected(profile_data: dict[str, Any]) -> None:
    del profile_data["basics"]["headline"]["es"]

    with pytest.raises(ValidationError, match=r"basics\.headline\.es"):
        Profile.model_validate(profile_data)


def test_misspelled_key_is_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["summery"] = profile_data.pop("summary")

    with pytest.raises(ValidationError, match="summery"):
        Profile.model_validate(profile_data)


def test_date_in_another_format_is_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["experience"][0]["roles"][0]["start"] = "Aug 2026"

    with pytest.raises(ValidationError, match="should match pattern"):
        Profile.model_validate(profile_data)


def test_role_ending_before_it_starts_is_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["experience"][0]["roles"][1]["end"] = "2018-06"

    with pytest.raises(ValidationError, match=r"ends \(2018-06\) before it starts \(2019\)"):
        Profile.model_validate(profile_data)


def test_end_in_the_same_year_without_month_is_accepted(profile_data: dict[str, Any]) -> None:
    profile_data["experience"][0]["roles"][1]["end"] = "2019"

    Profile.model_validate(profile_data)


def test_role_without_end_key_is_rejected(profile_data: dict[str, Any]) -> None:
    del profile_data["experience"][0]["roles"][0]["end"]

    with pytest.raises(ValidationError, match=r"roles\.0\.end"):
        Profile.model_validate(profile_data)


def test_roles_out_of_order_are_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["experience"][0]["roles"].reverse()

    with pytest.raises(ValidationError, match="most recent first"):
        Profile.model_validate(profile_data)


def test_project_reusing_an_experience_id_is_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["projects"]["items"][0]["id"] = "acme"

    with pytest.raises(ValidationError, match="duplicate experience or project ids: acme"):
        Profile.model_validate(profile_data)


def test_photo_outside_the_assets_folder_is_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["basics"]["photo"]["path"] = "assets/../../secrets.png"

    with pytest.raises(ValidationError, match=r"basics\.photo\.path"):
        Profile.model_validate(profile_data)


def test_id_with_spaces_is_rejected(profile_data: dict[str, Any]) -> None:
    profile_data["experience"][0]["id"] = "Acme Corp"

    with pytest.raises(ValidationError, match="should match pattern"):
        Profile.model_validate(profile_data)
