"""Tests for arabic_engine/core/trace.py — state containers."""

from __future__ import annotations

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.trace import (
    DecisionState,
    HypothesisState,
    KernelRuntimeState,
    SignalState,
)
from arabic_engine.core.types import HypothesisNode, SignalUnit, UnicodeAtom


def _make_atom(char: str = "ك", codepoint: int = 1603) -> UnicodeAtom:
    return UnicodeAtom(
        atom_id="a1",
        char=char,
        codepoint=codepoint,
        unicode_category="Lo",
        combining_class=0,
        position_index=0,
    )


def _make_signal_unit(unit_id: str = "s1", surface: str = "كتب") -> SignalUnit:
    return SignalUnit(
        unit_id=unit_id,
        surface_text=surface,
        normalized_text=surface,
        source_span=(0, len(surface)),
    )


def _make_hypothesis(
    node_id: str = "h1",
    stage: ActivationStage = ActivationStage.SIGNAL,
    status: HypothesisStatus = HypothesisStatus.ACTIVE,
) -> HypothesisNode:
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="test",
        stage=stage,
        confidence=0.9,
        status=status,
    )


# ── SignalState ─────────────────────────────────────────────────────


def test_signal_state_default_empty():
    s = SignalState()
    assert s.atoms == []
    assert s.signal_units == []


def test_signal_state_with_atoms():
    atom = _make_atom()
    s = SignalState(atoms=[atom])
    assert len(s.atoms) == 1
    assert s.atoms[0].char == "ك"


def test_signal_state_with_signal_units():
    su = _make_signal_unit()
    s = SignalState(signal_units=[su])
    assert len(s.signal_units) == 1
    assert s.signal_units[0].surface_text == "كتب"


# ── HypothesisState ────────────────────────────────────────────────


def test_hypothesis_state_default_empty():
    hs = HypothesisState()
    assert hs.hypotheses == {}
    assert hs.constraint_edges == []
    assert hs.support_edges == []
    assert hs.conflict_edges == []


def test_add_hypothesis():
    hs = HypothesisState()
    node = _make_hypothesis(stage=ActivationStage.SIGNAL)
    hs.add_hypothesis(node)
    assert ActivationStage.SIGNAL in hs.hypotheses
    assert hs.hypotheses[ActivationStage.SIGNAL] == [node]


def test_add_hypothesis_multiple_stages():
    hs = HypothesisState()
    n1 = _make_hypothesis(node_id="h1", stage=ActivationStage.SIGNAL)
    n2 = _make_hypothesis(node_id="h2", stage=ActivationStage.CONCEPT)
    hs.add_hypothesis(n1)
    hs.add_hypothesis(n2)
    assert len(hs.hypotheses[ActivationStage.SIGNAL]) == 1
    assert len(hs.hypotheses[ActivationStage.CONCEPT]) == 1


def test_all_hypotheses():
    hs = HypothesisState()
    n1 = _make_hypothesis(node_id="h1", stage=ActivationStage.SIGNAL)
    n2 = _make_hypothesis(node_id="h2", stage=ActivationStage.CONCEPT)
    hs.add_hypothesis(n1)
    hs.add_hypothesis(n2)
    assert len(hs.all_hypotheses()) == 2


def test_active_hypotheses_all():
    hs = HypothesisState()
    hs.add_hypothesis(_make_hypothesis(node_id="h1"))
    hs.add_hypothesis(_make_hypothesis(node_id="h2"))
    assert len(hs.active_hypotheses()) == 2


def test_active_hypotheses_by_stage():
    hs = HypothesisState()
    hs.add_hypothesis(_make_hypothesis(node_id="h1", stage=ActivationStage.SIGNAL))
    hs.add_hypothesis(_make_hypothesis(node_id="h2", stage=ActivationStage.CONCEPT))
    result = hs.active_hypotheses(stage=ActivationStage.SIGNAL)
    assert len(result) == 1
    assert result[0].node_id == "h1"


def test_active_hypotheses_excludes_pruned():
    hs = HypothesisState()
    hs.add_hypothesis(_make_hypothesis(node_id="h1", status=HypothesisStatus.ACTIVE))
    hs.add_hypothesis(_make_hypothesis(node_id="h2", status=HypothesisStatus.PRUNED))
    result = hs.active_hypotheses()
    assert len(result) == 1
    assert result[0].node_id == "h1"


# ── DecisionState ──────────────────────────────────────────────────


def test_decision_state_default_empty():
    ds = DecisionState()
    assert ds.activated == []
    assert ds.suspended == []
    assert ds.activation_log == []
    assert ds.trace == []
    assert ds.judgement is None


def test_decision_state_with_activated():
    ds = DecisionState()
    node = _make_hypothesis()
    ds.activated.append(node)
    assert len(ds.activated) == 1
    assert ds.activated[0].node_id == "h1"


# ── KernelRuntimeState ─────────────────────────────────────────────


def test_kernel_runtime_state_default():
    krs = KernelRuntimeState()
    assert krs.input_text == ""
    assert krs.iteration == 0


def test_kernel_runtime_state_composes_substates():
    krs = KernelRuntimeState()
    assert isinstance(krs.signal, SignalState)
    assert isinstance(krs.hypotheses, HypothesisState)
    assert isinstance(krs.decisions, DecisionState)


def test_kernel_runtime_state_metadata():
    krs = KernelRuntimeState(metadata={"key": "value"})
    assert krs.metadata["key"] == "value"
