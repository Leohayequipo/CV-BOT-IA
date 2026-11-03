"""Scripted answers that follow docs/API.md, standing in for the agents until Phase 5 (ADR-022).

The site is built and tested against them. Every fact comes from content/, so even placeholder
answers are true. A question picks its script by keywords, and "mock: <name>" picks one by name,
including the cases a real model can't produce on demand: a slow answer, a very long one, a
failure partway through and the question limit.
"""

import asyncio
import dataclasses
import re
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass

from app.content.format import format_period, localize
from app.content.models import Content, Experience, Locale, Role
from app.core.errors import RateLimitedError, UpstreamUnavailableError
from app.schemas.chat import (
    ChatRequest,
    CitationEvent,
    DoneEvent,
    NodeEvent,
    NodeName,
    StreamEvent,
    TokenEvent,
)

LIMIT_RETRY_AFTER = 60
# Tokens the failing answer sends before it breaks
FAIL_AFTER_TOKENS = 12

_COMMAND = re.compile(r"^mock:\s*([a-z-]+)")
# A word and the spaces after it: close enough to how models stream
_TOKEN = re.compile(r"\S+\s*")
_MARKER = re.compile(r"\[(\d+)\]")
_ANSWER_PATH: tuple[NodeName, ...] = ("guardrail", "supervisor", "profile")


@dataclass(frozen=True)
class Pace:
    """Seconds to wait before each graph step and each token."""

    step: float = 0.4
    token: float = 0.03

    def slowed(self, factor: float) -> "Pace":
        return Pace(step=self.step * factor, token=self.token * factor)


@dataclass(frozen=True)
class Script:
    nodes: tuple[NodeName, ...]
    # Markdown, with a [n] marker after each claim
    text: str
    citations: tuple[CitationEvent, ...] = ()
    suggestions: tuple[str, ...] = ()
    slow: bool = False
    fails_after: int | None = None


DEFAULT_PACE = Pace()


class MockChat:
    def __init__(self, content: Content, pace: Pace = DEFAULT_PACE) -> None:
        self._content = content
        self._pace = pace

    def check_limit(self, question: ChatRequest) -> None:
        """Refuse the question before streaming, as the real limiter of step 5.5 will."""
        if _command(question.message) == "limit":
            raise RateLimitedError(retry_after=LIMIT_RETRY_AFTER)

    async def answer(self, question: ChatRequest) -> AsyncIterator[StreamEvent]:
        script = self._script_for(question)
        pace = self._pace.slowed(5) if script.slow else self._pace
        for node in script.nodes:
            await asyncio.sleep(pace.step)
            yield NodeEvent(node=node)
        unsent = {citation.id: citation for citation in script.citations}
        for count, token in enumerate(_TOKEN.findall(script.text)):
            if count == script.fails_after:
                raise UpstreamUnavailableError
            # The contract sends each citation before the first token that shows its marker
            for marker in _MARKER.findall(token):
                citation = unsent.pop(int(marker), None)
                if citation is not None:
                    yield citation
            await asyncio.sleep(pace.token)
            yield TokenEvent(text=token)
        yield DoneEvent(suggestions=list(script.suggestions))

    def _script_for(self, question: ChatRequest) -> Script:
        name = _command(question.message) or _topic(question.message) or "summary"
        build = _SCRIPTS.get(name, _summary)
        return build(self._content, question.locale)


def _command(message: str) -> str | None:
    match = _COMMAND.match(message.casefold())
    return match.group(1) if match else None


def _topic(message: str) -> str | None:
    text = message.casefold()
    return next(
        (name for name, keywords in _KEYWORDS.items() if any(word in text for word in keywords)),
        None,
    )


def _summary(content: Content, locale: Locale) -> Script:
    """The opening paragraph of his summary and his current roles, each one cited."""
    profile = content.profile
    current = [
        (entry, entry.roles[0]) for entry in profile.experience if entry.roles[0].end is None
    ]
    summary = CitationEvent(
        id=1,
        label={"en": "Profile · Summary", "es": "Perfil · Resumen"}[locale],
        source="profile.yaml",
        section="summary",
    )
    citations = (
        summary,
        *(
            _role_citation(number, entry, role, locale)
            for number, (entry, role) in enumerate(current, start=2)
        ),
    )
    roles = "\n".join(
        f"- **{localize(role.title, locale)}**, {entry.company} [{number}]"
        for number, (entry, role) in enumerate(current, start=2)
    )
    opening = localize(profile.summary, locale).split("\n")[0]
    heading = {"en": "His current roles:", "es": "Sus roles actuales:"}[locale]
    return Script(
        nodes=_ANSWER_PATH,
        text=f"{opening} [1]\n\n{heading}\n\n{roles}",
        citations=citations,
        suggestions=_NEXT_QUESTIONS[locale],
    )


def _long(content: Content, locale: Locale) -> Script:
    """Every role and every project, to test scrolling and long Markdown."""
    profile = content.profile
    intro = {
        "en": "Here is his whole career, as his CV lists it.",
        "es": "Este es su recorrido completo, tal como figura en su CV.",
    }[locale]
    blocks = [intro]
    citations: list[CitationEvent] = []
    for entry in profile.experience:
        for role in entry.roles:
            number = len(citations) + 1
            citations.append(_role_citation(number, entry, role, locale))
            period = format_period(role.start, role.end, locale)
            heading = f"**{localize(role.title, locale)}**, {entry.company} · {period} [{number}]"
            bullets = "\n".join(f"- {localize(item, locale)}" for item in role.highlights)
            blocks.append(f"{heading}\n\n{bullets}")
    for project in profile.projects.items:
        number = len(citations) + 1
        name = localize(project.name, locale)
        citations.append(
            CitationEvent(
                id=number, label=name, source="profile.yaml", section=f"projects.{project.id}"
            )
        )
        blocks.append(f"**{name}**: {localize(project.summary, locale)} [{number}]")
    return Script(
        nodes=_ANSWER_PATH,
        text="\n\n".join(blocks),
        citations=tuple(citations),
        suggestions=_NEXT_QUESTIONS[locale],
    )


def _salary(content: Content, locale: Locale) -> Script:
    """Policy 3 in content/policies.md, in the words of the approved design."""
    text = {
        "en": "Compensation depends on the role and its scope, and Leonardo prefers to discuss "
        "it directly with each company. If you like, I can help you leave him a message.",
        "es": "La remuneración depende del puesto y de su alcance, y Leonardo prefiere "
        "conversarla directamente con cada empresa. Si querés, te ayudo a dejarle un mensaje.",
    }[locale]
    return Script(nodes=_ANSWER_PATH, text=text, suggestions=_REDIRECT_ACTIONS[locale])


def _availability(content: Content, locale: Locale) -> Script:
    """Policy 4: no start date, only his work preference and an offer to ask him."""
    preference = localize(content.profile.basics.work_preference, locale)
    preference = preference[0].lower() + preference[1:]
    text = {
        "en": "Leonardo will confirm his availability directly. "
        f"He prefers to work {preference} [1]. If you like, I can help you leave him a message.",
        "es": "Leonardo te confirma su disponibilidad directamente. "
        f"Su preferencia: {preference} [1]. Si querés, te ayudo a dejarle un mensaje.",
    }[locale]
    citation = CitationEvent(
        id=1,
        label={"en": "Profile · Work preference", "es": "Perfil · Modalidad de trabajo"}[locale],
        source="profile.yaml",
        section="basics.work_preference",
    )
    return Script(
        nodes=_ANSWER_PATH,
        text=text,
        citations=(citation,),
        suggestions=_REDIRECT_ACTIONS[locale],
    )


def _off_topic(content: Content, locale: Locale) -> Script:
    """The guardrail's redirect, in the words of the approved design."""
    text = {
        "en": "I can only talk about Leonardo's experience. "
        "Would you like to hear about his AI projects?",
        "es": "Solo puedo hablar de la experiencia de Leonardo. "
        "¿Querés saber de sus proyectos con IA?",
    }[locale]
    suggestions = {
        "en": ("What AI experience does he have?", "See his projects"),
        "es": ("¿Qué experiencia tiene con IA?", "Ver sus proyectos"),
    }[locale]
    return Script(nodes=("guardrail",), text=text, suggestions=suggestions)


def _slow(content: Content, locale: Locale) -> Script:
    return dataclasses.replace(_summary(content, locale), slow=True)


def _fail(content: Content, locale: Locale) -> Script:
    return dataclasses.replace(_summary(content, locale), fails_after=FAIL_AFTER_TOKENS)


def _role_citation(number: int, entry: Experience, role: Role, locale: Locale) -> CitationEvent:
    return CitationEvent(
        id=number,
        label=f"{entry.company} · {localize(role.title, locale)}",
        source="profile.yaml",
        section=f"experience.{entry.id}",
    )


_NEXT_QUESTIONS: dict[Locale, tuple[str, ...]] = {
    "en": ("What is ServiME?", "Has he led teams?", "Can he work in the EU?"),
    "es": ("¿Qué es ServiME?", "¿Lideró equipos?", "¿Puede trabajar en la UE?"),
}
_REDIRECT_ACTIONS: dict[Locale, tuple[str, ...]] = {
    "en": ("Leave him a message", "Analyse a job offer"),
    "es": ("Dejarle un mensaje", "Analizar una oferta"),
}

_SCRIPTS: dict[str, Callable[[Content, Locale], Script]] = {
    "summary": _summary,
    "long": _long,
    "slow": _slow,
    "fail": _fail,
    "salary": _salary,
    "availability": _availability,
    "off-topic": _off_topic,
}
# Checked in this order; the first topic with a keyword in the question wins
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "salary": ("salary", "compensation", "salario", "sueldo", "cobrar", "remuneración"),
    "availability": (
        "availability",
        "start date",
        "notice period",
        "disponibilidad",
        "fecha de inicio",
        "empezar",
    ),
    "off-topic": ("my code", "recipe", "weather", "mi código", "receta", "clima"),
}
