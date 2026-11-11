"""Takes email addresses and phone numbers out of anything sent to Langfuse (ADR-030)."""

import re
from typing import Any

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Nine digits or more, with the separators people type between them; dates and years stay
PHONE = re.compile(r"(?<![\w-])\+?\(?\d(?:[\d\s().-]*\d){8,}")


def redact(*, data: Any, **_: Any) -> Any:
    """The same data with contact details replaced, whatever mix of text, lists and dicts it is.

    The signature is the one Langfuse's `mask` option calls, which applies it to the input,
    output and metadata of every observation.
    """
    if isinstance(data, str):
        return PHONE.sub("[phone]", EMAIL.sub("[email]", data))
    if isinstance(data, dict):
        return {key: redact(data=value) for key, value in data.items()}
    if isinstance(data, list | tuple):
        return [redact(data=item) for item in data]
    return data
