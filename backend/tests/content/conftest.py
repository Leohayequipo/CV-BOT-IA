from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest


def _both(text: str) -> dict[str, str]:
    return {"en": text, "es": text}


@pytest.fixture
def profile_data() -> dict[str, Any]:
    """The smallest valid profile. Each test breaks one thing, so a failure has one cause."""
    return {
        "basics": {
            "name": "Ada Example",
            "photo": {"path": "assets/profile-photo.jpg", "alt": _both("Portrait of Ada")},
            "headline": _both("AI Engineer"),
            "focus": _both("RAG"),
            "location": _both("Argentina"),
            "citizenship": _both("Italian (EU)"),
            "work_authorization": _both("EU citizen"),
            "work_preference": _both("Remote"),
            "links": {
                "linkedin": "https://www.linkedin.com/in/example",
                "github": "https://github.com/example",
            },
        },
        "summary": _both("Builds AI products."),
        "skills": [
            {"id": "backend", "label": _both("Backend"), "items": ["Python", _both("queues")]},
        ],
        "experience": [
            {
                "id": "acme",
                "company": "Acme",
                "roles": [
                    {
                        "title": _both("Lead Developer"),
                        "start": "2022-01",
                        "end": None,
                        "highlights": [_both("Led the team.")],
                    },
                    {
                        "title": _both("Developer"),
                        "start": "2019",
                        "end": "2021-12",
                        "highlights": [_both("Built the platform.")],
                    },
                ],
            },
        ],
        "projects": {
            "note": _both("Private work."),
            "items": [
                {
                    "id": "demo",
                    "name": _both("Demo"),
                    "summary": _both("A demo."),
                    "stack": ["Python"],
                },
            ],
        },
        "education": [{"degree": _both("Degree"), "institution": "University", "year": "2014"}],
        "languages": [{"name": _both("Spanish"), "level": _both("Native")}],
    }


@pytest.fixture
def case_study_markdown() -> str:
    """The smallest valid case study; it relates to the `demo` project of `profile_data`."""
    return """\
---
id: demo
title: Demo
related: [demo]
period: "2026"
role: Lead developer
stack: [Python]
lang: en
---

# Demo

## Summary
What Demo is.

## Context and problem
Why Demo was needed.

## Leonardo's role
What Leonardo built.

## Architecture
How Demo works.

## Key decisions and trade-offs
What was chosen, and why.

## Results
What Demo achieved.
"""


@pytest.fixture
def write_case_study(tmp_path: Path) -> Callable[[str, str], Path]:
    def write(name: str, markdown: str) -> Path:
        path = tmp_path / name
        path.write_text(markdown, encoding="utf-8")
        return path

    return write
