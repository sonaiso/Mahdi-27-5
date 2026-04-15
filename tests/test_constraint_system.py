"""Tests for the arabic_engine.constraints sub-modules."""

from __future__ import annotations

from arabic_engine.constraints.propagation import get_constraint_edges, propagate
from arabic_engine.constraints.pruning import DEFAULT_CONFIDENCE_FLOOR, prune
from arabic_engine.constraints.revision import apply_revision, needs_revision
from arabic_engine.constraints.scoring import build_constraint_edges, score_support
from arabic_engine.core.enums import (
    ActivationStage,
    ConflictState,
    ConstraintStrength,
    HypothesisStatus,
)
from arabic_engine.core.types import (
    ConflictEdge,
    ConstraintEdge,
    HypothesisNode,
    SupportEdge,
)

# ── helpers ──────────────────────────────────────────────────────────


def _h(
    node_id: str,
    *,
    stage: ActivationStage = ActivationStage.MORPHOLOGY,
    source_refs: tuple[str, ...] = (),
    payload: tuple[tuple[str, object], ...] = (),
    confidence: float = 1.0,
    status: HypothesisStatus = HypothesisStatus.ACTIVE,
) -> HypothesisNode:
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="test",
        stage=stage,
        source_refs=source_refs,
        payload=payload,
        confidence=confidence,
        status=status,
    )


# ── TestScoring ──────────────────────────────────────────────────────


class TestScoring:
    """Tests for scoring.score_support and scoring.build_constraint_edges."""

    def test_shared_source_creates_support_edges(self):
        h1 = _h("h1", source_refs=("seg1",))
        h2 = _h("h2", source_refs=("seg1",))
        h3 = _h("h3", source_refs=("seg1",))
        edges = score_support([h1, h2, h3])
        assert len(edges) == 3
        assert all(isinstance(e, SupportEdge) for e in edges)

    def test_no_shared_source_creates_no_edges(self):
        h1 = _h("h1", source_refs=("a",))
        h2 = _h("h2", source_refs=("b",))
        assert score_support([h1, h2]) == []

    def test_score_support_empty(self):
        assert score_support([]) == []

    def test_support_edge_justification_contains_source(self):
        h1 = _h("h1", source_refs=("seg1",))
        h2 = _h("h2", source_refs=("seg1",))
        edges = score_support([h1, h2])
        assert len(edges) == 1
        assert "seg1" in edges[0].justification

    def test_compatible_role_case_no_constraint(self):
        role_h = _h("role1", stage=ActivationStage.ROLE, source_refs=("c1",))
        case_h = _h(
            "case1",
            stage=ActivationStage.CASE,
            source_refs=("role1",),
            payload=(("role", "فاعل"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert edges == []

    def test_incompatible_role_case_creates_constraint(self):
        role_h = _h("role1", stage=ActivationStage.ROLE, source_refs=("c1",))
        case_h = _h(
            "case1",
            stage=ActivationStage.CASE,
            source_refs=("role1",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) >= 1
        assert all(isinstance(e, ConstraintEdge) for e in edges)
        assert edges[0].relation == "role_case_incompatible"
        assert edges[0].strength == ConstraintStrength.STRONG

    def test_build_constraint_edges_empty(self):
        assert build_constraint_edges([]) == []


# ── TestPropagation ──────────────────────────────────────────────────


class TestPropagation:
    """Tests for propagation.propagate and propagation.get_constraint_edges."""

    def test_propagate_returns_tuple(self):
        support, conflicts = propagate([])
        assert isinstance(support, list)
        assert isinstance(conflicts, list)

    def test_propagate_empty(self):
        support, conflicts = propagate([])
        assert support == []
        assert conflicts == []

    def test_same_stage_same_source_soft_conflict(self):
        h1 = _h("h1", stage=ActivationStage.CONCEPT, source_refs=("seg1",))
        h2 = _h("h2", stage=ActivationStage.CONCEPT, source_refs=("seg1",))
        _, conflicts = propagate([h1, h2])
        soft = [c for c in conflicts if c.conflict_state == ConflictState.SOFT]
        assert len(soft) == 1
        assert {soft[0].node_a_ref, soft[0].node_b_ref} == {"h1", "h2"}

    def test_different_sources_no_conflict(self):
        h1 = _h("h1", stage=ActivationStage.CONCEPT, source_refs=("a",))
        h2 = _h("h2", stage=ActivationStage.CONCEPT, source_refs=("b",))
        _, conflicts = propagate([h1, h2])
        assert conflicts == []

    def test_get_constraint_edges_returns_list(self):
        result = get_constraint_edges([])
        assert isinstance(result, list)
        assert result == []

    def test_get_constraint_edges_delegates_to_build(self):
        role_h = _h("role1", stage=ActivationStage.ROLE, source_refs=("c1",))
        case_h = _h(
            "case1",
            stage=ActivationStage.CASE,
            source_refs=("role1",),
            payload=(("role", "مفعول"), ("case_state", "رفع")),
        )
        edges = get_constraint_edges([role_h, case_h])
        assert len(edges) >= 1
        assert edges[0].relation == "role_case_incompatible"


# ── TestPruning ──────────────────────────────────────────────────────


class TestPruning:
    """Tests for pruning.prune."""

    def test_low_confidence_active_pruned(self):
        h = _h("low", confidence=0.1)
        result, traces = prune([h])
        assert result[0].status == HypothesisStatus.PRUNED
        assert len(traces) == 1

    def test_high_confidence_survives(self):
        h = _h("high", confidence=0.9)
        result, traces = prune([h])
        assert result[0].status == HypothesisStatus.ACTIVE
        assert traces == []

    def test_already_pruned_not_repruned(self):
        h = _h("p", confidence=0.05, status=HypothesisStatus.PRUNED)
        result, traces = prune([h])
        assert result[0].status == HypothesisStatus.PRUNED
        assert traces == []

    def test_custom_confidence_floor(self):
        h = _h("med", confidence=0.3)
        result_default, _ = prune([h])
        assert result_default[0].status == HypothesisStatus.ACTIVE

        result_high, traces_high = prune([h], confidence_floor=0.5)
        assert result_high[0].status == HypothesisStatus.PRUNED
        assert len(traces_high) == 1

    def test_trace_id_and_justification(self):
        h = _h("t1", confidence=0.05)
        _, traces = prune([h])
        assert traces[0].trace_id == "PRUNE_t1"
        assert "0.05" in traces[0].justification
        assert traces[0].decision_type == "pruning"

    def test_prune_empty(self):
        result, traces = prune([])
        assert result == []
        assert traces == []

    def test_default_confidence_floor_value(self):
        assert DEFAULT_CONFIDENCE_FLOOR == 0.2

    def test_mixed_hypotheses(self):
        h_low = _h("low", confidence=0.1)
        h_high = _h("high", confidence=0.9)
        result, traces = prune([h_low, h_high])
        status_map = {r.node_id: r.status for r in result}
        assert status_map["low"] == HypothesisStatus.PRUNED
        assert status_map["high"] == HypothesisStatus.ACTIVE
        assert len(traces) == 1


# ── TestRevision ─────────────────────────────────────────────────────


class TestRevision:
    """Tests for revision.needs_revision and revision.apply_revision."""

    def test_needs_revision_hard_conflict(self):
        h1 = _h("h1")
        conflict = ConflictEdge(
            edge_id="c1",
            node_a_ref="h1",
            node_b_ref="h2",
            conflict_state=ConflictState.HARD,
        )
        assert needs_revision([h1], [conflict]) is True

    def test_needs_revision_no_conflicts(self):
        h1 = _h("h1")
        assert needs_revision([h1], []) is False

    def test_needs_revision_soft_conflict_only(self):
        h1 = _h("h1")
        conflict = ConflictEdge(
            edge_id="c1",
            node_a_ref="h1",
            node_b_ref="h2",
            conflict_state=ConflictState.SOFT,
        )
        assert needs_revision([h1], [conflict]) is False

    def test_needs_revision_low_confidence_stabilized(self):
        h = _h("s1", confidence=0.3, status=HypothesisStatus.STABILIZED)
        assert needs_revision([h], []) is True

    def test_needs_revision_high_confidence_stabilized(self):
        h = _h("s1", confidence=0.9, status=HypothesisStatus.STABILIZED)
        assert needs_revision([h], []) is False

    def test_apply_revision_hard_conflict_prunes_weaker(self):
        h1 = _h("h1", confidence=0.9)
        h2 = _h("h2", confidence=0.3)
        conflict = ConflictEdge(
            edge_id="c1",
            node_a_ref="h1",
            node_b_ref="h2",
            conflict_state=ConflictState.HARD,
        )
        result, traces = apply_revision([h1, h2], [conflict])
        status_map = {r.node_id: r.status for r in result}
        assert status_map["h2"] == HypothesisStatus.PRUNED
        assert status_map["h1"] == HypothesisStatus.ACTIVE
        assert len(traces) == 1
        assert traces[0].decision_type == "revision_prune"
        assert traces[0].trace_id == "REV_h2"

    def test_apply_revision_suspends_low_confidence_stabilized(self):
        h = _h("s1", confidence=0.3, status=HypothesisStatus.STABILIZED)
        result, traces = apply_revision([h], [])
        assert result[0].status == HypothesisStatus.SUSPENDED
        assert len(traces) == 1
        assert traces[0].decision_type == "suspension"
        assert traces[0].trace_id == "SUSP_s1"

    def test_apply_revision_no_changes_when_clean(self):
        h = _h("h1", confidence=0.9)
        result, traces = apply_revision([h], [])
        assert result[0].status == HypothesisStatus.ACTIVE
        assert traces == []

    def test_apply_revision_traces_contain_conflict_edge_id(self):
        h1 = _h("h1", confidence=0.8)
        h2 = _h("h2", confidence=0.2)
        conflict = ConflictEdge(
            edge_id="conflict_42",
            node_a_ref="h1",
            node_b_ref="h2",
            conflict_state=ConflictState.HARD,
        )
        _, traces = apply_revision([h1, h2], [conflict])
        assert "conflict_42" in traces[0].input_refs
