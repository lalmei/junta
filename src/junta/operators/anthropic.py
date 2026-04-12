"""Anthropic operator (Claude)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import anthropic

from junta.dispatch import Dispatch, DispatchRole
from junta.doctrine.doctrine import Doctrine
from junta.operators.base import Operator
from junta.operators.types import CapabilityInvocation, OperatorTurn
from junta.tribunal.breach import OperatorFailure


class AnthropicOperator(Operator):
    """Operator using Anthropic Messages API (Claude Sonnet)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        """Create a Claude Messages client for the given model."""
        self.name = "anthropic"
        self._model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        messages: list[dict[str, Any]],
        capabilities: list[dict[str, Any]],
        doctrine: Doctrine,
    ) -> OperatorTurn:
        """Run one non-streaming completion and map tool blocks to capability invocations."""
        system, msgs = _split_system(messages)
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=doctrine.max_tokens,
                temperature=doctrine.temperature,
                system=system or "",
                messages=cast("Any", msgs),
                tools=cast("Any", capabilities or None),
            )
        except Exception as exc:
            raise OperatorFailure(f"anthropic messages.create failed: {exc}") from exc
        return _message_to_turn(response)

    def stream(
        self,
        messages: list[dict[str, Any]],
        capabilities: list[dict[str, Any]],
        doctrine: Doctrine,
        callback: Callable[[str], None],
    ) -> None:
        """Stream assistant text; capability invocations are not reconstructed from deltas."""
        system, msgs = _split_system(messages)
        try:
            with self._client.messages.stream(
                model=self._model,
                max_tokens=doctrine.max_tokens,
                temperature=doctrine.temperature,
                system=system or "",
                messages=cast("Any", msgs),
                tools=cast("Any", capabilities or None),
            ) as stream:
                for text in stream.text_stream:
                    callback(text)
        except Exception as exc:
            raise OperatorFailure(f"anthropic stream failed: {exc}") from exc


def _split_system(messages: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    system_parts: list[str] = []
    rest: list[dict[str, Any]] = []
    for m in messages:
        if m.get("role") == "system":
            c = m.get("content", "")
            if isinstance(c, str):
                system_parts.append(c)
        else:
            rest.append({"role": m["role"], "content": m["content"]})
    return "\n".join(system_parts), rest


def _message_to_turn(response: Any) -> OperatorTurn:
    text_parts: list[str] = []
    invocations: list[CapabilityInvocation] = []
    content_blocks: list[dict[str, Any]] = []
    for block in response.content:
        btype = getattr(block, "type", None)
        if btype == "text":
            text_parts.append(getattr(block, "text", "") or "")
            content_blocks.append({"type": "text", "text": getattr(block, "text", "") or ""})
        elif btype == "tool_use":
            tid = getattr(block, "id", None)
            invocations.append(
                CapabilityInvocation(
                    name=block.name,
                    arguments=dict(block.input) if block.input else {},
                    anthropic_tool_use_id=tid,
                ),
            )
            content_blocks.append(
                {
                    "type": "tool_use",
                    "id": tid,
                    "name": block.name,
                    "input": dict(block.input) if block.input else {},
                },
            )
    content = "".join(text_parts).strip()
    dispatch = Dispatch(role=DispatchRole.OFFICER, content=content or "(no text)")
    assistant_msg = {"role": "assistant", "content": content_blocks}
    return OperatorTurn(
        dispatch=dispatch,
        capability_invocations=invocations,
        continuation_assistant_message=assistant_msg,
    )
