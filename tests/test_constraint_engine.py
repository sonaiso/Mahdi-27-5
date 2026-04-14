"""Tests for the constraint engine (scoring, pruning, propagation, revision).

Invariants tested
-----------------
1. No pruning without justification.
2. Revision loop terminates.
3. Support edges connect shared-source hypotheses.
4. Conflict detection finds same-stage overlaps.
"""

from __future__ import annotations

from arabic_engine.constraints.propagation import propagate
from arabic_engine.constraints.pruning import prune
from arabic_engine.constraints.revision import apply_revision, needs_revision
from arabic_engine.constraints.scoring import score_support
from arabic_engine.core.enums import (
    ActivationStage,
    ConflictState,
    HypothesisStatus,
)
from arabic_engine.core.types import ConflictEdge, HypothesisNode


def _make_hypothesis(
    node_id: str,
    stage: ActivationStage = ActivationStage.MORPHOLOGY,
    source_refs: tuple[str, ...] = (),
    confidence: float = 0.8,
    status: HypothesisStatus = HypothesisStatus.ACTIVE,
) -> HypothesisNode:
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="test",
        stage=stage,
        source_refs=source_refs,
        confidence=confidence,
        status=status,
    )


# ═══════════════════════════════════════════════════════════════════════
# Scoring
# ═══════════════════════════════════════════════════════════════════════


class TestScoring:
    def test_support_edges_for_shared_source(self):
        h1 = _make_hypothesis("H1", source_refs=("S1",))
        h2 = _make_hypothesis("H2", stage=ActivationStage.CONCEPT, source_refs=("S1",))
        edges = score_support([h1, h2])
        assert len(edges) >= 1
        # At least one edge connects H1 and H2
        refs = {(e.supporter_ref, e.target_ref) for e in edges}
        assert ("H1", "H2") in refs or ("H2", "H1") in refs

    def test_no_support_without_shared_source(self):
        h1 = _make_hypothesis("H1", source_refs=("S1",))
        h2 = _make_hypothesis("H2", source_refs=("S2",))
        edges = score_support([h1, h2])
        assert len(edges) == 0

    def test_empty_input(self):
        edges = score_support([])
        assert edges == []


# ═══════════════════════════════════════════════════════════════════════
# Pruning
# ═══════════════════════════════════════════════════════════════════════


class TestPruning:
    def test_low_confidence_pruned(self):
        h = _make_hypothesis("H1", confidence=0.1)
        result, traces = prune([h], confidence_floor=0.2)
        assert result[0].status == HypothesisStatus.PRUNED
        assert len(traces) == 1

    def test_no_pruning_without_justification(self):
        """Every pruning produces a trace with justification."""
        h = _make_hypothesis("H1", confidence=0.1)
        _, traces = prune([h])
        for t in traces:
            assert t.justification != ""

    def test_above_threshold_not_pruned(self):
        h = _make_hypothesis("H1", confidence=0.9)
        result, traces = prune([h])
        assert result[0].status == HypothesisStatus.ACTIVE
        assert len(traces) == 0

    def test_already_pruned_not_re_pruned(self):
        h = _make_hypothesis("H1", confidence=0.1, status=HypothesisStatus.PRUNED)
        result, traces = prune([h])
        assert result[0].status == HypothesisStatus.PRUNED
        assert len(traces) == 0  # no new trace

    def test_custom_floor(self):
        h = _make_hypothesis("H1", confidence=0.3)
        result, _ = prune([h], confidence_floor=0.5)
        assert result[0].status == HypothesisStatus.PRUNED


# ═══════════════════════════════════════════════════════════════════════
# Propagation
# ═══════════════════════════════════════════════════════════════════════


class TestPropagation:
    def test_returns_support_and_conflict_edges(self):
        h1 = _make_hypothesis("H1", source_refs=("S1",))
        h2 = _make_hypothesis("H2", source_refs=("S1",))
        support, conflicts = propagate([h1, h2])
        assert isinstance(support, list)
        assert isinstance(conflicts, list)

    def test_detects_same_stage_same_source_conflict(self):
        h1 = _make_hypothesis("H1", source_refs=("S1",))
        h2 = _make_hypothesis("H2", source_refs=("S1",))
        _, conflicts = propagate([h1, h2])
        # Soft conflict expected for same stage + same source
        assert len(conflicts) >= 1
        assert conflicts[0].conflict_state == ConflictState.SOFT


# ═══════════════════════════════════════════════════════════════════════
# Revision
# ═══════════════════════════════════════════════════════════════════════


class TestRevision:
    def test_no_revision_needed_when_clean(self):
        h1 = _make_hypothesis("H1", confidence=0.9)
        assert needs_revision([h1], []) is False

    def test_revision_needed_for_hard_conflict(self):
        h1 = _make_hypothesis("H1", confidence=0.9)
        c = ConflictEdge(
            edge_id="CF_0", node_a_ref="H1", node_b_ref="H2",
            conflict_state=ConflictState.HARD,
        )
        assert needs_revision([h1], [c]) is True

    def test_revision_prunes_weaker_in_hard_conflict(self):
        h1 = _make_hypothesis("H1", confidence=0.9)
        h2 = _make_hypothesis("H2", confidence=0.3)
        c = ConflictEdge(
            edge_id="CF_0", node_a_ref="H1", node_b_ref="H2",
            conflict_state=ConflictState.HARD,
        )
        result, traces = apply_revision([h1, h2], [c])
        # H2 should be pruned (lower confidence)
        result_by_id = {h.node_id: h for h in result}
        assert result_by_id["H2"].status == HypothesisStatus.PRUNED
        assert result_by_id["H1"].status == HypothesisStatus.ACTIVE
        assert len(traces) >= 1

    def test_revision_suspends_low_confidence_stabilized(self):
        h = _make_hypothesis("H1", confidence=0.1, status=HypothesisStatus.STABILIZED)
        assert needs_revision([h], []) is True
        result, traces = apply_revision([h], [])
        assert result[0].status == HypothesisStatus.SUSPENDED
        assert len(traces) >= 1

    def test_revision_loop_terminates(self):
        """Bounded revision: loop must terminate within max_iterations."""
        h1 = _make_hypothesis("H1", confidence=0.9)
        h2 = _make_hypothesis("H2", confidence=0.3)
        conflicts = [
            ConflictEdge(
                edge_id="CF_0", node_a_ref="H1", node_b_ref="H2",
                conflict_state=ConflictState.HARD,
            )
        ]
        max_iter = 5
        for i in range(max_iter):
            if not needs_revision([h1, h2], conflicts):
                break
            [h1, h2], _ = apply_revision([h1, h2], conflicts)
            _, conflicts = propagate([h1, h2])
        # Must have terminated
        assert i < max_iter - 1 or not needs_revision([h1, h2], conflicts)
