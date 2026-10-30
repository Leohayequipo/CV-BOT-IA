"""Read the files in content/ and validate them against the schema in models.py."""

import re
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.content.models import CaseStudy, Content, Profile
from app.core.errors import InvalidContentError

_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_CODE_FENCE = "```"


def load_content(content_dir: Path) -> Content:
    """Load the profile and every case study, and check the references between them."""
    profile = load_profile(content_dir / "profile.yaml")
    photo = content_dir / profile.basics.photo.path
    if not photo.is_file():
        raise InvalidContentError(photo, "the profile photo doesn't exist")
    case_studies = tuple(
        load_case_study(path)
        for path in sorted((content_dir / "case-studies").glob("*.md"))
        if not path.name.startswith("_")  # templates and drafts
    )
    try:
        return Content(profile=profile, case_studies=case_studies)
    except ValidationError as error:
        raise InvalidContentError(content_dir, _describe(error)) from error


def load_profile(path: Path) -> Profile:
    data = _parse_yaml(path, _read(path))
    try:
        return Profile.model_validate(data)
    except ValidationError as error:
        raise InvalidContentError(path, _describe(error)) from error


def load_case_study(path: Path) -> CaseStudy:
    front_matter, body = _split_front_matter(path, _read(path))
    title, sections = _split_sections(_HTML_COMMENT.sub("", body))
    data = {"meta": _parse_yaml(path, front_matter), "title": title, "sections": sections}
    try:
        case_study = CaseStudy.model_validate(data)
    except ValidationError as error:
        raise InvalidContentError(path, _describe(error)) from error
    if not path.name.startswith("_") and path.stem != case_study.meta.id:
        raise InvalidContentError(path, f"the file name must match its id: {case_study.meta.id}.md")
    return case_study


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise InvalidContentError(path, f"can't be read ({error.strerror})") from error


def _parse_yaml(path: Path, text: str) -> object:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise InvalidContentError(path, f"invalid YAML: {error}") from error


def _split_front_matter(path: Path, text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise InvalidContentError(path, "must start with YAML front matter between '---' lines")
    closing = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None
    )
    if closing is None:
        raise InvalidContentError(path, "the front matter is never closed with '---'")
    return "\n".join(lines[1:closing]), "\n".join(lines[closing + 1 :])


def _split_sections(markdown: str) -> tuple[str, dict[str, str]]:
    """Return the H1 title and the text under each H2 heading, ignoring code blocks."""
    title = ""
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    in_code_block = False
    for line in markdown.splitlines():
        if line.lstrip().startswith(_CODE_FENCE):
            in_code_block = not in_code_block
        elif not in_code_block and line.startswith("# ") and not title:
            title = line.removeprefix("# ").strip()
            continue
        elif not in_code_block and line.startswith("## "):
            current = sections.setdefault(line.removeprefix("## ").strip(), [])
            continue
        if current is not None:
            current.append(line)
    return title, {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _describe(error: ValidationError) -> str:
    """One problem per line, each with the path to the offending key."""
    return "\n".join(
        f"{'.'.join(str(part) for part in issue['loc']) or '(file)'}: {issue['msg']}"
        for issue in error.errors()
    )
