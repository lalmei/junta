"""Append operator-specific tool result messages after capability execution."""

from __future__ import annotations

from typing import Any

from junta.operators.types import CapabilityInvocation


def append_capability_results(
    messages: list[dict[str, Any]],
    operator_name: str,
    invocations: list[CapabilityInvocation],
    results: list[Any],
) -> None:
    """Append one user/tool turn carrying capability results for the next operator call."""
    if len(invocations) != len(results):
        msg = "invocations and results length mismatch"
        raise ValueError(msg)
    key = operator_name.lower().strip()
    if key == "anthropic":
        blocks: list[dict[str, Any]] = []
        for inv, res in zip(invocations, results, strict=True):
            tid = inv.anthropic_tool_use_id
            if not tid:
                msg = "anthropic capability response missing tool_use id"
                raise ValueError(msg)
            blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tid,
                    "content": str(res),
                },
            )
        messages.append({"role": "user", "content": blocks})
        return
    for inv, res in zip(invocations, results, strict=True):
        tcid = inv.openai_tool_call_id
        if not tcid:
            msg = "openai-compatible capability response missing tool_call id"
            raise ValueError(msg)
        messages.append(
            {
                "role": "tool",
                "content": str(res),
                "tool_call_id": tcid,
            },
        )
