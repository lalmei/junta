"""junta package.

Python library with a Typer command-line interface
"""

from __future__ import annotations

from junta._version import debug_info, get_version
from junta.cabinet.officer import Officer
from junta.cli import cli
from junta.cli.main_cli import main
from junta.junta import Junta
from junta.operation import (
    Complete,
    Condition,
    Continue,
    Doctrine,
    Dossier,
    Fail,
    FailurePolicy,
    Handoff,
    Mandate,
    Operation,
    RetryPolicy,
    RunResult,
    StepOutcome,
    Tracer,
    Tribunal,
)

__all__: list[str] = [
    "Complete",
    "Condition",
    "Continue",
    "Doctrine",
    "Dossier",
    "Fail",
    "FailurePolicy",
    "Handoff",
    "Junta",
    "Mandate",
    "Officer",
    "Operation",
    "RetryPolicy",
    "RunResult",
    "StepOutcome",
    "Tracer",
    "Tribunal",
    "cli",
    "debug_info",
    "get_version",
    "main",
]
