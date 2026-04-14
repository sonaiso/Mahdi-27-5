"""Ontological mapping — from lexical closure to concepts (التعريف 5).

O : T → C

Maps each lexical entry to a *concept node* with a semantic type
(entity / event / attribute / relation / norm) and a property vector.
"""

from __future__ import annotations

from typing import Dict, List

from arabic_engine.core.enums import POS, SemanticType
from arabic_engine.core.types import Concept, LexicalClosure
from arabic_engine.particle.registry import lookup as particle_lookup

# ── Concept registry (demo) ─────────────────────────────────────────

_CONCEPT_DB: Dict[str, Concept] = {
    "كَتَبَ": Concept(
        concept_id=101,
        label="كتابة",
        semantic_type=SemanticType.EVENT,
        properties={"transitivity": "muta3addi", "tense": "madi"},
    ),
    "زَيْد": Concept(
        concept_id=201,
        label="زَيْد",
        semantic_type=SemanticType.ENTITY,
        properties={"animacy": True, "proper_noun": True},
    ),
    "رِسَالَة": Concept(
        concept_id=301,
        label="رِسَالَة",
        semantic_type=SemanticType.ENTITY,
        properties={"animacy": False, "countable": True},
    ),
    # ── Time adverbs (v2) ───────────────────────────────────────
    "أَمْس": Concept(
        concept_id=401,
        label="أَمْس",
        semantic_type=SemanticType.ATTRIBUTE,
        properties={"temporal": True, "time_ref": "past"},
    ),
    "غَد": Concept(
        concept_id=402,
        label="غَد",
        semantic_type=SemanticType.ATTRIBUTE,
        properties={"temporal": True, "time_ref": "future"},
    ),
    # ── Particle entries (باب الحرف الفراكتالي) ──────────────────
    "في": Concept(
        concept_id=501,
        label="في",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "JARR", "direction": "ظرفية"},
    ),
    "من": Concept(
        concept_id=502,
        label="من",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "JARR", "direction": "ابتداء"},
    ),
    "إلى": Concept(
        concept_id=503,
        label="إلى",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "JARR", "direction": "انتهاء"},
    ),
    "على": Concept(
        concept_id=504,
        label="على",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "JARR", "direction": "استعلاء"},
    ),
    "إنّ": Concept(
        concept_id=505,
        label="إنّ",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "MASHABBAH", "direction": "توكيد"},
    ),
    "هل": Concept(
        concept_id=506,
        label="هل",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "ISTIFHAM", "direction": "استفهام"},
    ),
    "لا": Concept(
        concept_id=507,
        label="لا",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "NAFY", "direction": "نفي"},
    ),
    "و": Concept(
        concept_id=508,
        label="و",
        semantic_type=SemanticType.RELATION,
        properties={"particle_type": "ATF", "direction": "جمع"},
    ),
}

_POS_TO_STYPE = {
    POS.FI3L: SemanticType.EVENT,
    POS.ISM: SemanticType.ENTITY,
    POS.SIFA: SemanticType.ATTRIBUTE,
    POS.HARF: SemanticType.RELATION,
    POS.ZARF: SemanticType.ATTRIBUTE,
}

_next_concept_id = 900


def map_concept(closure: LexicalClosure) -> Concept:
    """Map a :class:`~arabic_engine.core.types.LexicalClosure` to a concept node.

    First consults the internal concept database keyed on the lemma.
    When no match is found, auto-generates a new concept with an
    incrementing ID and a semantic type inferred from the POS tag.

    Args:
        closure: The lexical closure whose lemma is used as the lookup key.

    Returns:
        A :class:`~arabic_engine.core.types.Concept` node.  The concept
        is either retrieved from the database or freshly created.
    """
    concept = _CONCEPT_DB.get(closure.lemma)
    if concept is not None:
        return concept

    global _next_concept_id
    _next_concept_id += 1

    # Enrich HARF concepts with particle metadata from the registry
    properties: dict = {}
    if closure.pos is POS.HARF:
        prec = particle_lookup(closure.lemma)
        if prec is not None:
            properties["particle_type"] = prec.particle_type.name
            properties["relation_type"] = prec.relation_type.name
            properties["direction"] = prec.direction

    return Concept(
        concept_id=_next_concept_id,
        label=closure.lemma,
        semantic_type=_POS_TO_STYPE.get(closure.pos, SemanticType.ENTITY),
        properties=properties,
    )


def batch_map(closures: List[LexicalClosure]) -> List[Concept]:
    """Map a list of closures to concept nodes.

    Convenience wrapper around :func:`map_concept` for a list of lexical
    closures (as produced by
    :func:`~arabic_engine.signifier.root_pattern.batch_closure`).

    Args:
        closures: List of lexical closures to map.

    Returns:
        A list of :class:`~arabic_engine.core.types.Concept` objects,
        one per input closure, preserving order.
    """
    return [map_concept(c) for c in closures]
