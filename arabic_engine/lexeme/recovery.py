"""Recovery rules — قواعد الرد (RR-01 … RR-06).

Every node in the lexeme ontology can be traced back to its source
layer.  These functions implement the formal recovery rules.

Public API
----------
recover_weight_from_lexeme    RR-01
recover_root_from_weight      RR-02
recover_concept_from_noun     RR-03
recover_action_from_verb      RR-04
recover_relation_from_particle RR-05
recover_composition_source    RR-06
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from arabic_engine.core.types import (
    CompositionReadyNode,
    LexemeNode,
    NounNode,
    ParticleNode,
    VerbNode,
    WeightNode,
)


def recover_weight_from_lexeme(lexeme: LexemeNode) -> Optional[str]:
    """RR-01: Recover the weight/template reference from a lexeme.

    Returns the weight_ref or closed_template_ref string, which
    can be used to look up the full WeightNode or ClosedTemplateNode.
    """
    return lexeme.weight_ref or lexeme.closed_template_ref


def recover_root_from_weight(weight: WeightNode) -> Optional[Tuple[str, ...]]:
    """RR-02: Recover root radicals from a WeightNode's slots.

    Parses slot descriptors of the form ``C1:ك`` to extract root letters.
    """
    if not weight.slots:
        return None
    radicals = []
    for slot in weight.slots:
        if slot.startswith("C") and ":" in slot:
            _, letter = slot.split(":", 1)
            radicals.append(letter)
    return tuple(radicals) if radicals else None


def recover_concept_from_noun(noun: NounNode) -> Optional[str]:
    """RR-03: Recover the referential/conceptual direction of a noun.

    Returns a string describing the noun's semantic orientation.
    """
    return f"{noun.referential_mode.name}:{noun.jamid_or_derived.name}"


def recover_action_from_verb(verb: VerbNode) -> Optional[str]:
    """RR-04: Recover the actional/temporal properties of a verb.

    Returns a string describing the verb's event + tense.
    """
    return f"{verb.action_type.name}:{verb.tense_direction.name}"


def recover_relation_from_particle(particle: ParticleNode) -> Optional[str]:
    """RR-05: Recover the relational/functional properties of a particle.

    Returns a string describing the particle's relation type + scope.
    """
    return f"{particle.relation_type.name}:{particle.governing_scope}"


def recover_composition_source(node: CompositionReadyNode) -> Dict[str, Any]:
    """RR-06: Recover the full composition source for audit.

    Returns a dictionary with all recoverable fields from the
    composition-ready node.
    """
    return {
        "lexeme_ref": node.lexeme_ref,
        "pos_final": node.pos_final.name,
        "concept_type": node.concept_type,
        "weight_or_template": node.weight_or_template,
        "ready": node.ready,
    }
