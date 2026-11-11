from app.agents.profile_context import render_profile
from app.content.models import Content
from app.evals.cases import EvalCase
from app.evals.judge import parse_grade


def case(must_include: list[str], must_not_include: list[str]) -> EvalCase:
    return EvalCase(
        id="c",
        lang="en",
        category="policy",
        route="profile",
        question="q",
        must_include=must_include,
        must_not_include=must_not_include,
    )


def test_a_null_list_from_the_judge_counts_as_empty() -> None:
    text = '{"included": [true], "violated": null, "unsupported": null, "language_matches": true}'

    grade = parse_grade(text, case(["a fact"], []))

    assert (grade.included, grade.violated, grade.unsupported) == ([True], [], [])


def test_what_the_judge_writes_for_a_list_the_case_leaves_empty_is_ignored() -> None:
    text = '{"included": [true], "violated": [false], "unsupported": [], "language_matches": true}'

    grade = parse_grade(text, case([], []))

    assert (grade.included, grade.violated) == ([], [])


def test_the_assistant_can_give_the_link_to_a_company_site(content: Content) -> None:
    text = render_profile(content.profile)

    assert "ServiME (site: https://servime.net/)" in text
