"""Intelligence: persistent briefing context merged into operator messages."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from junta.dispatch import Dispatch, DispatchRole
from junta.dossier.dossier import Dossier


class Intelligence(BaseModel):
    """Intelligence merges system briefing, prior dispatches, and dossier history."""

    system_briefing: str = ""
    context: list[Dispatch] = Field(default_factory=list)

    def inject(self, dossier: Dossier) -> list[dict[str, Any]]:
        """Build operator message dicts: system briefing, then dossier history."""
        messages: list[dict[str, Any]] = []
        if self.system_briefing.strip():
            messages.append({"role": "system", "content": self.system_briefing})
        for d in self.context:
            messages.append({"role": _role_to_operator(d.role), "content": d.content})
        for entry in dossier.history():
            messages.append(entry)
        return messages


def _role_to_operator(role: DispatchRole) -> str:
    if role == DispatchRole.OFFICER:
        return "assistant"
    if role == DispatchRole.USER:
        return "user"
    return "system"
