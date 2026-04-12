"""Dispatch (LLM message) and FieldReport (capability result)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DispatchRole(str, Enum):
    """Role of a dispatch in the dossier."""

    OFFICER = "officer"
    USER = "user"
    SYSTEM = "system"


class Dispatch(BaseModel):
    """A single message in the dossier (formerly assistant/user/system turns)."""

    role: DispatchRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FieldReport(BaseModel):
    """Structured record of a capability invocation and its result."""

    capability: str
    args: dict[str, Any]
    result: Any
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
