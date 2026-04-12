"""Contingency: retry and fallback policy after operator or capability failure."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Contingency(BaseModel):
    """Contingency limits and fallback behavior for operator and capability failures."""

    max_retries: int = Field(default=3, ge=0)
    backoff_seconds: float = Field(default=1.0, ge=0.0)
    fallback_operator: str | None = None
    on_breach: Literal["abort", "retry", "escalate"] = "abort"
