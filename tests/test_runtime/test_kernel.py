"""Tests for Junta kernel: convene, execute, handoffs, tribunal, retries."""

from __future__ import annotations

from unittest.mock import MagicMock

from junta import (
    Complete,
    Condition,
    Continue,
    Doctrine,
    Dossier,
    Fail,
    Handoff,
    Junta,
    Mandate,
    Officer,
    Operation,
    RetryPolicy,
    RunResult,
)


class _Officer:
    def __init__(self, name: str, outcome: Complete | Continue | Handoff | Fail) -> None:
        self._name = name
        self._outcome = outcome

    @property
    def name(self) -> str:
        return self._name

    def execute(self, _operation: Operation) -> Complete | Continue | Handoff | Fail:
        return self._outcome


def test_convene_uses_explicit_dossier() -> None:
    junta = Junta(officers=[_Officer("a", Complete())])
    m = Mandate(directive="x")
    d = Dossier(facts={"k": 1})
    op = junta.convene(mandate=m, dossier=d)
    assert op.dossier.facts["k"] == 1


def test_convene_builds_dossier_from_briefing_when_omitted() -> None:
    junta = Junta(officers=[_Officer("a", Complete())])
    m = Mandate(directive="x", briefing={"a": 2})
    op = junta.convene(mandate=m, dossier=None)
    assert op.dossier.facts["a"] == 2


def test_execute_single_complete() -> None:
    junta = Junta(officers=[_Officer("only", Complete(brief="done"))])
    r = junta.execute(Mandate(directive="run"))
    assert isinstance(r, RunResult)
    assert r.success is True
    assert r.final_brief == "done"
    assert len(r.outcomes) == 1


def test_execute_continue_second_officer() -> None:
    junta = Junta(
        officers=[
            _Officer("first", Continue()),
            _Officer("second", Complete(brief="ok")),
        ],
    )
    r = junta.execute(Mandate(directive="run"))
    assert r.success is True
    assert r.final_brief == "ok"
    assert len(r.outcomes) == 2


def test_handoff_to_named_officer() -> None:
    junta = Junta(
        officers=[
            _Officer("a", Handoff(to="b")),
            _Officer("b", Complete(brief="from-b")),
        ],
    )
    r = junta.execute(Mandate(directive="run"))
    assert r.success is True
    assert r.final_brief == "from-b"


def test_handoff_unknown_returns_failure() -> None:
    junta = Junta(officers=[_Officer("a", Handoff(to="missing"))])
    r = junta.execute(Mandate(directive="run"))
    assert r.success is False
    assert "unknown officer" in (r.error or "")


def test_fail_outcome() -> None:
    junta = Junta(officers=[_Officer("a", Fail(error="no"))])
    r = junta.execute(Mandate(directive="run"))
    assert r.success is False
    assert r.error == "no"


def test_tribunal_review_called() -> None:
    tribunal = MagicMock()
    junta = Junta(officers=[_Officer("a", Complete())], tribunal=tribunal)
    junta.execute(Mandate(directive="run"))
    tribunal.review.assert_called_once()


def test_max_steps_exceeded() -> None:
    """Handoff to self repeats forever until max_steps stops the run."""
    doctrine = Doctrine(max_steps=3)
    junta = Junta(officers=[_Officer("a", Handoff(to="a"))], doctrine=doctrine)
    r = junta.execute(Mandate(directive="run"))
    assert r.success is False
    assert r.error == "max_steps exceeded"


def test_retry_then_success() -> None:
    calls = {"n": 0}

    class Flaky:
        @property
        def name(self) -> str:
            return "flaky"

        def execute(self, _operation: Operation) -> Complete:
            calls["n"] += 1
            if calls["n"] == 1:
                msg = "transient"
                raise RuntimeError(msg)
            return Complete(brief="recovered")

    doctrine = Doctrine(retry_policy=RetryPolicy(max_attempts=3, backoff_base_seconds=0.0))
    junta = Junta(officers=[Flaky()], doctrine=doctrine)
    r = junta.execute(Mandate(directive="run"))
    assert r.success is True
    assert r.final_brief == "recovered"
    assert calls["n"] == 2


def test_end_state_enforced() -> None:
    junta = Junta(officers=[_Officer("a", Complete(brief="x"))])
    m = Mandate(
        directive="run",
        end_state=[Condition(metric="done", target=True)],
    )
    r = junta.execute(mandate=m)
    assert r.success is False
    assert "end_state" in (r.error or "")


def test_end_state_satisfied_via_dossier() -> None:
    class SetsFact:
        @property
        def name(self) -> str:
            return "writer"

        def execute(self, operation: Operation) -> Complete:
            operation.dossier.facts["done"] = True
            return Complete()

    junta = Junta(officers=[SetsFact()])
    m = Mandate(
        directive="run",
        end_state=[Condition(metric="done", target=True)],
    )
    r = junta.execute(mandate=m)
    assert r.success is True


def test_pipeline_exhausted_on_continue() -> None:
    junta = Junta(officers=[_Officer("only", Continue())])
    r = junta.execute(Mandate(directive="run"))
    assert r.success is False
    assert "pipeline exhausted" in (r.error or "")


def test_officer_isinstance_protocol() -> None:
    o = _Officer("x", Complete())
    assert isinstance(o, Officer)


def test_tracer_lifecycle_order() -> None:
    events: list[str] = []

    class RecordingTracer:
        def on_run_start(self, _op: object) -> None:
            events.append("run_start")

        def on_run_end(self, _op: object, _result: object) -> None:
            events.append("run_end")

        def on_officer_start(self, _op: object, officer_name: str) -> None:
            events.append(f"officer_start:{officer_name}")

        def on_officer_end(self, _op: object, officer_name: str, _outcome: object) -> None:
            events.append(f"officer_end:{officer_name}")

        def on_retry(self, _op: object, _officer_name: str, attempt: int, _exc: BaseException) -> None:
            events.append(f"retry:{attempt}")

        def on_handoff(self, _op: object, _from_o: str, _to_o: str) -> None:
            events.append("handoff")

        def on_failure(self, _op: object, _exc: BaseException) -> None:
            events.append("failure")

    doctrine = Doctrine(tracer=RecordingTracer())
    junta = Junta(officers=[_Officer("m", Complete())], doctrine=doctrine)
    junta.execute(Mandate(directive="go"))
    assert events[0] == "run_start"
    assert "officer_start:m" in events
    assert "officer_end:m" in events
    assert events[-1] == "run_end"
