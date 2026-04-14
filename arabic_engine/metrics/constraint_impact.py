"""Constraint Impact Rate — معدّل أثر القيود.

Measures how many decisions actually changed as a result of the
constraint engine (scoring, pruning, propagation, revision).
"""

from __future__ import annotations

from arabic_engine.core.enums import HypothesisStatus
from arabic_engine.core.trace import KernelRuntimeState


def compute_constraint_impact_rate(state: KernelRuntimeState) -> float:
    """Compute the fraction of hypotheses affected by constraints.

    Looks at the decision traces to count how many hypotheses were
    pruned, revised, or suspended by the constraint engine.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    float
        Fraction of hypotheses that were changed by constraints.
    """
    all_hyps = state.hypotheses.all_hypotheses()
    if not all_hyps:
        return 0.0

    affected = sum(
        1
        for h in all_hyps
        if h.status in (
            HypothesisStatus.PRUNED,
            HypothesisStatus.SUSPENDED,
            HypothesisStatus.REVISED,
        )
    )
    return affected / len(all_hyps)


def count_constraint_edges(state: KernelRuntimeState) -> int:
    """Count total constraint edges in the hypothesis state.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    int
        Number of constraint edges.
    """
    return len(state.hypotheses.constraint_edges)


def count_conflict_edges(state: KernelRuntimeState) -> int:
    """Count total conflict edges discovered.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    int
        Number of conflict edges.
    """
    return len(state.hypotheses.conflict_edges)


def count_support_edges(state: KernelRuntimeState) -> int:
    """Count total support edges discovered.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    int
        Number of support edges.
    """
    return len(state.hypotheses.support_edges)
