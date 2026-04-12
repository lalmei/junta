"""Framework Config (not environment settings)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from junta.doctrine.doctrine import Doctrine
from junta.tribunal.wiretap import WiretapLevel


class Config(BaseModel):
    """Junta-wide defaults: default operator, wiretap, tribunal, and doctrine."""

    version: str = "0.1.0"
    default_operator: str = "anthropic"
    wiretap_level: WiretapLevel = WiretapLevel.MONITOR
    tribunal_enabled: bool = False
    default_doctrine: Doctrine = Field(default_factory=Doctrine)
