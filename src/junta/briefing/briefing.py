"""Briefing builder: assemble operator message content from mandate and intelligence."""

from __future__ import annotations

from pydantic import BaseModel, Field

from junta.intelligence.intelligence import Intelligence
from junta.mandate.mandate import Mandate


class BriefingBuilder(BaseModel):
    """Builds the initial user message for a mandate run from intelligence and mandate."""

    intelligence: Intelligence = Field(default_factory=Intelligence)

    def mandate_user_content(self, mandate: Mandate) -> str:
        """Primary user turn: mandate briefing text."""
        return mandate.briefing.strip()
