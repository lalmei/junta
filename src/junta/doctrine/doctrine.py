"""Doctrine: policy limits for officers and operators."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Doctrine(BaseModel):
    """Doctrine constrains iterations, parallelism, tokens, and sampling."""

    max_iterations: int = Field(default=10, ge=1)
    allow_parallel: bool = False
    require_approval: bool = False
    max_tokens: int = Field(default=4096, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
