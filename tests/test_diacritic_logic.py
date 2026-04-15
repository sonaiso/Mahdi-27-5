"""Tests for the Diacritic Logic layer (E2).

Tests diacritical mark analysis, binding, validation, and rules.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    DiacriticConsistency,
    DiacriticRole,
    DiacriticType,
)
from arabic_engine.diacritics.analyzer import analyze
from arabic_engine.diacritics.rules import MAX_MARKS_PER_CONSONANT, is_valid_binding
from arabic_engine.diacritics.validator import validate


class TestDiacriticAnalysis:
    """Tests for diacritical mark analysis."""

    def test_analyze_fully_voweled(self) -> None:
        """Fully voweled word should have is_fully_voweled=True."""
        result = analyze("كَتَبَ")
        assert result.is_fully_voweled is True
        assert result.mark_count == 3

    def test_analyze_unvoweled(self) -> None:
        """Unvoweled word should have is_fully_voweled=False."""
        result = analyze("كتب")
        assert result.is_fully_voweled is False
        assert result.is_partially_voweled is False
        assert result.mark_count == 0

    def test_analyze_partially_voweled(self) -> None:
        """Partially voweled word should be detected."""
        result = analyze("كَتب")  # Only first consonant voweled
        assert result.is_partially_voweled is True
        assert result.is_fully_voweled is False

    def test_analyze_returns_correct_mark_types(self) -> None:
        """Check that fatha marks are correctly typed."""
        result = analyze("كَتَبَ")
        for binding in result.bindings:
            for mark in binding.marks:
                assert mark.mark_type == DiacriticType.FATHA

    def test_analyze_token_preserved(self) -> None:
        """Input token should be preserved in analysis."""
        token = "كَتَبَ"
        result = analyze(token)
        assert result.token == token

    def test_analyze_empty_string(self) -> None:
        """Empty string should return empty analysis."""
        result = analyze("")
        assert result.mark_count == 0
        assert len(result.bindings) == 0


class TestDiacriticBindings:
    """Tests for diacritical binding details."""

    def test_binding_base_char(self) -> None:
        """Each binding should record the correct base character."""
        result = analyze("كَتَبَ")
        bases = [b.base_char for b in result.bindings]
        assert "ك" in bases
        assert "ت" in bases
        assert "ب" in bases

    def test_binding_consistency_consistent(self) -> None:
        """Normal voweled word should have consistent bindings."""
        result = analyze("كَتَبَ")
        for binding in result.bindings:
            assert binding.consistency == DiacriticConsistency.CONSISTENT


class TestDiacriticValidation:
    """Tests for diacritical validation."""

    def test_validate_valid_token(self) -> None:
        """Correctly voweled token should pass validation."""
        is_valid, violations = validate("كَتَبَ")
        assert is_valid is True
        assert len(violations) == 0

    def test_validate_unvoweled_token(self) -> None:
        """Unvoweled token should pass (no conflicts)."""
        is_valid, violations = validate("كتب")
        assert is_valid is True

    def test_validate_returns_tuple(self) -> None:
        """Validation should return (bool, list) tuple."""
        result = validate("كَتَبَ")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)


class TestDiacriticRules:
    """Tests for diacritical rule functions."""

    def test_max_marks_constant(self) -> None:
        """MAX_MARKS_PER_CONSONANT should be 2 (shadda + vowel)."""
        assert MAX_MARKS_PER_CONSONANT == 2

    def test_valid_binding_single_fatha(self) -> None:
        """Single fatha binding should be valid."""
        result = analyze("كَ")
        for binding in result.bindings:
            if binding.marks:
                assert is_valid_binding(binding) is True


class TestDiacriticRole:
    """Tests for role classification."""

    def test_tanwin_is_inflectional(self) -> None:
        """Tanwin marks should be classified as inflectional."""
        result = analyze("كِتَابًا")  # tanwin fath
        last_binding = result.bindings[-1]
        assert last_binding.role == DiacriticRole.INFLECTIONAL
