"""Lexeme Epistemic Core — نواة اللفظ المفرد المعرفية.

This package implements the Rational Self Ontology v1 Lexeme Epistemic
Core: the formal model of the single word (مفرد لفظي) as the first
tool of cognitive designation before composition.

Public API
----------
weight          Weight extraction, classification, and scoring.
lexeme_builder  Lexeme construction from LexicalClosure + weight.
pos_finalization POS finalisation (noun / verb / particle).
composition_gate Composition readiness gate.
recovery        Recovery rules RR-01 … RR-06.
validation      Validation rules RS-01 … RS-12.
transitions     Formal transition rules between layers.
rational_self   Rational Self ↔ Lexeme bridge.
"""

from arabic_engine.lexeme.composition_gate import (
    check_composition_readiness,
    validate_readiness,
)
from arabic_engine.lexeme.lexeme_builder import (
    build_lexeme,
    compute_readiness,
    determine_independence,
)
from arabic_engine.lexeme.pos_finalization import (
    auto_finalize,
    finalize_as_noun,
    finalize_as_particle,
    finalize_as_verb,
)
from arabic_engine.lexeme.recovery import (
    recover_action_from_verb,
    recover_composition_source,
    recover_concept_from_noun,
    recover_relation_from_particle,
    recover_root_from_weight,
    recover_weight_from_lexeme,
)
from arabic_engine.lexeme.weight import (
    assess_productivity,
    classify_template_type,
    compute_completeness,
    compute_recoverability,
    extract_weight,
)

__all__ = [
    # weight
    "extract_weight",
    "classify_template_type",
    "compute_completeness",
    "compute_recoverability",
    "assess_productivity",
    # lexeme_builder
    "build_lexeme",
    "determine_independence",
    "compute_readiness",
    # pos_finalization
    "finalize_as_noun",
    "finalize_as_verb",
    "finalize_as_particle",
    "auto_finalize",
    # composition_gate
    "check_composition_readiness",
    "validate_readiness",
    # recovery
    "recover_weight_from_lexeme",
    "recover_root_from_weight",
    "recover_concept_from_noun",
    "recover_action_from_verb",
    "recover_relation_from_particle",
    "recover_composition_source",
]
