"""Dossier: conversation thread with dispatches and field reports."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from junta.dispatch import Dispatch, DispatchRole, FieldReport


class Dossier(BaseModel):
    """A dossier records dispatches and field reports for one mandate thread."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispatches: list[Dispatch] = Field(default_factory=list)
    field_reports: list[FieldReport] = Field(default_factory=list)

    def add(self, dispatch: Dispatch) -> None:
        """Append a dispatch to the dossier."""
        self.dispatches.append(dispatch)

    def add_field_report(self, report: FieldReport) -> None:
        """Append a field report."""
        self.field_reports.append(report)

    def history(self) -> list[dict[str, Any]]:
        """Flatten dispatches and field reports into operator message dicts (chronological)."""
        merged: list[tuple[datetime, str, Dispatch | FieldReport]] = []
        for d in self.dispatches:
            merged.append((d.timestamp, "dispatch", d))
        for fr in self.field_reports:
            merged.append((fr.timestamp, "field_report", fr))
        merged.sort(key=lambda x: x[0])
        out: list[dict[str, Any]] = []
        for _ts, kind, obj in merged:
            if kind == "dispatch":
                if not isinstance(obj, Dispatch):
                    msg = "internal dossier merge: expected Dispatch"
                    raise TypeError(msg)
                role = "assistant" if obj.role == DispatchRole.OFFICER else obj.role.value
                out.append({"role": role, "content": obj.content})
            elif not isinstance(obj, FieldReport):
                msg = "internal dossier merge: expected FieldReport"
                raise TypeError(msg)
            else:
                out.append({"role": "user", "content": _field_report_content(obj)})
        return out


def _field_report_content(fr: FieldReport) -> str:
    return f"[field_report capability={fr.capability!r} args={fr.args!r}]\nresult={fr.result!r}"
