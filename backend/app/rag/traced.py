"""A document search that records each query and what it found in the request's trace."""

from app.agents.profile_agent import DocumentSearch
from app.observability.tracing import current_trace
from app.rag.retrieval import Hit


class TracedSearch:
    def __init__(self, search: DocumentSearch) -> None:
        self._search = search

    async def search(self, query: str, limit: int) -> list[Hit]:
        trace = current_trace.get()
        observation = trace.retrieval(query) if trace else None
        try:
            hits = await self._search.search(query, limit)
        except BaseException as error:
            if observation:
                observation.end(error=type(error).__name__)
            raise
        if observation:
            observation.end(output=[{"id": hit.chunk.id, "score": hit.score} for hit in hits])
        return hits
