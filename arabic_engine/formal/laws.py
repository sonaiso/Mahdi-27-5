"""Axiomatic Arabic Structural Calculus v1 — القوانين الخمسة.

Five foundational laws that convert descriptive tables into generative
decision rules, forming the kernel of the calculus.

Law 1 — Rank Law (قانون الرتبة)
    Rank(x) ≠ Rank(y) → ¬DirectCompare(x, y)

Law 2 — Description-to-Decision (قانون التحويل من الوصف إلى الحكم)
    Description(x) + RuleSet → Decision(x)

Law 3 — Limit and Capacity (قانون الحد والسعة)
    L(x), C(x) → RankType(x)

Law 4 — Prior Constraint (قانون القيد السابق على التفسير)
    Ω(x) = 0 → NoInterpretation(x)

Law 5 — Layer Promotion (قانون الترقية الطبقية)
    Complete_n(x) → Requires(Level_{n+1})
"""

from __future__ import annotations

from arabic_engine.core.enums import OntologicalLayer, OntologicalMode, RankType, TriadType

# ── Law 1: Rank Law ─────────────────────────────────────────────────

def check_rank_comparable(mode_x: OntologicalMode, mode_y: OntologicalMode) -> bool:
    """Law 1 — return True only if two elements share the same ontological mode.

    Rank(x) ≠ Rank(y) → ¬DirectCompare(x, y)

    Elements from different ontological modes (e.g. SLOT vs UNIT) may
    **not** be directly compared.  This prevents confusing the structural
    zero with a letter or sukun with a syllable.

    Parameters
    ----------
    mode_x : OntologicalMode
        Mode of the first element.
    mode_y : OntologicalMode
        Mode of the second element.

    Returns
    -------
    bool
        ``True`` if direct comparison is permitted, ``False`` otherwise.
    """
    return mode_x is mode_y


# ── Law 2: Description-to-Decision ──────────────────────────────────

def apply_decision_rule(
    description: dict,
    rule_set: dict,
) -> dict:
    """Law 2 — transform a description dict into a decision dict via a rule set.

    Description(x) + RuleSet → Decision(x)

    A description becomes a *law* only when paired with a decision
    function.  This generic helper applies each key in ``rule_set``
    to the corresponding value in ``description`` and returns the
    resulting decision record.

    Parameters
    ----------
    description : dict
        Attribute dictionary for an element (e.g. from an AEU row).
    rule_set : dict
        Mapping from attribute key to a callable
        ``(value) -> decision_value``.

    Returns
    -------
    dict
        Decision record with keys matching ``rule_set`` and values
        produced by applying each rule.

    Raises
    ------
    KeyError
        If a required key from ``rule_set`` is missing in ``description``.
    """
    decision: dict = {}
    for key, rule_fn in rule_set.items():
        decision[key] = rule_fn(description[key])
    return decision


# ── Law 3: Limit and Capacity ──────────────────────────────────────

def classify_rank(
    limit_score: float,
    capacity_score: float,
    *,
    threshold: float = 0.3,
) -> RankType:
    """Law 3 — derive a :class:`RankType` from limit and capacity scores.

    L(x) = LimitScore, C(x) = CapacityScore

    * ``|L - C| ≤ threshold``  → TRANSITIONAL  (انتقالي)
    * ``L > C + threshold``    → LIMITAL       (حدّي)
    * ``C > L + threshold``    → CAPACITIVE    (سعوي)

    Parameters
    ----------
    limit_score : float
        How much the element acts as a boundary / limit.
    capacity_score : float
        How much the element acts as a container / capacity.
    threshold : float
        The margin within which the two scores are considered balanced.

    Returns
    -------
    RankType
    """
    diff = limit_score - capacity_score
    if abs(diff) <= threshold:
        return RankType.TRANSITIONAL
    if diff > 0:
        return RankType.LIMITAL
    return RankType.CAPACITIVE


# ── Law 4: Prior Constraint ─────────────────────────────────────────

def has_interpretation(omega: float) -> bool:
    """Law 4 — return True only when the constraint weight is non-zero.

    Ω(x) = 0 → NoInterpretation(x)

    No element may be interpreted if it carries no prior constraint
    weight.

    Parameters
    ----------
    omega : float
        The constraint weight Ω(x).

    Returns
    -------
    bool
        ``True`` if interpretation is possible, ``False`` otherwise.
    """
    return omega != 0.0


# ── Law 5: Layer Promotion ──────────────────────────────────────────

_LAYER_ORDER = list(OntologicalLayer)


def next_promotion_layer(current: OntologicalLayer) -> OntologicalLayer | None:
    """Law 5 — return the next ontological layer, or None at the top.

    Complete_n(x) → Requires(Level_{n+1})

    Every local completion is incomplete until it is promoted to the
    next layer:

    * CELL       → TRANSITION
    * TRANSITION → SYLLABLE
    * SYLLABLE   → ROOT
    * ROOT       → PATTERN
    * PATTERN    → (top — returns None)

    Parameters
    ----------
    current : OntologicalLayer
        The element's current layer.

    Returns
    -------
    OntologicalLayer | None
        The next layer, or ``None`` if already at the top (PATTERN).
    """
    idx = _LAYER_ORDER.index(current)
    if idx + 1 < len(_LAYER_ORDER):
        return _LAYER_ORDER[idx + 1]
    return None


def validate_triad_typed(triad_type: TriadType, node_a: str, node_b: str, node_c: str) -> bool:
    """Validate that a triad has three distinct members and a declared type.

    This enforces the *Triad Type Law* (قانون نوع المثلث):
    every triad must carry its formal type before entering computation.

    Parameters
    ----------
    triad_type : TriadType
        The declared type of the triad.
    node_a, node_b, node_c : str
        The three member identifiers.

    Returns
    -------
    bool
        ``True`` if the triad is non-degenerate and properly typed.
    """
    if not isinstance(triad_type, TriadType):
        return False
    return len({node_a, node_b, node_c}) == 3
