"""Syllable segmenter — تقطيع المقاطع.

Segments an Arabic word into phonological syllables, classifying each
by type (CV/CVC/CVV/CVVC/CVCC) and weight (light/heavy/super-heavy).
"""

from __future__ import annotations

import unicodedata
from typing import List

from arabic_engine.core.enums import SyllableType, SyllableWeight
from arabic_engine.core.types import SyllableAnalysis, SyllablePattern, SyllableUnit

# ── Phonological classification ─────────────────────────────────────

_SHORT_VOWELS = frozenset("\u064E\u064F\u0650")  # فتحة ضمة كسرة
_LONG_VOWELS = frozenset("\u0627\u0648\u064A")  # ا و ي (when preceded by short vowel)
_DIACRITICS = frozenset(
    "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655"
)
_SUKUN = "\u0652"
_SHADDA = "\u0651"


def _is_consonant(ch: str) -> bool:
    """Return True if ch is an Arabic consonant (base letter)."""
    if ch in _DIACRITICS or ch in _LONG_VOWELS:
        return False
    cat = unicodedata.category(ch)
    return cat.startswith("L")


def _classify_syllable(onset: str, nucleus: str, coda: str) -> SyllableType:
    """Classify a syllable by its structure."""
    has_long_nucleus = len(nucleus) > 1
    coda_len = len(coda)
    if coda_len == 0:
        return SyllableType.CVV if has_long_nucleus else SyllableType.CV
    if coda_len >= 2:
        return SyllableType.CVCC
    return SyllableType.CVVC if has_long_nucleus else SyllableType.CVC


def _get_weight(stype: SyllableType) -> SyllableWeight:
    """Return the phonological weight of a syllable type."""
    if stype == SyllableType.CV:
        return SyllableWeight.LIGHT
    if stype in {SyllableType.CVC, SyllableType.CVV}:
        return SyllableWeight.HEAVY
    return SyllableWeight.SUPER


def segment(word: str) -> SyllableAnalysis:
    """Segment *word* into phonological syllables.

    Parameters
    ----------
    word : str
        A single Arabic word (may include diacritics).

    Returns
    -------
    SyllableAnalysis
        Full syllabic analysis with pattern, validity, and mora count.
    """
    # Strip the word into a sequence of (consonant, vowel?) pairs
    units: List[SyllableUnit] = []
    violations: List[str] = []

    # Simple heuristic segmenter: scan characters and group into syllables
    chars = list(word)
    i = 0
    raw_syllables: List[tuple[str, str, str, str]] = []  # onset, nucleus, coda, text

    while i < len(chars):
        onset = ""
        nucleus = ""
        coda = ""
        text_start = i

        # Onset: consume consonant(s)
        if i < len(chars) and _is_consonant(chars[i]):
            onset = chars[i]
            i += 1
            # Skip shadda
            if i < len(chars) and chars[i] == _SHADDA:
                i += 1
        elif i < len(chars) and chars[i] not in _DIACRITICS:
            onset = chars[i]
            i += 1

        # Nucleus: consume short vowel + optional long vowel
        if i < len(chars) and chars[i] in _SHORT_VOWELS:
            nucleus = chars[i]
            i += 1
            # Check for long vowel letter following
            if i < len(chars) and chars[i] in _LONG_VOWELS:
                nucleus += chars[i]
                i += 1
        elif i < len(chars) and chars[i] in _LONG_VOWELS:
            nucleus = chars[i]
            i += 1

        # Coda: consume consonant if followed by another consonant or end
        if i < len(chars) and _is_consonant(chars[i]):
            # Look ahead: if next is also consonant or end of word, this is coda
            next_i = i + 1
            # Skip any diacritics after the potential coda consonant
            while next_i < len(chars) and chars[next_i] in _DIACRITICS:
                next_i += 1
            if next_i >= len(chars) or _is_consonant(chars[next_i]):
                coda = chars[i]
                i += 1
                # Check for second coda consonant (CVCC)
                if i < len(chars) and _is_consonant(chars[i]):
                    next_i2 = i + 1
                    while next_i2 < len(chars) and chars[next_i2] in _DIACRITICS:
                        next_i2 += 1
                    if next_i2 >= len(chars):
                        coda += chars[i]
                        i += 1

        # Skip remaining diacritics (sukun, etc.)
        while i < len(chars) and chars[i] in _DIACRITICS:
            i += 1

        text = word[text_start:i] if i > text_start else ""
        if onset or nucleus:
            raw_syllables.append((onset, nucleus, coda, text))
        elif i == text_start:
            # Prevent infinite loop: advance by one
            i += 1

    # Build SyllableUnit list
    for onset, nucleus, coda, text in raw_syllables:
        stype = _classify_syllable(onset, nucleus, coda)
        weight = _get_weight(stype)
        units.append(SyllableUnit(
            onset=onset,
            nucleus=nucleus,
            coda=coda,
            syllable_type=stype,
            weight=weight,
            text=text,
        ))

    # Build pattern
    pattern_str = ".".join(u.syllable_type.name for u in units)
    # Stress: default to penultimate if 2+ syllables, else 0
    stress = max(0, len(units) - 2) if len(units) >= 2 else 0
    syl_pattern = SyllablePattern(
        syllables=tuple(units),
        pattern=pattern_str,
        stress_position=stress,
    )

    # Mora count
    mora = sum(
        1 if u.weight == SyllableWeight.LIGHT
        else (2 if u.weight == SyllableWeight.HEAVY else 3)
        for u in units
    )

    is_valid = len(violations) == 0 and len(units) > 0

    return SyllableAnalysis(
        word=word,
        pattern=syl_pattern,
        is_valid=is_valid,
        mora_count=mora,
        violations=tuple(violations),
    )
