"""جهة الوحدة والكثرة — Number (singular / dual / plural) facet.

Detects the grammatical number of a noun using suffix analysis
and a broken-plural seed database.
"""

from __future__ import annotations

from arabic_engine.core.enums import NounNumber
from arabic_engine.core.types import LexicalClosure

# ── Known broken-plural pairs (lemma → broken plural forms) ─────────

_BROKEN_PLURALS = frozenset({
    "كُتُب", "كتب", "رِجال", "رجال", "نِساء", "نساء",
    "أَقلام", "أقلام", "بُيوت", "بيوت", "شُعوب", "شعوب",
    "أَيّام", "أيام", "دُروس", "دروس", "عُلوم", "علوم",
    "جِبال", "جبال", "أَنهار", "أنهار", "بِحار", "بحار",
    "مُدُن", "مدن", "قُرى", "قرى", "أَشجار", "أشجار",
    "صُوَر", "صور", "أَبواب", "أبواب",
})

# ── Collective nouns (اسم جمع) — no singular of their own form ──────

_COLLECTIVE_NOUNS = frozenset({
    "قوم", "ناس", "إبل", "غنم", "خيل", "جيش",
    "شعب", "قبيلة", "جماعة",
})

# ── Genus nouns (اسم جنس جمعي) — unit noun formed by adding ة ──────

_GENUS_NOUNS = frozenset({
    "شجر", "تمر", "نخل", "بقر", "تفاح", "عنب",
    "نحل", "نمل", "حجر", "ورق",
})

# ── Numeral nouns ────────────────────────────────────────────────────

_NUMERAL_WORDS = frozenset({
    "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة",
    "سبعة", "ثمانية", "تسعة", "عشرة", "مئة", "مائة",
    "ألف", "مليون", "مليار",
})


def resolve_number(closure: LexicalClosure) -> NounNumber:
    """Detect the grammatical number of a noun.

    Priority:
    1. Surface/lemma in numeral list → NUMERAL.
    2. Surface/lemma in broken-plural list → BROKEN_PLURAL.
    3. Surface/lemma in collective-noun list → COLLECTIVE_NOUN.
    4. Surface/lemma in genus-noun list → GENUS_NOUN.
    5. Dual suffix (ان / ين) → DUAL.
    6. Sound masculine plural suffix (ون / ين) → SOUND_MASC_PLURAL.
    7. Sound feminine plural suffix (ات) → SOUND_FEM_PLURAL.
    8. Fallback → SINGULAR.
    """
    surface = closure.surface
    lemma = closure.lemma
    bare = lemma.removeprefix("ال")

    if bare in _NUMERAL_WORDS or lemma in _NUMERAL_WORDS:
        return NounNumber.NUMERAL

    if bare in _BROKEN_PLURALS or lemma in _BROKEN_PLURALS:
        return NounNumber.BROKEN_PLURAL

    if bare in _COLLECTIVE_NOUNS or lemma in _COLLECTIVE_NOUNS:
        return NounNumber.COLLECTIVE_NOUN

    if bare in _GENUS_NOUNS or lemma in _GENUS_NOUNS:
        return NounNumber.GENUS_NOUN

    # Suffix analysis on surface form (strip article first)
    bare_surface = surface.removeprefix("ال")
    # Remove trailing diacritics for suffix check
    stripped = _strip_trailing_diacritics(bare_surface)

    if stripped.endswith("ان") or stripped.endswith("ين"):
        # Could be dual or sound masculine plural
        # Dual: nominative ان, accusative/genitive ين
        # Limitation: distinguishing dual-acc/gen from SMP-acc/gen
        # requires syntactic context not available at the noun level.
        if stripped.endswith("ان"):
            return NounNumber.DUAL
        # Default to SOUND_MASC_PLURAL for ين suffix.
        return NounNumber.SOUND_MASC_PLURAL

    if stripped.endswith("ون"):
        return NounNumber.SOUND_MASC_PLURAL

    if stripped.endswith("ات"):
        return NounNumber.SOUND_FEM_PLURAL

    return NounNumber.SINGULAR


def _strip_trailing_diacritics(text: str) -> str:
    """Remove trailing Arabic diacritical marks."""
    diacritics = frozenset(
        "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652"
    )
    while text and text[-1] in diacritics:
        text = text[:-1]
    return text
