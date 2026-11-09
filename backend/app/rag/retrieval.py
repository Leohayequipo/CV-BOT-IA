"""Hybrid search: keywords and meaning, merged with reciprocal rank fusion (ADR-008)."""

from dataclasses import dataclass
from typing import Protocol

from app.rag.chunking import Chunk
from app.rag.embeddings import Embedder

# How many candidates each search contributes before they are merged
CANDIDATES = 20
# Cormack's constant for reciprocal rank fusion: it keeps one list's top spot from dominating
RRF_K = 60


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class SearchIndex(Protocol):
    def search_text(self, query: str, limit: int) -> list[Chunk]:
        """Chunks that contain any of the query's words, best match first."""
        ...

    def search_vector(self, embedding: list[float], limit: int) -> list[Chunk]:
        """The chunks closest in meaning to the embedding, nearest first."""
        ...


def reciprocal_rank_fusion(rankings: list[list[Chunk]]) -> list[Hit]:
    """Merge ranked lists: a chunk scores 1 / (RRF_K + rank) in each list it appears in.

    Only ranks count, never the lists' own scores, because a keyword score and a vector
    distance are not comparable. A chunk both lists like beats one that only one does.
    """
    scores: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for ranking in rankings:
        for rank, chunk in enumerate(ranking, start=1):
            chunks[chunk.id] = chunk
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1 / (RRF_K + rank)
    ordered = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return [Hit(chunks[chunk_id], scores[chunk_id]) for chunk_id in ordered]


class Retriever:
    def __init__(self, index: SearchIndex, embedder: Embedder) -> None:
        self._index = index
        self._embedder = embedder

    def search(self, query: str, limit: int = 5) -> list[Hit]:
        """The `limit` chunks that best answer the query, from both searches merged."""
        (embedding,) = self._embedder.embed([query])
        rankings = [
            self._index.search_text(query, CANDIDATES),
            self._index.search_vector(embedding, CANDIDATES),
        ]
        return reciprocal_rank_fusion(rankings)[:limit]
