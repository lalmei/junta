"""Capability: executable unit registered on a manifest (operator-facing schema)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from junta.tribunal.breach import CapabilityBreach


class CapabilityParam(BaseModel):
    """Parameter description for a capability schema."""

    name: str
    type: str
    description: str
    required: bool = True


class Capability(BaseModel):
    """A capability binds a name and schema to an optional Python handler."""

    model_config = {"arbitrary_types_allowed": True}

    name: str
    description: str
    params: list[CapabilityParam] = Field(default_factory=list)
    handler: Callable[..., Any] | None = Field(default=None, exclude=True)

    def execute(self, args: dict[str, Any]) -> Any:
        """Run the handler with validated arguments."""
        if self.handler is None:
            msg = f"capability {self.name!r} has no handler"
            raise CapabilityBreach(msg)
        try:
            return self.handler(**args)
        except TypeError as exc:
            msg = f"capability {self.name!r} argument mismatch: {exc}"
            raise CapabilityBreach(msg) from exc
        except Exception as exc:
            msg = f"capability {self.name!r} failed: {exc}"
            raise CapabilityBreach(msg) from exc
