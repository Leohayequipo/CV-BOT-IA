"""Where the chunks live: a Store protocol and its Postgres implementation."""

import re
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

    def search_text(self, query: str, limit: int) -> list[Chunk]:
        words = _WORD.findall(query)
        if not words:
            return []
        # A question has many words and a chunk rarely holds them all, so any word may match.
        # websearch_to_tsquery reads "or" as an operator and drops stop words like "the".
        rows = self._connection.execute(
            """
            select id, source_id, title, section, content from chunks,
                websearch_to_tsquery('english', %s) as query
            where fts @@ query
            order by ts_rank_cd(fts, query) desc, id
            limit %s
            """,
            (" or ".join(words), limit),
        ).fetchall()
        return [Chunk(*row) for row in rows]

    def search_vector(self, embedding: list[float], limit: int) -> list[Chunk]:
        rows = self._connection.execute(
            """
            select id, source_id, title, section, content from chunks
            order by embedding <=> %s::vector, id limit %s
            """,
            (_vector_literal(embedding), limit),
        ).fetchall()
        return [Chunk(*row) for row in rows]


_WORD = re.compile(r"\w+")


def _vector_literal(embedding: list[float]) -> str:
    """pgvector reads '[0.1,0.2]', so no extra client library is needed."""
    return "[" + ",".join(str(value) for value in embedding) + "]"
