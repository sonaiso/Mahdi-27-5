"""Composition readiness gate — بوابة جاهزية التركيب.

No lexeme may enter the composition/syntax layer without passing
through this gate.

Public API
----------
check_composition_readiness  Produce a CompositionReadyNode.
validate_readiness           Boolean gate check.
"""

from __future__ import annotations

from arabic_engine.core.enums import POS
from arabic_engine.core.types import CompositionReadyNode, LexemeNode


def check_composition_readiness(lexeme: LexemeNode) -> CompositionReadyNode:
    """Gate: has POS, has concept type, has weight/template?

    Parameters
    ----------
    lexeme : LexemeNode
        The lexeme to check.

    Returns
    -------
    CompositionReadyNode
    """
    has_pos = lexeme.pos_final != POS.UNKNOWN
    has_concept = bool(lexeme.concept_type) and lexeme.concept_type != "غير_محدد"
    has_weight = bool(lexeme.weight_ref) or bool(lexeme.closed_template_ref)
    ready = has_pos and has_concept and has_weight

    return CompositionReadyNode(
        lexeme_ref=lexeme.id,
        pos_final=lexeme.pos_final,
        concept_type=lexeme.concept_type,
        weight_or_template=lexeme.weight_ref or lexeme.closed_template_ref or "",
        ready=ready,
    )


def validate_readiness(node: CompositionReadyNode) -> bool:
    """Boolean gate check.

    Parameters
    ----------
    node : CompositionReadyNode
        The composition readiness node.

    Returns
    -------
    bool
        True if the lexeme is ready for composition.
    """
    return node.ready
