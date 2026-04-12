"""Wiretap: observability for officers and Junta; Intercept records each log entry."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WiretapLevel(str, Enum):
    """Severity of a wiretap intercept (ordered for minimum-level filtering)."""

    INTERCEPT = "intercept"
    MONITOR = "monitor"
    ALERT = "alert"
    BREACH = "breach"
    BLACKOUT = "blackout"


_WIRETAP_RANK: dict[WiretapLevel, int] = {
    WiretapLevel.INTERCEPT: 0,
    WiretapLevel.MONITOR: 1,
    WiretapLevel.ALERT: 2,
    WiretapLevel.BREACH: 3,
    WiretapLevel.BLACKOUT: 4,
}


class WiretapChannel(str, Enum):
    """Where wiretap output is delivered."""

    CONSOLE = "console"
    FILE = "file"
    MEMORY = "memory"


class Intercept(BaseModel):
    """A single wiretap log entry (an intercept)."""

    timestamp: datetime
    level: WiretapLevel
    officer_id: str | None
    event: str
    payload: dict[str, Any]


class Wiretap(BaseModel):
    """Wiretap: records intercepts and writes to configured channels."""

    channel: WiretapChannel = WiretapChannel.CONSOLE
    level: WiretapLevel = WiretapLevel.MONITOR
    intercepts: list[Intercept] = Field(default_factory=list)

    def log(
        self,
        level: WiretapLevel,
        event: str,
        payload: dict[str, Any],
        officer_id: str | None = None,
    ) -> None:
        """Record an intercept at the given level and optionally mirror to the channel."""
        if _WIRETAP_RANK[level] < _WIRETAP_RANK[self.level]:
            return
        entry = Intercept(
            timestamp=datetime.now(timezone.utc),
            level=level,
            officer_id=officer_id,
            event=event,
            payload=payload,
        )
        if self.channel == WiretapChannel.MEMORY:
            self.intercepts.append(entry)
        elif self.channel == WiretapChannel.CONSOLE:
            line = f"[{entry.timestamp.isoformat()}] {level.value} {event} officer={officer_id!r} {payload}\n"
            sys.stderr.write(line)
