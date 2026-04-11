"""Junta: top-level execution kernel."""

from __future__ import annotations

import time
from collections.abc import Iterable

from junta.cabinet.officer import Officer
from junta.doctrine.doctrine import Doctrine, FailurePolicy
from junta.dossier import Dossier
from junta.mandate.mandate import Mandate
from junta.operation.operation import Operation
from junta.operation.outcomes import Complete, Continue, Fail, Handoff, RunResult
from junta.tribunal.tribunal import Tribunal


class Junta:
    """Registers officers, doctrine, and optional tribunal; runs mandates."""

    def __init__(
        self,
        officers: Iterable[Officer],
        doctrine: Doctrine | None = None,
        tribunal: Tribunal | None = None,
    ) -> None:
        """Register officers in iteration order; optional doctrine and tribunal."""
        self._officers: dict[str, Officer] = {m.name: m for m in officers}
        self._order: list[str] = [m.name for m in officers]
        self._doctrine = doctrine or Doctrine()
        self._tribunal = tribunal

    def execute(self, mandate: Mandate, dossier: Dossier | None = None) -> RunResult:
        """Convene an operation and run until completion or failure."""
        operation = self.convene(mandate=mandate, dossier=dossier)
        return self._run(operation)

    def convene(self, mandate: Mandate, dossier: Dossier | None = None) -> Operation:
        """Build an operation without executing (inspection, dry-run)."""
        resolved = dossier or Dossier.from_briefing(mandate.briefing)
        return Operation(mandate=mandate, dossier=resolved, doctrine=self._doctrine)

    def _run(self, operation: Operation) -> RunResult:
        doctrine = operation.doctrine
        tracer = doctrine.tracer
        tracer.on_run_start(operation)
        current_idx = 0
        final: RunResult | None = None
        try:
            for _step in range(doctrine.max_steps):
                try:
                    name = self._next_officer_name(operation, current_idx)
                except RuntimeError as exc:
                    final = RunResult(success=False, outcomes=list(operation.results), error=str(exc))
                    return final
                if name not in self._officers:
                    msg = f"unknown officer: {name!r}"
                    final = RunResult(success=False, outcomes=list(operation.results), error=msg)
                    return final
                active = self._officers[name]
                tracer.on_officer_start(operation, name)
                try:
                    outcome = self._invoke_officer(active, operation, name)
                except Exception as exc:  # noqa: BLE001 - boundary: convert to RunResult
                    tracer.on_failure(operation, exc)
                    final = RunResult(success=False, outcomes=list(operation.results), error=str(exc))
                    return final
                tracer.on_officer_end(operation, name, outcome)
                operation.record_result(outcome)
                if self._tribunal is not None:
                    self._tribunal.review(operation)

                if isinstance(outcome, Complete):
                    if not self._end_state_satisfied(operation):
                        err = "mandate end_state conditions not satisfied"
                        final = RunResult(
                            success=False,
                            outcomes=list(operation.results),
                            error=err,
                        )
                        return final
                    final = RunResult(
                        success=True,
                        outcomes=list(operation.results),
                        final_brief=outcome.brief,
                    )
                    return final
                if isinstance(outcome, Fail):
                    final = RunResult(
                        success=False,
                        outcomes=list(operation.results),
                        error=outcome.error,
                    )
                    return final
                if isinstance(outcome, Handoff):
                    if outcome.to not in self._officers:
                        msg = f"handoff to unknown officer: {outcome.to!r}"
                        final = RunResult(success=False, outcomes=list(operation.results), error=msg)
                        return final
                    operation.set_pending_handoff(outcome.to)
                    tracer.on_handoff(operation, name, outcome.to)
                    continue
                if isinstance(outcome, Continue):
                    current_idx += 1
                    continue

            final = RunResult(
                success=False,
                outcomes=list(operation.results),
                error="max_steps exceeded",
            )
            return final
        finally:
            tracer.on_run_end(operation, final)

    def _next_officer_name(self, operation: Operation, current_idx: int) -> str:
        if operation.pending_handoff:
            name = operation.pending_handoff
            operation.set_pending_handoff(None)
            return name
        if current_idx >= len(self._order):
            msg = "no officer available (pipeline exhausted)"
            raise RuntimeError(msg)
        return self._order[current_idx]

    def _invoke_officer(
        self,
        active: Officer,
        operation: Operation,
        name: str,
    ) -> Complete | Handoff | Fail | Continue:
        doctrine = operation.doctrine
        policy = doctrine.retry_policy
        for attempt in range(1, policy.max_attempts + 1):
            try:
                return active.execute(operation)
            except Exception as exc:
                doctrine.tracer.on_retry(operation, name, attempt, exc)
                if attempt >= policy.max_attempts and doctrine.failure_policy is FailurePolicy.ABORT:
                    raise
                delay = attempt * policy.backoff_base_seconds
                if delay > 0:
                    time.sleep(delay)
        msg = "retry loop exhausted without result"
        raise RuntimeError(msg)

    def _end_state_satisfied(self, operation: Operation) -> bool:
        conditions = operation.mandate.end_state
        if not conditions:
            return True
        facts = operation.dossier.facts
        return all(facts.get(c.metric) == c.target for c in conditions)
