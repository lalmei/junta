"""Structured results from officers and from execute()."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


class Complete(BaseModel):
    """Terminal success with optional payload (e.g. brief)."""

    kind: Literal["complete"] = "complete"
    brief: Any = None


class Handoff(BaseModel):
    """Route the next step to a named officer."""

    kind: Literal["handoff"] = "handoff"
    to: str


class Fail(BaseModel):
    """Terminal failure."""

    kind: Literal["fail"] = "fail"
    error: str


class Continue(BaseModel):
    """Advance to the next officer in pipeline order."""

    kind: Literal["continue"] = "continue"


StepOutcome = Annotated[
    Union[Complete, Handoff, Fail, Continue],
    Field(discriminator="kind"),
]


class RunResult(BaseModel):
    """Result of `Junta.execute`."""

    success: bool
    outcomes: list[Complete | Handoff | Fail | Continue] = Field(default_factory=list)
    final_brief: Any = None
    error: str | None = None
