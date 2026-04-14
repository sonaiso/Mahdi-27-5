"""Tests for quality metrics — اختبارات معايير الجودة.

Validates all four quality metrics: Stub Reduction Rate,
Ambiguity Honesty Rate, Constraint Impact Rate, and Trace
Causality Depth.
"""

from __future__ import annotations

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
    StubStatus,
    compute_stub_reduction_rate,
    stub_summary,
)
from arabic_engine.metrics.trace_depth import compute_trace_depth
from arabic_engine.runtime.orchestrator import run

# ═══════════════════════════════════════════════════════════════════════
# Stub Reduction Rate
# ═══════════════════════════════════════════════════════════════════════


class TestStubReductionRate:
    """Verify stub tracker reports accurate status."""

    def test_registry_has_entries(self):
        """Registry must contain at least 8 known stubs."""
        assert len(STUB_REGISTRY) >= 8

    def test_reduction_rate_is_between_0_and_1(self):
        rate = compute_stub_reduction_rate()
        assert 0.0 <= rate <= 1.0

    def test_stub_summary_keys(self):
        summary = stub_summary()
        assert set(summary.keys()) == {"stub", "partial", "complete"}

    def test_summary_counts_match_registry(self):
        summary = stub_summary()
        total = summary["stub"] + summary["partial"] + summary["complete"]
        assert total == len(STUB_REGISTRY)

    def test_each_record_has_module_and_function(self):
        for r in STUB_REGISTRY:
            assert r.module, f"Record missing module: {r}"
            assert r.function, f"Record missing function: {r}"
            assert isinstance(r.status, StubStatus)


# ═══════════════════════════════════════════════════════════════════════
# Ambiguity Honesty Rate
# ═══════════════════════════════════════════════════════════════════════


class TestAmbiguityHonestyRate:
    """Verify ambiguity honesty rate computation."""

    def test_rate_is_between_0_and_1(self):
        state = run("كتب الطالب الدرس")
        rate = compute_ambiguity_honesty_rate(state)
        assert 0.0 <= rate <= 1.0

    def test_competing_hypotheses_count(self):
        state = run("كتب الطالب")
        count = count_competing_hypotheses(state)
        assert isinstance(count, int)
        assert count >= 0

    def test_suspended_list_type(self):
        state = run("كتب")
        suspended = find_suspended_hypotheses(state)
        assert isinstance(suspended, list)


# ═══════════════════════════════════════════════════════════════════════
# Constraint Impact Rate
# ═══════════════════════════════════════════════════════════════════════


class TestConstraintImpactRate:
    """Verify constraint impact rate computation."""

    def test_rate_is_between_0_and_1(self):
        state = run("كتب الطالب الدرس")
        rate = compute_constraint_impact_rate(state)
        assert 0.0 <= rate <= 1.0

    def test_edge_counts_non_negative(self):
        state = run("كتب زيد")
        assert count_constraint_edges(state) >= 0
        assert count_conflict_edges(state) >= 0
        assert count_support_edges(state) >= 0


# ═══════════════════════════════════════════════════════════════════════
# Trace Causality Depth
# ═══════════════════════════════════════════════════════════════════════


class TestTraceCausalityDepth:
    """Verify trace depth computation."""

    def test_depth_report_for_simple_sentence(self):
        state = run("كتب")
        report = compute_trace_depth(state)
        assert report.max_depth >= 0
        assert report.avg_depth >= 0.0

    def test_depth_is_connected_for_valid_input(self):
        state = run("كتب الطالب")
        report = compute_trace_depth(state)
        assert report.is_connected, "Trace chain should be connected"

    def test_chain_passes_through_layers(self):
        """A two-word sentence should have trace depth ≥ 4."""
        state = run("كتب زيد")
        report = compute_trace_depth(state)
        assert report.max_depth >= 4, (
            f"Expected depth ≥ 4, got {report.max_depth}"
        )


# ═══════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════


class TestDashboard:
    """Verify the combined quality report."""

    def test_report_has_all_fields(self):
        state = run("كتب الطالب")
        report = generate_report(state)
        assert isinstance(report, QualityReport)
        assert 0.0 <= report.stub_reduction_rate <= 1.0
        assert 0.0 <= report.ambiguity_honesty_rate <= 1.0
        assert 0.0 <= report.constraint_impact_rate <= 1.0
        assert report.trace_depth.max_depth >= 0
