"""Foundational calculus operations — الحساب البنيوي التأسيسي.

Five primitive operations that convert the axiomatic architecture into
a computable calculus:

    occupy(slot, occupant)     — fill a zero-slot with a positive value
    validate(core, constraint) — check whether a core satisfies its guard
    promote(layer, rule)       — advance an element to a higher layer
    compose(units)             — combine units into a non-degenerate triad
    infer(proposition, engine) — derive new propositions via inference

These functions are *pure*: they return new frozen records and never
mutate their inputs.
"""

from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

from arabic_engine.core.enums import (
    ConditionToken,
    OntologicalLayer,
    SlotState,
    TriadType,
)
from arabic_engine.core.types import (
    EssenceConditionPair,
    InferenceResult,
    LayerPromotionRule,
    Proposition,
    StructuralSlot,
    TriadRecord,
    ZeroSlotRecord,
)

# ── occupy — إشغال الموضع ──────────────────────────────────────────


def occupy_zero_slot(
    slot: ZeroSlotRecord,
    occupant_id: str,
) -> ZeroSlotRecord:
    """Fill a :class:`ZeroSlotRecord` with its first positive occupancy.

    Implements A2::

        ZeroSlot(z) ∧ Fillable(z) → ∃x Occupies(x, z)

    Parameters
    ----------
    slot : ZeroSlotRecord
        A slot in EMPTY state (``is_fillable`` must be True).
    occupant_id : str
        The identifier of the element that fills the slot.

    Returns
    -------
    ZeroSlotRecord
        A new record with ``state=OCCUPIED`` and ``occupant_id`` set.

    Raises
    ------
    ValueError
        If the slot is BLOCKED or already OCCUPIED.
    """
    if not slot.is_fillable:
        raise ValueError(
            f"Slot '{slot.slot_id}' is BLOCKED and cannot be filled."
        )
    if slot.is_occupied:
        raise ValueError(
            f"Slot '{slot.slot_id}' is already OCCUPIED by "
            f"'{slot.occupant_id}'."
        )
    return replace(slot, state=SlotState.OCCUPIED, occupant_id=occupant_id)


def occupy_structural_slot(
    slot: StructuralSlot,
    occupant_id: str,
) -> StructuralSlot:
    """Fill a :class:`StructuralSlot` with a value.

    Parameters
    ----------
    slot : StructuralSlot
        A slot that is fillable and currently empty.
    occupant_id : str
        The identifier of the element that fills the slot.

    Returns
    -------
    StructuralSlot
        A new record with ``occupant_id`` set.

    Raises
    ------
    ValueError
        If the slot is not fillable or already occupied.
    """
    if not slot.fillable:
        raise ValueError(
            f"Slot '{slot.slot_id}' is not fillable."
        )
    if slot.is_occupied:
        raise ValueError(
            f"Slot '{slot.slot_id}' is already occupied by "
            f"'{slot.occupant_id}'."
        )
    return replace(slot, occupant_id=occupant_id)


# ── validate — التحقق من الجوهر + القيد ─────────────────────────────


def validate(
    pair: EssenceConditionPair,
    *,
    context_tokens: Optional[frozenset[ConditionToken]] = None,
) -> bool:
    """Check whether an essence–condition pair is satisfied.

    The rule is::

        Cond(x) = None  → True  (unconstrained)
        Cond(x) ∈ ctx   → True  (constraint met)
        otherwise        → False

    Parameters
    ----------
    pair : EssenceConditionPair
        The ``(slot, value, constraint)`` triple.
    context_tokens : frozenset[ConditionToken] | None
        The set of conditions currently active in context.
        When ``None``, defaults to the empty set.

    Returns
    -------
    bool
        ``True`` when the constraint is absent or satisfied.
    """
    if not pair.has_constraint:
        return True
    if context_tokens is None:
        return False
    return pair.constraint in context_tokens


# ── promote — الترقية الطبقية ────────────────────────────────────────


def promote(
    current_layer: OntologicalLayer,
    rule: LayerPromotionRule,
) -> OntologicalLayer:
    """Promote an element from one ontological layer to the next.

    Implements A4::

        L_n ≢ L_{n+1}
        Complete(x ∈ L_n) → RequiresHigherContext(x)

    Parameters
    ----------
    current_layer : OntologicalLayer
        The element's current layer (must match ``rule.source_layer``).
    rule : LayerPromotionRule
        The promotion rule to apply.

    Returns
    -------
    OntologicalLayer
        The new (higher) layer after promotion.

    Raises
    ------
    ValueError
        If the rule is invalid or the source layer doesn't match.
    """
    if not rule.is_valid:
        raise ValueError(
            f"Rule '{rule.rule_id}' is invalid: target layer "
            f"({rule.target_layer}) is not higher than source "
            f"({rule.source_layer})."
        )
    if current_layer is not rule.source_layer:
        raise ValueError(
            f"Current layer ({current_layer}) does not match rule "
            f"source ({rule.source_layer})."
        )
    return rule.target_layer


# ── compose — تركيب الثلاثية ─────────────────────────────────────────


def compose(
    node_a: str,
    node_b: str,
    node_c: str,
    *,
    triad_id: str = "TD_AUTO",
    triad_type: TriadType = TriadType.GENERATIVE,
    layer: OntologicalLayer = OntologicalLayer.CELL,
) -> TriadRecord:
    """Compose three elements into a non-degenerate :class:`TriadRecord`.

    Implements A3::

        CompleteDistinction(x, y) → ∃t ≠ x, y
        MinimalCompleteDistinction = 3

    Parameters
    ----------
    node_a, node_b, node_c : str
        The three element identifiers.
    triad_id : str
        Unique identifier for the resulting triad.
    triad_type : TriadType
        Formal type of the triad (default ``GENERATIVE``).
    layer : OntologicalLayer
        Ontological layer (default ``CELL``).

    Returns
    -------
    TriadRecord
        A new, non-degenerate triadic record.

    Raises
    ------
    ValueError
        If any two of the three elements coincide (degenerate triad).
    """
    if len({node_a, node_b, node_c}) < 3:
        raise ValueError(
            f"Degenerate triad: at least two members coincide "
            f"({node_a!r}, {node_b!r}, {node_c!r})."
        )
    return TriadRecord(
        triad_id=triad_id,
        triad_type=triad_type,
        node_a=node_a,
        node_b=node_b,
        node_c=node_c,
        layer=layer,
    )


# ── infer — الاستدلال ────────────────────────────────────────────────


def infer(
    propositions: List[Proposition],
    inference_engine: object,
) -> List[InferenceResult]:
    """Derive new propositions from existing ones via the inference engine.

    This is a thin wrapper that enforces the calling convention:

    * Takes a list of :class:`Proposition` objects.
    * Delegates to ``inference_engine.run(propositions)``.
    * Returns a list of :class:`InferenceResult` objects.

    Parameters
    ----------
    propositions : list[Proposition]
        The propositions to reason about.
    inference_engine : object
        Any object that exposes a ``run(propositions)`` method
        returning a list of :class:`InferenceResult`.

    Returns
    -------
    list[InferenceResult]
        Derived propositions (may be empty).

    Raises
    ------
    TypeError
        If the engine does not have a ``run`` method.
    """
    if not hasattr(inference_engine, "run"):
        raise TypeError(
            "inference_engine must have a 'run' method."
        )
    return inference_engine.run(propositions)  # type: ignore[union-attr]
