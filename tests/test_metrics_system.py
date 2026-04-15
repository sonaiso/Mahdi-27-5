"""System tests for arabic_engine.metrics — اختبارات النظام لمعايير الجودة.

Comprehensive coverage of all five metrics sub-modules:
stub_tracker, ambiguity_tracker, constraint_impact, trace_depth, and dashboard.
"""

from __future__ import annotations

import dataclasses

import pytest

from arabic_engine.metrics.ambiguity_tracker import (
    compute_ambiguity_honesty_rate,
    count_competing_hypotheses,
    find_suspended_hypotheses,
)
from arabic_engine.metrics.constraint_impact import (
    compute_constraint_impact_rate,
    count_conflict_edges,
    count_constraint_edges,
    count_support_edges,
)
from arabic_engine.metrics.dashboard import QualityReport, generate_report
from arabic_engine.metrics.stub_tracker import (
    STUB_REGISTRY,
    StubRecord,
    StubStatus,
    compute_stub_reduction_rate,
    stub_summary,
)
from arabic_engine.metrics.trace_depth import TraceDepthReport, compute_trace_depth
from arabic_engine.runtime.orchestrator import run

# ═══════════════════════════════════════════════════════════════════════════
# Shared fixture — cache the orchestrator result for the standard sentence
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def state_ktb_alrisala():
    """Run the orchestrator once for 'كتب الرسالة' and reuse."""
    return run("كتب الرسالة")


# ═══════════════════════════════════════════════════════════════════════════
# 1. Stub Tracker
# ═══════════════════════════════════════════════════════════════════════════


class TestStubTracker:
    """Validate stub_tracker module: enum, dataclass, registry, functions."""

    # ── StubStatus enum ───────────────────────────────────────────────

    def test_stub_status_has_stub(self):
        assert StubStatus.STUB is not None

    def test_stub_status_has_partial(self):
        assert StubStatus.PARTIAL is not None

    def test_stub_status_has_complete(self):
        assert StubStatus.COMPLETE is not None

    def test_stub_status_members(self):
        names = {m.name for m in StubStatus}
        assert names == {"STUB", "PARTIAL", "COMPLETE"}

    # ── StubRecord frozen dataclass ───────────────────────────────────

    def test_stub_record_is_frozen(self):
        record = StubRecord(
            module="test", function="fn", status=StubStatus.STUB,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.module = "changed"  # type: ignore[misc]

    def test_stub_record_default_description(self):
        record = StubRecord(
            module="m", function="f", status=StubStatus.COMPLETE,
        )
        assert record.description == ""

    def test_stub_record_with_description(self):
        record = StubRecord(
            module="m", function="f", status=StubStatus.PARTIAL,
            description="half done",
        )
        assert record.description == "half done"

    # ── STUB_REGISTRY ─────────────────────────────────────────────────

    def test_registry_has_8_entries(self):
        assert len(STUB_REGISTRY) == 8

    def test_registry_all_complete(self):
        for rec in STUB_REGISTRY:
            assert rec.status == StubStatus.COMPLETE, (
                f"{rec.module}:{rec.function} is not COMPLETE"
            )

    def test_registry_entries_are_stub_records(self):
        for rec in STUB_REGISTRY:
            assert isinstance(rec, StubRecord)

    def test_registry_each_has_module_and_function(self):
        for rec in STUB_REGISTRY:
            assert rec.module, f"Empty module in {rec}"
            assert rec.function, f"Empty function in {rec}"

    # ── compute_stub_reduction_rate ───────────────────────────────────

    def test_reduction_rate_is_1(self):
        assert compute_stub_reduction_rate() == 1.0

    def test_reduction_rate_type(self):
        assert isinstance(compute_stub_reduction_rate(), float)

    def test_reduction_rate_range(self):
        rate = compute_stub_reduction_rate()
        assert 0.0 <= rate <= 1.0

    # ── stub_summary ──────────────────────────────────────────────────

    def test_summary_exact_values(self):
        assert stub_summary() == {"stub": 0, "partial": 0, "complete": 8}

    def test_summary_keys(self):
        assert set(stub_summary().keys()) == {"stub", "partial", "complete"}

    def test_summary_total_matches_registry(self):
        s = stub_summary()
        assert s["stub"] + s["partial"] + s["complete"] == len(STUB_REGISTRY)


# ═══════════════════════════════════════════════════════════════════════════
# 2. Ambiguity Tracker
# ═══════════════════════════════════════════════════════════════════════════


class TestAmbiguityTracker:
    """Validate ambiguity_tracker functions with real orchestrator state."""

    # ── compute_ambiguity_honesty_rate ────────────────────────────────

    def test_rate_type(self, state_ktb_alrisala):
        rate = compute_ambiguity_honesty_rate(state_ktb_alrisala)
        assert isinstance(rate, float)

    def test_rate_in_range(self, state_ktb_alrisala):
        rate = compute_ambiguity_honesty_rate(state_ktb_alrisala)
        assert 0.0 <= rate <= 1.0

    def test_rate_is_zero_no_suspensions(self, state_ktb_alrisala):
        assert compute_ambiguity_honesty_rate(state_ktb_alrisala) == 0.0

    # ── count_competing_hypotheses ────────────────────────────────────

    def test_competing_type(self, state_ktb_alrisala):
        count = count_competing_hypotheses(state_ktb_alrisala)
        assert isinstance(count, int)

    def test_competing_non_negative(self, state_ktb_alrisala):
        assert count_competing_hypotheses(state_ktb_alrisala) >= 0

    def test_competing_value(self, state_ktb_alrisala):
        assert count_competing_hypotheses(state_ktb_alrisala) == 2

    # ── find_suspended_hypotheses ─────────────────────────────────────

    def test_suspended_returns_list(self, state_ktb_alrisala):
        result = find_suspended_hypotheses(state_ktb_alrisala)
        assert isinstance(result, list)

    def test_suspended_empty_for_standard(self, state_ktb_alrisala):
        assert find_suspended_hypotheses(state_ktb_alrisala) == []


# ═══════════════════════════════════════════════════════════════════════════
# 3. Constraint Impact
# ═══════════════════════════════════════════════════════════════════════════


class TestConstraintImpact:
    """Validate constraint_impact functions with real orchestrator state."""

    # ── compute_constraint_impact_rate ────────────────────────────────

    def test_impact_rate_type(self, state_ktb_alrisala):
        rate = compute_constraint_impact_rate(state_ktb_alrisala)
        assert isinstance(rate, float)

    def test_impact_rate_in_range(self, state_ktb_alrisala):
        rate = compute_constraint_impact_rate(state_ktb_alrisala)
        assert 0.0 <= rate <= 1.0

    def test_impact_rate_is_zero(self, state_ktb_alrisala):
        assert compute_constraint_impact_rate(state_ktb_alrisala) == 0.0

    # ── count_constraint_edges ────────────────────────────────────────

    def test_constraint_edges_type(self, state_ktb_alrisala):
        assert isinstance(count_constraint_edges(state_ktb_alrisala), int)

    def test_constraint_edges_non_negative(self, state_ktb_alrisala):
        assert count_constraint_edges(state_ktb_alrisala) >= 0

    def test_constraint_edges_value(self, state_ktb_alrisala):
        assert count_constraint_edges(state_ktb_alrisala) == 0

    # ── count_conflict_edges ──────────────────────────────────────────

    def test_conflict_edges_type(self, state_ktb_alrisala):
        assert isinstance(count_conflict_edges(state_ktb_alrisala), int)

    def test_conflict_edges_non_negative(self, state_ktb_alrisala):
        assert count_conflict_edges(state_ktb_alrisala) >= 0

    # ── count_support_edges ───────────────────────────────────────────

    def test_support_edges_type(self, state_ktb_alrisala):
        assert isinstance(count_support_edges(state_ktb_alrisala), int)

    def test_support_edges_non_negative(self, state_ktb_alrisala):
        assert count_support_edges(state_ktb_alrisala) >= 0


# ═══════════════════════════════════════════════════════════════════════════
# 4. Trace Depth
# ═══════════════════════════════════════════════════════════════════════════


class TestTraceDepth:
    """Validate trace_depth dataclass and computation."""

    # ── TraceDepthReport frozen ───────────────────────────────────────

    def test_report_is_frozen(self):
        report = TraceDepthReport(
            max_depth=3, avg_depth=2.5, is_connected=True, chain_lengths=(2, 3),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.max_depth = 10  # type: ignore[misc]

    def test_report_fields(self):
        report = TraceDepthReport(
            max_depth=1, avg_depth=1.0, is_connected=False, chain_lengths=(1,),
        )
        assert report.max_depth == 1
        assert report.avg_depth == 1.0
        assert report.is_connected is False
        assert report.chain_lengths == (1,)

    # ── compute_trace_depth ───────────────────────────────────────────

    def test_returns_trace_depth_report(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert isinstance(report, TraceDepthReport)

    def test_max_depth_positive(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert report.max_depth > 0

    def test_max_depth_value(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert report.max_depth == 6

    def test_avg_depth_value(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert report.avg_depth == 5.5

    def test_is_connected(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert report.is_connected is True

    def test_chain_lengths_non_empty(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert len(report.chain_lengths) > 0

    def test_chain_lengths_is_tuple(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert isinstance(report.chain_lengths, tuple)

    def test_chain_lengths_value(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert report.chain_lengths == (5, 6, 5, 6)

    def test_avg_depth_lte_max_depth(self, state_ktb_alrisala):
        report = compute_trace_depth(state_ktb_alrisala)
        assert report.avg_depth <= report.max_depth


# ═══════════════════════════════════════════════════════════════════════════
# 5. Dashboard
# ═══════════════════════════════════════════════════════════════════════════


class TestDashboard:
    """Validate dashboard report generation."""

    # ── QualityReport frozen ──────────────────────────────────────────

    def test_report_is_frozen(self):
        td = TraceDepthReport(
            max_depth=1, avg_depth=1.0, is_connected=True, chain_lengths=(1,),
        )
        report = QualityReport(
            stub_reduction_rate=1.0,
            ambiguity_honesty_rate=0.0,
            constraint_impact_rate=0.0,
            trace_depth=td,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.stub_reduction_rate = 0.5  # type: ignore[misc]

    # ── generate_report ───────────────────────────────────────────────

    def test_returns_quality_report(self, state_ktb_alrisala):
        report = generate_report(state_ktb_alrisala)
        assert isinstance(report, QualityReport)

    def test_stub_reduction_rate_field(self, state_ktb_alrisala):
        report = generate_report(state_ktb_alrisala)
        assert isinstance(report.stub_reduction_rate, float)
        assert report.stub_reduction_rate == 1.0

    def test_ambiguity_honesty_rate_field(self, state_ktb_alrisala):
        report = generate_report(state_ktb_alrisala)
        assert isinstance(report.ambiguity_honesty_rate, float)
        assert 0.0 <= report.ambiguity_honesty_rate <= 1.0

    def test_constraint_impact_rate_field(self, state_ktb_alrisala):
        report = generate_report(state_ktb_alrisala)
        assert isinstance(report.constraint_impact_rate, float)
        assert 0.0 <= report.constraint_impact_rate <= 1.0

    def test_trace_depth_field(self, state_ktb_alrisala):
        report = generate_report(state_ktb_alrisala)
        assert isinstance(report.trace_depth, TraceDepthReport)

    def test_report_all_fields_populated(self, state_ktb_alrisala):
        report = generate_report(state_ktb_alrisala)
        assert report.stub_reduction_rate is not None
        assert report.ambiguity_honesty_rate is not None
        assert report.constraint_impact_rate is not None
        assert report.trace_depth is not None
        assert report.trace_depth.chain_lengths is not None


# ═══════════════════════════════════════════════════════════════════════════
# 6. Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge-case behaviour with minimal or single-word input."""

    def test_single_word_ambiguity_rate(self):
        state = run("كتب")
        rate = compute_ambiguity_honesty_rate(state)
        assert isinstance(rate, float)
        assert 0.0 <= rate <= 1.0

    def test_single_word_competing_hypotheses(self):
        state = run("كتب")
        count = count_competing_hypotheses(state)
        assert isinstance(count, int)
        assert count >= 0

    def test_single_word_constraint_impact(self):
        state = run("كتب")
        rate = compute_constraint_impact_rate(state)
        assert 0.0 <= rate <= 1.0

    def test_single_word_trace_depth(self):
        state = run("كتب")
        report = compute_trace_depth(state)
        assert isinstance(report, TraceDepthReport)
        assert report.max_depth >= 0

    def test_single_word_dashboard(self):
        state = run("كتب")
        report = generate_report(state)
        assert isinstance(report, QualityReport)

    def test_single_word_find_suspended(self):
        state = run("كتب")
        suspended = find_suspended_hypotheses(state)
        assert isinstance(suspended, list)

    def test_single_word_edge_counts(self):
        state = run("كتب")
        assert count_constraint_edges(state) >= 0
        assert count_conflict_edges(state) >= 0
        assert count_support_edges(state) >= 0
