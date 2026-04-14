"""Bounded revision loop — حلقة مراجعة محدودة.

Detects whether the current hypothesis graph has unresolved conflicts
or low-confidence stabilised nodes, and requests a revision pass.

The revision loop is **bounded** by a ``max_iterations`` parameter
to guarantee termination.
"""

from __future__ import annotations

from typing import List, Tuple

from arabic_engine.core.enums import (
    ConflictState,
    HypothesisStatus,
)
from arabic_engine.core.types import (
    ConflictEdge,
    DecisionTrace,
    HypothesisNode,
)

# Minimum confidence below which a stabilised node triggers revision.
_REVISION_THRESHOLD = 0.4


def needs_revision(
    hypotheses: List[HypothesisNode],
    conflicts: List[ConflictEdge],
) -> bool:
    """Check whether the hypothesis graph needs another revision pass.

    Returns ``True`` if there are unresolved hard conflicts or any
    stabilised hypothesis has confidence below the revision threshold.

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        Current hypotheses.
    conflicts : list[ConflictEdge]
        Current conflict edges.

    Returns
    -------
    bool
    """
    # Any unresolved hard conflicts?
    if any(c.conflict_state == ConflictState.HARD for c in conflicts):
        return True

    # Any stabilised node with very low confidence?
    for h in hypotheses:
        if h.status == HypothesisStatus.STABILIZED and h.confidence < _REVISION_THRESHOLD:
            return True

    return False


def apply_revision(
    hypotheses: List[HypothesisNode],
    conflicts: List[ConflictEdge],
) -> Tuple[List[HypothesisNode], List[DecisionTrace]]:
    """Apply one revision pass.

    For each hard conflict, the lower-confidence hypothesis is pruned.
    For each low-confidence stabilised node, the node is suspended.

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        Current hypotheses.
    conflicts : list[ConflictEdge]
        Current conflict edges.

    Returns
    -------
    tuple[list[HypothesisNode], list[DecisionTrace]]
        Updated hypotheses and revision traces.
    """
    traces: List[DecisionTrace] = []
    nodes_by_id = {h.node_id: h for h in hypotheses}
    revised_ids: set[str] = set()

    # Resolve hard conflicts: prune the weaker hypothesis
    for c in conflicts:
        if c.conflict_state != ConflictState.HARD:
            continue
        a = nodes_by_id.get(c.node_a_ref)
        b = nodes_by_id.get(c.node_b_ref)
        if a is None or b is None:
            continue
        loser = a if a.confidence <= b.confidence else b
        if loser.node_id not in revised_ids:
            revised_ids.add(loser.node_id)
            nodes_by_id[loser.node_id] = HypothesisNode(
                node_id=loser.node_id,
                hypothesis_type=loser.hypothesis_type,
                stage=loser.stage,
                source_refs=loser.source_refs,
                payload=loser.payload,
                confidence=loser.confidence,
                status=HypothesisStatus.PRUNED,
            )
            traces.append(
                DecisionTrace(
                    trace_id=f"REV_{loser.node_id}",
                    stage=loser.stage,
                    decision_type="revision_prune",
                    input_refs=(c.edge_id,),
                    rejected_refs=(loser.node_id,),
                    justification="Hard conflict resolved: kept higher confidence",
                    confidence=loser.confidence,
                )
            )

    # Suspend low-confidence stabilised nodes
    for h in list(nodes_by_id.values()):
        if (
            h.status == HypothesisStatus.STABILIZED
            and h.confidence < _REVISION_THRESHOLD
            and h.node_id not in revised_ids
        ):
            revised_ids.add(h.node_id)
            nodes_by_id[h.node_id] = HypothesisNode(
                node_id=h.node_id,
                hypothesis_type=h.hypothesis_type,
                stage=h.stage,
                source_refs=h.source_refs,
                payload=h.payload,
                confidence=h.confidence,
                status=HypothesisStatus.SUSPENDED,
            )
            traces.append(
                DecisionTrace(
                    trace_id=f"SUSP_{h.node_id}",
                    stage=h.stage,
                    decision_type="suspension",
                    input_refs=(h.node_id,),
                    justification=f"Confidence {h.confidence:.4f} below revision threshold",
                    confidence=h.confidence,
                )
            )

    return list(nodes_by_id.values()), traces
