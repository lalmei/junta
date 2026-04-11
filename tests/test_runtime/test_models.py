"""Tests for Mandate, Dossier, and Doctrine."""

from __future__ import annotations

import pytest

from junta import Doctrine, Dossier, FailurePolicy, Mandate, RetryPolicy


def test_dossier_from_briefing_copies_facts() -> None:
    briefing = {"company": "Acme", "region": "EMEA"}
    d = Dossier.from_briefing(briefing)
    assert d.facts == briefing
    briefing["company"] = "Other"
    assert d.facts["company"] == "Acme"


def test_mandate_minimal() -> None:
    m = Mandate(directive="Go")
    assert m.briefing == {}
    assert m.doctrine_refs == []


def test_mandate_directive_non_empty() -> None:
    with pytest.raises(ValueError, match="directive"):
        Mandate(directive="   ")


def test_doctrine_defaults() -> None:
    d = Doctrine()
    assert d.max_steps == 100
    assert d.failure_policy is FailurePolicy.ABORT
    assert d.retry_policy == RetryPolicy()


def test_retry_policy_backoff() -> None:
    r = RetryPolicy(max_attempts=3, backoff_base_seconds=0.01)
    assert r.max_attempts == 3
