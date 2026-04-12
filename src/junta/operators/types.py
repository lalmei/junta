"""Structured operator turn: dispatch plus optional capability invocations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from junta.dispatch import Dispatch


class CapabilityInvocation(BaseModel):
    """One capability the operator asks the officer to run."""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    anthropic_tool_use_id: str | None = None
    openai_tool_call_id: str | None = None


class OperatorTurn(BaseModel):
    """Result of one operator completion: assistant dispatch and optional capability calls."""

    dispatch: Dispatch
    capability_invocations: list[CapabilityInvocation] = Field(default_factory=list)
    #: Next-turn message dict to append to ``messages`` (role + content / tool_calls).
    continuation_assistant_message: dict[str, Any] | None = None
