from collections.abc import Callable

import pytest

from app.content.models import CaseStudy, Content
from app.rag.chunking import Chunk
from app.rag.store import EMBEDDING_DIMENSIONS, Row

SECTIONS = {
    "Summary": "What Demo is.",
    "Context and problem": "Why Demo was needed.",
    "Leonardo's role": "What Leonardo built.",
    "Architecture": "How Demo works.",
    "Key decisions and trade-offs": "What was chosen, and why.",
    "Results": "What Demo achieved.",
}


@pytest.fixture
def make_case_study() -> Callable[..., CaseStudy]:
    def make(case_id: str = "demo", **changes: str) -> CaseStudy:
        return CaseStudy.model_validate(
            {
                "meta": {
                    "id": case_id,
                    "title": "Demo",
                    "related": ["servime"],
                    "period": "2026",
                    "role": "Lead developer",
                    "stack": ["Python"],
                    "lang": "en",
                },
                "title": "Demo",
                "sections": {**SECTIONS, **changes},
            }
        )

    return make


@pytest.fixture
def make_content(
    content: Content, make_case_study: Callable[..., CaseStudy]
) -> Callable[..., Content]:
    def make(*case_studies: CaseStudy) -> Content:
        return Content(
            profile=content.profile,
            case_studies=case_studies or (make_case_study(),),
        )

    return make


class FakeEmbedder:
    """Returns a vector per text and remembers what it was asked to embed."""

    def __init__(self, model: str = "fake-model") -> None:
        self.model = model
        self.embedded: list[str] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.embedded.extend(texts)
        return [[float(len(text))] + [0.0] * (EMBEDDING_DIMENSIONS - 1) for text in texts]


class InMemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, Row] = {}

    def hashes(self) -> dict[str, str]:
        return {chunk_id: row[1] for chunk_id, row in self.rows.items()}

    def upsert(self, rows: list[Row]) -> None:
        for row in rows:
            self.rows[row[0].id] = row

    def delete(self, ids: list[str]) -> None:
        for chunk_id in ids:
            del self.rows[chunk_id]

    def chunk(self, chunk_id: str) -> Chunk:
        return self.rows[chunk_id][0]
