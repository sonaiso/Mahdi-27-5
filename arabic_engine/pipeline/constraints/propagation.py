"""Cross-layer constraint propagation — نشر القيود عبر الطبقات.

Propagation performs three tasks:

1. Score all support edges.
2. Build constraint edges from cross-layer compatibility rules.
3. Mark conflicts between incompatible hypotheses at the same stage.

Returns updated edges for the hypothesis state.
"""

from __future__ import annotations

from typing import List

from arabic_engine.pipeline.constraints.scoring import build_constraint_edges, score_support
from arabic_engine.core.enums import ConflictState
from arabic_engine.core.types import (
    ConflictEdge,
    ConstraintEdge,
    HypothesisNode,
    SupportEdge,
)


def propagate(
    hypotheses: List[HypothesisNode],
) -> tuple[list[SupportEdge], list[ConflictEdge]]:
    """Run one pass of constraint propagation.

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        All hypotheses across all stages.

    Returns
    -------
    tuple[list[SupportEdge], list[ConflictEdge]]
        Support edges and conflict edges discovered during propagation.
    """
    support = score_support(hypotheses)
    conflicts = _detect_conflicts(hypotheses)

    # Build constraint edges and convert violations to conflicts
    constraint_edges = build_constraint_edges(hypotheses)
    constraint_conflicts = _constraints_to_conflicts(constraint_edges)
    conflicts.extend(constraint_conflicts)

    return support, conflicts


def get_constraint_edges(
    hypotheses: List[HypothesisNode],
) -> List[ConstraintEdge]:
    """Return constraint edges for the given hypotheses.

    Convenience function for callers that need the constraint edges
    separately (e.g. the orchestrator stores them on HypothesisState).

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        All hypotheses across all stages.

    Returns
    -------
    list[ConstraintEdge]
        Constraint edges.
    """
    return build_constraint_edges(hypotheses)


def _constraints_to_conflicts(
    constraint_edges: List[ConstraintEdge],
) -> List[ConflictEdge]:
    """Convert constraint edge violations to conflict edges.

    STRONG/ABSOLUTE constraints become HARD conflicts.
    MODERATE constraints become SOFT conflicts.

    Parameters
    ----------
    constraint_edges : list[ConstraintEdge]
        Constraint edges from ``build_constraint_edges``.

    Returns
    -------
    list[ConflictEdge]
        Conflict edges derived from constraint violations.
    """
    from arabic_engine.core.enums import ConstraintStrength

    conflicts: List[ConflictEdge] = []
    for i, ce in enumerate(constraint_edges):
        if ce.strength in (ConstraintStrength.ABSOLUTE, ConstraintStrength.STRONG):
            state = ConflictState.HARD
        else:
            state = ConflictState.SOFT
        conflicts.append(
            ConflictEdge(
                edge_id=f"CCONF_{i}",
                node_a_ref=ce.source_ref,
                node_b_ref=ce.target_ref,
                conflict_state=state,
                justification=ce.justification,
            )
        )
    return conflicts


def _detect_conflicts(hypotheses: List[HypothesisNode]) -> List[ConflictEdge]:
    """Detect hard conflicts between hypotheses at the same stage.

    Two hypotheses conflict if they occupy the same stage and share
    the same source_refs but propose incompatible values.  In this
    first iteration, we only flag hypotheses that share exact
    source_refs within a stage.

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        All hypotheses.

    Returns
    -------
    list[ConflictEdge]
        Conflict edges between incompatible hypotheses.
    """
    conflicts: List[ConflictEdge] = []
    idx = 0

    # Group by (stage, source_refs)
    groups: dict[tuple, list[HypothesisNode]] = {}
    for h in hypotheses:
        key = (h.stage, h.source_refs)
        groups.setdefault(key, []).append(h)

    for key, group in groups.items():
        if len(group) <= 1:
            continue
        # If multiple hypotheses exist for the same source at the same stage,
        # they are in soft conflict (only one should be stabilised).
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                conflicts.append(
                    ConflictEdge(
                        edge_id=f"CONF_{idx}",
                        node_a_ref=group[i].node_id,
                        node_b_ref=group[j].node_id,
                        conflict_state=ConflictState.SOFT,
                        justification=f"Same source at stage {key[0].name}",
                    )
                )
                idx += 1

    return conflicts
