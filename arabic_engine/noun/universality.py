"""جهة الكلي والجزئي — Universal vs. particular facet.

Universal (كلي): the noun can apply to many individuals (إنسان, شجر).
Particular (جزئي): the noun is restricted to one referent (زيد, عمّان).
"""

from __future__ import annotations

from arabic_engine.core.enums import UniversalParticular
from arabic_engine.core.types import Concept, LexicalClosure

# Proper-noun indicator in concept properties
_PROPER_KEY = "proper_noun"

# Universal quantifiers that force universality
_UNIVERSAL_QUANTIFIERS = frozenset({
    "كل", "جميع", "كافة", "عامة", "سائر",
})


def resolve_universality(
    closure: LexicalClosure,
    concept: Concept,
) -> UniversalParticular:
    """Classify a noun as universal or particular.

    Rules (in priority order):
    1. If the concept is marked ``proper_noun=True`` → PARTICULAR.
    2. If the lemma is a universal quantifier → UNIVERSAL.
    3. If the surface starts with 'ال' (generic definite article) → UNIVERSAL.
    4. Otherwise → PARTICULAR (indefinite defaults to particular).
    """
    # Proper nouns are always particular
    if concept.properties.get(_PROPER_KEY, False):
        return UniversalParticular.PARTICULAR

    # Universal quantifiers
    if closure.lemma in _UNIVERSAL_QUANTIFIERS:
        return UniversalParticular.UNIVERSAL

    # Generic definite article → universal interpretation
    if closure.surface.startswith("ال"):
        return UniversalParticular.UNIVERSAL

    return UniversalParticular.PARTICULAR
