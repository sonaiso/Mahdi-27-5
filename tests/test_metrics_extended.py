"""Tests for metrics.stub_tracker.StubRecord and metrics.trace_depth.TraceDepthReport.

Covers:
- StubRecord frozen dataclass instantiation and immutability
- TraceDepthReport frozen dataclass instantiation and immutability
- TraceDepthReport with None judgement
- _trace_chains circular reference detection
- Disconnected hypothesis graph behavior
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import ActivationStage
from arabic_engine.core.trace import (
    DecisionState,
    HypothesisState,
    KernelRuntimeState,
)
from arabic_engine.core.types import HypothesisNode
from arabic_engine.metrics.stub_tracker import StubRecord, StubStatus
from arabic_engine.metrics.trace_depth import (
    TraceDepthReport,
    _trace_chains,
    compute_trace_depth,
)


def _make_hypothesis(
    node_id: str,
    stage: ActivationStage = ActivationStage.MORPHOLOGY,
    source_refs: tuple[str, ...] = (),
    confidence: float = 0.8,
) -> HypothesisNode:
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="test",
        stage=stage,
        source_refs=source_refs,
        confidence=confidence,
    )


def _make_state(
    hypotheses: list[HypothesisNode] | None = None,
    judgement: HypothesisNode | None = None,
) -> KernelRuntimeState:
    """Create a minimal KernelRuntimeState for testing."""
    h_state = HypothesisState()
    for h in hypotheses or []:
        h_state.add_hypothesis(h)
    d_state = DecisionState(judgement=judgement)
    return KernelRuntimeState(
        input_text="test",
        hypotheses=h_state,
        decisions=d_state,
    )


# ═══════════════════════════════════════════════════════════════════════
# StubRecord
# ═══════════════════════════════════════════════════════════════════════


class TestStubRecord:
    """Tests for StubRecord frozen dataclass."""

    def test_basic_instantiation(self):
        """StubRecord can be instantiated with all fields."""
        record = StubRecord(
            module="hypothesis/judgements.py",
            function="generate",
            status=StubStatus.COMPLETE,
            description="test description",
        )
        assert record.module == "hypothesis/judgements.py"
        assert record.function == "generate"
        assert record.status == StubStatus.COMPLETE
        assert record.description == "test description"

    def test_default_description(self):
        """description defaults to empty string."""
        record = StubRecord(
            module="test.py",
            function="func",
            status=StubStatus.STUB,
        )
        assert record.description == ""

    def test_frozen_immutability(self):
        """StubRecord is frozen — attribute assignment should raise."""
        record = StubRecord(
            module="test.py",
            function="func",
            status=StubStatus.STUB,
        )
        with pytest.raises(AttributeError):
            record.module = "other.py"  # type: ignore[misc]

    def test_frozen_status_immutability(self):
        """Status cannot be changed after creation."""
        record = StubRecord(
            module="test.py",
            function="func",
            status=StubStatus.STUB,
        )
        with pytest.raises(AttributeError):
            record.status = StubStatus.COMPLETE  # type: ignore[misc]

    def test_all_status_values(self):
        """StubRecord accepts all StubStatus values."""
        for status in StubStatus:
            record = StubRecord(
                module="m.py", function="f", status=status
            )
            assert record.status == status

    def test_equality(self):
        """Two StubRecords with same fields are equal."""
        r1 = StubRecord("m.py", "f", StubStatus.STUB)
        r2 = StubRecord("m.py", "f", StubStatus.STUB)
        assert r1 == r2

    def test_inequality_different_status(self):
        """StubRecords with different status are not equal."""
        r1 = StubRecord("m.py", "f", StubStatus.STUB)
        r2 = StubRecord("m.py", "f", StubStatus.COMPLETE)
        assert r1 != r2


# ═══════════════════════════════════════════════════════════════════════
# TraceDepthReport
# ═══════════════════════════════════════════════════════════════════════


class TestTraceDepthReport:
    """Tests for TraceDepthReport frozen dataclass."""

    def test_basic_instantiation(self):
        """TraceDepthReport can be instantiated with all fields."""
        report = TraceDepthReport(
            max_depth=5,
            avg_depth=3.5,
            is_connected=True,
            chain_lengths=(3, 4, 5),
        )
        assert report.max_depth == 5
        assert report.avg_depth == 3.5
        assert report.is_connected is True
        assert report.chain_lengths == (3, 4, 5)

    def test_frozen_immutability(self):
        """TraceDepthReport is frozen — fields cannot be modified."""
        report = TraceDepthReport(
            max_depth=5, avg_depth=3.5, is_connected=True, chain_lengths=(5,)
        )
        with pytest.raises(AttributeError):
            report.max_depth = 10  # type: ignore[misc]

    def test_zero_depth_disconnected(self):
        """Report with zero depth and disconnected."""
        report = TraceDepthReport(
            max_depth=0, avg_depth=0.0, is_connected=False, chain_lengths=()
        )
        assert report.max_depth == 0
        assert report.is_connected is False
        assert report.chain_lengths == ()

    def test_single_chain(self):
        """Report with a single chain."""
        report = TraceDepthReport(
            max_depth=3, avg_depth=3.0, is_connected=True, chain_lengths=(3,)
        )
        assert len(report.chain_lengths) == 1

    def test_equality(self):
        """Two reports with same fields are equal."""
        r1 = TraceDepthReport(3, 2.5, True, (2, 3))
        r2 = TraceDepthReport(3, 2.5, True, (2, 3))
        assert r1 == r2


# ═══════════════════════════════════════════════════════════════════════
# compute_trace_depth — None judgement
# ═══════════════════════════════════════════════════════════════════════


class TestComputeTraceDepthNoneJudgement:
    """Tests for compute_trace_depth with None judgement."""

    def test_none_judgement_returns_disconnected(self):
        """State with no judgement should return disconnected report."""
        state = _make_state(hypotheses=[], judgement=None)
        report = compute_trace_depth(state)
        assert report.max_depth == 0
        assert report.avg_depth == 0.0
        assert report.is_connected is False
        assert report.chain_lengths == ()


# ═══════════════════════════════════════════════════════════════════════
# compute_trace_depth — chain tracing
# ═══════════════════════════════════════════════════════════════════════


class TestComputeTraceDepthChains:
    """Tests for compute_trace_depth with various chain structures."""

    def test_single_node_no_sources(self):
        """Judgement with no source_refs should have depth 0."""
        j = _make_hypothesis("J1", stage=ActivationStage.JUDGEMENT)
        state = _make_state(hypotheses=[j], judgement=j)
        report = compute_trace_depth(state)
        assert report.max_depth == 0
        assert report.chain_lengths == (0,)

    def test_linear_chain_depth_2(self):
        """Linear chain: J -> R -> C should have depth 2."""
        c = _make_hypothesis("C1", stage=ActivationStage.CONCEPT)
        r = _make_hypothesis("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        j = _make_hypothesis(
            "J1", stage=ActivationStage.JUDGEMENT, source_refs=("R1",)
        )
        state = _make_state(hypotheses=[c, r, j], judgement=j)
        report = compute_trace_depth(state)
        assert report.max_depth == 2
        assert report.is_connected is True

    def test_branching_chain(self):
        """Branching chain: J -> [R1, R2], R1 -> C1, R2 -> C2."""
        c1 = _make_hypothesis("C1", stage=ActivationStage.CONCEPT)
        c2 = _make_hypothesis("C2", stage=ActivationStage.CONCEPT)
        r1 = _make_hypothesis("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        r2 = _make_hypothesis("R2", stage=ActivationStage.ROLE, source_refs=("C2",))
        j = _make_hypothesis(
            "J1", stage=ActivationStage.JUDGEMENT, source_refs=("R1", "R2")
        )
        state = _make_state(hypotheses=[c1, c2, r1, r2, j], judgement=j)
        report = compute_trace_depth(state)
        assert report.max_depth == 2
        assert len(report.chain_lengths) == 2  # two branches

    def test_judgement_with_missing_parents(self):
        """Judgement referencing non-existent nodes — depth 0."""
        j = _make_hypothesis(
            "J1", stage=ActivationStage.JUDGEMENT, source_refs=("MISSING",)
        )
        state = _make_state(hypotheses=[j], judgement=j)
        report = compute_trace_depth(state)
        assert report.max_depth == 0


# ═══════════════════════════════════════════════════════════════════════
# _trace_chains — circular reference detection
# ═══════════════════════════════════════════════════════════════════════


class TestTraceChainsCycleDetection:
    """Tests for _trace_chains cycle detection."""

    def test_circular_reference_terminates(self):
        """Circular chain A -> B -> A should terminate without infinite loop."""
        a = _make_hypothesis("A", source_refs=("B",))
        b = _make_hypothesis("B", source_refs=("A",))
        index = {"A": a, "B": b}
        results: list[int] = []
        _trace_chains(a, index, 0, results)
        # Should terminate and produce results
        assert len(results) > 0
        # Depth should not be excessively large
        assert max(results) <= 3

    def test_self_reference_terminates(self):
        """Self-referencing node A -> A should terminate."""
        a = _make_hypothesis("A", source_refs=("A",))
        index = {"A": a}
        results: list[int] = []
        _trace_chains(a, index, 0, results)
        assert len(results) > 0

    def test_three_node_cycle_terminates(self):
        """Three-node cycle A -> B -> C -> A should terminate."""
        a = _make_hypothesis("A", source_refs=("B",))
        b = _make_hypothesis("B", source_refs=("C",))
        c = _make_hypothesis("C", source_refs=("A",))
        index = {"A": a, "B": b, "C": c}
        results: list[int] = []
        _trace_chains(a, index, 0, results)
        assert len(results) > 0

    def test_no_cycle_deep_chain(self):
        """Deep linear chain without cycles."""
        nodes = {}
        for i in range(5):
            refs = (f"N{i-1}",) if i > 0 else ()
            nodes[f"N{i}"] = _make_hypothesis(f"N{i}", source_refs=refs)
        # Remove reference to N-1 from N0
        nodes["N0"] = _make_hypothesis("N0", source_refs=())

        results: list[int] = []
        _trace_chains(nodes["N4"], nodes, 0, results)
        assert max(results) == 4
