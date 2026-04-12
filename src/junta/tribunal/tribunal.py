"""Tribunal: evaluates mandate results (LLM or heuristic)."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

from junta.doctrine.doctrine import Doctrine
from junta.mandate.mandate import Mandate
from junta.operators.base import Operator
from junta.tribunal.ruling import Ruling, Verdict


class Tribunal(BaseModel):
    """Tribunal scores final officer output against the mandate briefing."""

    model_config = {"arbitrary_types_allowed": True}

    operator: Operator | None = Field(default=None, exclude=True)
    doctrine: Doctrine = Field(default_factory=Doctrine)

    def evaluate(self, mandate: Mandate, result: str) -> Ruling:
        """Return a ruling; uses the operator when set, else a lightweight heuristic."""
        if self.operator is None:
            return _heuristic_ruling(mandate, result)
        return _llm_ruling(self.operator, self.doctrine, mandate, result)


def _heuristic_ruling(mandate: Mandate, result: str) -> Ruling:
    ok = bool(result and result.strip())
    return Ruling(
        mandate_id=mandate.id,
        verdict=Verdict.APPROVED if ok else Verdict.REJECTED,
        score=1.0 if ok else 0.0,
        reasoning="Heuristic: non-empty result approved when no tribunal operator is set.",
        feedback=None,
    )


def _llm_ruling(
    op: Operator,
    doctrine: Doctrine,
    mandate: Mandate,
    result: str,
) -> Ruling:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a tribunal. Respond ONLY with JSON: "
                '{"verdict":"approved"|"rejected"|"retrial","score":0..1,"reasoning":"...",'
                '"feedback":null or string for retrial}'
            ),
        },
        {
            "role": "user",
            "content": f"Mandate briefing:\n{mandate.briefing}\n\nOfficer result:\n{result}\n",
        },
    ]
    turn = op.complete(messages, [], doctrine)
    raw = turn.dispatch.content
    data = _parse_json_payload(raw)
    verdict_s = str(data.get("verdict", "rejected")).lower()
    verdict = Verdict.REJECTED
    if verdict_s == "approved":
        verdict = Verdict.APPROVED
    elif verdict_s == "retrial":
        verdict = Verdict.RETRIAL
    score = float(data.get("score", 0.0))
    score = max(0.0, min(1.0, score))
    return Ruling(
        mandate_id=mandate.id,
        verdict=verdict,
        score=score,
        reasoning=str(data.get("reasoning", "")),
        feedback=data.get("feedback"),
    )


def _parse_json_payload(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {"verdict": "rejected", "score": 0.0, "reasoning": "unparseable tribunal dispatch"}
