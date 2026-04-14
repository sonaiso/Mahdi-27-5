"""Validation rules — قواعد التحقق (RS-01 … RS-12).

No lexeme enters the composition layer without passing all applicable
validation rules.

Public API
----------
validate_rs01 … validate_rs12   Individual rule checks.
validate_all                    Run all applicable rules.
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Union

from arabic_engine.core.enums import (
    POS,
    IndependenceType,
    JamidDerivedType,
    LexemeLayer,
)
from arabic_engine.core.types import (
    CompositionReadyNode,
    LexemeNode,
    NounNode,
    ParticleNode,
    VerbNode,
    WeightNode,
)


def validate_rs01(lexeme: LexemeNode) -> bool:
    """RS-01: LexemeNode requires surface_form, concept_type, and pos_final."""
    return bool(
        lexeme.surface_form
        and lexeme.concept_type
        and lexeme.pos_final is not None
    )


def validate_rs02(lexeme: LexemeNode) -> bool:
    """RS-02: Must be independent by meaning or function."""
    return lexeme.independence_type != IndependenceType.DEPENDENT


def validate_rs03(weight: WeightNode) -> bool:
    """RS-03: WeightNode completeness_score must be >= 0.65."""
    return weight.completeness_score >= 0.65


def validate_rs04(weight: WeightNode) -> bool:
    """RS-04: WeightNode must be recoverable to slots and root/additions."""
    if not weight.slots:
        return False
    has_root_slots = any(s.startswith("C") and ":" in s for s in weight.slots)
    return has_root_slots and weight.recoverability_score > 0.0


def validate_rs05(noun: NounNode) -> bool:
    """RS-05: Derived noun must link to root or derivation template.

    For derived nouns (مشتق), the lexeme_ref must be non-empty.
    Rigid nouns (جامد) pass automatically.
    """
    if noun.jamid_or_derived == JamidDerivedType.JAMID:
        return True
    return bool(noun.lexeme_ref)


def validate_rs06(noun: NounNode) -> bool:
    """RS-06: Rigid noun must have referential/classificatory independence.

    For rigid nouns, referential_mode must be set to a valid mode.
    Derived nouns pass automatically.
    """
    if noun.jamid_or_derived == JamidDerivedType.MUSHTAQ:
        return True
    return noun.referential_mode is not None


def validate_rs07(verb: VerbNode) -> bool:
    """RS-07: Verb must identify event/linking/copula power."""
    return (
        verb.action_type is not None
        and verb.predicate_power > 0.0
    )


def validate_rs08(particle: ParticleNode) -> bool:
    """RS-08: Particle must identify relation/binding direction."""
    return particle.relation_type is not None


def validate_rs09(
    source_layer: LexemeLayer,
    target_layer: LexemeLayer,
) -> bool:
    """RS-09: No confusion between layers.

    The source layer must precede the target layer in the canonical
    chain ordering.
    """
    order = list(LexemeLayer)
    return order.index(source_layer) < order.index(target_layer)


def validate_rs10(node: CompositionReadyNode) -> bool:
    """RS-10: POS + concept must be set before composition."""
    return (
        node.pos_final != POS.UNKNOWN
        and bool(node.concept_type)
        and node.concept_type != "غير_محدد"
    )


def validate_rs11(
    pos_node: Union[NounNode, VerbNode, ParticleNode],
) -> bool:
    """RS-11: Matching mode must be specified."""
    if isinstance(pos_node, NounNode):
        return pos_node.match_mode is not None
    if isinstance(pos_node, VerbNode):
        return pos_node.matching_mode is not None
    if isinstance(pos_node, ParticleNode):
        return pos_node.matching_mode is not None
    return False


def validate_rs12(lexeme: LexemeNode) -> bool:
    """RS-12: Full chain Unicode→lexeme must be recoverable.

    Checks that the lexeme has enough information to trace back
    through the entire chain.
    """
    return bool(
        lexeme.surface_form
        and (lexeme.root_ref or lexeme.closed_template_ref)
        and (lexeme.weight_ref or lexeme.closed_template_ref)
    )


def validate_all(
    lexeme: LexemeNode,
    weight: Optional[WeightNode] = None,
    pos_node: Optional[Union[NounNode, VerbNode, ParticleNode]] = None,
    composition_node: Optional[CompositionReadyNode] = None,
) -> List[Tuple[str, bool]]:
    """Run all applicable validation rules.

    Returns a list of ``(rule_id, passed)`` tuples.
    """
    results: List[Tuple[str, bool]] = []

    # Always applicable
    results.append(("RS-01", validate_rs01(lexeme)))
    results.append(("RS-02", validate_rs02(lexeme)))
    results.append(("RS-12", validate_rs12(lexeme)))

    # Weight-dependent
    if weight is not None:
        results.append(("RS-03", validate_rs03(weight)))
        results.append(("RS-04", validate_rs04(weight)))

    # POS-dependent
    if pos_node is not None:
        if isinstance(pos_node, NounNode):
            results.append(("RS-05", validate_rs05(pos_node)))
            results.append(("RS-06", validate_rs06(pos_node)))
        elif isinstance(pos_node, VerbNode):
            results.append(("RS-07", validate_rs07(pos_node)))
        elif isinstance(pos_node, ParticleNode):
            results.append(("RS-08", validate_rs08(pos_node)))

        results.append(("RS-11", validate_rs11(pos_node)))

    # Composition-dependent
    if composition_node is not None:
        results.append(("RS-10", validate_rs10(composition_node)))

    return results
