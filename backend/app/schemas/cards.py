"""The cards an answer can carry, as docs/API.md defines them. Texts may hold [n] markers."""

from typing import ClassVar, Literal

from pydantic import BaseModel

CardType = Literal["project", "timeline", "skills", "job_fit", "contact_summary"]


class ProjectCard(BaseModel):
    type: ClassVar[CardType] = "project"

    name: str
    summary: str
    role: str
    period: str
    highlight: str
    stack: list[str]
    url: str | None
    # A project with its own colours in DESIGN.md; None uses the teal set
    brand: str | None


class TimelineItem(BaseModel):
    role: str
    company: str
    period: str
    initials: str


class TimelineCard(BaseModel):
    type: ClassVar[CardType] = "timeline"

    # Newest first
    items: list[TimelineItem]


class SkillsGroup(BaseModel):
    label: str
    items: list[str]


class SkillsCard(BaseModel):
    type: ClassVar[CardType] = "skills"

    groups: list[SkillsGroup]


class Requirement(BaseModel):
    requirement: str
    status: Literal["met", "partial", "missing"]
    evidence: str


class JobFitCard(BaseModel):
    type: ClassVar[CardType] = "job_fit"

    title: str
    # The site counts the totals, so the summary can't disagree with the rows
    requirements: list[Requirement]


class ContactSummaryCard(BaseModel):
    type: ClassVar[CardType] = "contact_summary"

    name: str
    company: str
    email: str
    message: str


Card = ProjectCard | TimelineCard | SkillsCard | JobFitCard | ContactSummaryCard
