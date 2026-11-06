"""Scripted answers that follow docs/API.md, standing in for the agents until Phase 5 (ADR-022).

The site is built and tested against them. A question picks its script by keywords, and
"mock: <name>" picks one by name, including the cases a real model can't produce on demand: a slow
answer, a very long one, a failure partway through and the question limit.

Every fact comes from content/, so even placeholder answers are true. The two exceptions are
samples from the approved designs: the job-fit report for a fictional offer, since matching an
offer needs a model, and the contact summary of a fictional recruiter.
"""

import asyncio
import dataclasses
import re
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass

from app.content.cards import project_card, skills_card, timeline_card
from app.content.format import format_date, format_period, localize
from app.content.models import Content, Experience, Locale, Role
from app.core.errors import RateLimitedError, UpstreamUnavailableError
from app.schemas.cards import ContactSummaryCard, JobFitCard, Requirement
from app.schemas.chat import (
    CardEvent,
    ChatRequest,
    CitationEvent,
    DoneEvent,
    NodeEvent,
    NodeName,
    StreamEvent,
    TokenEvent,
)
from app.schemas.contact import ContactRequest

LIMIT_RETRY_AFTER = 60
# Tokens the failing answer sends before it breaks
FAIL_AFTER_TOKENS = 12
# A message this long is a pasted job offer, whatever words it uses
JOB_OFFER_MIN_CHARS = 400

_COMMAND = re.compile(r"^mock:\s*([a-z-]+)")
# A word and the spaces after it: close enough to how models stream
_TOKEN = re.compile(r"\S+\s*")
_MARKER = re.compile(r"\[(\d+)\]")
_ANSWER_PATH: tuple[NodeName, ...] = ("guardrail", "supervisor", "profile")
_JOB_FIT_PATH: tuple[NodeName, ...] = ("guardrail", "supervisor", "job_fit")


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
    cards: tuple[CardEvent, ...] = ()
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
        for card in script.cards:
            await asyncio.sleep(pace.step)
            yield card
        yield DoneEvent(suggestions=list(script.suggestions))

    def _script_for(self, question: ChatRequest) -> Script:
        name = _command(question.message) or _topic(question.message) or "summary"
        build = _SCRIPTS.get(name, _summary)
        return build(self._content, question.locale)


class MockMailer:
    """Accepts confirmed messages without sending them, until step 6.3 adds the email provider."""

    async def send(self, contact: ContactRequest) -> None:
        command = _command(contact.message)
        if command == "fail":
            raise UpstreamUnavailableError
        if command == "limit":
            raise RateLimitedError(retry_after=LIMIT_RETRY_AFTER)


def _command(message: str) -> str | None:
    match = _COMMAND.match(message.casefold())
    return match.group(1) if match else None


def _topic(message: str) -> str | None:
    if len(message) >= JOB_OFFER_MIN_CHARS:
        return "job-fit"
    text = message.casefold()
    return next(
        (
            name
            for name, keywords in _KEYWORDS.items()
            # Keywords match at the start of a word: "project" finds "projects", not "subproject"
            if any(re.search(rf"(?<!\w){re.escape(word)}", text) for word in keywords)
        ),
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


def _project(content: Content, locale: Locale) -> Script:
    """ServiME, the project the approved design shows."""
    entry = _experience(content, "servime")
    role = entry.roles[0]
    # ServiME's last highlight is its result in production
    result = role.highlights[-1]
    description = localize(entry.description, locale) if entry.description else ""
    title = localize(role.title, locale).lower()
    since = format_date(role.start, locale)
    outcome = localize(result, locale).rstrip(".")
    text = {
        "en": f"{entry.company}: {description}. Leonardo has been its {title} since {since} [1]. "
        f"{outcome} [1].",
        "es": f"{entry.company}: {description}. Leonardo es su {title} desde {since} [1]. "
        f"{outcome} [1].",
    }[locale]
    suggestions = {
        "en": ("What AI experience does he have?", "Has he led teams?", "Analyse a job offer"),
        "es": ("¿Qué experiencia tiene con IA?", "¿Lideró equipos?", "Analizar una oferta"),
    }[locale]
    return Script(
        nodes=_ANSWER_PATH,
        text=text,
        citations=(_role_citation(1, entry, role, locale),),
        cards=(CardEvent.of(project_card(entry, result, locale)),),
        suggestions=suggestions,
    )


def _timeline(content: Content, locale: Locale) -> Script:
    """Every role; policy 6 answers the concurrent ones briefly."""
    text = {
        "en": "Here is his career, from the most recent role to the oldest. Today he holds "
        "several ongoing roles, which he meets on different schedules [1].",
        "es": "Este es su recorrido, del puesto más reciente al más antiguo. Hoy combina varios "
        "roles en curso, que cumple en distintos horarios [1].",
    }[locale]
    citation = CitationEvent(
        id=1,
        label={"en": "Profile · Experience", "es": "Perfil · Experiencia"}[locale],
        source="profile.yaml",
        section="experience",
    )
    suggestions = {
        "en": ("See his projects", "What's his stack?"),
        "es": ("Ver sus proyectos", "¿Cuál es su stack?"),
    }[locale]
    return Script(
        nodes=_ANSWER_PATH,
        text=text,
        citations=(citation,),
        cards=(CardEvent.of(timeline_card(content.profile, locale)),),
        suggestions=suggestions,
    )


def _skills(content: Content, locale: Locale) -> Script:
    text = {
        "en": "His main stack, as his CV lists it [1]:",
        "es": "Su stack principal, tal como figura en su CV [1]:",
    }[locale]
    citation = CitationEvent(
        id=1,
        label={"en": "Profile · Skills", "es": "Perfil · Skills"}[locale],
        source="profile.yaml",
        section="skills",
    )
    suggestions = {
        "en": ("What AI experience does he have?", "See his projects"),
        "es": ("¿Qué experiencia tiene con IA?", "Ver sus proyectos"),
    }[locale]
    return Script(
        nodes=_ANSWER_PATH,
        text=text,
        citations=(citation,),
        cards=(CardEvent.of(skills_card(content.profile, _MAIN_STACK, locale)),),
        suggestions=suggestions,
    )


def _job_offer(content: Content, locale: Locale) -> Script:
    """Asks for the offer, as the approved design does before the report."""
    text = {
        "en": "Paste the job description in the box below. I'll put together a report with the "
        "requirements he meets, the evidence from his CV for each one and what he's missing, "
        "without exaggerating.",
        "es": "Pegá la descripción del puesto en el cuadro de abajo. Te armo un informe con los "
        "requisitos que cumple, la evidencia de su CV para cada uno y lo que le falta, sin "
        "exagerar.",
    }[locale]
    return Script(nodes=_JOB_FIT_PATH, text=text)


def _job_fit(content: Content, locale: Locale) -> Script:
    """The approved design's report on a fictional offer, whatever offer was pasted."""
    utn = _experience(content, "utn")
    servime = _experience(content, "servime")
    profile = CitationEvent(
        id=3,
        label={
            "en": "Profile · Summary, languages and citizenship",
            "es": "Perfil · Resumen, idiomas y ciudadanía",
        }[locale],
        source="profile.yaml",
        section="summary",
    )
    text = {
        "en": "I compared the offer with his CV. He meets 5 of the 7 requirements, and one more "
        "in part; there is no evidence of AWS [1] [2] [3]. Here are the details:",
        "es": "Comparé la oferta con su CV. Cumple 5 de los 7 requisitos y uno en parte; de AWS "
        "no hay evidencia [1] [2] [3]. Este es el detalle:",
    }[locale]
    return Script(
        nodes=_JOB_FIT_PATH,
        text=text,
        citations=(
            _role_citation(1, utn, utn.roles[0], locale),
            _role_citation(2, servime, servime.roles[0], locale),
            profile,
        ),
        cards=(CardEvent.of(_SAMPLE_FIT[locale]),),
        suggestions=_REDIRECT_ACTIONS[locale][:1],
    )


def _contact(content: Content, locale: Locale) -> Script:
    """The summary to confirm; the real contact agent (step 6.3) collects it step by step."""
    text = {
        "en": "Here is the summary. Check it and, if everything is right, I'll send it.",
        "es": "Este es el resumen. Revisalo y, si está todo bien, se lo envío.",
    }[locale]
    return Script(
        nodes=("guardrail", "supervisor", "contact"),
        text=text,
        cards=(CardEvent.of(_SAMPLE_CONTACT[locale]),),
    )


def _experience(content: Content, entry_id: str) -> Experience:
    return next(entry for entry in content.profile.experience if entry.id == entry_id)


def _role_citation(number: int, entry: Experience, role: Role, locale: Locale) -> CitationEvent:
    return CitationEvent(
        id=number,
        label=f"{entry.display_name} · {localize(role.title, locale)}",
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

# The skill groups DESIGN.md puts on the skills card
_MAIN_STACK = ("ai", "backend", "frontend", "data")

_SAMPLE_FIT: dict[Locale, JobFitCard] = {
    "en": JobFitCard(
        title="AI Engineer · remote in the EU",
        requirements=[
            Requirement(
                requirement="Python and FastAPI",
                status="met",
                evidence="Python backend with FastAPI at UTN [1]",
            ),
            Requirement(
                requirement="RAG and agents with LangGraph",
                status="met",
                evidence="RAG document assistant and an AI agent with tool use [1]",
            ),
            Requirement(
                requirement="LLMs in production",
                status="met",
                evidence="Chat with OpenAI and Gemini at ServiME, in production [2]",
            ),
            Requirement(
                requirement="5+ years of experience",
                status="met",
                evidence="10+ years as a developer [3]",
            ),
            Requirement(
                requirement="EU work permit",
                status="met",
                evidence="Italian citizen, no visa needed [3]",
            ),
            Requirement(
                requirement="English C1",
                status="partial",
                evidence="B1, with daily conversation practice [3]",
            ),
            Requirement(requirement="AWS", status="missing", evidence="Not in his CV"),
        ],
    ),
    "es": JobFitCard(
        title="AI Engineer · remoto en la UE",
        requirements=[
            Requirement(
                requirement="Python y FastAPI",
                status="met",
                evidence="Backend en Python con FastAPI en la UTN [1]",
            ),
            Requirement(
                requirement="RAG y agentes con LangGraph",
                status="met",
                evidence="Asistente de documentos con RAG y agente con herramientas [1]",
            ),
            Requirement(
                requirement="LLMs en producción",
                status="met",
                evidence="Chat con OpenAI y Gemini en ServiME, ya en producción [2]",
            ),
            Requirement(
                requirement="5 años o más de experiencia",
                status="met",
                evidence="Más de 10 años como desarrollador [3]",
            ),
            Requirement(
                requirement="Permiso de trabajo en la UE",
                status="met",
                evidence="Ciudadanía italiana, sin necesidad de visado [3]",
            ),
            Requirement(
                requirement="Inglés C1",
                status="partial",
                evidence="Tiene B1, con práctica diaria de conversación [3]",
            ),
            Requirement(requirement="AWS", status="missing", evidence="No figura en su CV"),
        ],
    ),
}
# A fictional recruiter, as in the approved design
_SAMPLE_CONTACT: dict[Locale, ContactSummaryCard] = {
    "en": ContactSummaryCard(
        name="Laura Gómez",
        company="Example Ltd",
        email="laura.gomez@example.com",
        message="I'd like to arrange an interview for an AI Engineer role next week.",
    ),
    "es": ContactSummaryCard(
        name="Laura Gómez",
        company="Empresa de Ejemplo",
        email="laura.gomez@example.com",
        message="Me gustaría coordinar una entrevista para un puesto de AI Engineer la semana "
        "que viene.",
    ),
}

_SCRIPTS: dict[str, Callable[[Content, Locale], Script]] = {
    "summary": _summary,
    "long": _long,
    "slow": _slow,
    "fail": _fail,
    "salary": _salary,
    "availability": _availability,
    "off-topic": _off_topic,
    "job-offer": _job_offer,
    "job-fit": _job_fit,
    "contact": _contact,
    "project": _project,
    "timeline": _timeline,
    "skills": _skills,
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
    "job-offer": ("job offer", "oferta"),
    "contact": ("contact", "message", "interview", "contactar", "mensaje", "entrevista"),
    "project": ("servime", "project", "proyecto"),
    "timeline": (
        "his experience",
        "career",
        "led",
        "teams",
        "su experiencia",
        "trayectoria",
        "lideró",
        "equipos",
    ),
    "skills": ("stack", "skills", "technolog", "tecnolog", "habilidades"),
}
