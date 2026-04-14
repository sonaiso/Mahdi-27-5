"""Trace Causality Depth — عمق السببية في التتبع.

Measures the depth of the causal chain from the final judgement
back to the original signal atoms via ``source_refs``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from arabic_engine.core.trace import KernelRuntimeState
from arabic_engine.core.types import HypothesisNode


@dataclass(frozen=True)
class TraceDepthReport:
    """Summary of trace causality depth analysis."""

    max_depth: int
    avg_depth: float
    is_connected: bool
    chain_lengths: tuple[int, ...]


def compute_trace_depth(state: KernelRuntimeState) -> TraceDepthReport:
    """Analyse the causal depth from judgement back to signal.

    Builds a node index from all hypotheses, then traces back
    from the judgement node through ``source_refs`` to find the
    longest chain and check connectivity.

    Parameters
    ----------
    state : KernelRuntimeState
        The output of the orchestrator.

    Returns
    -------
    TraceDepthReport
        Summary of depth analysis.
    """
    all_hyps = state.hypotheses.all_hypotheses()
    node_index: Dict[str, HypothesisNode] = {h.node_id: h for h in all_hyps}

    judgement = state.decisions.judgement
    if judgement is None:
        return TraceDepthReport(
            max_depth=0, avg_depth=0.0, is_connected=False, chain_lengths=()
        )

    # Trace all chains from judgement back to roots
    chains: List[int] = []
    _trace_chains(judgement, node_index, 0, chains)

    if not chains:
        return TraceDepthReport(
            max_depth=0, avg_depth=0.0, is_connected=False, chain_lengths=()
        )

    max_depth = max(chains)
    avg_depth = sum(chains) / len(chains)
    # Connected if at least one chain reaches a node with no further refs
    is_connected = max_depth > 0

    return TraceDepthReport(
        max_depth=max_depth,
        avg_depth=round(avg_depth, 2),
        is_connected=is_connected,
        chain_lengths=tuple(chains),
    )


def _trace_chains(
    node: HypothesisNode,
    index: Dict[str, HypothesisNode],
    depth: int,
    results: List[int],
    _visited: Optional[set[str]] = None,
) -> None:
    """Recursively trace back through source_refs.

    Parameters
    ----------
    node : HypothesisNode
        Current node being traced.
    index : dict[str, HypothesisNode]
        Map of node_id to HypothesisNode.
    depth : int
        Current depth in the chain.
    results : list[int]
        Collects leaf depths.
    _visited : set[str] or None
        Nodes already visited (cycle detection).
    """
    if _visited is None:
        _visited = set()

    if node.node_id in _visited:
        results.append(depth)
        return

    _visited = _visited | {node.node_id}

    if not node.source_refs:
        results.append(depth)
        return

    found_parent = False
    for ref in node.source_refs:
        parent = index.get(ref)
        if parent is not None:
            found_parent = True
            _trace_chains(parent, index, depth + 1, results, _visited)

    if not found_parent:
        results.append(depth)
