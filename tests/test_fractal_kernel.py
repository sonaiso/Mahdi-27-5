"""Tests for the Fractal Kernel core types and enums.

Invariants tested
-----------------
1. All new enums have expected members.
2. All new frozen dataclasses can be instantiated with defaults.
3. HypothesisNode.get() works correctly.
4. Payload is stored as tuple-of-pairs (hashable / frozen).
5. Kernel runtime state composes three sub-states.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    ActivationStage,
    ConflictState,
    ConstraintStrength,
    HypothesisStatus,
    RevisionType,
    SignalType,
)
from arabic_engine.core.trace import (
    DecisionState,
    HypothesisState,
    KernelRuntimeState,
    SignalState,
)
from arabic_engine.core.types import (
    ActivationRecord,
    ConflictEdge,
    ConstraintEdge,
    DecisionTrace,
    HypothesisNode,
    SignalUnit,
    SupportEdge,
    UnicodeAtom,
)

# ═══════════════════════════════════════════════════════════════════════
# Enum completeness
# ═══════════════════════════════════════════════════════════════════════


class TestEnumCompleteness:
    """All new enums have the expected members."""

    def test_hypothesis_status_members(self):
        assert len(HypothesisStatus) == 5
        assert HypothesisStatus.ACTIVE.name == "ACTIVE"
        assert HypothesisStatus.PRUNED.name == "PRUNED"
        assert HypothesisStatus.STABILIZED.name == "STABILIZED"
        assert HypothesisStatus.SUSPENDED.name == "SUSPENDED"
        assert HypothesisStatus.REVISED.name == "REVISED"

    def test_constraint_strength_members(self):
        assert len(ConstraintStrength) == 5
        assert ConstraintStrength.ABSOLUTE.name == "ABSOLUTE"
        assert ConstraintStrength.TENTATIVE.name == "TENTATIVE"

    def test_conflict_state_members(self):
        assert len(ConflictState) == 4
        assert ConflictState.NONE.name == "NONE"
        assert ConflictState.UNRESOLVED.name == "UNRESOLVED"

    def test_revision_type_members(self):
        assert len(RevisionType) == 5
        assert RevisionType.CONFLICT_RESOLUTION.name == "CONFLICT_RESOLUTION"
        assert RevisionType.EXTERNAL_EVIDENCE.name == "EXTERNAL_EVIDENCE"

    def test_signal_type_members(self):
        assert len(SignalType) == 6
        assert SignalType.BASE_LETTER.name == "BASE_LETTER"
        assert SignalType.DIACRITIC.name == "DIACRITIC"

    def test_activation_stage_members(self):
        assert len(ActivationStage) == 9
        assert ActivationStage.SIGNAL.name == "SIGNAL"
        assert ActivationStage.JUDGEMENT.name == "JUDGEMENT"


# ═══════════════════════════════════════════════════════════════════════
# Frozen dataclass instantiation
# ═══════════════════════════════════════════════════════════════════════


class TestDataclassInstantiation:
    """All frozen dataclasses can be instantiated with required fields only."""

    def test_unicode_atom(self):
        a = UnicodeAtom(
            atom_id="A_0", char="ك", codepoint=0x0643,
            unicode_category="Lo", combining_class=0, position_index=0,
        )
        assert a.char == "ك"
        assert a.signal_type == SignalType.UNKNOWN  # default

    def test_signal_unit(self):
        u = SignalUnit(
            unit_id="SU_0", surface_text="كتب",
            normalized_text="كتب", source_span=(0, 3),
        )
        assert u.signal_type == SignalType.BASE_LETTER

    def test_hypothesis_node_defaults(self):
        h = HypothesisNode(
            node_id="H_0", hypothesis_type="test",
            stage=ActivationStage.SIGNAL,
        )
        assert h.source_refs == ()
        assert h.payload == ()
        assert h.confidence == 1.0
        assert h.status == HypothesisStatus.ACTIVE

    def test_constraint_edge(self):
        e = ConstraintEdge(
            edge_id="CE_0", source_ref="A", target_ref="B",
            relation="restricts",
        )
        assert e.strength == ConstraintStrength.MODERATE
        assert e.justification == ""

    def test_support_edge(self):
        e = SupportEdge(
            edge_id="SE_0", supporter_ref="A", target_ref="B",
        )
        assert e.weight == 1.0

    def test_conflict_edge(self):
        e = ConflictEdge(
            edge_id="CF_0", node_a_ref="A", node_b_ref="B",
        )
        assert e.conflict_state == ConflictState.HARD

    def test_activation_record(self):
        r = ActivationRecord(
            record_id="AR_0", node_ref="H_0",
            old_status=HypothesisStatus.ACTIVE,
            new_status=HypothesisStatus.STABILIZED,
        )
        assert r.revision_type is None

    def test_decision_trace(self):
        t = DecisionTrace(
            trace_id="DT_0", stage=ActivationStage.MORPHOLOGY,
            decision_type="pruning",
        )
        assert t.input_refs == ()
        assert t.confidence == 1.0


# ═══════════════════════════════════════════════════════════════════════
# HypothesisNode.get()
# ═══════════════════════════════════════════════════════════════════════


class TestHypothesisNodeGet:
    """HypothesisNode.get() works like dict.get() on the payload."""

    def test_get_existing_key(self):
        h = HypothesisNode(
            node_id="H_1", hypothesis_type="morphology",
            stage=ActivationStage.MORPHOLOGY,
            payload=(("lemma", "كتب"), ("root", ("ك", "ت", "ب"))),
        )
        assert h.get("lemma") == "كتب"
        assert h.get("root") == ("ك", "ت", "ب")

    def test_get_missing_key_default(self):
        h = HypothesisNode(
            node_id="H_2", hypothesis_type="test",
            stage=ActivationStage.SIGNAL,
        )
        assert h.get("nonexistent") is None
        assert h.get("nonexistent", "fallback") == "fallback"


# ═══════════════════════════════════════════════════════════════════════
# Frozen immutability
# ═══════════════════════════════════════════════════════════════════════


class TestFrozenImmutability:
    """Frozen dataclasses cannot be mutated."""

    def test_hypothesis_node_is_frozen(self):
        h = HypothesisNode(
            node_id="H_0", hypothesis_type="test",
            stage=ActivationStage.SIGNAL,
        )
        with pytest.raises(AttributeError):
            h.confidence = 0.5  # type: ignore[misc]

    def test_unicode_atom_is_frozen(self):
        a = UnicodeAtom(
            atom_id="A_0", char="x", codepoint=120,
            unicode_category="Ll", combining_class=0, position_index=0,
        )
        with pytest.raises(AttributeError):
            a.char = "y"  # type: ignore[misc]

    def test_decision_trace_is_frozen(self):
        t = DecisionTrace(
            trace_id="DT_0", stage=ActivationStage.SIGNAL,
            decision_type="test",
        )
        with pytest.raises(AttributeError):
            t.justification = "changed"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# Kernel runtime state
# ═══════════════════════════════════════════════════════════════════════


class TestKernelRuntimeState:
    """KernelRuntimeState composes three sub-states correctly."""

    def test_default_construction(self):
        state = KernelRuntimeState()
        assert state.input_text == ""
        assert isinstance(state.signal, SignalState)
        assert isinstance(state.hypotheses, HypothesisState)
        assert isinstance(state.decisions, DecisionState)

    def test_signal_state_defaults(self):
        s = SignalState()
        assert s.atoms == []
        assert s.signal_units == []

    def test_hypothesis_state_add_and_retrieve(self):
        hs = HypothesisState()
        h = HypothesisNode(
            node_id="H_X", hypothesis_type="test",
            stage=ActivationStage.MORPHOLOGY,
        )
        hs.add_hypothesis(h)
        assert len(hs.all_hypotheses()) == 1
        assert hs.active_hypotheses(ActivationStage.MORPHOLOGY) == [h]
        assert hs.active_hypotheses(ActivationStage.CONCEPT) == []

    def test_decision_state_defaults(self):
        d = DecisionState()
        assert d.activated == []
        assert d.suspended == []
        assert d.trace == []
        assert d.judgement is None


# ═══════════════════════════════════════════════════════════════════════
# Re-exports
# ═══════════════════════════════════════════════════════════════════════


class TestReExports:
    """New symbols are accessible from arabic_engine.core."""

    def test_enums_re_exported(self):
        import arabic_engine.core as core
        for name in [
            "ActivationStage", "ConflictState", "ConstraintStrength",
            "HypothesisStatus", "RevisionType", "SignalType",
        ]:
            assert hasattr(core, name), f"{name} not re-exported"

    def test_types_re_exported(self):
        import arabic_engine.core as core
        for name in [
            "ActivationRecord", "ConflictEdge", "ConstraintEdge",
            "DecisionTrace", "HypothesisNode", "SignalUnit",
            "SupportEdge", "UnicodeAtom",
        ]:
            assert hasattr(core, name), f"{name} not re-exported"

    def test_trace_re_exported(self):
        import arabic_engine.core as core
        for name in [
            "DecisionState", "HypothesisState",
            "KernelRuntimeState", "SignalState",
        ]:
            assert hasattr(core, name), f"{name} not re-exported"
