"""The first node: decides whether a message is for the assistant before any agent sees it.

Cheap rules catch the obvious attacks without a model call; a small model classifies the rest.
It only decides on topic, off topic or injection. Salary, start date and the other sensitive
questions are on topic: the profile agent answers them under content/policies.md. The visitor's
text and the history are untrusted, so both reach the model as delimited data (ADR-028).
"""

import re
from typing import Literal

from app.content.models import Locale
from app.llm.chat import ChatModel, TextDelta
from app.prompts import render_prompt
from app.schemas.chat import ChatRequest, DoneEvent, NodeEvent, StreamEvent, TokenEvent

Verdict = Literal["on_topic", "off_topic", "injection"]
Refused = Literal["off_topic", "injection"]
VERDICTS: tuple[Verdict, ...] = ("on_topic", "off_topic", "injection")

# The rules look only at short messages. A long one is usually a pasted job offer, which is data,
# and an instruction hidden inside it must not make the assistant refuse to analyse the offer.
RULES_MAX_CHARS = 600
# The model reads at most this much of a message, and of each turn of history
MODEL_MAX_CHARS = 4000
HISTORY_TURNS = 4
HISTORY_TURN_CHARS = 500

# Only phrasings that have no innocent use in a question about a candidate. The rest is the
# model's job.
INJECTION_PATTERNS = [
    re.compile(
        r"\bignor(e|ar|a|á)\b.{0,30}\b(previous|prior|above|earlier|anteriores|previas)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(reveal|show|print|repeat|leak|muestr\w*|mostr\w*|revel\w*|repet\w*|imprim\w*)\b.{0,25}"
        r"\b(system prompt|your instructions|tus instrucciones|prompt del sistema)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(developer|dan|jailbreak)\s+mode\b|\bmodo\s+(desarrollador|dios)\b", re.IGNORECASE
    ),
    re.compile(
        r"\bsystem\s+override\b|\bdisregard\b.{0,30}\b(rules|instructions)\b", re.IGNORECASE
    ),
]

REDIRECTS: dict[Refused, dict[Locale, str]] = {
    "off_topic": {
        "en": (
            "I can only help with questions about Leonardo's professional profile: his "
            "experience, projects, skills or how to work with him. What would you like to know?"
        ),
        "es": (
            "Solo puedo ayudarte con preguntas sobre el perfil profesional de Leonardo: su "
            "experiencia, sus proyectos, sus habilidades o cómo trabajar con él. "
            "¿Qué te gustaría saber?"
        ),
    },
    "injection": {
        "en": (
            "I can't change how I work, but I'm happy to answer questions about Leonardo's "
            "experience, projects and skills. For anything else, such as compensation or "
            "availability, he prefers to talk directly, and I can pass him a message."
        ),
        "es": (
            "No puedo cambiar cómo trabajo, pero con gusto respondo sobre la experiencia, los "
            "proyectos y las habilidades de Leonardo. Para lo demás, como remuneración o "
            "disponibilidad, él prefiere hablar directamente, y puedo pasarle un mensaje."
        ),
    },
}


def matches_injection_rules(message: str) -> bool:
    return len(message) <= RULES_MAX_CHARS and any(
        pattern.search(message) for pattern in INJECTION_PATTERNS
    )


class Guardrail:
    def __init__(self, model: ChatModel) -> None:
        self._model = model
        self._system = render_prompt("guardrail")

    async def check(self, request: ChatRequest) -> Verdict:
        if matches_injection_rules(request.message):
            return "injection"
        text = ""
        async for event in self._model.stream(self._messages(request), []):
            if isinstance(event, TextDelta):
                text += event.text
        return parse_verdict(text)

    def _messages(self, request: ChatRequest) -> list[dict[str, str]]:
        turns = "\n".join(
            f"{turn.role}: {turn.content[:HISTORY_TURN_CHARS]}"
            for turn in request.history[-HISTORY_TURNS:]
        )
        context = f"<history>\n{turns}\n</history>\n\n" if turns else ""
        message = request.message[:MODEL_MAX_CHARS]
        return [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"{context}<user_message>\n{message}\n</user_message>"},
        ]


def parse_verdict(text: str) -> Verdict:
    """The model's word as a verdict. Anything else counts as on topic.

    Failing open is deliberate: the profile agent keeps its own policies, so a garbled
    classification costs one answer within them, while failing closed would turn a model hiccup
    into a refusal of a legitimate recruiter.
    """
    word = text.strip().lower().strip(".")
    return next((verdict for verdict in VERDICTS if verdict == word), "on_topic")


def redirect_events(verdict: Refused, locale: Locale) -> list[StreamEvent]:
    """The stream for a message that is not answered: the node, the redirect and done."""
    return [
        NodeEvent(node="guardrail"),
        TokenEvent(text=REDIRECTS[verdict][locale]),
        DoneEvent(suggestions=[]),
    ]
