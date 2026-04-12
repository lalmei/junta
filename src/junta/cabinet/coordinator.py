"""Coordinator officer: orchestrates other officers via Junta."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from junta.cabinet.officer import Officer
from junta.intelligence.intelligence import Intelligence


class Coordinator(Officer):
    """Coordination officer; may delegate sub-mandates through the Junta when set."""

    junta: Any | None = Field(default=None, description="Junta reference for issuing sub-mandates.")
    intelligence: Intelligence = Field(
        default_factory=lambda: Intelligence(
            system_briefing=(
                "You are a coordination officer. Route work to the right officers "
                "and consolidate outcomes per doctrine."
            ),
        ),
    )

    def attach_junta(self, junta: Any) -> None:
        """Wire the top-level Junta for sub-mandate delegation."""
        self.junta = junta
