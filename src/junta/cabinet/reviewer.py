"""Reviewer officer: evaluates other officers' output."""

from __future__ import annotations

import json

from pydantic import Field

from junta.cabinet.officer import Officer
from junta.capability.capability import Capability, CapabilityParam
from junta.intelligence.intelligence import Intelligence
from junta.manifest.manifest import Manifest


def _review_stub(draft: str, criteria: str) -> str:
    return json.dumps({"ok": len(draft) > 0, "criteria": criteria})


def _reviewer_manifest() -> Manifest:
    m = Manifest()
    m.register(
        Capability(
            name="review_draft",
            description="Structured review of a draft against criteria.",
            params=[
                CapabilityParam(name="draft", type="str", description="Draft text.", required=True),
                CapabilityParam(
                    name="criteria",
                    type="str",
                    description="Acceptance criteria.",
                    required=True,
                ),
            ],
            handler=_review_stub,
        ),
    )
    return m


class Reviewer(Officer):
    """Review officer that critiques prior work against criteria."""

    intelligence: Intelligence = Field(
        default_factory=lambda: Intelligence(
            system_briefing=("You are a review officer. Assess clarity, correctness, and doctrine fit."),
        ),
    )
    manifest: Manifest = Field(default_factory=_reviewer_manifest)
