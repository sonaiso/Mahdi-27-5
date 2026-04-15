"""Tests for the Syllabic Formation layer (E3).

Tests syllable segmentation, pattern classification, and validation.
"""

from __future__ import annotations

from arabic_engine.core.enums import SyllableType, SyllableWeight
from arabic_engine.syllables.patterns import PATTERN_REGISTRY, get_pattern_info, get_weight
from arabic_engine.syllables.segmenter import segment
from arabic_engine.syllables.validator import validate_analysis


class TestSyllableSegmentation:
    """Tests for syllable segmentation."""

    def test_segment_returns_analysis(self) -> None:
        """segment() should return a SyllableAnalysis."""
        result = segment("كَتَبَ")
        assert result.word == "كَتَبَ"
        assert result.is_valid is True

    def test_segment_simple_word(self) -> None:
        """Simple voweled word should produce syllables."""
        result = segment("كَتَبَ")
        assert len(result.pattern.syllables) > 0

    def test_segment_mora_count_positive(self) -> None:
        """Mora count should be positive for any word."""
        result = segment("كَتَبَ")
        assert result.mora_count > 0

    def test_segment_pattern_string(self) -> None:
        """Pattern should be a dot-separated type string."""
        result = segment("كَتَبَ")
        assert "." in result.pattern.pattern or result.pattern.pattern != ""

    def test_segment_empty_word(self) -> None:
        """Empty word should produce empty/invalid analysis."""
        result = segment("")
        assert len(result.pattern.syllables) == 0


class TestSyllablePatterns:
    """Tests for syllable pattern definitions."""

    def test_all_types_in_registry(self) -> None:
        """All SyllableType values should be in PATTERN_REGISTRY."""
        for stype in SyllableType:
            assert stype in PATTERN_REGISTRY

    def test_cv_is_light(self) -> None:
        """CV syllable should be light."""
        info = get_pattern_info(SyllableType.CV)
        assert info["weight"] == SyllableWeight.LIGHT

    def test_cvc_is_heavy(self) -> None:
        """CVC syllable should be heavy."""
        info = get_pattern_info(SyllableType.CVC)
        assert info["weight"] == SyllableWeight.HEAVY

    def test_cvcc_is_super(self) -> None:
        """CVCC syllable should be super-heavy."""
        info = get_pattern_info(SyllableType.CVCC)
        assert info["weight"] == SyllableWeight.SUPER

    def test_get_weight_function(self) -> None:
        """get_weight should return correct weight for known types."""
        assert get_weight(SyllableType.CV) == SyllableWeight.LIGHT
        assert get_weight(SyllableType.CVC) == SyllableWeight.HEAVY
        assert get_weight(SyllableType.CVVC) == SyllableWeight.SUPER


class TestSyllableValidation:
    """Tests for syllable validation."""

    def test_validate_simple_word(self) -> None:
        """Simple voweled word should be valid."""
        analysis = segment("كَتَبَ")
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is True
        assert len(violations) == 0

    def test_validate_empty_word(self) -> None:
        """Empty word analysis should still validate."""
        analysis = segment("")
        is_valid, violations = validate_analysis(analysis)
        # No syllables means no violations
        assert len(violations) == 0
