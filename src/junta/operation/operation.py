"""Operation bundles mandate, dossier, doctrine for one run."""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from junta.doctrine.doctrine import Doctrine
from junta.mandate.mandate import Mandate
from junta.dossier import Dossier
from junta.operation.outcomes import Complete, Continue, Fail, Handoff


class Operation(BaseModel):
    """One execution context: inputs plus recorded officer results."""

    model_config = {"arbitrary_types_allowed": True}

    mandate: Mandate
    dossier: Dossier
    doctrine: Doctrine
    results: list[Complete | Handoff | Fail | Continue] = Field(default_factory=list)

    _pending_handoff: str | None = PrivateAttr(default=None)

    def record_result(self, outcome: Complete | Handoff | Fail | Continue) -> None:
        """Append an officer step outcome to history."""
        self.results.append(outcome)

    def set_pending_handoff(self, target: str | None) -> None:
        """Kernel sets the next officer name after a Handoff outcome."""
        self._pending_handoff = target

    @property
    def pending_handoff(self) -> str | None:
        """Next officer name when a handoff is active."""
        return self._pending_handoff
