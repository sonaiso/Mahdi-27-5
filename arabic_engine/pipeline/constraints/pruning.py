"""Constraint pruning — تقليم الفرضيات.

Applies threshold-based pruning to hypotheses below a confidence
floor.  Pruned hypotheses are NOT deleted — their status is changed
to ``PRUNED`` and a justification trace is recorded.

Architectural rule: **no pruning without justification**.
"""

from __future__ import annotations

from typing import List, Tuple

from arabic_engine.core.enums import HypothesisStatus
from arabic_engine.core.types import DecisionTrace, HypothesisNode

# Default confidence floor — hypotheses below this are pruned.
DEFAULT_CONFIDENCE_FLOOR = 0.2


def prune(
    hypotheses: List[HypothesisNode],
    *,
    confidence_floor: float = DEFAULT_CONFIDENCE_FLOOR,
) -> Tuple[List[HypothesisNode], List[DecisionTrace]]:
    """Apply threshold pruning to hypotheses.

    Hypotheses with confidence below *confidence_floor* are replaced
    with a copy whose status is ``PRUNED``.  All others pass through
    unchanged.

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        All hypotheses to evaluate.
    confidence_floor : float
        Minimum confidence to survive.  Default ``0.2``.

    Returns
    -------
    tuple[list[HypothesisNode], list[DecisionTrace]]
        Updated hypotheses (some may now be PRUNED) and traces.
    """
    result: List[HypothesisNode] = []
    traces: List[DecisionTrace] = []

    for h in hypotheses:
        if h.confidence < confidence_floor and h.status == HypothesisStatus.ACTIVE:
            pruned = HypothesisNode(
                node_id=h.node_id,
                hypothesis_type=h.hypothesis_type,
                stage=h.stage,
                source_refs=h.source_refs,
                payload=h.payload,
                confidence=h.confidence,
                status=HypothesisStatus.PRUNED,
            )
            result.append(pruned)
            traces.append(
                DecisionTrace(
                    trace_id=f"PRUNE_{h.node_id}",
                    stage=h.stage,
                    decision_type="pruning",
                    input_refs=(h.node_id,),
                    rejected_refs=(h.node_id,),
                    justification=(
                        f"Confidence {h.confidence:.4f} "
                        f"below floor {confidence_floor}"
                    ),
                    confidence=h.confidence,
                )
            )
        else:
            result.append(h)

    return result, traces
