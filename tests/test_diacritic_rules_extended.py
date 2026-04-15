"""Tests for diacritics.rules.classify_role and diacritics.validator.validate_analysis.

Covers:
- classify_role with inflectional marks (tanwin)
- classify_role with is_final=True/False
- classify_role with lexical marks (non-final position)
- validate_analysis with pre-computed DiacriticAnalysis
- validate_analysis with various consistency states
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    DiacriticConsistency,
    DiacriticRole,
    DiacriticType,
)
from arabic_engine.core.types import DiacriticAnalysis, DiacriticBinding, DiacriticMark
from arabic_engine.diacritics.analyzer import analyze
from arabic_engine.diacritics.rules import classify_role
from arabic_engine.diacritics.validator import validate, validate_analysis


def _make_binding(
    base_char: str = "ك",
    base_index: int = 0,
    mark_types: tuple[DiacriticType, ...] = (),
    consistency: DiacriticConsistency = DiacriticConsistency.CONSISTENT,
    role: DiacriticRole = DiacriticRole.LEXICAL,
) -> DiacriticBinding:
    """Create a DiacriticBinding for testing."""
    marks = tuple(
        DiacriticMark(
            code_point=0x064E,  # placeholder
            mark_type=mt,
            base_char=base_char,
            position=base_index,
        )
        for mt in mark_types
    )
    return DiacriticBinding(
        base_char=base_char,
        base_index=base_index,
        marks=marks,
        consistency=consistency,
        role=role,
    )


def _make_analysis(
    token: str = "كَتَبَ",
    bindings: tuple[DiacriticBinding, ...] = (),
    mark_count: int = 0,
    consistency: DiacriticConsistency = DiacriticConsistency.CONSISTENT,
    is_fully_voweled: bool = True,
    is_partially_voweled: bool = False,
) -> DiacriticAnalysis:
    """Create a DiacriticAnalysis for testing."""
    return DiacriticAnalysis(
        token=token,
        bindings=bindings,
        mark_count=mark_count,
        consistency=consistency,
        is_fully_voweled=is_fully_voweled,
        is_partially_voweled=is_partially_voweled,
    )


# ═══════════════════════════════════════════════════════════════════════
# classify_role
# ═══════════════════════════════════════════════════════════════════════


class TestClassifyRole:
    """Tests for rules.classify_role."""

    def test_tanwin_fath_is_inflectional(self):
        """Tanwin fath mark should be classified as INFLECTIONAL."""
        binding = _make_binding(mark_types=(DiacriticType.TANWIN_F,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.INFLECTIONAL

    def test_tanwin_damm_is_inflectional(self):
        """Tanwin damm mark should be classified as INFLECTIONAL."""
        binding = _make_binding(mark_types=(DiacriticType.TANWIN_D,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.INFLECTIONAL

    def test_tanwin_kasr_is_inflectional(self):
        """Tanwin kasr mark should be classified as INFLECTIONAL."""
        binding = _make_binding(mark_types=(DiacriticType.TANWIN_K,))
        role = classify_role(binding, is_final=True)
        assert role == DiacriticRole.INFLECTIONAL

    def test_final_position_is_inflectional(self):
        """Final consonant (حرف الإعراب) should be classified as INFLECTIONAL."""
        binding = _make_binding(mark_types=(DiacriticType.FATHA,))
        role = classify_role(binding, is_final=True)
        assert role == DiacriticRole.INFLECTIONAL

    def test_non_final_fatha_is_lexical(self):
        """Non-final fatha should be classified as LEXICAL."""
        binding = _make_binding(mark_types=(DiacriticType.FATHA,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.LEXICAL

    def test_non_final_damma_is_lexical(self):
        """Non-final damma should be classified as LEXICAL."""
        binding = _make_binding(mark_types=(DiacriticType.DAMMA,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.LEXICAL

    def test_non_final_kasra_is_lexical(self):
        """Non-final kasra should be classified as LEXICAL."""
        binding = _make_binding(mark_types=(DiacriticType.KASRA,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.LEXICAL

    def test_non_final_sukun_is_lexical(self):
        """Non-final sukun should be classified as LEXICAL."""
        binding = _make_binding(mark_types=(DiacriticType.SUKUN,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.LEXICAL

    def test_non_final_shadda_is_lexical(self):
        """Non-final shadda (gemination) should be classified as LEXICAL."""
        binding = _make_binding(mark_types=(DiacriticType.SHADDA,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.LEXICAL

    def test_empty_marks_non_final_is_lexical(self):
        """Consonant with no marks in non-final position is LEXICAL."""
        binding = _make_binding(mark_types=())
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.LEXICAL

    def test_empty_marks_final_is_inflectional(self):
        """Consonant with no marks in final position is INFLECTIONAL."""
        binding = _make_binding(mark_types=())
        role = classify_role(binding, is_final=True)
        assert role == DiacriticRole.INFLECTIONAL

    def test_tanwin_overrides_non_final(self):
        """Tanwin in non-final position still classifies as INFLECTIONAL."""
        binding = _make_binding(mark_types=(DiacriticType.TANWIN_F,))
        role = classify_role(binding, is_final=False)
        assert role == DiacriticRole.INFLECTIONAL

    def test_with_real_analyzed_binding(self):
        """classify_role works with bindings from analyze()."""
        analysis = analyze("كَتَبَ")
        if analysis.bindings:
            last_binding = analysis.bindings[-1]
            role = classify_role(last_binding, is_final=True)
            assert role == DiacriticRole.INFLECTIONAL


# ═══════════════════════════════════════════════════════════════════════
# validate_analysis
# ═══════════════════════════════════════════════════════════════════════


class TestValidateAnalysis:
    """Tests for validator.validate_analysis."""

    def test_consistent_analysis_valid(self):
        """All consistent bindings should pass validation."""
        binding = _make_binding(
            mark_types=(DiacriticType.FATHA,),
            consistency=DiacriticConsistency.CONSISTENT,
        )
        analysis = _make_analysis(bindings=(binding,), mark_count=1)
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is True
        assert violations == []

    def test_conflicting_binding_fails(self):
        """Conflicting binding should produce a violation."""
        binding = _make_binding(
            base_char="ت",
            base_index=1,
            mark_types=(DiacriticType.FATHA, DiacriticType.KASRA),
            consistency=DiacriticConsistency.CONFLICTING,
        )
        analysis = _make_analysis(bindings=(binding,), mark_count=2)
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is False
        assert len(violations) == 1
        assert "Conflicting" in violations[0]
        assert "ت" in violations[0]

    def test_redundant_binding_fails(self):
        """Redundant binding should produce a violation."""
        binding = _make_binding(
            base_char="ب",
            base_index=2,
            mark_types=(DiacriticType.FATHA, DiacriticType.FATHA),
            consistency=DiacriticConsistency.REDUNDANT,
        )
        analysis = _make_analysis(bindings=(binding,), mark_count=2)
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is False
        assert len(violations) == 1
        assert "Redundant" in violations[0]

    def test_incomplete_binding_passes(self):
        """Incomplete (missing marks) should not produce a violation."""
        binding = _make_binding(
            consistency=DiacriticConsistency.INCOMPLETE,
        )
        analysis = _make_analysis(bindings=(binding,))
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is True
        assert violations == []

    def test_empty_bindings_valid(self):
        """Analysis with no bindings should be valid."""
        analysis = _make_analysis(bindings=())
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is True
        assert violations == []

    def test_multiple_violations_collected(self):
        """Multiple problematic bindings should collect all violations."""
        binding1 = _make_binding(
            base_char="ك",
            base_index=0,
            consistency=DiacriticConsistency.CONFLICTING,
        )
        binding2 = _make_binding(
            base_char="ت",
            base_index=1,
            consistency=DiacriticConsistency.REDUNDANT,
        )
        analysis = _make_analysis(bindings=(binding1, binding2))
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is False
        assert len(violations) == 2

    def test_matches_token_based_validate(self):
        """validate_analysis should match validate() for same token."""
        token = "كَتَبَ"
        analysis = analyze(token)
        is_valid_token, violations_token = validate(token)
        is_valid_analysis, violations_analysis = validate_analysis(analysis)
        assert is_valid_token == is_valid_analysis
        assert violations_token == violations_analysis

    def test_with_real_analysis(self):
        """validate_analysis works with real analyze() output."""
        analysis = analyze("كَتَبَ")
        is_valid, violations = validate_analysis(analysis)
        assert is_valid is True
        assert violations == []
