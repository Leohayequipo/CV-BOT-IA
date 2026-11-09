"""Runs against the real database when DATABASE_URL is set, and always rolls back."""

from collections.abc import Iterator

import psycopg
import pytest

from app.config import Settings
from app.rag.chunking import Chunk
from app.rag.store import EMBEDDING_DIMENSIONS, PostgresStore

pytestmark = pytest.mark.skipif(Settings().database_url is None, reason="needs DATABASE_URL")

VECTOR = [1.0] + [0.0] * (EMBEDDING_DIMENSIONS - 1)
CHUNK = Chunk(id="t#a", source_id="t", title="T", section="A", content="FilamentPHP admin panel")


@pytest.fixture
def store() -> Iterator[PostgresStore]:
    url = Settings().database_url
    assert url is not None
    with psycopg.connect(url.get_secret_value()) as connection:
        postgres_store = PostgresStore(connection)
        postgres_store.ensure_schema()
        yield postgres_store
        connection.rollback()  # the test leaves nothing behind


def test_a_chunk_is_stored_replaced_and_deleted(store: PostgresStore) -> None:
    store.upsert([(CHUNK, "hash-1", VECTOR)])
    store.upsert([(CHUNK, "hash-2", VECTOR)])

    assert store.hashes()["t#a"] == "hash-2"

    store.delete(["t#a"])

    assert "t#a" not in store.hashes()
