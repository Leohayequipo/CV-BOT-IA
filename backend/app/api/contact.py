"""POST /contact: send the message the visitor confirmed to Leonardo (ADR-021)."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.agents.mock import MockMailer
from app.api.limits import Limits, get_limits, visitor_ip
from app.schemas.contact import ContactReceipt, ContactRequest

router = APIRouter()


def get_mailer() -> MockMailer:
    return MockMailer()


@router.post("/contact", status_code=202)
async def contact(
    message: ContactRequest,
    mailer: Annotated[MockMailer, Depends(get_mailer)],
    limits: Annotated[Limits, Depends(get_limits)],
    ip: Annotated[str, Depends(visitor_ip)],
) -> ContactReceipt:
    limits.contact_by_ip.check(ip)
    await mailer.send(message)
    return ContactReceipt(sent_at=datetime.now(UTC).replace(microsecond=0))
