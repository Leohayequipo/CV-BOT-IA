from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def content_dir(repo_root: Path) -> Path:
    return repo_root / "content"
