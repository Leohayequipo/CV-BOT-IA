"""The whole assistant for one question: the guardrail, then the agent that answers.

The chat endpoint and the evals both run this, so what the evals score is what visitors get.
"""

from collections.abc import AsyncIterator

from app.agents.guardrail import Guardrail, redirect_events
from app.agents.profile_agent import ProfileAgent, build_system_prompt, read_policies
from app.config import Settings
from app.content.models import Content
from app.llm.chat import ChatModel, OpenAIChatModel
from app.llm.client import async_openai_client, openai_client
from app.llm.metered import MeteredModel, TokenSink
from app.llm.traced import TracedModel
from app.rag.embeddings import OpenAIEmbedder
from app.rag.search import PostgresDocumentSearch
from app.rag.traced import TracedSearch
from app.schemas.chat import ChatRequest, NodeEvent, StreamEvent


class Assistant:
    def __init__(self, guardrail: Guardrail, agent: ProfileAgent) -> None:
        self._guardrail = guardrail
        self._agent = agent

    async def answer(self, request: ChatRequest) -> AsyncIterator[StreamEvent]:
        yield NodeEvent(node="guardrail")
        verdict = await self._guardrail.check(request)
        if verdict == "on_topic":
            async for event in self._agent.answer(request):
                yield event
        else:
            for event in redirect_events(verdict, request.locale):
                yield event


def build_assistant(settings: Settings, content: Content, usage: TokenSink) -> Assistant:
    """The real assistant, from the settings. Tokens every model call uses go to `usage`."""
    if settings.openai_api_key is None or settings.database_url is None:
        msg = "OPENAI_API_KEY and DATABASE_URL must be set"
        raise RuntimeError(msg)
    client = async_openai_client(settings.openai_api_key)

    def model(name: str, model_id: str, max_tokens: int, reasoning: str) -> ChatModel:
        chat = OpenAIChatModel(client, model_id, max_tokens, reasoning)
        return MeteredModel(TracedModel(chat, name, model_id), usage)

    embedder = OpenAIEmbedder(openai_client(settings.openai_api_key), settings.embedding_model)
    guardrail = Guardrail(
        model(
            "guardrail",
            settings.guardrail_model,
            settings.guardrail_max_tokens,
            settings.guardrail_reasoning_effort,
        )
    )
    prompt = build_system_prompt(
        content.profile,
        read_policies(settings.content_dir),
        settings.contact_email,
        settings.contact_phone,
    )
    agent = ProfileAgent(
        model(
            "answer",
            settings.answer_model,
            settings.answer_max_tokens,
            settings.answer_reasoning_effort,
        ),
        TracedSearch(PostgresDocumentSearch(settings.database_url, embedder)),
        prompt,
        settings.max_tool_rounds,
        settings.search_results,
    )
    return Assistant(guardrail, agent)
