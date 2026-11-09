import re
from pathlib import Path

import pytest

from app.agents.profile_agent import build_system_prompt, read_policies
from app.agents.profile_context import render_profile
from app.agents.sources import PROFILE_SECTIONS, profile_sources
from app.content.models import Content
from app.prompts import render_prompt


def test_every_citable_profile_section_has_a_block_in_the_prompt(content: Content) -> None:
    text = render_profile(content.profile)

    for key in PROFILE_SECTIONS:
        assert f'<source id="profile:{key}">' in text
    assert set(profile_sources()) == {f"profile:{key}" for key in PROFILE_SECTIONS}


def test_the_profile_text_carries_the_facts_the_assistant_must_know(content: Content) -> None:
    text = render_profile(content.profile)

    assert "ServiME" in text
    assert "Jun 2025 – present" in text
    assert "Italian" in text


def test_the_profile_text_has_no_email_address_or_phone_number(content: Content) -> None:
    text = render_profile(content.profile)

    assert "@" not in text
    assert not re.search(r"\+?\d[\d\s().-]{8,}\d", text)


def test_the_system_prompt_holds_the_policies_and_the_profile(
    content: Content, content_dir: Path
) -> None:
    prompt = build_system_prompt(content.profile, read_policies(content_dir))

    assert "# Assistant policies" in prompt
    assert '<source id="profile:experience">' in prompt
    assert "{{" not in prompt


def test_the_system_prompt_is_the_same_every_time_so_it_can_be_cached(
    content: Content, content_dir: Path
) -> None:
    policies = read_policies(content_dir)

    assert build_system_prompt(content.profile, policies) == build_system_prompt(
        content.profile, policies
    )


def test_a_prompt_rejects_missing_or_extra_variables() -> None:
    with pytest.raises(ValueError, match="takes"):
        render_prompt("profile_agent", policies="x")
    with pytest.raises(ValueError, match="takes"):
        render_prompt("profile_agent", policies="x", profile="y", extra="z")
