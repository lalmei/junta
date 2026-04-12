"""Event: state transitions emitted during mandate execution."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Kinds of events the Junta kernel may emit."""

    MANDATE_ISSUED = "mandate_issued"
    MANDATE_COMPLETE = "mandate_complete"
    CAPABILITY_CALLED = "capability_called"
    DISPATCH_RECEIVED = "dispatch_received"
    BREACH_DETECTED = "breach_detected"
    RULING_ISSUED = "ruling_issued"


class Event(BaseModel):
    """An event records a transition with payload and optional officer scope."""

    type: EventType
    officer_id: str | None
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
