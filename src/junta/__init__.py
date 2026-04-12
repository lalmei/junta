"""Junta: officer framework with operators, manifest, doctrine, and tribunal."""

from __future__ import annotations

from junta._version import debug_info, get_version
from junta.briefing import BriefingBuilder
from junta.cabinet import Analyst, Coordinator, Executor, Officer, Planner, Reviewer
from junta.cli import cli
from junta.cli.main_cli import main
from junta.config import Config, JuntaEnvSettings
from junta.dispatch import Dispatch, DispatchRole, FieldReport
from junta.doctrine.doctrine import Doctrine
from junta.dossier import Dossier
from junta.event import Event, EventType
from junta.intelligence import Intelligence
from junta.junta import Junta
from junta.mandate import Mandate, MandateStatus
from junta.manifest import Manifest
from junta.operators import (
    AnthropicOperator,
    CapabilityInvocation,
    LlamaOperator,
    OpenAIOperator,
    Operator,
    OperatorTurn,
)
from junta.tribunal import (
    Breach,
    CapabilityBreach,
    Contingency,
    DoctrineViolation,
    Intercept,
    OperatorFailure,
    Ruling,
    Tribunal,
    TribunalRejection,
    Verdict,
    Wiretap,
    WiretapChannel,
    WiretapLevel,
)

__all__: list[str] = [
    "Analyst",
    "AnthropicOperator",
    "Breach",
    "BriefingBuilder",
    "CapabilityBreach",
    "CapabilityInvocation",
    "Config",
    "Contingency",
    "Coordinator",
    "Dispatch",
    "DispatchRole",
    "Doctrine",
    "DoctrineViolation",
    "Dossier",
    "Event",
    "EventType",
    "Executor",
    "FieldReport",
    "Intelligence",
    "Intercept",
    "Junta",
    "JuntaEnvSettings",
    "LlamaOperator",
    "Mandate",
    "MandateStatus",
    "Manifest",
    "Officer",
    "OpenAIOperator",
    "Operator",
    "OperatorFailure",
    "OperatorTurn",
    "Planner",
    "Reviewer",
    "Ruling",
    "Tribunal",
    "TribunalRejection",
    "Verdict",
    "Wiretap",
    "WiretapChannel",
    "WiretapLevel",
    "cli",
    "debug_info",
    "get_version",
    "main",
]
