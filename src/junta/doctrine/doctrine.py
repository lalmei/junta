"""Cross-cutting runtime policy: retries, failure handling, tracing."""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class FailurePolicy(str, Enum):
    """What the kernel does after a terminal failure."""

    ABORT = "abort"


class RetryPolicy(BaseModel):
    """Per-officer-step retry limits."""

    max_attempts: int = Field(default=1, ge=1)
    backoff_base_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Sleep (attempt * backoff_base_seconds) before retry when attempts remain.",
    )


@runtime_checkable
class Tracer(Protocol):
    """Hooks for observability; optional on Doctrine."""

    def on_run_start(self, operation: Any) -> None: ...
    def on_run_end(self, operation: Any, result: Any) -> None: ...
    def on_officer_start(self, operation: Any, officer_name: str) -> None: ...
    def on_officer_end(self, operation: Any, officer_name: str, outcome: Any) -> None: ...
    def on_retry(self, operation: Any, officer_name: str, attempt: int, exc: BaseException) -> None: ...
    def on_handoff(self, operation: Any, from_officer: str, to_officer: str) -> None: ...
    def on_failure(self, operation: Any, exc: BaseException) -> None: ...


class NoOpTracer:
    """Default tracer that does nothing."""

    def on_run_start(self, _operation: Any) -> None:
        return

    def on_run_end(self, _operation: Any, _result: Any) -> None:
        return

    def on_officer_start(self, _operation: Any, _officer_name: str) -> None:
        return

    def on_officer_end(self, _operation: Any, _officer_name: str, _outcome: Any) -> None:
        return

    def on_retry(self, _operation: Any, _officer_name: str, _attempt: int, _exc: BaseException) -> None:
        return

    def on_handoff(self, _operation: Any, _from_officer: str, _to_officer: str) -> None:
        return

    def on_failure(self, _operation: Any, _exc: BaseException) -> None:
        return


class Doctrine(BaseModel):
    """Kernel-wide policy container."""

    model_config = {"arbitrary_types_allowed": True}

    max_steps: int = Field(default=100, ge=1)
    failure_policy: FailurePolicy = FailurePolicy.ABORT
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    tracer: Any = Field(default_factory=NoOpTracer)
