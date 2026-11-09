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


def other_chunk(name: str, content: str) -> Chunk:
    return Chunk(id=f"t#{name}", source_id="t", title="T", section=name, content=content)


def test_the_text_search_finds_an_exact_name_among_other_words(store: PostgresStore) -> None:
    store.upsert([(other_chunk("a", "zzqxname admin panel"), "h", VECTOR)])
    store.upsert([(other_chunk("b", "something unrelated"), "h", VECTOR)])

    found = store.search_text("Does he know zzqxname?", limit=5)

    # Other words of the question may match real chunks too; the vector search and the
    # fusion sort those out, so this only checks that the exact name is found
    assert "t#a" in [chunk.id for chunk in found]
    assert "t#b" not in [chunk.id for chunk in found]
    assert [chunk.id for chunk in store.search_text("zzqxname", limit=5)] == ["t#a"]


def test_the_text_search_returns_nothing_for_a_query_without_words(store: PostgresStore) -> None:
    assert store.search_text("?!", limit=5) == []


def test_the_vector_search_returns_the_nearest_chunk_first(store: PostgresStore) -> None:
    far = [0.0, 1.0] + [0.0] * (EMBEDDING_DIMENSIONS - 2)
    store.upsert([(other_chunk("near", "x"), "h", VECTOR), (other_chunk("far", "y"), "h", far)])

    found = store.search_vector(VECTOR, limit=1)

    assert found[0].id == "t#near"
    assert found[0].content == "x"


def test_a_chunk_is_stored_replaced_and_deleted(store: PostgresStore) -> None:
    store.upsert([(CHUNK, "hash-1", VECTOR)])
    store.upsert([(CHUNK, "hash-2", VECTOR)])

    assert store.hashes()["t#a"] == "hash-2"

    store.delete(["t#a"])

    assert "t#a" not in store.hashes()
