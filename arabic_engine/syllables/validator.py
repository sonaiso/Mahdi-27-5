"""Syllable validator — التحقق من شرعية المقطع.

Validates syllable structures against Arabic phonotactic constraints.
"""

from __future__ import annotations

from typing import List, Tuple

from arabic_engine.core.enums import SyllableType
from arabic_engine.core.types import SyllableAnalysis, SyllableUnit

# Arabic permits these syllable types
LEGAL_TYPES = frozenset({
    SyllableType.CV,
    SyllableType.CVV,
    SyllableType.CVC,
    SyllableType.CVVC,
    SyllableType.CVCC,
})

# CVCC and CVVC are only legal word-finally in standard Arabic
FINAL_ONLY_TYPES = frozenset({
    SyllableType.CVCC,
    SyllableType.CVVC,
})


def validate_syllable(syllable: SyllableUnit, is_final: bool) -> Tuple[bool, List[str]]:
    """Validate a single syllable.

    Parameters
    ----------
    syllable : SyllableUnit
        The syllable to validate.
    is_final : bool
        Whether this syllable is word-final.

    Returns
    -------
    tuple[bool, list[str]]
        ``(is_valid, violations)``.
    """
    violations: List[str] = []

    if syllable.syllable_type not in LEGAL_TYPES:
        violations.append(
            f"Illegal syllable type: {syllable.syllable_type.name}"
        )

    if syllable.syllable_type in FINAL_ONLY_TYPES and not is_final:
        violations.append(
            f"{syllable.syllable_type.name} only permitted word-finally"
        )

    if not syllable.onset:
        violations.append("Arabic syllables must have an onset (consonant)")

    return len(violations) == 0, violations


def validate_analysis(analysis: SyllableAnalysis) -> Tuple[bool, List[str]]:
    """Validate a full syllable analysis.

    Parameters
    ----------
    analysis : SyllableAnalysis
        Pre-computed analysis from :func:`segmenter.segment`.

    Returns
    -------
    tuple[bool, list[str]]
        ``(is_valid, violations)``.
    """
    all_violations: List[str] = []
    syllables = analysis.pattern.syllables

    for i, syl in enumerate(syllables):
        is_final = i == len(syllables) - 1
        _, violations = validate_syllable(syl, is_final)
        all_violations.extend(violations)

    return len(all_violations) == 0, all_violations
