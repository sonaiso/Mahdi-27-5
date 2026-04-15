"""Constraint scoring — تقييم الدعم.

Assigns support scores to hypotheses based on inter-layer consistency
and builds constraint edges that enforce compatibility rules.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, ConstraintStrength
from arabic_engine.core.types import ConstraintEdge, HypothesisNode, SupportEdge

# ── Compatibility rules: role → expected case ────────────────────────
_ROLE_CASE_COMPAT: dict[str, frozenset[str]] = {
    "فاعل": frozenset({"رفع"}),
    "مبتدأ": frozenset({"رفع"}),
    "خبر": frozenset({"رفع"}),
    "مفعول": frozenset({"نصب"}),
    "حرف_جر": frozenset({"مبني"}),
    "فعل": frozenset({"مبني"}),
    "مضاف_إليه": frozenset({"جر"}),
    "اسم_إن": frozenset({"نصب"}),
    "خبر_كان": frozenset({"نصب"}),
    "حال": frozenset({"نصب"}),
    "تمييز": frozenset({"نصب"}),
    "منادى": frozenset({"بناء", "نصب", "مبني"}),
    "مجرور": frozenset({"جر"}),
}

# ── Invariant (مبني) words cannot have رفع/نصب/جر ──────────────────
_DECLINED_CASES = frozenset({"رفع", "نصب", "جر"})


def score_support(hypotheses: List[HypothesisNode]) -> List[SupportEdge]:
    """Create support edges between hypotheses that share source refs.

    When two hypotheses at different stages reference the same upstream
    node, a support edge is created linking them.  This is the simplest
    form of support scoring: shared provenance = mutual support.

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        All hypotheses across all stages.

    Returns
    -------
    list[SupportEdge]
        Support edges between hypotheses with overlapping sources.
    """
    edges: List[SupportEdge] = []
    idx = 0

    # Build a reverse index: source_ref → list of node_ids
    source_index: dict[str, list[str]] = {}
    for h in hypotheses:
        for ref in h.source_refs:
            source_index.setdefault(ref, []).append(h.node_id)

    # For each shared source, create support edges between the nodes
    for source_ref, node_ids in source_index.items():
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                edges.append(
                    SupportEdge(
                        edge_id=f"SUP_{idx}",
                        supporter_ref=node_ids[i],
                        target_ref=node_ids[j],
                        weight=1.0,
                        justification=f"shared source {source_ref}",
                    )
                )
                idx += 1

    return edges


def build_constraint_edges(
    hypotheses: List[HypothesisNode],
) -> List[ConstraintEdge]:
    """Build constraint edges from hypothesis relationships.

    Implements two types of constraints:

    1. **Compatibility constraints**: role ↔ case must be compatible
       (e.g. فاعل → رفع, مفعول → نصب)
    2. **Declension constraints**: مبني words cannot have رفع/نصب/جر

    Parameters
    ----------
    hypotheses : list[HypothesisNode]
        All hypotheses across all stages.

    Returns
    -------
    list[ConstraintEdge]
        Constraint edges enforcing compatibility.
    """
    edges: List[ConstraintEdge] = []
    idx = 0

    # Index hypotheses by node_id for quick lookup
    by_id: dict[str, HypothesisNode] = {h.node_id: h for h in hypotheses}

    # Index by stage
    case_hyps = [h for h in hypotheses if h.stage == ActivationStage.CASE]
    axis_hyps = [h for h in hypotheses if h.stage == ActivationStage.AXIS]

    # 1. Role ↔ Case compatibility constraints
    for case_h in case_hyps:
        role = str(case_h.get("role", ""))
        case_state = str(case_h.get("case_state", ""))
        expected = _ROLE_CASE_COMPAT.get(role)

        if expected is not None and case_state not in expected:
            # Find the role hypothesis this case came from
            for ref in case_h.source_refs:
                if ref in by_id:
                    edges.append(
                        ConstraintEdge(
                            edge_id=f"CONSTR_{idx}",
                            source_ref=ref,
                            target_ref=case_h.node_id,
                            relation="role_case_incompatible",
                            strength=ConstraintStrength.STRONG,
                            justification=(
                                f"Role '{role}' expects case "
                                f"{expected} but got '{case_state}'"
                            ),
                        )
                    )
                    idx += 1

    # 2. Declension (مبني/معرب) ↔ Case constraints
    # If an axis says مبني, then case should not be رفع/نصب/جر
    axis_index: dict[str, str] = {}
    for ax in axis_hyps:
        if str(ax.get("axis_name", "")) == "مبني/معرب":
            # Map the concept source to its declension value
            for ref in ax.source_refs:
                axis_index[ref] = str(ax.get("axis_value", ""))

    for case_h in case_hyps:
        case_state = str(case_h.get("case_state", ""))
        # Find the concept this case relates to (via role → concept chain)
        for ref in case_h.source_refs:
            role_h = by_id.get(ref)
            if role_h is not None:
                for rref in role_h.source_refs:
                    decl = axis_index.get(rref, "")
                    if decl == "مبني" and case_state in _DECLINED_CASES:
                        edges.append(
                            ConstraintEdge(
                                edge_id=f"CONSTR_{idx}",
                                source_ref=ref,
                                target_ref=case_h.node_id,
                                relation="declension_case_incompatible",
                                strength=ConstraintStrength.MODERATE,
                                justification=(
                                    f"Word is مبني but case is "
                                    f"'{case_state}' (should be مبني)"
                                ),
                            )
                        )
                        idx += 1

    return edges
