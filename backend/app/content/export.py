"""Export the profile as JSON for the site, which can't read YAML (ADR-023).

After changing content/profile.yaml, run from backend/:

    uv run python -m app.content.export

A test fails while the committed file is out of date.
"""

import json
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.content.cards import initials
from app.content.format import format_period
from app.content.loader import load_content
from app.content.models import Profile

SITE_PROFILE = Path(__file__).resolve().parents[3] / "frontend" / "src" / "content" / "profile.json"


def site_profile(profile: Profile) -> dict[str, Any]:
    """The whole profile, plus what the site would otherwise have to compute a second time:
    each company's initials and each role's period in both languages."""
    data: dict[str, Any] = profile.model_dump(mode="json")
    for entry, exported in zip(profile.experience, data["experience"], strict=True):
        exported["initials"] = initials(entry.company)
        for role, exported_role in zip(entry.roles, exported["roles"], strict=True):
            exported_role["period"] = {
                "en": format_period(role.start, role.end, "en"),
                "es": format_period(role.start, role.end, "es"),
            }
    return data


def render(profile: Profile) -> str:
    return json.dumps(site_profile(profile), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    profile = load_content(get_settings().content_dir).profile
    SITE_PROFILE.write_text(render(profile), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
