from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.content.loader import load_case_study
from app.content.models import REQUIRED_SECTIONS, Content, Profile
from app.core.errors import InvalidContentError

WriteCaseStudy = Callable[[str, str], Path]


def test_valid_case_study_is_loaded(
    write_case_study: WriteCaseStudy, case_study_markdown: str
) -> None:
    case_study = load_case_study(write_case_study("demo.md", case_study_markdown))

    assert case_study.meta.id == "demo"
    assert case_study.title == "Demo"
    assert set(REQUIRED_SECTIONS) <= case_study.sections.keys()
    assert case_study.sections["Summary"] == "What Demo is."


def test_missing_required_section_is_rejected(
    write_case_study: WriteCaseStudy, case_study_markdown: str
) -> None:
    markdown = case_study_markdown.replace("## Results\nWhat Demo achieved.\n", "")

    with pytest.raises(InvalidContentError, match="missing or empty sections: Results"):
        load_case_study(write_case_study("demo.md", markdown))


def test_section_with_only_a_comment_counts_as_empty(
    write_case_study: WriteCaseStudy, case_study_markdown: str
) -> None:
    markdown = case_study_markdown.replace("What Demo achieved.", "<!-- numbers pending -->")

    with pytest.raises(InvalidContentError, match="missing or empty sections: Results"):
        load_case_study(write_case_study("demo.md", markdown))


def test_case_study_without_front_matter_is_rejected(write_case_study: WriteCaseStudy) -> None:
    with pytest.raises(InvalidContentError, match="must start with YAML front matter"):
        load_case_study(write_case_study("demo.md", "# Demo\n\n## Summary\nText.\n"))


def test_unclosed_front_matter_is_rejected(write_case_study: WriteCaseStudy) -> None:
    with pytest.raises(InvalidContentError, match="never closed"):
        load_case_study(write_case_study("demo.md", "---\nid: demo\n# Demo\n"))


def test_title_differing_from_front_matter_is_rejected(
    write_case_study: WriteCaseStudy, case_study_markdown: str
) -> None:
    markdown = case_study_markdown.replace("# Demo\n", "# Another title\n")

    with pytest.raises(InvalidContentError, match="differs from the front matter"):
        load_case_study(write_case_study("demo.md", markdown))


def test_file_name_must_match_the_id(
    write_case_study: WriteCaseStudy, case_study_markdown: str
) -> None:
    with pytest.raises(InvalidContentError, match=r"must match its id: demo\.md"):
        load_case_study(write_case_study("other-name.md", case_study_markdown))


def test_headings_inside_code_blocks_are_not_sections(
    write_case_study: WriteCaseStudy, case_study_markdown: str
) -> None:
    diagram = "How Demo works.\n\n```\n## not a heading\n```"
    markdown = case_study_markdown.replace("How Demo works.", diagram)

    case_study = load_case_study(write_case_study("demo.md", markdown))

    assert "not a heading" not in case_study.sections
    assert "## not a heading" in case_study.sections["Architecture"]


def test_case_study_related_to_an_unknown_id_is_rejected(
    write_case_study: WriteCaseStudy, case_study_markdown: str, profile_data: dict[str, Any]
) -> None:
    markdown = case_study_markdown.replace("related: [demo]", "related: [missing-project]")
    case_study = load_case_study(write_case_study("demo.md", markdown))

    with pytest.raises(ValidationError, match="aren't in the profile: missing-project"):
        Content(profile=Profile.model_validate(profile_data), case_studies=(case_study,))
