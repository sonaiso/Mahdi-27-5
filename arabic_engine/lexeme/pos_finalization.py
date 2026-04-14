"""POS finalisation — تثبيت قسم المفرد.

Transforms a generic :class:`LexemeNode` into a specialised
:class:`NounNode`, :class:`VerbNode`, or :class:`ParticleNode` with
full epistemic proof fields.

Public API
----------
finalize_as_noun      Finalise as noun with referential/derivational info.
finalize_as_verb      Finalise as verb with actional/temporal info.
finalize_as_particle  Finalise as particle with relational info.
auto_finalize         Heuristic auto-finalisation from POS.
"""

from __future__ import annotations

from typing import Optional, Union

from arabic_engine.core.enums import (
    POS,
    IndependenceType,
    JamidDerivedType,
    MatchingMode,
    ParticleRelationType,
    ReferentialMode,
    TimeRef,
    VerbActionType,
)
from arabic_engine.core.types import (
    LexemeNode,
    NounNode,
    ParticleNode,
    VerbNode,
)


def finalize_as_noun(
    lexeme: LexemeNode,
    referential_mode: ReferentialMode = ReferentialMode.JINS,
    jamid_derived: JamidDerivedType = JamidDerivedType.JAMID,
    match_mode: MatchingMode = MatchingMode.MUTABAQA,
    countability: Optional[str] = None,
    ontological_class: Optional[str] = None,
) -> NounNode:
    """Finalise a lexeme as a noun.

    Parameters
    ----------
    lexeme : LexemeNode
        The source lexeme.
    referential_mode : ReferentialMode
        How the noun refers (proper name, genus, species, …).
    jamid_derived : JamidDerivedType
        Whether the noun is a rigid (جامد) or derived (مشتق) form.
    match_mode : MatchingMode
        The matching mode for signification.

    Returns
    -------
    NounNode
    """
    return NounNode(
        lexeme_ref=lexeme.id,
        referential_mode=referential_mode,
        jamid_or_derived=jamid_derived,
        match_mode=match_mode,
        countability=countability,
        ontological_class=ontological_class,
    )


def finalize_as_verb(
    lexeme: LexemeNode,
    action_type: VerbActionType = VerbActionType.EVENT,
    tense: TimeRef = TimeRef.PAST,
    transitivity: Optional[str] = None,
    match_mode: MatchingMode = MatchingMode.MUTABAQA,
    predicate_power: float = 1.0,
) -> VerbNode:
    """Finalise a lexeme as a verb.

    Parameters
    ----------
    lexeme : LexemeNode
        The source lexeme.
    action_type : VerbActionType
        Event / linking / copula.
    tense : TimeRef
        Temporal direction.
    transitivity : str, optional
        Transitive / intransitive.
    match_mode : MatchingMode
        The matching mode for signification.

    Returns
    -------
    VerbNode
    """
    return VerbNode(
        lexeme_ref=lexeme.id,
        action_type=action_type,
        tense_direction=tense,
        transitivity=transitivity,
        matching_mode=match_mode,
        predicate_power=predicate_power,
    )


def finalize_as_particle(
    lexeme: LexemeNode,
    relation_type: ParticleRelationType = ParticleRelationType.JARR,
    independence_mode: IndependenceType = IndependenceType.FUNCTION_INDEPENDENT,
    match_mode: MatchingMode = MatchingMode.MUTABAQA,
    governing_scope: str = "",
) -> ParticleNode:
    """Finalise a lexeme as a particle.

    Parameters
    ----------
    lexeme : LexemeNode
        The source lexeme.
    relation_type : ParticleRelationType
        The particle's functional relation type.
    match_mode : MatchingMode
        The matching mode for signification.

    Returns
    -------
    ParticleNode
    """
    return ParticleNode(
        lexeme_ref=lexeme.id,
        relation_type=relation_type,
        independence_mode=independence_mode,
        matching_mode=match_mode,
        governing_scope=governing_scope,
    )


def auto_finalize(
    lexeme: LexemeNode,
) -> Union[NounNode, VerbNode, ParticleNode]:
    """Heuristic auto-finalisation from POS.

    Uses the lexeme's ``pos_final`` to choose the appropriate
    finalisation path with default parameters.

    Returns
    -------
    NounNode | VerbNode | ParticleNode
    """
    pos = lexeme.pos_final
    if pos == POS.FI3L:
        return finalize_as_verb(lexeme)
    if pos == POS.HARF:
        return finalize_as_particle(lexeme)
    # Default: noun (covers ISM, SIFA, ZARF, DAMIR, UNKNOWN)
    return finalize_as_noun(lexeme)
