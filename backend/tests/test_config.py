import pytest

from app.config import Settings


def test_settings_read_the_commit_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_SHA", "abc1234")

    assert Settings(_env_file=None).git_sha == "abc1234"


def test_settings_say_local_when_no_commit_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GIT_SHA", raising=False)

    assert Settings(_env_file=None).git_sha == "local"


def test_settings_read_the_site_origins_as_a_json_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["https://example.com", "https://www.example.com"]')

    assert Settings(_env_file=None).cors_origins == (
        "https://example.com",
        "https://www.example.com",
    )
