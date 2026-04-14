"""جهة المعرفة والنكرة — Definiteness facet.

Classifies a noun into one of eight definiteness types:
article, proper, pronoun, demonstrative, relative, annexation,
vocative, or indefinite.
"""

from __future__ import annotations

from arabic_engine.core.enums import Definiteness, POS
from arabic_engine.core.types import LexicalClosure

# ── Demonstrative pronouns ──────────────────────────────────────────

_DEMONSTRATIVES = frozenset({
    "هذا", "هذه", "ذلك", "تلك", "هؤلاء", "أولئك",
    "ذاك", "ذانك", "هاتان", "هاتين",
})

# ── Relative pronouns ──────────────────────────────────────────────

_RELATIVE_PRONOUNS = frozenset({
    "الذي", "التي", "الذين", "اللاتي", "اللواتي",
    "اللتان", "اللتين",
})

# ── Personal pronouns ──────────────────────────────────────────────

_PRONOUNS = frozenset({
    "هو", "هي", "هم", "هن", "أنت", "أنتم", "أنتن",
    "أنا", "نحن", "هما", "أنتما",
})

# ── Vocative particles ─────────────────────────────────────────────

_VOCATIVE_PARTICLES = frozenset({"يا", "أيّها", "أيّتها", "أي"})


def resolve_definiteness(
    closure: LexicalClosure,
    *,
    is_proper: bool = False,
    is_annexed: bool = False,
    preceded_by_vocative: bool = False,
) -> Definiteness:
    """Detect the definiteness type of a noun.

    Parameters
    ----------
    closure : LexicalClosure
        The lexical closure of the noun.
    is_proper : bool
        Whether the noun has been identified as a proper noun.
    is_annexed : bool
        Whether the noun is the first element of an iḍāfa construct.
    preceded_by_vocative : bool
        Whether the noun is preceded by a vocative particle.
    """
    surface = closure.surface
    lemma = closure.lemma

    # Pronoun
    if closure.pos == POS.DAMIR or lemma in _PRONOUNS:
        return Definiteness.DEFINITE_PRONOUN

    # Demonstrative
    if lemma in _DEMONSTRATIVES or surface in _DEMONSTRATIVES:
        return Definiteness.DEFINITE_DEMONSTRATIVE

    # Relative pronoun
    if lemma in _RELATIVE_PRONOUNS or surface in _RELATIVE_PRONOUNS:
        return Definiteness.DEFINITE_RELATIVE

    # Vocative
    if preceded_by_vocative:
        return Definiteness.DEFINITE_VOCATIVE

    # Proper noun
    if is_proper:
        return Definiteness.DEFINITE_PROPER

    # Article (ال)
    if surface.startswith("ال") or surface.startswith("الـ"):
        return Definiteness.DEFINITE_ARTICLE

    # Annexation (iḍāfa)
    if is_annexed:
        return Definiteness.DEFINITE_ANNEXATION

    return Definiteness.INDEFINITE
