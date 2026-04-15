"""Diacritic rules — قواعد ربط التشكيل.

Defines the binding rules that determine how diacritical marks
attach to base consonants and what analytical effects they carry.
"""

from __future__ import annotations

from arabic_engine.core.enums import DiacriticRole, DiacriticType
from arabic_engine.core.types import DiacriticBinding

# ── Rule constants ──────────────────────────────────────────────────

# Marks that indicate grammatical case (إعراب)
INFLECTIONAL_MARKS = frozenset({
    DiacriticType.TANWIN_F,
    DiacriticType.TANWIN_D,
    DiacriticType.TANWIN_K,
})

# Marks that can combine with SHADDA
SHADDA_COMPANIONS = frozenset({
    DiacriticType.FATHA,
    DiacriticType.DAMMA,
    DiacriticType.KASRA,
})

# Maximum marks per consonant (SHADDA + one vowel)
MAX_MARKS_PER_CONSONANT = 2


def is_valid_binding(binding: DiacriticBinding) -> bool:
    """Return True if the binding follows Arabic diacritical rules.

    A binding is valid when:
    1. At most one vowel mark (فتحة / ضمة / كسرة / سكون / تنوين)
    2. SHADDA may combine with exactly one vowel mark
    3. No more than MAX_MARKS_PER_CONSONANT marks total
    """
    mark_types = [m.mark_type for m in binding.marks]
    vowel_count = sum(1 for mt in mark_types if mt != DiacriticType.SHADDA)
    has_shadda = DiacriticType.SHADDA in mark_types

    if len(mark_types) > MAX_MARKS_PER_CONSONANT:
        return False
    if vowel_count > 1:
        return False
    if has_shadda and vowel_count == 1:
        companion = next(mt for mt in mark_types if mt != DiacriticType.SHADDA)
        if companion not in SHADDA_COMPANIONS:
            return False
    return True


def classify_role(binding: DiacriticBinding, is_final: bool) -> DiacriticRole:
    """Classify the functional role of marks on a consonant.

    Parameters
    ----------
    binding : DiacriticBinding
        The binding to classify.
    is_final : bool
        Whether this is the final consonant of the word (حرف الإعراب).

    Returns
    -------
    DiacriticRole
        The classified role.
    """
    mark_types = {m.mark_type for m in binding.marks}
    if mark_types & INFLECTIONAL_MARKS:
        return DiacriticRole.INFLECTIONAL
    if is_final:
        return DiacriticRole.INFLECTIONAL
    return DiacriticRole.LEXICAL
