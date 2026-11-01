import pytest

from app.config import Settings


def test_settings_read_the_commit_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_SHA", "abc1234")

    assert Settings(_env_file=None).git_sha == "abc1234"


def test_settings_say_local_when_no_commit_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GIT_SHA", raising=False)

    assert Settings(_env_file=None).git_sha == "local"
