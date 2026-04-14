"""Lexeme builder — بناء المفرد.

Constructs a formal :class:`LexemeNode` from a :class:`LexicalClosure`
together with an optional :class:`WeightNode` or :class:`ClosedTemplateNode`.

Public API
----------
build_lexeme            Construct a LexemeNode.
determine_independence  Determine independence type.
compute_readiness       Compute readiness score 0–1.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import (
    POS,
    IndependenceType,
)
from arabic_engine.core.types import (
    ClosedTemplateNode,
    LexemeNode,
    LexicalClosure,
    WeightNode,
)

# ── Internal counter ────────────────────────────────────────────────
_lexeme_counter = 0


def _next_lexeme_id() -> str:
    global _lexeme_counter
    _lexeme_counter += 1
    return f"LEX_{_lexeme_counter:04d}"


# ── Public API ──────────────────────────────────────────────────────


def build_lexeme(
    closure: LexicalClosure,
    weight: Optional[WeightNode] = None,
    template: Optional[ClosedTemplateNode] = None,
) -> LexemeNode:
    """Construct a formal :class:`LexemeNode`.

    Parameters
    ----------
    closure : LexicalClosure
        The morphological record from L2.
    weight : WeightNode, optional
        The weight node (for nouns and verbs).
    template : ClosedTemplateNode, optional
        The closed template (for particles/built forms).

    Returns
    -------
    LexemeNode
    """
    concept_type = _infer_concept_type(closure)
    independence = determine_independence(closure.pos, concept_type)
    weight_ref = weight.id if weight else None
    template_ref = template.id if template else None
    root_ref = ":".join(closure.root) if closure.root else None

    node = LexemeNode(
        id=_next_lexeme_id(),
        surface_form=closure.surface,
        normalized_form=closure.lemma,
        root_ref=root_ref,
        weight_ref=weight_ref,
        closed_template_ref=template_ref,
        independence_type=independence,
        concept_type=concept_type,
        pos_final=closure.pos,
        readiness_score=0.0,
    )
    score = compute_readiness(node)
    return LexemeNode(
        id=node.id,
        surface_form=node.surface_form,
        normalized_form=node.normalized_form,
        root_ref=node.root_ref,
        weight_ref=node.weight_ref,
        closed_template_ref=node.closed_template_ref,
        independence_type=node.independence_type,
        concept_type=node.concept_type,
        pos_final=node.pos_final,
        readiness_score=score,
    )


def determine_independence(pos: POS, concept_type: str) -> IndependenceType:
    """Determine the independence type of a lexeme.

    Nouns and verbs are meaning-independent; particles are
    function-independent; unknown POS yields dependent.
    """
    if pos in (POS.ISM, POS.FI3L, POS.SIFA, POS.ZARF, POS.DAMIR):
        return IndependenceType.MEANING_INDEPENDENT
    if pos == POS.HARF:
        return IndependenceType.FUNCTION_INDEPENDENT
    return IndependenceType.DEPENDENT


def compute_readiness(lexeme: LexemeNode) -> float:
    """Compute readiness score 0–1 for composition.

    The score reflects how many of the required fields are populated
    before the lexeme can enter the composition layer.
    """
    score = 0.0
    # 1. Surface form present
    if lexeme.surface_form:
        score += 0.15
    # 2. Normalized form present
    if lexeme.normalized_form:
        score += 0.10
    # 3. Root or closed template reference present
    if lexeme.root_ref or lexeme.closed_template_ref:
        score += 0.15
    # 4. Weight or template reference present
    if lexeme.weight_ref or lexeme.closed_template_ref:
        score += 0.15
    # 5. Concept type assigned
    if lexeme.concept_type:
        score += 0.15
    # 6. POS finalised (not UNKNOWN)
    if lexeme.pos_final != POS.UNKNOWN:
        score += 0.15
    # 7. Independence type is not DEPENDENT
    if lexeme.independence_type != IndependenceType.DEPENDENT:
        score += 0.15
    return round(score, 4)


# ── Internal helpers ────────────────────────────────────────────────


def _infer_concept_type(closure: LexicalClosure) -> str:
    """Infer the concept type from a LexicalClosure."""
    pos = closure.pos
    if pos == POS.ISM:
        return "ذات"
    if pos == POS.FI3L:
        return "حدث"
    if pos == POS.SIFA:
        return "صفة"
    if pos == POS.HARF:
        return "نسبة"
    if pos == POS.ZARF:
        return "ظرف"
    if pos == POS.DAMIR:
        return "إشارة"
    return "غير_محدد"
