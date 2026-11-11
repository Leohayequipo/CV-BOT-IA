"""evals/RESULTS.md: the latest run in detail and one line per run in a history table."""

from dataclasses import dataclass, field
from pathlib import Path

from app.evals.scoring import CaseResult, Summary

HISTORY_HEADER = (
    "| Date | Commit | Cases | Passed | Fact recall | Policy | Faithful | Citations | Routing "
    "| p95 s | Tokens/case |\n|---|---|---|---|---|---|---|---|---|---|---|"
)
INTRO = (
    "# Eval results\n\n"
    "Scores of the assistant over `evals/questions.yaml`, from `uv run python -m app.evals.run "
    "--write` in `backend/` (ADR-031). Each case passes only if every fact is said, no forbidden "
    "claim is made, nothing is unsupported by the content, the citations are valid, the route is "
    "right and the language matches. The judge is a model with a written rubric, so a score "
    "moves a little between runs of the same code.\n"
)


@dataclass(frozen=True)
class RunMeta:
    date: str
    commit: str
    answer_model: str
    guardrail_model: str
    judge_model: str
    embedding_model: str
    skipped: list[str] = field(default_factory=list)


def _pct(value: float) -> str:
    return f"{value * 100:.0f} %"


def history_row(summary: Summary, meta: RunMeta) -> str:
    metrics = summary.metrics
    return (
        f"| {meta.date} | {meta.commit} | {summary.cases} | {summary.passed} "
        f"| {_pct(metrics['fact_recall'])} | {_pct(metrics['policy_compliance'])} "
        f"| {_pct(metrics['faithfulness'])} | {_pct(metrics['citation_validity'])} "
        f"| {_pct(metrics['routing_accuracy'])} | {summary.latency_p95:.1f} "
        f"| {summary.tokens_per_case} |"
    )


def render_run(summary: Summary, results: list[CaseResult], meta: RunMeta) -> str:
    metric_names = {
        "fact_recall": "Fact recall",
        "policy_compliance": "Policy compliance",
        "faithfulness": "Faithfulness",
        "citation_validity": "Citation validity",
        "routing_accuracy": "Routing accuracy",
        "language_match": "Language match",
    }
    lines = [
        f"## Latest run: {meta.date}, commit {meta.commit}",
        "",
        f"Answers `{meta.answer_model}`, guardrail `{meta.guardrail_model}`, judge "
        f"`{meta.judge_model}`, embeddings `{meta.embedding_model}`.",
        "",
        f"**{summary.passed} of {summary.cases} cases passed** "
        f"({summary.errors} not graded because of an error).",
        "",
        "| Metric | Score |",
        "|---|---|",
        *(f"| {title} | {_pct(summary.metrics[key])} |" for key, title in metric_names.items()),
        f"| Latency p50 / p95 | {summary.latency_p50:.1f} s / {summary.latency_p95:.1f} s |",
        f"| Tokens per case (answer, guardrail and search) | {summary.tokens_per_case} |",
        "",
        "| Category | Passed |",
        "|---|---|",
        *(
            f"| {name} | {passed} of {total} |"
            for name, (passed, total) in summary.by_category.items()
        ),
    ]
    failed = [result for result in results if not result.passed]
    if failed:
        lines += ["", "### Cases that failed", ""]
        for result in failed:
            lines.append(f"- `{result.case.id}` ({result.case.category})")
            lines += [f"  - {reason}" for reason in result.failures]
    if meta.skipped:
        lines += [
            "",
            "Not run, because their agent arrives in Phase 6: " + ", ".join(meta.skipped) + ".",
        ]
    return "\n".join(lines) + "\n"


def update_results_file(path: Path, run: str, row: str) -> None:
    """Replace the latest run and put its row on top of the history."""
    rows: list[str] = []
    if path.exists():
        rows = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("| 20")
        ]
    history = "\n".join([HISTORY_HEADER, row, *rows])
    path.write_text(f"{INTRO}\n{run}\n## History\n\n{history}\n", encoding="utf-8")
