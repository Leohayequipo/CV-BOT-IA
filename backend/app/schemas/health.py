"""Response of the health check."""

from typing import Literal

from pydantic import BaseModel


class Health(BaseModel):
    status: Literal["ok"]
    git_sha: str
