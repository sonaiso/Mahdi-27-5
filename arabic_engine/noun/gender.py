"""جهة التذكير والتأنيث — Gender facet.

Detects masculine / feminine and the basis for the classification:
real (حقيقي), metaphorical (مجازي), lexical (لفظي), semantic (معنوي).
"""

from __future__ import annotations

from typing import Tuple

from arabic_engine.core.enums import Gender, GenderBasis
from arabic_engine.core.types import LexicalClosure

# ── Known feminine nouns without a feminine marker (سماعي) ──────────

_KNOWN_FEMININE_NOUNS = frozenset({
    "أرض", "شمس", "نار", "ريح", "حرب", "دار",
    "نفس", "عين", "يد", "رجل", "أذن", "سن",
    "كأس", "سوق", "طريق", "سبيل", "بئر",
    "عصا", "رحى", "ذكرى", "منى", "هدى",
})

# ── Known dual-gender nouns ─────────────────────────────────────────

_DUAL_GENDER_NOUNS = frozenset({
    "طريق", "سبيل", "سكين", "لسان", "عنق",
    "ذراع", "حال", "سلاح", "سلطان",
})

# ── Feminine suffix markers ─────────────────────────────────────────
# ة (taa marbuta), اء (alef + hamza), ى (alef maqsura)

_TAA_MARBUTA = "\u0629"  # ة
_ALEF_HAMZA_ABOVE = "\u0623"  # أ


def resolve_gender(closure: LexicalClosure) -> Tuple[Gender, GenderBasis]:
    """Detect the gender of a noun and its basis.

    Returns a ``(Gender, GenderBasis)`` pair.

    Priority:
    1. Dual-gender database → DUAL_GENDER / LEXICAL.
    2. Known feminine database → FEMININE / SEMANTIC.
    3. Taa-marbuta suffix (ة) → FEMININE / LEXICAL.
    4. Alef-hamza suffix (اء) → FEMININE / LEXICAL.
    5. Alef-maqsura suffix (ى) → FEMININE / LEXICAL.
    6. Concept animacy + specific conditions → REAL.
    7. Fallback → MASCULINE / LEXICAL.
    """
    lemma = closure.lemma
    bare = lemma.removeprefix("ال")

    # Dual-gender nouns
    if bare in _DUAL_GENDER_NOUNS:
        return Gender.DUAL_GENDER, GenderBasis.LEXICAL

    # Known feminine nouns (semantic femininity without a marker)
    if bare in _KNOWN_FEMININE_NOUNS:
        return Gender.FEMININE, GenderBasis.SEMANTIC

    # Suffix-based detection
    if bare.endswith(_TAA_MARBUTA):
        # Nouns with taa marbuta are typically feminine
        # Check if animate (real) or not (metaphorical/lexical)
        if closure.features.get("animacy", False):
            return Gender.FEMININE, GenderBasis.REAL
        return Gender.FEMININE, GenderBasis.LEXICAL

    if bare.endswith("اء"):
        return Gender.FEMININE, GenderBasis.LEXICAL

    if bare.endswith("ى") and len(bare) >= 3:
        return Gender.FEMININE, GenderBasis.LEXICAL

    # Default: masculine (lexical basis)
    return Gender.MASCULINE, GenderBasis.LEXICAL
