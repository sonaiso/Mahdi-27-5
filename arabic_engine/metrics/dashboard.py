"""Quality Dashboard — لوحة معايير الجودة.

Combines all four quality metrics into a single report.
"""

from __future__ import annotations

from dataclasses import dataclass

from arabic_engine.core.trace import KernelRuntimeState
from arabic_engine.metrics.ambiguity_tracker import compute_ambiguity_honesty_rate
from arabic_engine.metrics.constraint_impact import compute_constraint_impact_rate
from arabic_engine.metrics.stub_tracker import compute_stub_reduction_rate
from arabic_engine.metrics.trace_depth import TraceDepthReport, compute_trace_depth


@dataclass(frozen=True)
class QualityReport:
    """Combined quality metrics report."""

    stub_reduction_rate: float
    ambiguity_honesty_rate: float
    constraint_impact_rate: float
    trace_depth: TraceDepthReport


def generate_report(state: KernelRuntimeState) -> QualityReport:
    """Generate a quality report for a pipeline run.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    QualityReport
        Combined metrics.
    """
    return QualityReport(
        stub_reduction_rate=compute_stub_reduction_rate(),
        ambiguity_honesty_rate=compute_ambiguity_honesty_rate(state),
        constraint_impact_rate=compute_constraint_impact_rate(state),
        trace_depth=compute_trace_depth(state),
    )
