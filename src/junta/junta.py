"""Junta: top-level orchestrator (registers operators and officers, issues mandates)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from junta.cabinet.officer import Officer
from junta.config.config import Config
from junta.doctrine.doctrine import Doctrine
from junta.event.event import Event, EventType
from junta.mandate.mandate import Mandate
from junta.manifest.manifest import Manifest
from junta.operators.base import Operator
from junta.tribunal.contingency import Contingency
from junta.tribunal.ruling import Ruling
from junta.tribunal.tribunal import Tribunal
from junta.tribunal.wiretap import Wiretap, WiretapLevel


def _merge_manifests(base: Manifest, officer_manifest: Manifest) -> Manifest:
    """Officer capabilities override Junta capabilities on name collision."""
    out = Manifest()
    for _name, cap in base.capabilities.items():
        out.register(cap)
    for _name, cap in officer_manifest.capabilities.items():
        out.register(cap)
    return out


class Junta(BaseModel):
    """Junta registers operators (LLM backends), officers, and optional tribunal."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: Config = Field(default_factory=Config)
    manifest: Manifest = Field(default_factory=Manifest)
    doctrine: Doctrine = Field(default_factory=Doctrine)
    contingency: Contingency = Field(default_factory=Contingency)
    wiretap: Wiretap = Field(default_factory=Wiretap)
    tribunal: Tribunal | None = None
    cabinet: dict[str, Officer] = Field(default_factory=dict)
    operators: dict[str, Operator] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)

    @classmethod
    def from_config(cls, config: Config) -> Junta:
        """Build Junta from framework Config (wiretap level, default doctrine, tribunal flag)."""
        wt = Wiretap(level=config.wiretap_level)
        tribunal: Tribunal | None = Tribunal() if config.tribunal_enabled else None
        return cls(
            config=config,
            doctrine=config.default_doctrine,
            wiretap=wt,
            tribunal=tribunal,
        )

    def conscript(self, operator: Operator) -> None:
        """Register an operator by name for later deployment to officers."""
        self.operators[operator.name] = operator
        self.wiretap.log(
            WiretapLevel.MONITOR,
            "operator_conscripted",
            {"operator": operator.name},
        )

    def deploy(self, officer: Officer) -> None:
        """Register an officer under its codename; inject defaults from Junta."""
        key = officer.codename
        self.cabinet[key] = officer
        if officer.operator is None:
            dname = self.config.default_operator
            if dname in self.operators:
                officer.operator = self.operators[dname]
        officer.manifest = _merge_manifests(self.manifest, officer.manifest)
        if officer.wiretap is None:
            officer.wiretap = self.wiretap
        self.wiretap.log(
            WiretapLevel.MONITOR,
            "officer_deployed",
            {"codename": key, "officer_id": officer.id},
        )

    def issue(self, mandate: Mandate, to: str) -> Ruling:
        """Issue a mandate to one officer by codename; run tribunal when enabled."""
        officer = self.cabinet[to]
        self.wiretap.log(
            WiretapLevel.MONITOR,
            "mandate_issue",
            {"mandate_id": mandate.id, "to": to},
        )
        result = officer.execute_mandate(mandate)
        for ev in officer.events:
            self.events.append(ev)
        tribunal = (
            (self.tribunal or Tribunal(operator=None)) if self.config.tribunal_enabled else Tribunal(operator=None)
        )
        ruling = tribunal.evaluate(mandate, result)
        self.events.append(
            Event(type=EventType.RULING_ISSUED, officer_id=officer.id, payload={"mandate_id": mandate.id}),
        )
        self.wiretap.log(
            WiretapLevel.MONITOR,
            "ruling_issued",
            {"mandate_id": mandate.id, "verdict": ruling.verdict.value},
        )
        return ruling

    def broadcast(self, mandate: Mandate) -> dict[str, Ruling]:
        """Issue the same briefing to every officer in the cabinet (fresh mandate ids)."""
        out: dict[str, Ruling] = {}
        for key in self.cabinet:
            m = mandate.model_copy(
                update={"id": f"{mandate.id}-{key}-{uuid.uuid4().hex[:8]}"},
                deep=True,
            )
            out[key] = self.issue(m, to=key)
        return out
