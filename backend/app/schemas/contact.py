"""The request and the receipt of POST /contact, as docs/API.md defines them."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

# Catches typos without a dependency; the email provider rejects the rest
_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class ContactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    company: Annotated[str, StringConstraints(max_length=100)]
    email: Annotated[str, StringConstraints(max_length=254, pattern=_EMAIL)]
    message: Annotated[str, StringConstraints(min_length=1, max_length=2000)]
    session_id: UUID


class ContactReceipt(BaseModel):
    sent_at: datetime
