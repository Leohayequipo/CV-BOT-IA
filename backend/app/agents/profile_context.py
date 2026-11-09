"""The profile as text for the system prompt, one tagged block per citable section.

It reads English because the prompt does; the assistant answers in the visitor's language.
The text depends only on content/, so it is identical on every request and OpenAI caches it.
"""

from app.content.format import format_period, localize
from app.content.models import Experience, Profile, Role


def render_profile(
    profile: Profile, contact_email: str | None = None, contact_phone: str | None = None
) -> str:
    basics = profile.basics
    blocks = {
        "basics": [
            f"Name: {basics.name}",
            f"Headline: {localize(basics.headline, 'en')}",
            f"Focus: {localize(basics.focus, 'en')}",
            f"Location: {localize(basics.location, 'en')}",
            f"Citizenship: {localize(basics.citizenship, 'en')}",
            f"Work authorization: {localize(basics.work_authorization, 'en')}",
            f"Work preference: {localize(basics.work_preference, 'en')}",
            f"LinkedIn: {basics.links.linkedin}",
            f"GitHub: {basics.links.github}",
        ],
        "summary": [localize(profile.summary, "en")],
        "skills": [
            f"{localize(group.label, 'en')}: "
            + ", ".join(localize(item, "en") for item in group.items)
            for group in profile.skills
        ],
        "experience": [line for entry in profile.experience for line in _experience(entry)],
        "projects": [
            localize(profile.projects.note, "en"),
            *(
                f"- {localize(item.name, 'en')}: {localize(item.summary, 'en')} "
                f"(stack: {', '.join(item.stack)})"
                for item in profile.projects.items
            ),
        ],
        "education": [
            f"- {localize(entry.degree, 'en')}, {entry.institution} ({entry.year})"
            + (f". {localize(entry.note, 'en')}" if entry.note else "")
            for entry in profile.education
        ],
        "languages": [
            f"- {localize(language.name, 'en')}: {localize(language.level, 'en')}"
            for language in profile.languages
        ],
        "gaps": _gaps(profile),
        "contact": _contact(contact_email, contact_phone),
    }
    return "\n\n".join(
        f'<source id="profile:{key}">\n' + "\n".join(lines) + "\n</source>"
        for key, lines in blocks.items()
    )


def _gaps(profile: Profile) -> list[str]:
    if profile.gaps is None:
        return ["No gaps are listed."]
    lines = ["No professional experience with: " + ", ".join(profile.gaps.no_experience) + "."]
    if profile.gaps.learning:
        lines.append("Currently learning: " + ", ".join(profile.gaps.learning) + ".")
    return lines


def _contact(email: str | None, phone: str | None) -> list[str]:
    """Where the deployment says he can be reached; a detail that isn't set isn't given."""
    return [
        f"Email: {email}" if email else "Email: not available, never invent one.",
        f"Phone and WhatsApp: {phone}" if phone else "Phone: not available, never invent one.",
        "Other ways: the contact option in this chat, and his LinkedIn profile.",
    ]


def _experience(entry: Experience) -> list[str]:
    heading = f"## {entry.company}"
    if entry.formerly:
        heading += f" (formerly {entry.formerly})"
    lines = [heading]
    if entry.description:
        lines.append(localize(entry.description, "en"))
    lines.extend(_role(role) for role in entry.roles)
    return lines


def _role(role: Role) -> str:
    details = [format_period(role.start, role.end, "en")]
    if role.work_mode:
        details.append(role.work_mode)
    if role.stack:
        details.append("stack: " + ", ".join(role.stack))
    highlights = " ".join(localize(highlight, "en") for highlight in role.highlights)
    return f"- {localize(role.title, 'en')} ({'; '.join(details)}). {highlights}"
