"""الدستور الاسمي — Noun Constitution (master classifier).

Orchestrates all 12 facet resolvers to produce a fully classified
:class:`~arabic_engine.core.types.NounNode` from a
:class:`~arabic_engine.core.types.LexicalClosure`.
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import (
    DerivationStatus,
    NounFractalStage,
    NounKind,
)
from arabic_engine.core.types import Concept, LexicalClosure, NounNode
from arabic_engine.noun.attribute import resolve_noun_attribute
from arabic_engine.noun.borrowed import resolve_borrowed
from arabic_engine.noun.compound import resolve_compound
from arabic_engine.noun.definiteness import resolve_definiteness
from arabic_engine.noun.gender import resolve_gender
from arabic_engine.noun.number import resolve_number
from arabic_engine.noun.proper import resolve_proper_type
from arabic_engine.noun.rigid_pattern import resolve_rigid_pattern
from arabic_engine.noun.taxonomy import resolve_genus_species_individual
from arabic_engine.noun.universality import resolve_universality


def classify_noun(
    closure: LexicalClosure,
    concept: Optional[Concept] = None,
    all_tokens: Optional[List[LexicalClosure]] = None,
    token_index: int = 0,
) -> NounNode:
    """Classify a noun through all 12 facets.

    Parameters
    ----------
    closure : LexicalClosure
        A lexical closure with ``pos == POS.ISM``.
    concept : Concept, optional
        The ontological concept mapped to this noun.  When ``None`` a
        minimal fallback concept is constructed.
    all_tokens : list[LexicalClosure], optional
        All tokens in the utterance (needed for compound detection).
    token_index : int
        Position of this noun in *all_tokens*.

    Returns
    -------
    NounNode
        A frozen dataclass capturing the complete noun identity.
    """
    from arabic_engine.core.enums import SemanticType

    if concept is None:
        concept = Concept(
            concept_id=0,
            label=closure.lemma,
            semantic_type=SemanticType.ENTITY,
        )

    # 1. Gender
    gender, gender_basis = resolve_gender(closure)

    # 2. Number
    number = resolve_number(closure)

    # 3. Proper-noun type
    proper_type = resolve_proper_type(closure)
    is_proper = proper_type is not None

    # 4. Definiteness
    definiteness = resolve_definiteness(closure, is_proper=is_proper)

    # 5. Universality
    universality = resolve_universality(closure, concept)

    # If it's a proper noun, override universality to PARTICULAR
    if is_proper:
        from arabic_engine.core.enums import UniversalParticular
        universality = UniversalParticular.PARTICULAR

    # 6. Taxonomy (genus / species / individual)
    noun_kind = resolve_genus_species_individual(closure, concept, universality)

    # 7. Attribute check — may override noun_kind
    is_attribute = resolve_noun_attribute(closure)
    if is_attribute and noun_kind == NounKind.ENTITY:
        noun_kind = NounKind.ATTRIBUTE

    # 8. Proper noun — may override noun_kind
    if is_proper and noun_kind not in (NounKind.INDIVIDUAL,):
        noun_kind = NounKind.PROPER

    # 9. Compound detection
    compound_type = None
    if all_tokens is not None:
        compound_type = resolve_compound(all_tokens, token_index)
    else:
        # Still detect single-token blend compounds
        compound_type = resolve_compound([closure], 0)
    if compound_type is not None and noun_kind in (
        NounKind.ENTITY, NounKind.INDIVIDUAL, NounKind.PROPER,
    ):
        noun_kind = NounKind.COMPOUND

    # 10. Borrowed detection
    is_borrowed, source_language = resolve_borrowed(closure)
    if is_borrowed and noun_kind in (NounKind.ENTITY, NounKind.INDIVIDUAL):
        noun_kind = NounKind.BORROWED

    # 11. Rigid pattern
    rigid_template = resolve_rigid_pattern(closure)

    # 12. Derivation status
    derivation = (
        DerivationStatus.DERIVED if is_attribute else DerivationStatus.RIGID
    )

    return NounNode(
        surface=closure.surface,
        lemma=closure.lemma,
        root=closure.root,
        pattern=closure.pattern,
        noun_kind=noun_kind,
        universality=universality,
        gender=gender,
        gender_basis=gender_basis,
        number=number,
        definiteness=definiteness,
        derivation=derivation,
        proper_type=proper_type,
        compound_type=compound_type,
        is_borrowed=is_borrowed,
        source_language=source_language,
        rigid_template=rigid_template,
        fractal_stage=NounFractalStage.JUDGMENT,
        confidence=closure.confidence,
    )


def validate_noun_completeness(node: NounNode) -> bool:
    """Verify that a :class:`NounNode` satisfies the minimum complete threshold.

    The threshold requires:

    1. **Existence** — non-empty surface form.
    2. **Distinction** — distinguished from verb / particle (has noun_kind).
    3. **Extension** — has phonological (surface), written, semantic, and
       referential extension (definiteness is set).
    4. **Constituent** — has material (root or lemma), pattern or rigid
       template, semantic direction (noun_kind), and relative independence.
    5. **Structural relations** — number, gender, definiteness are populated.
    6. **Unity** — forms a single nominal unit (surface is non-empty).
    7. **Assignability** — can be judged as proper/genus/species/…
    """
    if not node.surface:
        return False
    if not node.lemma:
        return False
    # Must have either root or be borrowed/compound
    if not node.root and not node.is_borrowed and node.compound_type is None:
        return False
    # Noun kind must be set
    if node.noun_kind is None:
        return False
    # Definiteness must be set
    if node.definiteness is None:
        return False
    # Gender must be set
    if node.gender is None:
        return False
    # Number must be set
    if node.number is None:
        return False
    return True
