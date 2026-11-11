from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import pytest

from app.agents.assistant import Assistant
from app.agents.guardrail import Guardrail
from app.agents.profile_agent import ProfileAgent
from app.content.models import Content
from app.evals.cases import EvalCase, load_cases
from app.evals.judge import Grade, Judge, JudgeError, parse_grade, reference_text
from app.evals.report import RunMeta, history_row, render_run, update_results_file
from app.evals.run import TokenCounter, run_case
from app.evals.scoring import CaseResult, citations_valid, percentile, summarize
from app.llm.chat import Message, ModelEvent, TextDelta, Usage
from app.rag.retrieval import Hit
from app.schemas.chat import ChatRequest, StreamEvent


def make_case(**changes: object) -> EvalCase:
    fields: dict[str, object] = {
        "id": "case",
        "lang": "en",
        "category": "experience",
        "route": "profile",
        "question": "What did he build?",
        "must_include": ["a fact", "another fact"],
        "must_not_include": ["a forbidden claim"],
    }
    return EvalCase.model_validate(fields | changes)


def good_grade() -> Grade:
    return Grade(included=[True, True], violated=[False], unsupported=[], language_matches=True)


def result(grade: Grade | None = None, **changes: object) -> CaseResult:
    fields: dict[str, object] = {
        "case": make_case(),
        "answer": "He built it [1].",
        "nodes": ["guardrail", "profile"],
        "citation_ids": [1],
        "grade": grade or good_grade(),
    }
    return CaseResult(**(fields | changes))  # type: ignore[arg-type]


def test_every_case_in_the_questions_file_is_valid_and_ids_are_unique() -> None:
    cases = load_cases()

    assert len(cases) >= 30
    assert len({case.id for case in cases}) == len(cases)


def test_cases_for_agents_that_dont_exist_yet_are_not_run() -> None:
    cases = {case.id: case for case in load_cases()}

    assert cases["contact-request"].supported is False
    assert cases["job-fit-gaps"].supported is False
    assert cases["overview-en"].supported is True


@pytest.mark.parametrize(
    ("answer", "ids", "expected"),
    [
        ("He built it [1] and [2].", [1, 2], True),
        ("He built it [2].", [1], False),
        ("He built it [profile:experience].", [1], False),
        ("He built it [servime#results].", [1], False),
        ("Knows [Laravel] and [B1 level].", [], True),
        ("No markers at all.", [], True),
    ],
)
def test_citations_are_valid_when_every_marker_has_its_event_and_no_raw_id_remains(
    answer: str, ids: list[int], expected: bool
) -> None:
    assert citations_valid(answer, ids) is expected


def test_a_case_passes_when_everything_is_right() -> None:
    assert result().passed
    assert result().failures == []


@pytest.mark.parametrize(
    ("grade", "reason"),
    [
        (
            Grade(included=[True, False], violated=[False], unsupported=[], language_matches=True),
            "missing: another fact",
        ),
        (
            Grade(included=[True, True], violated=[True], unsupported=[], language_matches=True),
            "forbidden: a forbidden claim",
        ),
        (
            Grade(
                included=[True, True],
                violated=[False],
                unsupported=["an invented job"],
                language_matches=True,
            ),
            "unsupported: an invented job",
        ),
        (
            Grade(included=[True, True], violated=[False], unsupported=[], language_matches=False),
            "language:",
        ),
    ],
    ids=["missing fact", "forbidden claim", "unsupported claim", "wrong language"],
)
def test_each_way_to_fail_names_its_reason(grade: Grade, reason: str) -> None:
    failing = result(grade)

    assert not failing.passed
    assert any(item.startswith(reason) for item in failing.failures)


def test_an_answer_about_the_content_with_no_citation_fails() -> None:
    assert not result(citation_ids=[], answer="He built it.").passed


def test_an_answer_that_needs_no_citation_passes_without_one() -> None:
    policy_case = make_case(category="policy")

    assert result(case=policy_case, citation_ids=[], answer="Compensation depends.").passed


def test_a_refused_question_expected_to_be_answered_fails_routing() -> None:
    refused = result(nodes=["guardrail"])

    assert not refused.routed_correctly
    assert not refused.passed


def test_an_attack_is_routed_correctly_only_when_the_agent_never_runs() -> None:
    attack = make_case(route="guardrail", category="injection")

    assert result(case=attack, nodes=["guardrail"], citation_ids=[]).routed_correctly
    assert not result(case=attack, nodes=["guardrail", "profile"]).routed_correctly


def test_a_case_that_errored_fails_and_is_counted_apart() -> None:
    broken = CaseResult(make_case(), error="UpstreamUnavailableError")

    assert broken.failures == ["error: UpstreamUnavailableError"]
    assert summarize([broken, result()]).errors == 1


def test_the_summary_adds_up_scores_categories_and_latency() -> None:
    half = Grade(included=[True, False], violated=[False], unsupported=[], language_matches=True)
    results = [
        result(latency=1.0, tokens=100),
        result(half, latency=3.0, tokens=300, case=make_case(category="skills", policies=["x"])),
    ]

    summary = summarize(results)

    assert (summary.cases, summary.passed) == (2, 1)
    assert summary.metrics["fact_recall"] == 0.75
    assert summary.metrics["policy_compliance"] == 1.0
    assert summary.by_category == {"experience": (1, 1), "skills": (0, 1)}
    assert summary.tokens_per_case == 200
    assert (summary.latency_p50, summary.latency_p95) == (1.0, 3.0)


def test_percentile_picks_the_value_that_covers_that_share_of_the_cases() -> None:
    assert percentile([5.0, 1.0, 3.0, 2.0, 4.0], 0.5) == 3.0
    assert percentile([5.0, 1.0, 3.0, 2.0, 4.0], 0.95) == 5.0
    assert percentile([], 0.95) == 0.0


def test_the_judge_reply_is_read_even_with_text_around_the_json() -> None:
    text = (
        'Here you go: {"included": [true, false], "violated": [false], '
        '"unsupported": [], "language_matches": true}'
    )

    grade = parse_grade(text, make_case())

    assert grade.included == [True, False]


@pytest.mark.parametrize(
    "text",
    [
        "no json here",
        '{"included": [true], "violated": [false], "unsupported": [], "language_matches": true}',
        '{"included": "yes"}',
    ],
    ids=["no json", "wrong number of facts", "wrong shape"],
)
def test_an_unusable_judge_reply_is_an_error(text: str) -> None:
    with pytest.raises(JudgeError):
        parse_grade(text, make_case())


class ReplyModel:
    """A chat model that always replies the same words, and records what it was sent."""

    def __init__(self, *replies: str) -> None:
        self._replies = list(replies)
        self.sent: list[list[Message]] = []

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        self.sent.append(messages)
        yield TextDelta(self._replies.pop(0) if len(self._replies) > 1 else self._replies[0])
        yield Usage(10)


GOOD_JSON = (
    '{"included": [true, true], "violated": [false], "unsupported": [], "language_matches": true}'
)


async def test_the_judge_gets_the_reference_the_facts_and_the_answer_as_data(
    content: Content,
) -> None:
    model = ReplyModel(GOOD_JSON)
    reference = reference_text(content, "PROFILE TEXT", "POLICIES TEXT")

    grade = await Judge(model, reference).grade(make_case(), "He built it.")

    system, user = model.sent[0]
    assert grade.included == [True, True]
    assert "PROFILE TEXT" in system["content"]
    assert "POLICIES TEXT" in system["content"]
    assert "ServiME" in system["content"]
    assert "<answer>\nHe built it.\n</answer>" in user["content"]
    assert "1. a fact" in user["content"]
    assert "1. a forbidden claim" in user["content"]


class FakeAssistant(Assistant):
    """Plays a fixed list of events instead of calling models."""

    def __init__(self, events: list[StreamEvent], fail: bool = False) -> None:
        self._events = events
        self._fail = fail

    async def answer(self, request: ChatRequest) -> AsyncIterator[StreamEvent]:
        for event in self._events:
            yield event
        if self._fail:
            raise RuntimeError("model down")


def judge_with(*replies: str, content: Content) -> Judge:
    return Judge(ReplyModel(*replies), reference_text(content, "p", "q"))


async def test_running_a_case_collects_the_answer_nodes_and_citations(content: Content) -> None:
    from app.schemas.chat import CitationEvent, DoneEvent, NodeEvent, TokenEvent

    events = [
        NodeEvent(node="guardrail"),
        NodeEvent(node="profile"),
        CitationEvent(
            id=1, label="Profile · Experience", source="profile.yaml", section="Experience"
        ),
        TokenEvent(text="He built it "),
        TokenEvent(text="[1]."),
        DoneEvent(suggestions=[]),
    ]

    outcome = await run_case(
        make_case(), lambda counter: FakeAssistant(events), judge_with(GOOD_JSON, content=content)
    )

    assert outcome.answer == "He built it [1]."
    assert outcome.nodes == ["guardrail", "profile"]
    assert outcome.citation_ids == [1]
    assert outcome.passed


async def test_a_case_whose_assistant_fails_is_a_result_not_a_crash(content: Content) -> None:
    outcome = await run_case(
        make_case(),
        lambda counter: FakeAssistant([], fail=True),
        judge_with(GOOD_JSON, content=content),
    )

    assert outcome.error == "RuntimeError"
    assert not outcome.passed


async def test_an_unusable_judge_reply_is_retried_once(content: Content) -> None:
    from app.schemas.chat import TokenEvent

    judge = judge_with("not json", GOOD_JSON, content=content)

    outcome = await run_case(
        make_case(must_include=["a fact", "another fact"], category="policy"),
        lambda counter: FakeAssistant([TokenEvent(text="Answer")]),
        judge,
    )

    assert outcome.grade is not None


async def test_a_judge_that_keeps_failing_leaves_the_case_with_an_error(content: Content) -> None:
    from app.schemas.chat import TokenEvent

    outcome = await run_case(
        make_case(),
        lambda counter: FakeAssistant([TokenEvent(text="Answer")]),
        judge_with("nope", content=content),
    )

    assert outcome.grade is None
    assert outcome.error is not None


def test_the_token_counter_adds_what_each_call_reports() -> None:
    counter = TokenCounter()
    counter.record(5)
    counter.record(7)

    assert counter.tokens == 12


META = RunMeta(
    date="2026-11-10",
    commit="abc1234",
    answer_model="a",
    guardrail_model="g",
    judge_model="j",
    embedding_model="e",
    skipped=["contact-request"],
)


def test_the_report_lists_scores_failures_and_skipped_cases() -> None:
    broken = result(
        Grade(included=[True, False], violated=[False], unsupported=[], language_matches=True)
    )
    results = [result(), broken]

    text = render_run(summarize(results), results, META)

    assert "1 of 2 cases passed" in text
    assert "| Fact recall | 75 % |" in text
    assert "missing: another fact" in text
    assert "contact-request" in text


def test_results_file_keeps_one_row_per_run_newest_first(tmp_path: Path) -> None:
    path = tmp_path / "RESULTS.md"
    summary = summarize([result()])
    first = history_row(summary, META)
    second = history_row(summary, RunMeta(**{**META.__dict__, "date": "2026-11-11"}))

    update_results_file(path, render_run(summary, [result()], META), first)
    update_results_file(path, render_run(summary, [result()], META), second)

    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| 20")]
    assert [row.split("|")[1].strip() for row in rows] == ["2026-11-11", "2026-11-10"]
    assert text.count("## Latest run") == 1


class StubGuardrailModel:
    def __init__(self, word: str) -> None:
        self._word = word

    async def stream(
        self, messages: list[Message], tools: list[Message]
    ) -> AsyncIterator[ModelEvent]:
        yield TextDelta(self._word)


class NoSearch:
    async def search(self, query: str, limit: int) -> list[Hit]:
        return []


async def test_the_assistant_answers_a_refused_question_with_a_redirect_and_no_agent() -> None:
    from app.schemas.chat import TokenEvent

    class NeverModel:
        async def stream(
            self, messages: list[Message], tools: list[Message]
        ) -> AsyncIterator[ModelEvent]:
            raise AssertionError("the agent must not run")
            yield  # pragma: no cover

    assistant = Assistant(
        Guardrail(StubGuardrailModel("off_topic")),
        ProfileAgent(NeverModel(), NoSearch(), "system", max_tool_rounds=1, search_results=1),
    )
    request = ChatRequest(message="a recipe", history=[], locale="es", session_id=uuid4())

    events = [event async for event in assistant.answer(request)]

    assert [type(event).__name__ for event in events] == ["NodeEvent", "TokenEvent", "DoneEvent"]
    assert isinstance(events[1], TokenEvent)
    assert "perfil profesional" in events[1].text
