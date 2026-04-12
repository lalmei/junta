"""Executor officer: capability-heavy execution."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from junta.cabinet.officer import Officer
from junta.capability.capability import Capability, CapabilityParam
from junta.intelligence.intelligence import Intelligence
from junta.manifest.manifest import Manifest


def _shell_stub(command: str) -> str:
    return f"[shell stub] would run: {command!r}"


def _file_read_stub(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        return f"[file_read stub] missing: {path}"
    return p.read_text(encoding="utf-8", errors="replace")[:50_000]


def _file_write_stub(path: str, content: str) -> str:
    return f"[file_write stub] would write {len(content)} chars to {path!r}"


def _executor_manifest() -> Manifest:
    m = Manifest()
    m.register(
        Capability(
            name="shell",
            description="Run a shell command (stubbed in default executor).",
            params=[
                CapabilityParam(
                    name="command",
                    type="str",
                    description="Command line to execute.",
                    required=True,
                ),
            ],
            handler=_shell_stub,
        ),
    )
    m.register(
        Capability(
            name="file_read",
            description="Read a file from disk.",
            params=[
                CapabilityParam(
                    name="path",
                    type="str",
                    description="Filesystem path.",
                    required=True,
                ),
            ],
            handler=_file_read_stub,
        ),
    )
    m.register(
        Capability(
            name="file_write",
            description="Write content to a file (stubbed).",
            params=[
                CapabilityParam(name="path", type="str", description="Path.", required=True),
                CapabilityParam(name="content", type="str", description="Content.", required=True),
            ],
            handler=_file_write_stub,
        ),
    )
    return m


class Executor(Officer):
    """Execution officer oriented toward shell and filesystem capabilities."""

    intelligence: Intelligence = Field(
        default_factory=lambda: Intelligence(
            system_briefing=(
                "You are an execution officer. Prefer capabilities for concrete actions "
                "on the host when doctrine allows."
            ),
        ),
    )
    manifest: Manifest = Field(default_factory=_executor_manifest)
