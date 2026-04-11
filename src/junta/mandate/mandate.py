"""Mandate and terminal condition models."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Field, model_validator


class Condition(BaseModel):
    """A single measurable end-state target."""

    metric: str
    target: Any


class Mandate(BaseModel):
    """Intent and constraints for a run."""

    directive: str
    briefing: dict[str, Any] = Field(default_factory=dict)
    doctrine_refs: list[str] = Field(
        default_factory=list,
        description="References to doctrine tags or rule ids (distinct from junta.doctrine.doctrine.Doctrine instance).",
    )
    end_state: list[Condition] = Field(default_factory=list)
    urgency: Literal["routine", "priority", "critical"] = "routine"
    contingency: Annotated[int, Field(ge=0)] = 0

    @model_validator(mode="after")
    def _validate_non_empty_directive(self) -> Self:
        if not self.directive.strip():
            msg = "directive must be non-empty"
            raise ValueError(msg)
        return self
