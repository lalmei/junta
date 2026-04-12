"""Ruling: tribunal verdict for a mandate result."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    """Tribunal verdict on an officer result."""

    APPROVED = "approved"
    REJECTED = "rejected"
    RETRIAL = "retrial"


class Ruling(BaseModel):
    """Ruling records verdict, score, and optional retrial feedback."""

    mandate_id: str
    verdict: Verdict
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    feedback: str | None = None
