"""POST /contact: send the message the visitor confirmed to Leonardo (ADR-021)."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.agents.mock import MockMailer
from app.schemas.contact import ContactReceipt, ContactRequest

router = APIRouter()


def get_mailer() -> MockMailer:
    return MockMailer()


@router.post("/contact", status_code=202)
async def contact(
    message: ContactRequest, mailer: Annotated[MockMailer, Depends(get_mailer)]
) -> ContactReceipt:
    await mailer.send(message)
    return ContactReceipt(sent_at=datetime.now(UTC).replace(microsecond=0))
