"""Breach hierarchy: Junta-specific exceptions (never generic Exception at boundaries)."""

from __future__ import annotations


class Breach(Exception):  # noqa: N818
    """Base class for all Junta execution failures."""

    def __init__(self, message: str) -> None:
        """Store the breach message for callers and wiretap output."""
        super().__init__(message)
        self.message = message


class CapabilityBreach(Breach):
    """Raised when a capability handler fails or returns an invalid outcome."""


class DoctrineViolation(Breach):
    """Raised when an officer exceeds doctrine limits (iterations, tokens, policy)."""


class OperatorFailure(Breach):
    """Raised when an operator (LLM) call fails."""


class TribunalRejection(Breach):
    """Raised when the tribunal rejects output or cannot produce a ruling."""
