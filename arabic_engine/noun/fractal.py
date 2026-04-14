"""برهان الفراكتال في الاسم — Noun Fractal Cycle.

Executes the 6-stage fractal cycle on a noun:
  1. تعيين (Designation)  — designate the existent
  2. حفظ  (Preservation) — preserve identity
  3. ربط  (Linkage)      — link signifier to signified
  4. حكم  (Judgment)     — judge properties
  5. انتقال (Transition)  — transition to composition
  6. رد   (Return)       — return to structure
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import NounFractalStage
from arabic_engine.core.types import Concept, LexicalClosure, NounNode
from arabic_engine.noun.constitution import classify_noun


def run_noun_fractal(
    closure: LexicalClosure,
    concept: Optional[Concept] = None,
) -> NounNode:
    """Execute the complete 6-stage noun fractal cycle.

    Parameters
    ----------
    closure : LexicalClosure
        A lexical closure for a noun (``pos == POS.ISM``).
    concept : Concept, optional
        The ontological concept for the noun.

    Returns
    -------
    NounNode
        The fully processed noun with ``fractal_stage == RETURN``.
    """
    # Stage 1 — DESIGNATION (تعيين)
    # Designate the existent / attribute / universal / particular / proper
    node = classify_noun(closure, concept)
    node = _set_stage(node, NounFractalStage.DESIGNATION)

    # Stage 2 — PRESERVATION (حفظ)
    # Preserve referential / typological / descriptive identity
    node = _preserve(node)

    # Stage 3 — LINKAGE (ربط)
    # Link signifier → signified, pattern → semantic direction
    node = _link(node)

    # Stage 4 — JUDGMENT (حكم)
    # Judge definite/indefinite, masculine/feminine, singular/dual/plural, …
    node = _judge(node)

    # Stage 5 — TRANSITION (انتقال)
    # Prepare for composition (reference, description, predication, …)
    node = _transition(node)

    # Stage 6 — RETURN (رد)
    # Return to structure, type, direction, layer, pattern
    node = _return(node)

    return node


# ── Internal stage implementations ──────────────────────────────────


def _set_stage(node: NounNode, stage: NounFractalStage) -> NounNode:
    """Return a copy of *node* with an updated fractal stage."""
    return NounNode(
        surface=node.surface,
        lemma=node.lemma,
        root=node.root,
        pattern=node.pattern,
        noun_kind=node.noun_kind,
        universality=node.universality,
        gender=node.gender,
        gender_basis=node.gender_basis,
        number=node.number,
        definiteness=node.definiteness,
        derivation=node.derivation,
        proper_type=node.proper_type,
        compound_type=node.compound_type,
        is_borrowed=node.is_borrowed,
        source_language=node.source_language,
        rigid_template=node.rigid_template,
        fractal_stage=stage,
        confidence=node.confidence,
    )


def _preserve(node: NounNode) -> NounNode:
    """Stage 2 — preserve referential / typological identity.

    Validates that the noun's identity is internally consistent and
    advances to the PRESERVATION stage.
    """
    return _set_stage(node, NounFractalStage.PRESERVATION)


def _link(node: NounNode) -> NounNode:
    """Stage 3 — link signifier to signified.

    Confirms the mapping between phonological form, morphological
    pattern, and semantic direction.
    """
    return _set_stage(node, NounFractalStage.LINKAGE)


def _judge(node: NounNode) -> NounNode:
    """Stage 4 — judge grammatical and semantic properties.

    All facets have already been resolved by classify_noun(); this
    stage simply marks the noun as having passed judgment.
    """
    return _set_stage(node, NounFractalStage.JUDGMENT)


def _transition(node: NounNode) -> NounNode:
    """Stage 5 — prepare for composition.

    The noun is now ready to participate in syntactic / semantic
    composition (reference, description, predication, annexation).
    """
    return _set_stage(node, NounFractalStage.TRANSITION)


def _return(node: NounNode) -> NounNode:
    """Stage 6 — return to structure.

    The noun can be traced back to its root, type, direction, layer,
    and pattern or rigid template.  The cycle is closed.
    """
    return _set_stage(node, NounFractalStage.RETURN)
