"""Officer: base class with operator ReAct loop over manifest capabilities."""

from __future__ import annotations

import time
from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from junta.dispatch import FieldReport
from junta.doctrine.doctrine import Doctrine
from junta.dossier.dossier import Dossier
from junta.event.event import Event, EventType
from junta.intelligence.intelligence import Intelligence
from junta.mandate.mandate import Mandate, MandateStatus
from junta.manifest.manifest import Manifest
from junta.operators.base import Operator
from junta.operators.tool_messages import append_capability_results
from junta.operators.types import OperatorTurn
from junta.tribunal.breach import CapabilityBreach, DoctrineViolation, OperatorFailure
from junta.tribunal.contingency import Contingency
from junta.tribunal.wiretap import Wiretap, WiretapLevel


class Officer(BaseModel, ABC):
    """Officer executes a mandate via an operator, manifest, intelligence, and doctrine."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    id: str
    codename: str
    intelligence: Intelligence = Field(default_factory=Intelligence)
    manifest: Manifest = Field(default_factory=Manifest)
    doctrine: Doctrine = Field(default_factory=Doctrine)
    contingency: Contingency = Field(default_factory=Contingency)
    operator: Operator | None = Field(default=None, exclude=True)
    wiretap: Wiretap | None = None
    events: list[Event] = Field(default_factory=list)

    def execute_mandate(self, mandate: Mandate) -> str:
        """Run the ReAct loop until a final dispatch or doctrine breach."""
        op = self.operator
        if op is None:
            raise OperatorFailure("officer has no operator conscripted")
        doctrine = mandate.doctrine
        dossier = Dossier()
        messages: list[dict[str, Any]] = self.intelligence.inject(dossier)
        messages.append({"role": "user", "content": mandate.briefing})
        mandate.status = MandateStatus.ACTIVE
        self._emit(EventType.MANDATE_ISSUED, {"mandate_id": mandate.id})
        self._log(WiretapLevel.MONITOR, "mandate_issued", {"mandate_id": mandate.id})
        schema = self.manifest.to_operator_schema(op.name)
        iterations = 0
        while iterations < doctrine.max_iterations:
            iterations += 1
            turn = self._complete_with_contingency(op, messages, schema, doctrine)
            self._emit(EventType.DISPATCH_RECEIVED, {"text": turn.dispatch.content[:500]})
            if turn.continuation_assistant_message is not None:
                messages.append(turn.continuation_assistant_message)
            dossier.add(turn.dispatch)
            if not turn.capability_invocations:
                mandate.status = MandateStatus.COMPLETE
                mandate.result = turn.dispatch.content
                self._emit(EventType.MANDATE_COMPLETE, {"mandate_id": mandate.id})
                self._log(WiretapLevel.MONITOR, "mandate_complete", {"mandate_id": mandate.id})
                return turn.dispatch.content
            results: list[Any] = []
            for inv in turn.capability_invocations:
                self._emit(
                    EventType.CAPABILITY_CALLED,
                    {"capability": inv.name, "args": inv.arguments},
                )
                self._log(
                    WiretapLevel.INTERCEPT,
                    "capability_called",
                    {"capability": inv.name},
                )
                try:
                    cap = self.manifest.get(inv.name)
                except KeyError as exc:
                    raise CapabilityBreach(f"unknown capability {inv.name!r}") from exc
                res = cap.execute(inv.arguments)
                dossier.add_field_report(FieldReport(capability=inv.name, args=inv.arguments, result=res))
                results.append(res)
            append_capability_results(messages, op.name, turn.capability_invocations, results)
        mandate.status = MandateStatus.BREACHED
        raise DoctrineViolation("max_iterations exceeded for mandate execution")

    def _complete_with_contingency(
        self,
        op: Operator,
        messages: list[dict[str, Any]],
        schema: list[dict[str, Any]],
        doctrine: Doctrine,
    ) -> OperatorTurn:
        last_exc: BaseException | None = None
        for attempt in range(self.contingency.max_retries + 1):
            try:
                return op.complete(messages, schema, doctrine)
            except OperatorFailure as exc:
                last_exc = exc
                self._emit(EventType.BREACH_DETECTED, {"kind": "operator_failure", "detail": str(exc)})
                self._log(WiretapLevel.BREACH, "operator_failure", {"detail": str(exc)})
                if self.contingency.on_breach == "abort":
                    raise
                if attempt >= self.contingency.max_retries:
                    raise OperatorFailure(f"operator failed after contingency: {last_exc!r}") from last_exc
                delay = self.contingency.backoff_seconds * (attempt + 1)
                if delay > 0:
                    time.sleep(delay)
        raise OperatorFailure("contingency loop exited without operator result")

    def _emit(self, kind: EventType, payload: dict[str, Any]) -> None:
        ev = Event(type=kind, officer_id=self.id, payload=payload)
        self.events.append(ev)

    def _log(self, level: WiretapLevel, event: str, payload: dict[str, Any]) -> None:
        if self.wiretap is not None:
            self.wiretap.log(level, event, payload, officer_id=self.id)
