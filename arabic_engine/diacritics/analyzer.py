"""Diacritic analyzer — تحليل التشكيل.

Decomposes an Arabic token into its constituent diacritical marks,
identifies each mark's type (فتحة / ضمة / كسرة / سكون / شدة / تنوين),
and binds it to the correct base consonant.
"""

from __future__ import annotations

import unicodedata
from typing import List, Tuple

from arabic_engine.core.enums import (
    DiacriticConsistency,
    DiacriticRole,
    DiacriticType,
)
from arabic_engine.core.types import (
    DiacriticAnalysis,
    DiacriticBinding,
    DiacriticMark,
)

# Unicode code-point → DiacriticType mapping
_MARK_MAP: dict[int, DiacriticType] = {
    0x064E: DiacriticType.FATHA,     # فتحة
    0x064F: DiacriticType.DAMMA,     # ضمة
    0x0650: DiacriticType.KASRA,     # كسرة
    0x0652: DiacriticType.SUKUN,     # سكون
    0x0651: DiacriticType.SHADDA,    # شدة
    0x064B: DiacriticType.TANWIN_F,  # تنوين فتح
    0x064C: DiacriticType.TANWIN_D,  # تنوين ضم
    0x064D: DiacriticType.TANWIN_K,  # تنوين كسر
    0x0654: DiacriticType.HAMZA,     # همزة فوقية
    0x0655: DiacriticType.HAMZA,     # همزة تحتية
    0x0653: DiacriticType.MADDA,     # مدة
}

# Vowel marks that are mutually exclusive on a single consonant
_VOWEL_MARKS = {
    DiacriticType.FATHA,
    DiacriticType.DAMMA,
    DiacriticType.KASRA,
    DiacriticType.SUKUN,
    DiacriticType.TANWIN_F,
    DiacriticType.TANWIN_D,
    DiacriticType.TANWIN_K,
}


def _is_arabic_diacritic(cp: int) -> bool:
    """Return True if the code point is a known Arabic diacritical mark."""
    return cp in _MARK_MAP


def _classify_role(marks: Tuple[DiacriticMark, ...], position: int,
                   token_len: int) -> DiacriticRole:
    """Classify the functional role of a mark group on a consonant."""
    for m in marks:
        if m.mark_type in {DiacriticType.TANWIN_F, DiacriticType.TANWIN_D,
                           DiacriticType.TANWIN_K}:
            return DiacriticRole.INFLECTIONAL
    # Last character marks are typically inflectional (i'rāb)
    if position == token_len - 1:
        return DiacriticRole.INFLECTIONAL
    return DiacriticRole.LEXICAL


def _check_consistency(marks: Tuple[DiacriticMark, ...]) -> DiacriticConsistency:
    """Check whether the diacritic marks on a single consonant are consistent."""
    vowel_marks = [m for m in marks if m.mark_type in _VOWEL_MARKS]
    if len(vowel_marks) > 1:
        return DiacriticConsistency.CONFLICTING
    if len(marks) != len(set(m.mark_type for m in marks)):
        return DiacriticConsistency.REDUNDANT
    return DiacriticConsistency.CONSISTENT


def analyze(token: str) -> DiacriticAnalysis:
    """Analyze diacritical marks on *token* and return a full analysis.

    Parameters
    ----------
    token : str
        A single Arabic token (word) possibly containing diacritical marks.

    Returns
    -------
    DiacriticAnalysis
        Complete diacritical analysis with mark bindings, consistency,
        and voweling status.
    """
    bindings: List[DiacriticBinding] = []
    mark_count = 0
    consonant_count = 0

    current_base: str | None = None
    current_base_idx = -1
    current_marks: List[DiacriticMark] = []
    base_index_in_consonants = -1

    for i, ch in enumerate(token):
        cp = ord(ch)
        if _is_arabic_diacritic(cp):
            mark = DiacriticMark(
                code_point=cp,
                mark_type=_MARK_MAP[cp],
                base_char=current_base or "",
                position=i,
            )
            current_marks.append(mark)
            mark_count += 1
        else:
            # Flush previous consonant's marks
            if current_base is not None:
                marks_tuple = tuple(current_marks)
                consistency = _check_consistency(marks_tuple)
                role = _classify_role(
                    marks_tuple, base_index_in_consonants, consonant_count + 1,
                )
                bindings.append(DiacriticBinding(
                    base_char=current_base,
                    base_index=current_base_idx,
                    marks=marks_tuple,
                    consistency=consistency,
                    role=role,
                ))
            current_base = ch
            current_base_idx = i
            current_marks = []
            consonant_count += 1
            base_index_in_consonants = consonant_count - 1

    # Flush last consonant
    if current_base is not None:
        marks_tuple = tuple(current_marks)
        consistency = _check_consistency(marks_tuple)
        role = _classify_role(
            marks_tuple, base_index_in_consonants, consonant_count,
        )
        bindings.append(DiacriticBinding(
            base_char=current_base,
            base_index=current_base_idx,
            marks=marks_tuple,
            consistency=consistency,
            role=role,
        ))

    bindings_tuple = tuple(bindings)

    # Overall consistency
    all_consistent = all(
        b.consistency == DiacriticConsistency.CONSISTENT for b in bindings_tuple
    )
    overall = (DiacriticConsistency.CONSISTENT if all_consistent
               else DiacriticConsistency.CONFLICTING)

    # Voweling status: check how many base chars have vowel marks
    voweled_count = sum(
        1 for b in bindings_tuple
        if any(m.mark_type in _VOWEL_MARKS for m in b.marks)
    )
    total_bases = len(bindings_tuple)
    is_fully = total_bases > 0 and voweled_count == total_bases
    is_partially = 0 < voweled_count < total_bases

    return DiacriticAnalysis(
        token=token,
        bindings=bindings_tuple,
        mark_count=mark_count,
        consistency=overall,
        is_fully_voweled=is_fully,
        is_partially_voweled=is_partially,
    )
