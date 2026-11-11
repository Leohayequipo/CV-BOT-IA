"""Grades an answer against its case with a model and a written rubric (prompts/eval_judge.md).

Only what can't be checked mechanically goes to the judge: whether a fact is said by meaning,
whether a forbidden claim is made, and whether anything is stated that the content doesn't say.
"""

from pydantic import BaseModel, ValidationError, field_validator

from app.content.models import Content
from app.evals.cases import EvalCase
from app.llm.chat import ChatModel, TextDelta
from app.prompts import render_prompt


class JudgeError(Exception):
    """The judge's reply wasn't a usable grade."""


class Grade(BaseModel):
    included: list[bool] = []
    violated: list[bool] = []
    unsupported: list[str] = []
    language_matches: bool

    @field_validator("included", "violated", "unsupported", mode="before")
    @classmethod
    def _null_is_empty(cls, value: object) -> object:
        return [] if value is None else value


class Judge:
    def __init__(self, model: ChatModel, reference: str) -> None:
        self._model = model
        self._system = render_prompt("eval_judge", reference=reference)

    async def grade(self, case: EvalCase, answer: str) -> Grade:
        text = ""
        async for event in self._model.stream(self._messages(case, answer), []):
            if isinstance(event, TextDelta):
                text += event.text
        return parse_grade(text, case)

    def _messages(self, case: EvalCase, answer: str) -> list[dict[str, str]]:
        facts = "\n".join(f"{n}. {fact}" for n, fact in enumerate(case.must_include, 1))
        claims = "\n".join(f"{n}. {claim}" for n, claim in enumerate(case.must_not_include, 1))
        user = (
            f"<question>\n{case.question}\n</question>\n\n"
            f"<answer>\n{answer}\n</answer>\n\n"
            f"Facts the answer must contain:\n{facts or '(none)'}\n\n"
            f"Claims the answer must not make:\n{claims or '(none)'}"
        )
        return [{"role": "system", "content": self._system}, {"role": "user", "content": user}]


def parse_grade(text: str, case: EvalCase) -> Grade:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        msg = f"no JSON in the judge's reply: {text[:80]!r}"
        raise JudgeError(msg)
    try:
        grade = Grade.model_validate_json(text[start : end + 1])
    except ValidationError as error:
        msg = f"the judge's JSON doesn't fit: {error.error_count()} problems"
        raise JudgeError(msg) from error
    # A list the case leaves empty has nothing to grade, whatever the judge wrote there
    grade = grade.model_copy(
        update={
            "included": grade.included if case.must_include else [],
            "violated": grade.violated if case.must_not_include else [],
        }
    )
    if len(grade.included) != len(case.must_include) or len(grade.violated) != len(
        case.must_not_include
    ):
        msg = "the judge graded a different number of facts or claims than the case lists"
        raise JudgeError(msg)
    return grade


def reference_text(content: Content, rendered_profile: str, policies: str) -> str:
    """Everything the assistant may say: its profile, the case studies and its policies."""
    studies = "\n\n".join(
        f"## Case study: {study.title}\n"
        + "\n\n".join(f"### {name}\n{body}" for name, body in study.sections.items())
        for study in content.case_studies
    )
    return f"# Profile\n{rendered_profile}\n\n{studies}\n\n{policies}"
