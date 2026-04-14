"""Judgment construction and evaluation (التعريفان 7 و 8).

J : G_s × G_m × D → P   (judgment)
E : P × W → V            (evaluation)

The separation between *judgment* and *evaluation* mirrors the
manuscript's distinction: judging that something *exists* may be
certain, but judging its *truth or quality* is fallible and revisable.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import (
    POS,
    GuidanceState,
    TimeRef,
    TruthState,
)
from arabic_engine.core.types import (
    Concept,
    DalalaLink,
    EvalResult,
    LexicalClosure,
    Proposition,
)

# ── Judgment ────────────────────────────────────────────────────────

def build_proposition(
    closures: List[LexicalClosure],
    concepts: List[Concept],
    links: List[DalalaLink],
) -> Proposition:
    """Compose a :class:`~arabic_engine.core.types.Proposition` from the analysis layers.

    Applies a minimal heuristic over the token list:

    * First verb closure → ``predicate`` (and sets ``time`` from its pattern).
    * First noun closure → ``subject`` (فاعل).
    * Second noun closure → ``object`` (مفعول به).

    Args:
        closures: Lexical closures for the sentence tokens.
        concepts: Corresponding concept nodes (not used directly, kept
            for API symmetry with other pipeline steps).
        links: Dalāla links (not used directly; available for future
            refinement).

    Returns:
        A :class:`~arabic_engine.core.types.Proposition` with ``subject``,
        ``predicate``, ``obj``, ``time``, and ``polarity`` populated.
        Fields that cannot be filled are left as empty strings or their
        enum defaults.
    """
    subject = ""
    predicate = ""
    obj = ""
    time = TimeRef.UNSPECIFIED
    polarity = True

    for cl in closures:
        if cl.pos == POS.FI3L and not predicate:
            predicate = cl.lemma
            # Simple tense detection from pattern
            if cl.pattern in ("فَعَلَ",):
                time = TimeRef.PAST
            elif cl.pattern in ("يَفْعَلُ",):
                time = TimeRef.PRESENT
        elif cl.pos == POS.ISM and not subject:
            subject = cl.lemma
        elif cl.pos == POS.ISM and not obj:
            obj = cl.lemma

    return Proposition(
        subject=subject,
        predicate=predicate,
        obj=obj,
        time=time,
        polarity=polarity,
    )


# ── Evaluation ──────────────────────────────────────────────────────

def evaluate(
    proposition: Proposition,
    links: List[DalalaLink],
) -> EvalResult:
    """Evaluate a proposition, producing truth/guidance/confidence.

    The truth state is derived from the average confidence of all
    dalāla links using the following thresholds:

    ================  ============
    avg_confidence    TruthState
    ================  ============
    ≥ 0.9             CERTAIN
    0.7 – 0.9         PROBABLE
    0.4 – 0.7         POSSIBLE
    < 0.4             DOUBTFUL
    ================  ============

    Guidance state defaults to ``NOT_APPLICABLE`` for declarative
    propositions; normative evaluation requires additional context.

    Args:
        proposition: The proposition to evaluate.
        links: Dalāla links whose confidence scores drive the result.
            An empty list yields confidence 0.0 and ``DOUBTFUL``.

    Returns:
        An :class:`~arabic_engine.core.types.EvalResult` with
        ``truth_state``, ``guidance_state``, and ``confidence`` set.
    """
    if links:
        avg_conf = sum(lk.confidence for lk in links) / len(links)
    else:
        avg_conf = 0.0

    if avg_conf >= 0.9:
        truth = TruthState.CERTAIN
    elif avg_conf >= 0.7:
        truth = TruthState.PROBABLE
    elif avg_conf >= 0.4:
        truth = TruthState.POSSIBLE
    else:
        truth = TruthState.DOUBTFUL

    return EvalResult(
        proposition=proposition,
        truth_state=truth,
        guidance_state=GuidanceState.NOT_APPLICABLE,
        confidence=round(avg_conf, 4),
    )
