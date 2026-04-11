"""Officer protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from junta.operation.operation import Operation
from junta.operation.outcomes import Complete, Continue, Fail, Handoff


@runtime_checkable
class Officer(Protocol):
    """A named participant invoked by the kernel with an Operation."""

    @property
    def name(self) -> str: ...

    def execute(self, operation: Operation) -> Complete | Handoff | Fail | Continue:
        """Perform one step; kernel interprets the outcome."""
        ...
