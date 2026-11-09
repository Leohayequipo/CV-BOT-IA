from app.rag.chunking import Chunk
from app.rag.retrieval import CANDIDATES, RRF_K, Retriever, reciprocal_rank_fusion
from tests.rag.conftest import FakeEmbedder


def chunk(name: str) -> Chunk:
    return Chunk(id=f"demo#{name}", source_id="demo", title="Demo", section=name, content=name)


class FakeIndex:
    """Returns the rankings it was given and remembers how it was asked."""

    def __init__(self, text: list[Chunk], vector: list[Chunk]) -> None:
        self.text = text
        self.vector = vector
        self.calls: list[tuple[str, object, int]] = []

    def search_text(self, query: str, limit: int) -> list[Chunk]:
        self.calls.append(("text", query, limit))
        return self.text

    def search_vector(self, embedding: list[float], limit: int) -> list[Chunk]:
        self.calls.append(("vector", embedding[0], limit))
        return self.vector


def test_a_chunk_both_searches_return_beats_one_only_one_returns() -> None:
    a, b, c = chunk("a"), chunk("b"), chunk("c")

    hits = reciprocal_rank_fusion([[a, b], [c, b]])

    assert [hit.chunk.id for hit in hits] == ["demo#b", "demo#a", "demo#c"]


def test_the_score_is_the_sum_of_one_over_k_plus_rank() -> None:
    a = chunk("a")

    (hit,) = reciprocal_rank_fusion([[a], [chunk("x"), a]])[:1]

    assert hit.chunk == a
    assert hit.score == 1 / (RRF_K + 1) + 1 / (RRF_K + 2)


def test_ties_are_broken_by_id_so_the_order_never_changes() -> None:
    hits = reciprocal_rank_fusion([[chunk("b")], [chunk("a")]])

    assert [hit.chunk.id for hit in hits] == ["demo#a", "demo#b"]


def test_no_results_give_no_hits() -> None:
    assert reciprocal_rank_fusion([[], []]) == []


def test_the_retriever_runs_both_searches_with_the_query_and_its_embedding() -> None:
    index = FakeIndex(text=[chunk("a")], vector=[chunk("b")])
    embedder = FakeEmbedder()

    Retriever(index, embedder).search("FilamentPHP admin", limit=5)

    assert embedder.embedded == ["FilamentPHP admin"]
    assert index.calls == [
        ("text", "FilamentPHP admin", CANDIDATES),
        ("vector", float(len("FilamentPHP admin")), CANDIDATES),
    ]


def test_the_retriever_returns_at_most_the_limit() -> None:
    names = ["a", "b", "c", "d"]
    index = FakeIndex(text=[chunk(name) for name in names], vector=[])

    hits = Retriever(index, FakeEmbedder()).search("anything", limit=2)

    assert [hit.chunk.section for hit in hits] == ["a", "b"]
