"""Tests for Mandate, Dossier, and Doctrine."""

from __future__ import annotations

import pytest

from junta import Dispatch, DispatchRole, Doctrine, Dossier, Mandate


def test_dossier_add_dispatch() -> None:
    d = Dossier()
    d.add(Dispatch(role=DispatchRole.USER, content="briefing text"))
    assert len(d.dispatches) == 1
    assert d.dispatches[0].content == "briefing text"


def test_mandate_minimal() -> None:
    m = Mandate(id="m1", briefing="Go")
    assert m.briefing == "Go"


def test_mandate_briefing_non_empty() -> None:
    with pytest.raises(ValueError, match="briefing"):
        Mandate(id="m2", briefing="   ")


def test_doctrine_defaults() -> None:
    d = Doctrine()
    assert d.max_iterations == 10
    assert d.allow_parallel is False
    assert d.max_tokens == 4096
