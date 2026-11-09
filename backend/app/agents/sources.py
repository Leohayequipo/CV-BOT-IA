"""What the assistant can cite: the sections of the profile and the chunks it retrieved."""

from dataclasses import dataclass

from app.rag.chunking import Chunk


@dataclass(frozen=True)
class Source:
    id: str  # what the model writes between brackets: [profile:experience], [servime#results]
    label: str  # what the sources row shows
    source: str  # the file the fact comes from
    section: str


PROFILE_SECTIONS = {
    "basics": "Basics",
    "summary": "Summary",
    "skills": "Skills",
    "experience": "Experience",
    "projects": "Other projects",
    "education": "Education",
    "languages": "Languages",
}


def profile_sources() -> dict[str, Source]:
    return {
        f"profile:{key}": Source(
            id=f"profile:{key}",
            label=f"Profile · {name}",
            source="profile.yaml",
            section=name,
        )
        for key, name in PROFILE_SECTIONS.items()
    }


def chunk_source(chunk: Chunk) -> Source:
    return Source(
        id=chunk.id,
        label=f"{chunk.title} · {chunk.section}",
        source=f"case-studies/{chunk.source_id}.md",
        section=chunk.section,
    )
