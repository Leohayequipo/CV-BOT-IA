from pathlib import Path
from typing import Any

import pytest
import yaml

from app.content.loader import load_content
from app.core.errors import InvalidContentError


@pytest.fixture
def minimal_content_dir(tmp_path: Path, profile_data: dict[str, Any]) -> Path:
    """A content/ folder with the minimal profile, its photo and no case studies."""
    (tmp_path / "profile.yaml").write_text(yaml.safe_dump(profile_data), encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "profile-photo.jpg").write_bytes(b"")
    (tmp_path / "case-studies").mkdir()
    return tmp_path


def test_minimal_content_is_loaded(minimal_content_dir: Path) -> None:
    content = load_content(minimal_content_dir)

    assert content.profile.basics.name == "Ada Example"
    assert content.case_studies == ()


def test_missing_profile_photo_is_rejected(minimal_content_dir: Path) -> None:
    (minimal_content_dir / "assets" / "profile-photo.jpg").unlink()

    with pytest.raises(InvalidContentError, match="the profile photo doesn't exist"):
        load_content(minimal_content_dir)


def test_files_starting_with_underscore_are_skipped(minimal_content_dir: Path) -> None:
    (minimal_content_dir / "case-studies" / "_draft.md").write_text("Not ready.", encoding="utf-8")

    assert load_content(minimal_content_dir).case_studies == ()
