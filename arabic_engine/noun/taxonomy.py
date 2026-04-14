"""جهة الجنس والنوع والفرد — Genus / species / individual facet.

Genus (جنس): broadest category encompassing multiple species (حيوان).
Species (نوع): narrower category sharing a closer reality (إنسان).
Individual (فرد): a specific realised or mentally determined entity (زيد).
"""

from __future__ import annotations

from arabic_engine.core.enums import NounKind, UniversalParticular
from arabic_engine.core.types import Concept, LexicalClosure

# Known genus-level nouns (broad categories)
_GENUS_NOUNS = frozenset({
    "حيوان", "نبات", "جماد", "مخلوق", "كائن", "شيء", "جسم",
    "مادة", "طعام", "شراب", "آلة", "أداة", "سلاح",
})

# Known species-level nouns (narrower categories with specific realities)
_SPECIES_NOUNS = frozenset({
    "إنسان", "رجل", "امرأة", "طفل", "شجرة", "زهرة",
    "نهر", "جبل", "بحر", "مدينة", "قرية", "كتاب",
    "قلم", "بيت", "سيارة", "طائرة", "حصان", "أسد",
})


def resolve_genus_species_individual(
    closure: LexicalClosure,
    concept: Concept,
    universality: UniversalParticular,
) -> NounKind:
    """Classify a noun as genus, species, or individual.

    Rules:
    1. If universality is PARTICULAR and concept is a proper noun → INDIVIDUAL.
    2. If lemma is in the genus database → GENUS.
    3. If lemma is in the species database → SPECIES.
    4. If universality is PARTICULAR → INDIVIDUAL.
    5. Fallback → ENTITY (generic noun).
    """
    is_proper = concept.properties.get("proper_noun", False)

    if universality == UniversalParticular.PARTICULAR and is_proper:
        return NounKind.INDIVIDUAL

    if closure.lemma in _GENUS_NOUNS:
        return NounKind.GENUS

    if closure.lemma in _SPECIES_NOUNS:
        return NounKind.SPECIES

    if universality == UniversalParticular.PARTICULAR:
        return NounKind.INDIVIDUAL

    return NounKind.ENTITY
