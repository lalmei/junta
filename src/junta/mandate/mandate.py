"""Mandate: unit of work issued to an officer."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from junta.doctrine.doctrine import Doctrine


class MandateStatus(str, Enum):
    """Lifecycle state of a mandate."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    BREACHED = "breached"


class Mandate(BaseModel):
    """A mandate is the briefing and doctrine an officer must satisfy."""

    id: str
    briefing: str
    status: MandateStatus = MandateStatus.PENDING
    doctrine: Doctrine = Field(default_factory=Doctrine)
    result: str | None = None

    @field_validator("briefing")
    @classmethod
    def _non_empty_briefing(cls, v: str) -> str:
        if not v.strip():
            msg = "briefing must be non-empty"
            raise ValueError(msg)
        return v
