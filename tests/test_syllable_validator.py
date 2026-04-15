"""Tests for syllables.validator.validate_syllable — individual syllable validation.

Covers:
- Legal syllable types (CV, CVC, CVV, CVVC, CVCC)
- Final-only types (CVCC, CVVC) in non-final position
- Syllables without onset
- All boolean is_final combinations
"""

from __future__ import annotations

from arabic_engine.core.enums import SyllableType, SyllableWeight
from arabic_engine.core.types import SyllableUnit
from arabic_engine.syllables.validator import (
    FINAL_ONLY_TYPES,
    LEGAL_TYPES,
    validate_syllable,
)


def _make_syllable(
    onset: str = "ك",
    nucleus: str = "َ",
    coda: str = "",
    syllable_type: SyllableType = SyllableType.CV,
    weight: SyllableWeight = SyllableWeight.LIGHT,
    text: str = "كَ",
) -> SyllableUnit:
    return SyllableUnit(
        onset=onset,
        nucleus=nucleus,
        coda=coda,
        syllable_type=syllable_type,
        weight=weight,
        text=text,
    )


# ═══════════════════════════════════════════════════════════════════════
# Legal syllable types
# ═══════════════════════════════════════════════════════════════════════


class TestLegalSyllableTypes:
    """Test all legal syllable types in appropriate positions."""

    def test_cv_valid_final(self):
        """CV syllable is valid in final position."""
        syl = _make_syllable(syllable_type=SyllableType.CV)
        valid, violations = validate_syllable(syl, is_final=True)
        assert valid is True
        assert violations == []

    def test_cv_valid_non_final(self):
        """CV syllable is valid in non-final position."""
        syl = _make_syllable(syllable_type=SyllableType.CV)
        valid, violations = validate_syllable(syl, is_final=False)
        assert valid is True
        assert violations == []

    def test_cvc_valid_final(self):
        """CVC syllable is valid in final position."""
        syl = _make_syllable(
            onset="ك", nucleus="َ", coda="ت",
            syllable_type=SyllableType.CVC,
            weight=SyllableWeight.HEAVY,
            text="كَت",
        )
        valid, violations = validate_syllable(syl, is_final=True)
        assert valid is True

    def test_cvc_valid_non_final(self):
        """CVC syllable is valid in non-final position."""
        syl = _make_syllable(
            onset="ك", nucleus="َ", coda="ت",
            syllable_type=SyllableType.CVC,
            weight=SyllableWeight.HEAVY,
        )
        valid, violations = validate_syllable(syl, is_final=False)
        assert valid is True

    def test_cvv_valid_any_position(self):
        """CVV syllable is valid in any position."""
        syl = _make_syllable(
            onset="ك", nucleus="ا",
            syllable_type=SyllableType.CVV,
            weight=SyllableWeight.HEAVY,
        )
        valid_final, _ = validate_syllable(syl, is_final=True)
        valid_non_final, _ = validate_syllable(syl, is_final=False)
        assert valid_final is True
        assert valid_non_final is True

    def test_cvvc_valid_final(self):
        """CVVC syllable is valid word-finally."""
        syl = _make_syllable(
            onset="ك", nucleus="ا", coda="ت",
            syllable_type=SyllableType.CVVC,
            weight=SyllableWeight.SUPER,
        )
        valid, violations = validate_syllable(syl, is_final=True)
        assert valid is True
        assert violations == []

    def test_cvcc_valid_final(self):
        """CVCC syllable is valid word-finally."""
        syl = _make_syllable(
            onset="ك", nucleus="َ", coda="تب",
            syllable_type=SyllableType.CVCC,
            weight=SyllableWeight.SUPER,
        )
        valid, violations = validate_syllable(syl, is_final=True)
        assert valid is True
        assert violations == []


# ═══════════════════════════════════════════════════════════════════════
# Final-only types in non-final position
# ═══════════════════════════════════════════════════════════════════════


class TestFinalOnlyTypes:
    """CVCC and CVVC are only legal word-finally."""

    def test_cvcc_non_final_invalid(self):
        """CVCC in non-final position should produce a violation."""
        syl = _make_syllable(
            onset="ك", nucleus="َ", coda="تب",
            syllable_type=SyllableType.CVCC,
            weight=SyllableWeight.SUPER,
        )
        valid, violations = validate_syllable(syl, is_final=False)
        assert valid is False
        assert len(violations) == 1
        assert "CVCC" in violations[0]
        assert "word-finally" in violations[0]

    def test_cvvc_non_final_invalid(self):
        """CVVC in non-final position should produce a violation."""
        syl = _make_syllable(
            onset="ك", nucleus="ا", coda="ت",
            syllable_type=SyllableType.CVVC,
            weight=SyllableWeight.SUPER,
        )
        valid, violations = validate_syllable(syl, is_final=False)
        assert valid is False
        assert len(violations) == 1
        assert "CVVC" in violations[0]

    def test_final_only_types_constant(self):
        """FINAL_ONLY_TYPES should contain exactly CVCC and CVVC."""
        assert SyllableType.CVCC in FINAL_ONLY_TYPES
        assert SyllableType.CVVC in FINAL_ONLY_TYPES
        assert len(FINAL_ONLY_TYPES) == 2


# ═══════════════════════════════════════════════════════════════════════
# Onset requirement
# ═══════════════════════════════════════════════════════════════════════


class TestOnsetRequirement:
    """Arabic syllables must have an onset (consonant)."""

    def test_no_onset_invalid(self):
        """Syllable without onset violates Arabic phonotactics."""
        syl = _make_syllable(
            onset="",
            nucleus="َ",
            syllable_type=SyllableType.CV,
        )
        valid, violations = validate_syllable(syl, is_final=True)
        assert valid is False
        assert any("onset" in v.lower() for v in violations)

    def test_no_onset_non_final_invalid(self):
        """Syllable without onset in non-final position is also invalid."""
        syl = _make_syllable(
            onset="",
            nucleus="َ",
            syllable_type=SyllableType.CV,
        )
        valid, violations = validate_syllable(syl, is_final=False)
        assert valid is False

    def test_with_onset_valid(self):
        """Syllable with onset is valid (onset requirement met)."""
        syl = _make_syllable(onset="ك", syllable_type=SyllableType.CV)
        valid, violations = validate_syllable(syl, is_final=True)
        assert valid is True


# ═══════════════════════════════════════════════════════════════════════
# Multiple violations
# ═══════════════════════════════════════════════════════════════════════


class TestMultipleViolations:
    """A syllable can have multiple violations simultaneously."""

    def test_cvcc_non_final_no_onset(self):
        """CVCC, non-final, AND no onset = 2 violations."""
        syl = _make_syllable(
            onset="",
            nucleus="َ",
            coda="تب",
            syllable_type=SyllableType.CVCC,
            weight=SyllableWeight.SUPER,
        )
        valid, violations = validate_syllable(syl, is_final=False)
        assert valid is False
        assert len(violations) == 2  # final-only + no onset


# ═══════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════


class TestConstants:
    """Verify module-level constants."""

    def test_legal_types_has_five_entries(self):
        """LEGAL_TYPES should have exactly 5 entries."""
        assert len(LEGAL_TYPES) == 5

    def test_legal_types_contains_all_syllable_types(self):
        """All SyllableType values should be legal."""
        for st in SyllableType:
            assert st in LEGAL_TYPES
