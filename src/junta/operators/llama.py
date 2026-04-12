"""Llama operator: OpenAI-compatible HTTP server (llama.cpp)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx

from junta.dispatch import Dispatch, DispatchRole
from junta.doctrine.doctrine import Doctrine
from junta.operators.base import Operator
from junta.operators.types import CapabilityInvocation, OperatorTurn
from junta.tribunal.breach import OperatorFailure


class LlamaOperator(Operator):
    """Operator calling a local or remote OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080/v1",
        model: str = "llama",
        timeout: float = 120.0,
    ) -> None:
        """Point at an OpenAI-compatible server's ``base_url`` (e.g. llama.cpp)."""
        self.name = "llama"
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def complete(
        self,
        messages: list[dict[str, Any]],
        capabilities: list[dict[str, Any]],
        doctrine: Doctrine,
    ) -> OperatorTurn:
        """POST JSON to ``/chat/completions`` and parse the response body."""
        url = f"{self._base_url}/chat/completions"
        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_tokens": doctrine.max_tokens,
            "temperature": doctrine.temperature,
        }
        if capabilities:
            body["tools"] = capabilities
            body["tool_choice"] = "auto"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                r = client.post(url, json=body)
                r.raise_for_status()
                data = r.json()
        except Exception as exc:
            raise OperatorFailure(f"llama http completion failed: {exc}") from exc
        return _openai_style_response_to_turn(data)

    def stream(
        self,
        messages: list[dict[str, Any]],
        capabilities: list[dict[str, Any]],
        doctrine: Doctrine,
        callback: Callable[[str], None],
    ) -> None:
        """Stream SSE chunks from an OpenAI-compatible server."""
        url = f"{self._base_url}/chat/completions"
        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_tokens": doctrine.max_tokens,
            "temperature": doctrine.temperature,
            "stream": True,
        }
        if capabilities:
            body["tools"] = capabilities
            body["tool_choice"] = "auto"
        try:
            with httpx.Client(timeout=self._timeout) as client, client.stream("POST", url, json=body) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    payload = line.removeprefix("data: ").strip()
                    if payload == "[DONE]":
                        break
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0].get("delta") or {}
                    piece = delta.get("content")
                    if piece:
                        callback(piece)
        except Exception as exc:
            raise OperatorFailure(f"llama http stream failed: {exc}") from exc


def _openai_style_response_to_turn(data: dict[str, Any]) -> OperatorTurn:
    choice = data["choices"][0]
    msg = choice["message"]
    text = (msg.get("content") or "").strip()
    invocations: list[CapabilityInvocation] = []
    tool_calls = msg.get("tool_calls") or []
    for tc in tool_calls:
        fn = tc["function"]
        raw = fn.get("arguments") or "{}"
        try:
            args = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except json.JSONDecodeError:
            args = {}
        invocations.append(
            CapabilityInvocation(
                name=fn["name"],
                arguments=args,
                openai_tool_call_id=tc.get("id"),
            ),
        )
    dispatch = Dispatch(role=DispatchRole.OFFICER, content=text or "(no text)")
    assistant_msg: dict[str, Any] = {"role": "assistant", "content": msg.get("content")}
    if tool_calls:
        assistant_msg["tool_calls"] = tool_calls
    return OperatorTurn(
        dispatch=dispatch,
        capability_invocations=invocations,
        continuation_assistant_message=assistant_msg,
    )
