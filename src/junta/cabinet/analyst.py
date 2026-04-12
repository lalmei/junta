"""Analyst officer: research and reasoning."""

from __future__ import annotations

from pydantic import Field

from junta.cabinet.officer import Officer
from junta.capability.capability import Capability, CapabilityParam
from junta.intelligence.intelligence import Intelligence
from junta.manifest.manifest import Manifest


def _web_search_stub(query: str) -> str:
    return f"[web_search stub] query={query!r}"


_SUMMARY_MAX_CHARS = 400


def _summarize_stub(text: str) -> str:
    return text[:_SUMMARY_MAX_CHARS] if len(text) > _SUMMARY_MAX_CHARS else text


def _analyst_manifest() -> Manifest:
    m = Manifest()
    m.register(
        Capability(
            name="web_search",
            description="Retrieve information relevant to a query.",
            params=[
                CapabilityParam(
                    name="query",
                    type="str",
                    description="Search query text.",
                    required=True,
                ),
            ],
            handler=_web_search_stub,
        ),
    )
    m.register(
        Capability(
            name="summarize",
            description="Summarize a body of text.",
            params=[
                CapabilityParam(
                    name="text",
                    type="str",
                    description="Text to summarize.",
                    required=True,
                ),
            ],
            handler=_summarize_stub,
        ),
    )
    return m


class Analyst(Officer):
    """Analytical officer with web_search and summarize capabilities."""

    intelligence: Intelligence = Field(
        default_factory=lambda: Intelligence(
            system_briefing=(
                "You are an analytical officer. Reason carefully and use capabilities "
                "when you need external facts or condensed text."
            ),
        ),
    )
    manifest: Manifest = Field(default_factory=_analyst_manifest)
