"""Schema of the files in content/.

Every model forbids unknown keys, so a typo in a YAML key fails validation instead of being
silently ignored, and every text a visitor can read must exist in English and Spanish.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

_PARTIAL_DATE = r"\d{4}(?:-(?:0[1-9]|1[0-2]))?"

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
# "YYYY-MM", or "YYYY" when the month isn't known.
PartialDate = Annotated[str, StringConstraints(pattern=rf"^{_PARTIAL_DATE}$")]
Year = Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
# A partial date, or a range of two joined by "/".
Period = Annotated[str, StringConstraints(pattern=rf"^{_PARTIAL_DATE}(?:/{_PARTIAL_DATE})?$")]
# An image in content/assets/; the pattern also keeps paths from leaving that folder.
AssetPath = Annotated[str, StringConstraints(pattern=r"^assets/[a-z0-9-]+\.(?:jpg|png|webp|avif)$")]
WorkMode = Literal["remote", "hybrid", "onsite"]

REQUIRED_SECTIONS = (
    "Summary",
    "Context and problem",
    "Leonardo's role",
    "Architecture",
    "Key decisions and trade-offs",
    "Results",
)


class ContentModel(BaseModel):
    """Base for content models: immutable, and unknown keys are errors."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Localized(ContentModel):
    """A text visitors can read, in English and Spanish."""

    en: Text
    es: Text


class Links(ContentModel):
    linkedin: HttpUrl
    github: HttpUrl


class Photo(ContentModel):
    path: AssetPath
    alt: Localized


class Basics(ContentModel):
    name: Text
    photo: Photo
    headline: Localized
    focus: Localized
    location: Localized
    citizenship: Localized
    work_authorization: Localized
    work_preference: Localized
    links: Links


class SkillGroup(ContentModel):
    id: Slug
    label: Localized
    # A plain string when the item reads the same in both languages.
    items: list[Text | Localized] = Field(min_length=1)


class Role(ContentModel):
    title: Localized
    start: PartialDate
    end: PartialDate | None  # None means the role is current; the key is still required
    work_mode: WorkMode | None = None
    stack: list[Text] = Field(default_factory=list)
    highlights: list[Localized] = Field(min_length=1)

    @model_validator(mode="after")
    def _ends_after_it_starts(self) -> Role:
        if self.end is not None and _is_before(self.end, self.start):
            msg = f"the role ends ({self.end}) before it starts ({self.start})"
            raise ValueError(msg)
        return self


class Experience(ContentModel):
    id: Slug
    company: Text
    formerly: Text | None = None
    description: Localized | None = None
    url: HttpUrl | None = None
    location: Localized | None = None
    roles: list[Role] = Field(min_length=1)

    @model_validator(mode="after")
    def _roles_are_most_recent_first(self) -> Experience:
        starts = [role.start for role in self.roles]
        if starts != sorted(starts, reverse=True):
            msg = "roles must be listed most recent first"
            raise ValueError(msg)
        return self


class Project(ContentModel):
    id: Slug
    name: Localized
    summary: Localized
    stack: list[Text] = Field(min_length=1)
    freelance: bool = False


class Projects(ContentModel):
    note: Localized
    items: list[Project] = Field(min_length=1)


class Education(ContentModel):
    degree: Localized
    institution: Text
    year: Year
    note: Localized | None = None


class Language(ContentModel):
    name: Localized
    level: Localized


class Profile(ContentModel):
    """content/profile.yaml: what the profile card, the chat cards and the assistant read."""

    basics: Basics
    summary: Localized
    skills: list[SkillGroup] = Field(min_length=1)
    experience: list[Experience] = Field(min_length=1)
    projects: Projects
    education: list[Education] = Field(min_length=1)
    languages: list[Language] = Field(min_length=1)

    @property
    def entry_ids(self) -> set[str]:
        """Ids a case study can relate to: every experience and every project."""
        return {entry.id for entry in self.experience} | {item.id for item in self.projects.items}

    @model_validator(mode="after")
    def _ids_are_unique(self) -> Profile:
        _require_unique("skill group", [group.id for group in self.skills])
        _require_unique(
            "experience or project",
            [entry.id for entry in self.experience] + [item.id for item in self.projects.items],
        )
        return self


class CaseStudyMeta(ContentModel):
    """Front matter of a case study, used for retrieval and citations."""

    id: Slug
    title: Text
    related: list[Slug] = Field(min_length=1)
    period: Period
    role: Text
    stack: list[Text] = Field(min_length=1)
    lang: Literal["en"]


class CaseStudy(ContentModel):
    """A file in content/case-studies/: front matter, an H1 title and one entry per H2 section."""

    meta: CaseStudyMeta
    title: Text
    sections: dict[str, str]

    @model_validator(mode="after")
    def _is_complete(self) -> CaseStudy:
        if self.title != self.meta.title:
            msg = f"the H1 title '{self.title}' differs from the front matter '{self.meta.title}'"
            raise ValueError(msg)
        missing = [name for name in REQUIRED_SECTIONS if not self.sections.get(name)]
        if missing:
            msg = f"missing or empty sections: {', '.join(missing)}"
            raise ValueError(msg)
        return self


class Content(ContentModel):
    """Everything in content/, with the references between files checked."""

    profile: Profile
    case_studies: tuple[CaseStudy, ...]

    @model_validator(mode="after")
    def _references_resolve(self) -> Content:
        _require_unique("case study", [case_study.meta.id for case_study in self.case_studies])
        known = self.profile.entry_ids
        for case_study in self.case_studies:
            unknown = sorted(set(case_study.meta.related) - known)
            if unknown:
                msg = (
                    f"case study '{case_study.meta.id}' relates to ids that aren't in the "
                    f"profile: {', '.join(unknown)}"
                )
                raise ValueError(msg)
        return self


def _is_before(date: str, other: str) -> bool:
    """Compare partial dates, using months only when both dates have one."""
    length = min(len(date), len(other))
    return date[:length] < other[:length]


def _require_unique(kind: str, ids: list[str]) -> None:
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        msg = f"duplicate {kind} ids: {', '.join(duplicates)}"
        raise ValueError(msg)
