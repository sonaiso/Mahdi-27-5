"""Rational Self ↔ Lexeme bridge — جسر الذات العاقلة والمفرد.

The rational self is the epistemic agent that drives the chain:
perception → designation → classification → judgement → composition.

This module provides the bridge between the :class:`RationalSelfRecord`
and the lexeme construction pipeline.

Public API
----------
self_perceives_material     Self perceives raw text as bare material.
self_identifies_weight      Self applies weight recognition.
self_builds_lexeme          Self constructs a lexeme.
self_prepares_composition   Self prepares for composition.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import POS, LexemeLayer
from arabic_engine.core.types import (
    BareLexicalMaterial,
    CompositionReadyNode,
    LexemeNode,
    LexicalClosure,
    RationalSelfRecord,
    WeightNode,
)
from arabic_engine.lexeme.composition_gate import check_composition_readiness
from arabic_engine.lexeme.lexeme_builder import build_lexeme
from arabic_engine.lexeme.weight import extract_weight


def self_perceives_material(
    self_record: RationalSelfRecord,
    material: str,
) -> BareLexicalMaterial:
    """Self perceives raw Unicode/text as bare material.

    The rational self applies its perception mode to transform raw
    text into a :class:`BareLexicalMaterial` — the first step of the
    epistemic chain.

    Parameters
    ----------
    self_record : RationalSelfRecord
        The rational self performing perception.
    material : str
        The raw text to perceive.

    Returns
    -------
    BareLexicalMaterial
    """
    return BareLexicalMaterial(
        material=material,
        source_layer=LexemeLayer.BARE_MATERIAL,
        grapheme_count=len(material),
    )


def self_identifies_weight(
    self_record: RationalSelfRecord,
    material: BareLexicalMaterial,
    root: tuple[str, ...] = (),
    pattern: str = "",
) -> Optional[WeightNode]:
    """Self applies weight recognition.

    The rational self attempts to identify the weight/pattern of the
    bare material based on root extraction.

    Parameters
    ----------
    self_record : RationalSelfRecord
        The rational self performing recognition.
    material : BareLexicalMaterial
        The bare material to analyse.
    root : tuple of str
        Pre-identified root radicals, if any.
    pattern : str
        Optional pattern hint.

    Returns
    -------
    WeightNode or None
        The weight node if recognition succeeds.
    """
    if not root and not pattern:
        return None
    return extract_weight(root, material.material, pattern)


def self_builds_lexeme(
    self_record: RationalSelfRecord,
    closure: LexicalClosure,
    weight: Optional[WeightNode] = None,
) -> LexemeNode:
    """Self constructs a lexeme from closure + weight.

    Parameters
    ----------
    self_record : RationalSelfRecord
        The rational self performing construction.
    closure : LexicalClosure
        The morphological record.
    weight : WeightNode, optional
        The identified weight.

    Returns
    -------
    LexemeNode
    """
    return build_lexeme(closure, weight=weight)


def self_prepares_composition(
    self_record: RationalSelfRecord,
    lexeme: LexemeNode,
) -> CompositionReadyNode:
    """Self prepares a lexeme for composition.

    Parameters
    ----------
    self_record : RationalSelfRecord
        The rational self.
    lexeme : LexemeNode
        The lexeme to prepare.

    Returns
    -------
    CompositionReadyNode
    """
    return check_composition_readiness(lexeme)
