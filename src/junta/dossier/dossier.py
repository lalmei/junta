"""Structured working state for a run."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Dossier(BaseModel):
    """Working memory for a run, evolved by officers."""

    facts: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_briefing(cls, briefing: dict[str, Any]) -> Dossier:
        """Build an initial dossier from unstructured mandate briefing."""
        return cls(facts=dict(briefing))
