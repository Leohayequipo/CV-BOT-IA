"""The database search the agent uses: one short connection per search, off the event loop."""

import asyncio

import psycopg
from pydantic import SecretStr

from app.rag.embeddings import Embedder
from app.rag.retrieval import Hit, Retriever
from app.rag.store import PostgresStore


class PostgresDocumentSearch:
    def __init__(self, database_url: SecretStr, embedder: Embedder) -> None:
        self._database_url = database_url
        self._embedder = embedder

    async def search(self, query: str, limit: int) -> list[Hit]:
        # psycopg and the embeddings client here are blocking, so they run in a worker thread
        return await asyncio.to_thread(self._search, query, limit)

    def _search(self, query: str, limit: int) -> list[Hit]:
        with psycopg.connect(self._database_url.get_secret_value()) as connection:
            return Retriever(PostgresStore(connection), self._embedder).search(query, limit)
