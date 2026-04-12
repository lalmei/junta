"""OpenAI operator (GPT)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from openai import OpenAI

from junta.dispatch import Dispatch, DispatchRole
from junta.doctrine.doctrine import Doctrine
from junta.operators.base import Operator
from junta.operators.types import CapabilityInvocation, OperatorTurn
from junta.tribunal.breach import OperatorFailure


class OpenAIOperator(Operator):
    """Operator using OpenAI Chat Completions (gpt-4o)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
    ) -> None:
        """Create an OpenAI client for chat completions."""
        self.name = "openai"
        self._model = model
        self._client = OpenAI(api_key=api_key)

    def complete(
        self,
        messages: list[dict[str, Any]],
        capabilities: list[dict[str, Any]],
        doctrine: Doctrine,
    ) -> OperatorTurn:
        """Run one chat completion and parse tool calls into capability invocations."""
        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "max_tokens": doctrine.max_tokens,
                "temperature": doctrine.temperature,
            }
            if capabilities:
                kwargs["tools"] = capabilities
                kwargs["tool_choice"] = "auto"
            resp = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            raise OperatorFailure(f"openai chat.completions failed: {exc}") from exc
        return _choice_to_turn(resp)

    def stream(
        self,
        messages: list[dict[str, Any]],
        capabilities: list[dict[str, Any]],
        doctrine: Doctrine,
        callback: Callable[[str], None],
    ) -> None:
        """Stream chat completion deltas to the callback."""
        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "max_tokens": doctrine.max_tokens,
                "temperature": doctrine.temperature,
                "stream": True,
            }
            if capabilities:
                kwargs["tools"] = capabilities
                kwargs["tool_choice"] = "auto"
            stream = self._client.chat.completions.create(**kwargs)
            for chunk in stream:
                ch = chunk.choices[0]
                if ch.delta and ch.delta.content:
                    callback(ch.delta.content)
        except Exception as exc:
            raise OperatorFailure(f"openai stream failed: {exc}") from exc


def _choice_to_turn(resp: Any) -> OperatorTurn:
    choice = resp.choices[0]
    msg = choice.message
    text = (msg.content or "").strip()
    invocations: list[CapabilityInvocation] = []
    tool_calls = getattr(msg, "tool_calls", None) or []
    for tc in tool_calls:
        fn = tc.function
        raw = fn.arguments or "{}"
        try:
            args = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except json.JSONDecodeError:
            args = {}
        invocations.append(
            CapabilityInvocation(
                name=fn.name,
                arguments=args,
                openai_tool_call_id=tc.id,
            ),
        )
    dispatch = Dispatch(role=DispatchRole.OFFICER, content=text or "(no text)")
    assistant_msg: dict[str, Any] = {
        "role": "assistant",
        "content": msg.content,
    }
    if tool_calls:
        assistant_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments or "{}",
                },
            }
            for tc in tool_calls
        ]
    return OperatorTurn(
        dispatch=dispatch,
        capability_invocations=invocations,
        continuation_assistant_message=assistant_msg,
    )
