"""Where the chunks live: a Store protocol and its Postgres implementation."""

from importlib import resources
from typing import Protocol

from psycopg import Connection

from app.rag.chunking import Chunk

# Must match vector(1536) in schema.sql; text-embedding-3-small returns this many numbers
EMBEDDING_DIMENSIONS = 1536

# A chunk, its content hash and its embedding
Row = tuple[Chunk, str, list[float]]


class Store(Protocol):
    def hashes(self) -> dict[str, str]:
        """The content hash of every stored chunk, by id."""
        ...

    def upsert(self, rows: list[Row]) -> None:
        """Insert or replace chunks."""
        ...

    def delete(self, ids: list[str]) -> None: ...


class PostgresStore:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def ensure_schema(self) -> None:
        self._connection.execute(
            resources.files("app.rag").joinpath("schema.sql").read_text(encoding="utf-8")
        )

    def hashes(self) -> dict[str, str]:
        rows = self._connection.execute("select id, content_hash from chunks").fetchall()
        return dict(rows)

    def upsert(self, rows: list[Row]) -> None:
        with self._connection.cursor() as cursor:
            cursor.executemany(
                """
                insert into chunks (id, source_id, title, section, content, content_hash, embedding)
                values (%s, %s, %s, %s, %s, %s, %s::vector)
                on conflict (id) do update set
                    source_id = excluded.source_id,
                    title = excluded.title,
                    section = excluded.section,
                    content = excluded.content,
                    content_hash = excluded.content_hash,
                    embedding = excluded.embedding,
                    updated_at = now()
                """,
                [
                    (
                        chunk.id,
                        chunk.source_id,
                        chunk.title,
                        chunk.section,
                        chunk.content,
                        content_hash,
                        _vector_literal(embedding),
                    )
                    for chunk, content_hash, embedding in rows
                ],
            )

    def delete(self, ids: list[str]) -> None:
        if ids:
            self._connection.execute("delete from chunks where id = any(%s)", (ids,))


def _vector_literal(embedding: list[float]) -> str:
    """pgvector reads '[0.1,0.2]', so no extra client library is needed."""
    return "[" + ",".join(str(value) for value in embedding) + "]"
