"""Manifest: registry of capabilities; single source of operator schema serialization."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from junta.capability.capability import Capability


class Manifest(BaseModel):
    """Manifest holds capabilities and serializes them for each operator."""

    capabilities: dict[str, Capability] = Field(default_factory=dict)

    def register(self, capability: Capability) -> Manifest:
        """Register a capability by name; returns self for chaining."""
        self.capabilities[capability.name] = capability
        return self

    def get(self, name: str) -> Capability:
        """Return a capability by name."""
        if name not in self.capabilities:
            msg = f"unknown capability: {name!r}"
            raise KeyError(msg)
        return self.capabilities[name]

    def to_operator_schema(self, operator: str) -> list[dict[str, Any]]:
        """Serialize capabilities to the operator's expected schema (single source of truth).

        ``operator`` is one of: ``anthropic``, ``openai``, ``llama`` (OpenAI-compatible).
        """
        op = operator.lower().strip()
        if op == "anthropic":
            return [self._anthropic_tool(c) for c in self.capabilities.values()]
        if op in ("openai", "llama"):
            return [self._openai_function(c) for c in self.capabilities.values()]
        msg = f"unknown operator for schema: {operator!r}"
        raise ValueError(msg)

    def _anthropic_tool(self, cap: Capability) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for p in cap.params:
            properties[p.name] = {
                "type": self._json_schema_type(p.type),
                "description": p.description,
            }
            if p.required:
                required.append(p.name)
        return {
            "name": cap.name,
            "description": cap.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _openai_function(self, cap: Capability) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for p in cap.params:
            properties[p.name] = {
                "type": self._json_schema_type(p.type),
                "description": p.description,
            }
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": cap.name,
                "description": cap.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    @staticmethod
    def _json_schema_type(t: str) -> str:
        mapping = {
            "str": "string",
            "string": "string",
            "int": "integer",
            "integer": "integer",
            "float": "number",
            "number": "number",
            "bool": "boolean",
            "boolean": "boolean",
            "object": "object",
            "array": "array",
        }
        return mapping.get(t.lower(), "string")
