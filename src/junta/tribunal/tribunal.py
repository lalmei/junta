"""Optional oversight hook after officer steps."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tribunal(Protocol):
    """Review accumulated operation state after each officer result."""

    def review(self, operation: Any) -> None:
        """Inspect operation; may raise to abort."""
        ...
