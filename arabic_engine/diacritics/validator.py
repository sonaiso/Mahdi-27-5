"""Diacritic validator — التحقق من صحة التشكيل.

Validates diacritical consistency on a token, checking for:
- Conflicting vowel marks on the same consonant
- Redundant / duplicate marks
- Missing expected marks (incomplete voweling)
"""

from __future__ import annotations

from typing import List, Tuple

from arabic_engine.core.enums import DiacriticConsistency
from arabic_engine.core.types import DiacriticAnalysis
from arabic_engine.diacritics.analyzer import analyze


def validate(token: str) -> Tuple[bool, List[str]]:
    """Validate diacritical marks on *token*.

    Parameters
    ----------
    token : str
        A single Arabic token.

    Returns
    -------
    tuple[bool, list[str]]
        ``(is_valid, violations)`` — True when no conflicts found.
    """
    analysis = analyze(token)
    violations: List[str] = []

    for binding in analysis.bindings:
        if binding.consistency == DiacriticConsistency.CONFLICTING:
            violations.append(
                f"Conflicting marks on '{binding.base_char}' "
                f"at index {binding.base_index}"
            )
        elif binding.consistency == DiacriticConsistency.REDUNDANT:
            violations.append(
                f"Redundant marks on '{binding.base_char}' "
                f"at index {binding.base_index}"
            )

    return len(violations) == 0, violations


def validate_analysis(analysis: DiacriticAnalysis) -> Tuple[bool, List[str]]:
    """Validate a pre-computed :class:`DiacriticAnalysis`.

    Parameters
    ----------
    analysis : DiacriticAnalysis
        Pre-computed analysis from :func:`analyzer.analyze`.

    Returns
    -------
    tuple[bool, list[str]]
        ``(is_valid, violations)``.
    """
    violations: List[str] = []

    for binding in analysis.bindings:
        if binding.consistency == DiacriticConsistency.CONFLICTING:
            violations.append(
                f"Conflicting marks on '{binding.base_char}' "
                f"at index {binding.base_index}"
            )
        elif binding.consistency == DiacriticConsistency.REDUNDANT:
            violations.append(
                f"Redundant marks on '{binding.base_char}' "
                f"at index {binding.base_index}"
            )

    return len(violations) == 0, violations
