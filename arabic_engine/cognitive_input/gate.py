"""Gate logic — بوابات العبور بين الطبقات العقلية.

Each transition Tᵢ: Uᵢ → Uᵢ₊₁ is guarded by a gate that enforces:

1. Membership: Cᵢ(x) = 1  (Art. 42)
2. Minimum completeness: Mᵢ(x) ≥ θᵢ  (Art. 43)
3. No blocker: ¬Fᵢ(x)  (Art. 45)

The gate decision is one of: PASS, REJECT, SUSPEND, COMPLETE.
"""

from __future__ import annotations

from arabic_engine.core.enums import CognitiveLayerID, LayerGateDecision
from arabic_engine.core.types import CognitiveGateRecord

# ── Default thresholds per layer (Art. 43) ──────────────────────────

_DEFAULT_THRESHOLDS: dict[CognitiveLayerID, float] = {
    CognitiveLayerID.UNICODE_RAW: 0.0,
    CognitiveLayerID.ATOMIZED: 0.5,
    CognitiveLayerID.DIFFERENTIATED: 0.5,
    CognitiveLayerID.NORMALIZED: 0.5,
    CognitiveLayerID.DESIGNATED: 0.5,
    CognitiveLayerID.INITIAL_CONCEPTION: 0.6,
    CognitiveLayerID.DISCIPLINED_CONCEPTION: 0.7,
    CognitiveLayerID.SEMANTIC_SUBJECT: 0.7,
    CognitiveLayerID.JUDGEMENT_READY: 0.8,
}


def evaluate_gate(
    from_layer: CognitiveLayerID,
    to_layer: CognitiveLayerID,
    membership: bool,
    completeness: float,
    has_blocker: bool,
    *,
    reason: str = "",
    evidence: tuple[str, ...] = (),
    threshold: float | None = None,
) -> CognitiveGateRecord:
    """Evaluate a gate transition between two cognitive layers.

    Implements the general crossing condition (Art. 45):

        Cᵢ(x) = 1  ∧  Mᵢ(x) ≥ θᵢ  ∧  ¬Fᵢ(x)

    Parameters
    ----------
    from_layer : CognitiveLayerID
        Source layer.
    to_layer : CognitiveLayerID
        Target layer.
    membership : bool
        Whether the element belongs to the source layer (Cᵢ(x)).
    completeness : float
        Minimum completeness score (Mᵢ(x)).
    has_blocker : bool
        Whether a blocking condition exists (Fᵢ(x)).
    reason : str
        Human-readable reason for the decision.
    evidence : tuple[str, ...]
        Supporting evidence references.
    threshold : float or None
        Override for the layer threshold θᵢ.  If *None*, the default
        threshold for *from_layer* is used.

    Returns
    -------
    CognitiveGateRecord
        The gate decision record.
    """
    theta = threshold if threshold is not None else _DEFAULT_THRESHOLDS.get(
        from_layer, 0.5
    )

    # Determine decision (Art. 45)
    if not membership:
        decision = LayerGateDecision.REJECT
        if not reason:
            reason = (
                f"Element does not belong to layer {from_layer.name} "
                f"(Cᵢ(x) = 0)"
            )
    elif has_blocker:
        decision = LayerGateDecision.REJECT
        if not reason:
            reason = (
                f"Blocking condition at layer {from_layer.name} "
                f"(Fᵢ(x) = True)"
            )
    elif completeness < theta:
        decision = LayerGateDecision.SUSPEND
        if not reason:
            reason = (
                f"Incomplete at layer {from_layer.name}: "
                f"Mᵢ(x) = {completeness:.2f} < θᵢ = {theta:.2f}"
            )
    elif completeness >= 1.0:
        decision = LayerGateDecision.COMPLETE
        if not reason:
            reason = f"Layer {from_layer.name} fully complete (Mᵢ(x) = 1.0)"
    else:
        decision = LayerGateDecision.PASS
        if not reason:
            reason = (
                f"Minimum completeness met at layer {from_layer.name}: "
                f"Mᵢ(x) = {completeness:.2f} ≥ θᵢ = {theta:.2f}"
            )

    gate_id = f"G_{from_layer.name}_to_{to_layer.name}"

    return CognitiveGateRecord(
        gate_id=gate_id,
        from_layer=from_layer,
        to_layer=to_layer,
        decision=decision,
        completeness_score=completeness,
        threshold=theta,
        has_blocker=has_blocker,
        reason=reason,
        evidence=evidence,
    )


def is_valid_transition(
    from_layer: CognitiveLayerID,
    to_layer: CognitiveLayerID,
) -> bool:
    """Check whether a transition from *from_layer* to *to_layer* is valid.

    Only transitions to the immediately next layer are permitted (Art. 37).
    Any skip is a jump violation.

    Returns
    -------
    bool
        ``True`` if the transition is valid (adjacent layers), ``False``
        if it constitutes a jump.
    """
    order = list(CognitiveLayerID)
    try:
        from_idx = order.index(from_layer)
        to_idx = order.index(to_layer)
    except ValueError:
        return False
    return to_idx == from_idx + 1


def detect_jump_violations(
    from_layer: CognitiveLayerID,
    to_layer: CognitiveLayerID,
) -> list[str]:
    """Return a list of jump-violation descriptions if any exist.

    Prohibited jumps (Art. 35):
    - Unicode → meaning
    - Unicode → admitted lexeme
    - Unicode → concept
    - Unicode → judgement
    - Normalization → judgement
    - Initial conception → judgement
    - Conceptual encoding → judgement without subject liberation

    Returns
    -------
    list[str]
        Empty if no violations; otherwise descriptive strings.
    """
    violations: list[str] = []
    order = list(CognitiveLayerID)
    try:
        from_idx = order.index(from_layer)
        to_idx = order.index(to_layer)
    except ValueError:
        violations.append(
            f"Unknown layer in transition: {from_layer} → {to_layer}"
        )
        return violations

    if to_idx > from_idx + 1:
        skipped = [order[i].name for i in range(from_idx + 1, to_idx)]
        violations.append(
            f"Jump from {from_layer.name} to {to_layer.name} "
            f"skips required layers: {', '.join(skipped)}"
        )

    if to_idx < from_idx:
        violations.append(
            f"Backward transition from {from_layer.name} to "
            f"{to_layer.name} is not permitted"
        )

    return violations
