"""Planner officer: decomposes mandates into sub-mandates."""

from __future__ import annotations

import json

from pydantic import Field

from junta.cabinet.officer import Officer
from junta.capability.capability import Capability, CapabilityParam
from junta.intelligence.intelligence import Intelligence
from junta.manifest.manifest import Manifest


def _sub_mandates_stub(goal: str) -> str:
    payload = [{"briefing": f"Sub-mandate A for: {goal[:80]}"}, {"briefing": f"Sub-mandate B for: {goal[:80]}"}]
    return json.dumps(payload)


def _planner_manifest() -> Manifest:
    m = Manifest()
    m.register(
        Capability(
            name="plan_steps",
            description="Emit a JSON list of sub-mandate briefing strings.",
            params=[
                CapabilityParam(
                    name="goal",
                    type="str",
                    description="High-level goal to decompose.",
                    required=True,
                ),
            ],
            handler=_sub_mandates_stub,
        ),
    )
    return m


class Planner(Officer):
    """Planning officer that breaks work into ordered sub-mandates."""

    intelligence: Intelligence = Field(
        default_factory=lambda: Intelligence(
            system_briefing=(
                "You are a planning officer. Decompose mandates into clear sub-mandates "
                "and use plan_steps when structured output is required."
            ),
        ),
    )
    manifest: Manifest = Field(default_factory=_planner_manifest)
