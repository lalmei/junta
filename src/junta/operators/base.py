"""Abstract operator (LLM provider) base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from junta.doctrine.doctrine import Doctrine
from junta.operators.types import OperatorTurn


class Operator(ABC):
    """Operator: abstracts an LLM backend (Anthropic, OpenAI, Llama server)."""

    name: str

    @abstractmethod
    def complete(
        self,
        messages: list[dict],
        capabilities: list[dict],
        doctrine: Doctrine,
    ) -> OperatorTurn:
        """Return one completion turn, possibly requesting capability invocations."""

    @abstractmethod
    def stream(
        self,
        messages: list[dict],
        capabilities: list[dict],
        doctrine: Doctrine,
        callback: Callable[[str], None],
    ) -> None:
        """Stream assistant text chunks to callback (capability invocations may be empty)."""
