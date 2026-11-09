"""Prompts as Markdown files, filled with named variables by one loader."""

import re
from importlib import resources

_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def render_prompt(name: str, **variables: str) -> str:
    """Read prompts/<name>.md and replace each {{variable}}; a missing or unused one is an error."""
    template = resources.files("app.prompts").joinpath(f"{name}.md").read_text(encoding="utf-8")
    wanted = set(_PLACEHOLDER.findall(template))
    if wanted != set(variables):
        msg = f"prompt '{name}' takes {sorted(wanted)}, got {sorted(variables)}"
        raise ValueError(msg)
    return _PLACEHOLDER.sub(lambda match: variables[match.group(1)], template)
