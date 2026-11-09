"""Keep the stored chunks equal to the case studies, embedding only what changed.

Run it from backend/ with `uv run python -m app.rag.ingest`. It is idempotent, so CI can run it
on every change to content/.
"""

import sys
from dataclasses import dataclass

import psycopg

from app.config import Settings, get_settings
from app.content.loader import load_content
from app.content.models import Content
from app.llm.client import openai_client
from app.rag.chunking import chunk_case_study
from app.rag.embeddings import Embedder, OpenAIEmbedder
from app.rag.store import PostgresStore, Store


@dataclass(frozen=True)
class IngestReport:
    added: int
    updated: int
    removed: int
    unchanged: int

    def __str__(self) -> str:
        return (
            f"{self.added} added, {self.updated} updated, "
            f"{self.removed} removed, {self.unchanged} unchanged"
        )


def ingest(content: Content, embedder: Embedder, store: Store) -> IngestReport:
    chunks = [
        chunk for case_study in content.case_studies for chunk in chunk_case_study(case_study)
    ]
    hashes = {chunk.id: chunk.content_hash(embedder.model) for chunk in chunks}
    stored = store.hashes()

    stale = [chunk for chunk in chunks if stored.get(chunk.id) != hashes[chunk.id]]
    removed = sorted(set(stored) - set(hashes))

    if stale:
        embeddings = embedder.embed([chunk.text for chunk in stale])
        store.upsert(
            [
                (chunk, hashes[chunk.id], embedding)
                for chunk, embedding in zip(stale, embeddings, strict=True)
            ]
        )
    store.delete(removed)

    updated = sum(1 for chunk in stale if chunk.id in stored)
    return IngestReport(
        added=len(stale) - updated,
        updated=updated,
        removed=len(removed),
        unchanged=len(chunks) - len(stale),
    )


def main(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if settings.database_url is None or settings.openai_api_key is None:
        sys.exit("DATABASE_URL and OPENAI_API_KEY must be set (see backend/.env.example)")

    content = load_content(settings.content_dir)
    embedder = OpenAIEmbedder(openai_client(settings.openai_api_key), settings.embedding_model)
    # Leaving the block commits; an exception rolls everything back
    with psycopg.connect(settings.database_url.get_secret_value()) as connection:
        store = PostgresStore(connection)
        store.ensure_schema()
        report = ingest(content, embedder, store)
    sys.stdout.write(f"Ingestion done: {report}\n")


if __name__ == "__main__":
    main()
