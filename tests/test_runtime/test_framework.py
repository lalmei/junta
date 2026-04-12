"""Tests for manifest schema, mock operator, Junta.issue, and doctrine limits."""

from __future__ import annotations

from typing import Any

import pytest

from junta.cabinet.analyst import Analyst
from junta.capability.capability import Capability, CapabilityParam
from junta.config import Config
from junta.dispatch import Dispatch, DispatchRole
from junta.doctrine.doctrine import Doctrine
from junta.junta import Junta
from junta.mandate.mandate import Mandate, MandateStatus
from junta.manifest.manifest import Manifest
from junta.operators.base import Operator
from junta.operators.types import CapabilityInvocation, OperatorTurn
from junta.tribunal.breach import DoctrineViolation
from junta.tribunal.ruling import Verdict


class MockOperator(Operator):
    """Deterministic operator for tests (no network)."""

    def __init__(self, name: str = "anthropic", text: str = "final answer") -> None:
        """Configure operator name and fixed assistant text."""
        self.name = name
        self._text = text

    def complete(
        self,
        _messages: list[dict[str, Any]],
        _capabilities: list[dict[str, Any]],
        _doctrine: Doctrine,
    ) -> OperatorTurn:
        """Return a single assistant dispatch without capability invocations."""
        dispatch = Dispatch(role=DispatchRole.OFFICER, content=self._text)
        return OperatorTurn(
            dispatch=dispatch,
            continuation_assistant_message={"role": "assistant", "content": self._text},
        )

    def stream(
        self,
        _messages: list[dict[str, Any]],
        _capabilities: list[dict[str, Any]],
        _doctrine: Doctrine,
        callback: Any,
    ) -> None:
        """Invoke callback once with the fixed text."""
        callback(self._text)


def test_manifest_to_operator_schema_openai() -> None:
    m = Manifest()
    m.register(
        Capability(
            name="echo",
            description="Echo text.",
            params=[CapabilityParam(name="text", type="str", description="Input", required=True)],
            handler=lambda text: text,
        ),
    )
    schema = m.to_operator_schema("openai")
    assert len(schema) == 1
    assert schema[0]["type"] == "function"
    assert schema[0]["function"]["name"] == "echo"


def test_manifest_to_operator_schema_anthropic() -> None:
    m = Manifest()
    m.register(
        Capability(
            name="echo",
            description="Echo text.",
            params=[CapabilityParam(name="text", type="str", description="Input", required=True)],
            handler=lambda text: text,
        ),
    )
    schema = m.to_operator_schema("anthropic")
    assert schema[0]["name"] == "echo"
    assert schema[0]["input_schema"]["type"] == "object"


def test_junta_issue_heuristic_ruling() -> None:
    j = Junta.from_config(Config(tribunal_enabled=False))
    j.conscript(MockOperator())
    off = Analyst(
        id="a1",
        codename="alpha",
        operator=j.operators["anthropic"],
        wiretap=j.wiretap,
    )
    j.deploy(off)
    m = Mandate(id="m1", briefing="Say hello.")
    r = j.issue(m, to="alpha")
    assert r.verdict == Verdict.APPROVED
    assert m.status == MandateStatus.COMPLETE


def test_junta_issue_requires_officer() -> None:
    j = Junta.from_config(Config(tribunal_enabled=False))
    j.conscript(MockOperator())
    m = Mandate(id="m2", briefing="x")
    with pytest.raises(KeyError):
        j.issue(m, to="missing")


def _echo_manifest() -> Manifest:
    m = Manifest()
    m.register(
        Capability(
            name="echo",
            description="Echo.",
            params=[CapabilityParam(name="text", type="str", description="t", required=True)],
            handler=lambda text: text,
        ),
    )
    return m


class LoopingMockOperator(Operator):
    """Always requests echo capability to force multiple iterations."""

    def __init__(self) -> None:
        """Use the anthropic operator name for manifest schema lookup."""
        self.name = "anthropic"

    def complete(
        self,
        _messages: list[dict[str, Any]],
        _capabilities: list[dict[str, Any]],
        _doctrine: Doctrine,
    ) -> OperatorTurn:
        """Always emit one echo capability invocation."""
        return OperatorTurn(
            dispatch=Dispatch(role=DispatchRole.OFFICER, content="call echo"),
            capability_invocations=[
                CapabilityInvocation(name="echo", arguments={"text": "x"}, anthropic_tool_use_id="tu1"),
            ],
            continuation_assistant_message={
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "call echo"},
                    {
                        "type": "tool_use",
                        "id": "tu1",
                        "name": "echo",
                        "input": {"text": "x"},
                    },
                ],
            },
        )

    def stream(
        self,
        _messages: list[dict[str, Any]],
        _capabilities: list[dict[str, Any]],
        _doctrine: Doctrine,
        _callback: Any,
    ) -> None:
        """Not used in these tests."""
        raise NotImplementedError


def test_doctrine_violation_max_iterations() -> None:
    j = Junta()
    j.conscript(LoopingMockOperator())
    off = Analyst(
        id="o2",
        codename="two",
        operator=j.operators["anthropic"],
        manifest=_echo_manifest(),
        wiretap=j.wiretap,
    )
    j.deploy(off)
    m2 = Mandate(id="m4", briefing="loop", doctrine=Doctrine(max_iterations=2))
    with pytest.raises(DoctrineViolation):
        j.issue(m2, to="two")
