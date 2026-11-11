"""What one answer scored, and the numbers a whole run adds up to."""

import math
import re
from dataclasses import dataclass, field

from app.evals.cases import EvalCase
from app.evals.judge import Grade

MARKER = re.compile(r"\[(\d+)\]")
# A source id the model wrote that never became a number: `[profile:summary]`, `[servime#results]`
RAW_SOURCE_ID = re.compile(r"\[[a-z0-9][a-z0-9-]*[:#][a-z0-9:#_-]+\]")


def citations_valid(answer: str, citation_ids: list[int]) -> bool:
    """Every [n] in the text has its citation event, and no raw source id is left over."""
    numbers = {int(number) for number in MARKER.findall(answer)}
    return numbers <= set(citation_ids) and not RAW_SOURCE_ID.search(answer)


@dataclass(frozen=True)
class CaseResult:
    case: EvalCase
    answer: str = ""
    nodes: list[str] = field(default_factory=list)
    citation_ids: list[int] = field(default_factory=list)
    latency: float = 0.0
    tokens: int = 0
    grade: Grade | None = None
    error: str | None = None

    @property
    def routed_correctly(self) -> bool:
        # The profile agent only runs for what the guardrail lets through
        return ("profile" not in self.nodes) == (self.case.route == "guardrail")

    @property
    def recall(self) -> float:
        if self.grade is None or not self.grade.included:
            return 1.0 if self.grade else 0.0
        return sum(self.grade.included) / len(self.grade.included)

    @property
    def clean(self) -> bool:
        return self.grade is not None and not any(self.grade.violated)

    @property
    def faithful(self) -> bool:
        return self.grade is not None and not self.grade.unsupported

    @property
    def language_ok(self) -> bool:
        return self.grade is not None and self.grade.language_matches

    @property
    def cited(self) -> bool:
        valid = citations_valid(self.answer, self.citation_ids)
        return valid and (bool(self.citation_ids) or not self.case.needs_citation)

    @property
    def failures(self) -> list[str]:
        """Why the case didn't pass, in words; empty when it passed."""
        if self.error or self.grade is None:
            return [f"error: {self.error or 'not graded'}"]
        case, grade = self.case, self.grade
        reasons = [
            f"missing: {fact}"
            for fact, ok in zip(case.must_include, grade.included, strict=True)
            if not ok
        ]
        reasons += [
            f"forbidden: {claim}"
            for claim, hit in zip(case.must_not_include, grade.violated, strict=True)
            if hit
        ]
        reasons += [f"unsupported: {claim}" for claim in grade.unsupported]
        if not self.routed_correctly:
            reasons.append(f"routing: expected the {case.route} route, got nodes {self.nodes}")
        if not self.cited:
            reasons.append("citations: a marker without its citation, or none where one is needed")
        if not grade.language_matches:
            reasons.append("language: the answer isn't in the question's language")
        return reasons

    @property
    def passed(self) -> bool:
        return not self.failures


@dataclass(frozen=True)
class Summary:
    cases: int
    passed: int
    errors: int
    metrics: dict[str, float]
    by_category: dict[str, tuple[int, int]]
    latency_p50: float
    latency_p95: float
    tokens_per_case: int


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 1.0


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def summarize(results: list[CaseResult]) -> Summary:
    graded = [result for result in results if result.grade is not None]
    with_policies = [result for result in graded if result.case.policies]
    categories: dict[str, tuple[int, int]] = {}
    for result in results:
        passed, total = categories.get(result.case.category, (0, 0))
        categories[result.case.category] = (passed + result.passed, total + 1)
    latencies = [result.latency for result in results]
    return Summary(
        cases=len(results),
        passed=sum(result.passed for result in results),
        errors=len(results) - len(graded),
        metrics={
            "fact_recall": _mean([result.recall for result in graded]),
            "policy_compliance": _mean([result.clean for result in with_policies]),
            "faithfulness": _mean([result.faithful for result in graded]),
            "citation_validity": _mean([result.cited for result in graded]),
            "routing_accuracy": _mean([result.routed_correctly for result in results]),
            "language_match": _mean([result.language_ok for result in graded]),
        },
        by_category=dict(sorted(categories.items())),
        latency_p50=percentile(latencies, 0.5),
        latency_p95=percentile(latencies, 0.95),
        tokens_per_case=round(sum(r.tokens for r in results) / len(results)) if results else 0,
    )
