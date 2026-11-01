"""The real files in content/ and evals/: a broken fact must fail CI, not the chat."""

from pathlib import Path

from app.content.loader import load_case_study, load_content
from app.content.privacy import find_contact_details


def test_content_matches_the_schema(content_dir: Path) -> None:
    content = load_content(content_dir)

    assert content.profile.experience


def test_case_study_template_is_a_valid_case_study(content_dir: Path) -> None:
    template = load_case_study(content_dir / "case-studies" / "_TEMPLATE.md")

    assert template.meta.related


def test_published_files_have_no_contact_details(repo_root: Path) -> None:
    findings = [
        f"{path.relative_to(repo_root)}: {detail}"
        for folder in ("content", "evals")
        for path in sorted((repo_root / folder).rglob("*"))
        if path.is_file()
        for detail in find_contact_details(path.read_text(encoding="utf-8"))
    ]

    assert findings == []
