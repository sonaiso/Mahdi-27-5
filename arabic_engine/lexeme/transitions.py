"""Formal transition rules — قواعد الانتقال الرسمية.

Implements the transition table from §12 of the Rational Self Ontology v1.
Each transition function moves data from one layer to the next in the
canonical chain:

    Unicode → Material → Root/Weight → Lexeme → POS → CompositionReady

Public API
----------
transition_unicode_to_material
transition_material_to_root_weight
transition_root_weight_to_lexeme
transition_lexeme_to_pos
transition_pos_to_composition
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

from arabic_engine.core.enums import POS, LexemeLayer
from arabic_engine.core.types import (
    BareLexicalMaterial,
    ClosedTemplateNode,
    CompositionReadyNode,
    LexemeNode,
    LexicalClosure,
    NounNode,
    ParticleNode,
    VerbNode,
    WeightNode,
)
from arabic_engine.lexeme.composition_gate import check_composition_readiness
from arabic_engine.lexeme.lexeme_builder import build_lexeme
from arabic_engine.lexeme.pos_finalization import auto_finalize
from arabic_engine.lexeme.weight import extract_weight


def transition_unicode_to_material(text: str) -> BareLexicalMaterial:
    """Transition from Unicode/grapheme layer to bare material.

    Parameters
    ----------
    text : str
        Raw Unicode text (single token).

    Returns
    -------
    BareLexicalMaterial
    """
    return BareLexicalMaterial(
        material=text,
        source_layer=LexemeLayer.BARE_MATERIAL,
        grapheme_count=len(text),
    )


def transition_material_to_root_weight(
    material: BareLexicalMaterial,
    root: Tuple[str, ...] = (),
    pattern: str = "",
) -> Tuple[Optional[Tuple[str, ...]], Optional[WeightNode]]:
    """Transition from bare material to root + weight.

    Parameters
    ----------
    material : BareLexicalMaterial
        The bare material.
    root : tuple of str
        Pre-identified root radicals.
    pattern : str
        Optional pattern hint.

    Returns
    -------
    tuple of (root, WeightNode or None)
    """
    if not root:
        return (None, None)
    weight = extract_weight(root, material.material, pattern)
    return (root, weight)


def transition_root_weight_to_lexeme(
    closure: LexicalClosure,
    weight: Optional[WeightNode] = None,
    template: Optional[ClosedTemplateNode] = None,
) -> LexemeNode:
    """Transition from root/weight to a LexemeNode.

    Parameters
    ----------
    closure : LexicalClosure
        The morphological record.
    weight : WeightNode, optional
        The weight node.
    template : ClosedTemplateNode, optional
        The closed template.

    Returns
    -------
    LexemeNode
    """
    return build_lexeme(closure, weight=weight, template=template)


def transition_lexeme_to_pos(
    lexeme: LexemeNode,
) -> Union[NounNode, VerbNode, ParticleNode]:
    """Transition from LexemeNode to a POS-specialised node.

    Parameters
    ----------
    lexeme : LexemeNode
        The lexeme to finalise.

    Returns
    -------
    NounNode | VerbNode | ParticleNode
    """
    return auto_finalize(lexeme)


def transition_pos_to_composition(
    lexeme: LexemeNode,
) -> CompositionReadyNode:
    """Transition from POS-finalised lexeme to composition readiness.

    Parameters
    ----------
    lexeme : LexemeNode
        The POS-finalised lexeme.

    Returns
    -------
    CompositionReadyNode
    """
    return check_composition_readiness(lexeme)
