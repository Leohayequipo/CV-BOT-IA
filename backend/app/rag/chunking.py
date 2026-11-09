"""Split a case study into one chunk per section, each one understandable on its own."""

import hashlib
import re
from dataclasses import dataclass

from app.content.models import CaseStudy


@dataclass(frozen=True)
class Chunk:
    """A piece of a case study. `id` is stable, so re-ingesting updates it instead of copying it."""

    id: str
    source_id: str
    title: str
    section: str
    content: str

    @property
    def text(self) -> str:
        """What gets embedded: the title and the section name give the body its context."""
        return f"{self.title} - {self.section}\n\n{self.content}"

    def content_hash(self, model: str) -> str:
        """Changes when the text or the embedding model does, which is when a chunk is stale."""
        return hashlib.sha256(f"{model}\n{self.text}".encode()).hexdigest()


def chunk_case_study(case_study: CaseStudy) -> list[Chunk]:
    return [
        Chunk(
            id=f"{case_study.meta.id}#{_slug(section)}",
            source_id=case_study.meta.id,
            title=case_study.title,
            section=section,
            content=content,
        )
        for section, content in case_study.sections.items()
        if content  # optional sections left empty have nothing to retrieve
    ]


def _slug(section: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-")
