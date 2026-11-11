"""The recruiter questions in evals/questions.yaml (ADR-010), as typed cases."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from app.content.models import Locale

EVALS_DIR = Path(__file__).resolve().parents[3] / "evals"

Route = Literal["profile", "job_fit", "contact", "guardrail"]
# The agents that exist so far; the rest of the cases wait for Phase 6
SUPPORTED_ROUTES: frozenset[str] = frozenset({"profile", "guardrail"})
# Questions whose answer comes from the content, so the answer has to cite it
CITED_CATEGORIES = frozenset({"overview", "experience", "skills", "ai", "education", "languages"})


class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    lang: Locale
    category: str
    route: Route
    question: str
    policies: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)
    must_not_include: list[str] = Field(default_factory=list)

    @property
    def supported(self) -> bool:
        return self.route in SUPPORTED_ROUTES

    @property
    def needs_citation(self) -> bool:
        return self.route == "profile" and self.category in CITED_CATEGORIES


def load_cases(path: Path = EVALS_DIR / "questions.yaml") -> list[EvalCase]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [EvalCase.model_validate(case) for case in data["cases"]]
