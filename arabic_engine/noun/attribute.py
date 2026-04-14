"""جهة الصفة الاسمية — Adjectival-noun facet.

Determines whether a noun is an adjectival noun (صفة اسمية) such as
الأبيض, الطويل, الكريم — i.e. a noun that primarily describes a
quality and stands independently as a concept.
"""

from __future__ import annotations

from arabic_engine.core.types import LexicalClosure

# ── Derivative patterns that indicate adjectival nouns ──────────────

# Active participle: فاعل
# Passive participle: مفعول
# Intensive form: فعّال, فَعول, فعيل, مِفعال
# Comparative/superlative: أفعل
# Resembling adjective: فَعِل, فَعْلان

_ADJECTIVAL_PATTERNS = frozenset({
    "فاعل", "مفعول", "فعيل", "أفعل", "فَعّال", "فَعول",
    "فَعِل", "فَعْلان", "مِفْعال", "فَعَلان",
})

# Shadda diacritic for stripping
_SHADDA = "\u0651"

# Known adjectival nouns (seed list)
_KNOWN_ADJECTIVES = frozenset({
    "أبيض", "أسود", "أحمر", "أخضر", "أزرق", "أصفر",
    "طويل", "قصير", "كبير", "صغير", "جميل", "قبيح",
    "كريم", "لئيم", "عاقل", "جاهل", "حكيم", "شجاع",
    "سعيد", "حزين", "غني", "فقير", "قوي", "ضعيف",
    "عالم", "عامل", "كاتب", "قارئ",
})


def resolve_noun_attribute(closure: LexicalClosure) -> bool:
    """Return ``True`` if the noun is an adjectival noun (صفة اسمية).

    Uses pattern matching against known derivative patterns and
    a seed list of common adjectival nouns.
    """
    lemma = closure.lemma
    pattern = closure.pattern

    # Direct match on pattern
    if pattern in _ADJECTIVAL_PATTERNS:
        return True

    # Seed-list match (strip leading article for lookup)
    bare = lemma.removeprefix("ال")
    if bare in _KNOWN_ADJECTIVES:
        return True

    # Heuristic: active participle starts with م and has 4+ letters
    stripped = lemma.replace(_SHADDA, "")
    if stripped.startswith("م") and len(stripped) >= 4:
        return True

    # Heuristic: فاعل pattern — second character is alef
    if len(stripped) >= 4 and stripped[1:2] == "ا":
        return True

    return False
