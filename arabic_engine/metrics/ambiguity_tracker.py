"""Ambiguity Honesty Rate — معدّل صدق الغموض.

Measures how many genuinely ambiguous cases the system honestly
suspends instead of resolving with false confidence.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import HypothesisStatus
from arabic_engine.core.trace import KernelRuntimeState
from arabic_engine.core.types import HypothesisNode


def compute_ambiguity_honesty_rate(state: KernelRuntimeState) -> float:
    """Compute the ambiguity honesty rate from a pipeline run.

    The rate is: suspended hypotheses / (suspended + activated).
    A higher rate means the system is more honest about what it
    doesn't know.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    float
        Value between 0.0 (never suspends) and 1.0 (always suspends).
    """
    suspended = len(state.decisions.suspended)
    activated = len(state.decisions.activated)
    total = suspended + activated
    if total == 0:
        return 0.0
    return suspended / total


def count_competing_hypotheses(state: KernelRuntimeState) -> int:
    """Count how many stage-source groups have multiple competing hypotheses.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    int
        Number of groups where multiple hypotheses compete.
    """
    groups: dict[tuple, list[HypothesisNode]] = {}
    for h in state.hypotheses.all_hypotheses():
        key = (h.stage, h.source_refs)
        groups.setdefault(key, []).append(h)
    return sum(1 for g in groups.values() if len(g) > 1)


def find_suspended_hypotheses(
    state: KernelRuntimeState,
) -> List[HypothesisNode]:
    """Return all suspended hypotheses from the decision state.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    list[HypothesisNode]
        All hypotheses with status SUSPENDED.
    """
    return [
        h
        for h in state.hypotheses.all_hypotheses()
        if h.status == HypothesisStatus.SUSPENDED
    ]
