"""Runs the recruiter questions through the assistant and scores the answers.

From backend/: `uv run python -m app.evals.run`. It calls the real models, so it costs a little
and needs the keys in .env. `--write` records the run in evals/RESULTS.md.
"""

import argparse
import asyncio
import subprocess
import time
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from app.agents.assistant import Assistant, build_assistant
from app.agents.profile_agent import read_policies
from app.agents.profile_context import render_profile
from app.config import Settings, get_settings
from app.content.loader import load_content
from app.evals.cases import EVALS_DIR, EvalCase, load_cases
from app.evals.judge import Judge, JudgeError, reference_text
from app.evals.report import RunMeta, history_row, render_run, update_results_file
from app.evals.scoring import CaseResult, summarize
from app.llm.chat import OpenAIChatModel
from app.llm.client import async_openai_client
from app.observability.tracing import Tracing, current_trace
from app.schemas.chat import ChatRequest, CitationEvent, NodeEvent, TokenEvent


class TokenCounter:
    def __init__(self) -> None:
        self.tokens = 0

    def record(self, tokens: int) -> None:
        self.tokens += tokens


async def run_case(
    case: EvalCase,
    make_assistant: Callable[[TokenCounter], Assistant],
    judge: Judge,
    tracing: Tracing | None = None,
) -> CaseResult:
    counter = TokenCounter()
    request = ChatRequest(message=case.question, history=[], locale=case.lang, session_id=uuid4())
    trace = tracing.start(request) if tracing else None
    current_trace.set(trace)
    answer = ""
    nodes: list[str] = []
    citation_ids: list[int] = []
    started = time.monotonic()
    try:
        async for event in make_assistant(counter).answer(request):
            if isinstance(event, TokenEvent):
                answer += event.text
            elif isinstance(event, NodeEvent):
                nodes.append(event.node)
            elif isinstance(event, CitationEvent):
                citation_ids.append(event.id)
    except Exception as failure:  # a case that fails is a result, not a crash
        return CaseResult(case, answer, nodes, citation_ids, error=type(failure).__name__)
    finally:
        if trace:
            trace.end(answer, {"case": case.id, "nodes": nodes})
    latency = time.monotonic() - started
    grade, problem = None, None
    for _ in range(2):
        try:
            grade = await judge.grade(case, answer)
            break
        except JudgeError as unusable:
            problem = str(unusable)
    return CaseResult(
        case,
        answer,
        nodes,
        citation_ids,
        latency,
        counter.tokens,
        grade,
        None if grade else problem,
    )


def current_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607 - git is on the PATH of whoever runs the evals
            capture_output=True,
            text=True,
            check=True,
            cwd=EVALS_DIR,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()


async def run_all(cases: list[EvalCase], settings: Settings, concurrency: int) -> list[CaseResult]:
    content = load_content(settings.content_dir)
    if settings.openai_api_key is None:
        msg = "OPENAI_API_KEY must be set"
        raise RuntimeError(msg)
    reference = reference_text(
        content,
        render_profile(content.profile, settings.contact_email, settings.contact_phone),
        read_policies(settings.content_dir),
    )
    judge = Judge(
        OpenAIChatModel(
            async_openai_client(settings.openai_api_key),
            settings.judge_model,
            settings.judge_max_tokens,
            settings.judge_reasoning_effort,
        ),
        reference,
    )
    tracing = Tracing.from_settings(settings)
    limit = asyncio.Semaphore(concurrency)
    done = 0

    async def one(case: EvalCase) -> CaseResult:
        nonlocal done
        async with limit:
            result = await run_case(
                case, lambda counter: build_assistant(settings, content, counter), judge, tracing
            )
        done += 1
        mark = "pass" if result.passed else "FAIL"
        print(f"[{done}/{len(cases)}] {mark} {case.id}", flush=True)
        return result

    try:
        return await asyncio.gather(*(one(case) for case in cases))
    finally:
        tracing.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Score the assistant on the recruiter questions.")
    parser.add_argument("--only", help="comma-separated case ids to run")
    parser.add_argument("--write", action="store_true", help="record the run in evals/RESULTS.md")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    # Traces of eval runs get their own environment, apart from visitors' conversations
    # Made-up contact details, so scores don't depend on the developer's .env and the
    # published results never hold a real address
    settings = get_settings().model_copy(
        update={
            "langfuse_environment": "eval",
            "contact_email": "leonardo@example.com",
            "contact_phone": "+00 0000 0000",
        }
    )
    every_case = load_cases()
    wanted = set(args.only.split(",")) if args.only else {case.id for case in every_case}
    unknown = wanted - {case.id for case in every_case}
    if unknown:
        parser.error(f"unknown case ids: {', '.join(sorted(unknown))}")
    chosen = [case for case in every_case if case.id in wanted and case.supported]
    skipped = [case.id for case in every_case if case.id in wanted and not case.supported]

    results = asyncio.run(run_all(chosen, settings, args.concurrency))
    summary = summarize(results)
    meta = RunMeta(
        date=datetime.now(UTC).date().isoformat(),
        commit=current_commit(),
        answer_model=settings.answer_model,
        guardrail_model=settings.guardrail_model,
        judge_model=settings.judge_model,
        embedding_model=settings.embedding_model,
        skipped=skipped,
    )
    report = render_run(summary, results, meta)
    print("\n" + report)
    if args.write:
        update_results_file(EVALS_DIR / "RESULTS.md", report, history_row(summary, meta))
        print(f"Recorded in {EVALS_DIR / 'RESULTS.md'}")


if __name__ == "__main__":
    main()
