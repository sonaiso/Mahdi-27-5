"""Tests for Wad' and Mental Meaning Constitution v1.

Invariants tested
-----------------
Wad' Record (Art. 5–8):
  1. build_wad_record produces a valid WadRecord with all four elements.
  2. build_wad_record rejects empty lafz.
  3. build_wad_record rejects empty mental_meaning.
  4. build_wad_record rejects missing tasawwur.
  5. build_wad_record rejects invalid confidence.
  6. WadRecord is frozen.

Mental Meaning (Art. 18–23):
  7. build_mental_meaning produces a valid MentalMeaningRecord.
  8. build_mental_meaning rejects empty content.
  9. MentalMeaningRecord is frozen.
  10. Mental meaning may or may not match external reality (Art. 23).

Nisba / Ratios (Art. 32–35):
  11. build_nisba produces a valid NisbaRecord.
  12. build_nisba rejects empty first_term.
  13. build_nisba rejects empty second_term.
  14. NisbaRecord is frozen.
  15. All NisbaType members are constructible.

Anti-Jump (Art. 40–42):
  16. check_wad_jump detects missing tasawwur.
  17. check_wad_jump detects missing mental meaning.
  18. check_wad_jump detects missing method.
  19. check_wad_jump detects missing mental mediation.
  20. check_wad_jump detects missing nisab.
  21. check_all_wad_jumps returns 5 results.
  22. check_all_wad_jumps with all flags True → no violations.
  23. WadJumpCheckResult is frozen.

Chain Validation (Art. 43–44):
  24. Full valid chain passes.
  25. Missing tasawwur breaks chain.
  26. Wad' without tasawwur breaks chain.
  27. Mental meaning without wad' breaks chain.
  28. Nisab without mental meaning breaks chain.
  29. Expression without nisab breaks chain.

Constitution Validation (Art. 1–51):
  30. validate_wad_constitution returns valid result for default input.
  31. validate_wad_constitution result is frozen.
  32. Chain position is correct.
  33. Jump checks contain exactly 5 entries.
  34. Wad records are non-empty.
  35. Mental meanings are non-empty.
  36. Nisab are non-empty.

Enums:
  37. WadElement has exactly 4 members.
  38. MentalMeaningSource has exactly 4 members.
  39. ExpressionMode has exactly 3 members.
  40. NisbaType has exactly 5 members.
  41. WadJumpViolation has exactly 5 members.

Constants:
  42. GOVERNING_CHAIN has 11 positions.
  43. CHAIN_POSITION is in GOVERNING_CHAIN.
  44. EXPRESSION_PREFERENCE_ORDER starts with LAFZ.
  45. EXPRESSION_PREFERENCE_ORDER has 3 entries.

Public API:
  46. All public names importable from arabic_engine.core.
  47. Constitution module importable from arabic_engine.linkage.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    ExpressionMode,
    MentalMeaningSource,
    NisbaType,
    WadElement,
    WadJumpViolation,
)
from arabic_engine.core.types import (
    MentalMeaningRecord,
    NisbaRecord,
    WadConstitutionResult,
    WadRecord,
)
from arabic_engine.linkage.wad_constitution import (
    CHAIN_POSITION,
    EXPRESSION_PREFERENCE_ORDER,
    GOVERNING_CHAIN,
    build_mental_meaning,
    build_nisba,
    build_wad_record,
    check_all_wad_jumps,
    check_wad_jump,
    validate_wad_chain,
    validate_wad_constitution,
)

# ═══════════════════════════════════════════════════════════════════════
# Wad' Record tests (Art. 5–8)
# ═══════════════════════════════════════════════════════════════════════


class TestBuildWadRecord:
    """build_wad_record produces valid WadRecord or raises ValueError."""

    def test_valid_wad_record(self):
        wr = build_wad_record(
            wad_id="W1",
            lafz="كتب",
            mental_meaning="فعل الكتابة",
            tasawwur_present=True,
        )
        assert isinstance(wr, WadRecord)
        assert wr.wad_id == "W1"
        assert wr.lafz == "كتب"
        assert wr.mental_meaning == "فعل الكتابة"
        assert wr.tasawwur_present is True
        assert wr.confidence == 1.0

    def test_all_four_elements_present(self):
        wr = build_wad_record("W1", "كتب", "فعل الكتابة", True)
        assert len(wr.elements) == 4
        element_set = set(wr.elements)
        assert WadElement.LAFZ in element_set
        assert WadElement.MEANING in element_set
        assert WadElement.TAKHSIS in element_set
        assert WadElement.COMPREHENSIBILITY in element_set

    def test_rejects_empty_lafz(self):
        with pytest.raises(ValueError, match="lafz"):
            build_wad_record("W1", "", "meaning", True)

    def test_rejects_empty_mental_meaning(self):
        with pytest.raises(ValueError, match="mental meaning"):
            build_wad_record("W1", "كتب", "", True)

    def test_rejects_missing_tasawwur(self):
        with pytest.raises(ValueError, match="tasawwur"):
            build_wad_record("W1", "كتب", "meaning", False)

    def test_rejects_invalid_confidence_above(self):
        with pytest.raises(ValueError, match="Confidence"):
            build_wad_record("W1", "كتب", "meaning", True, confidence=1.5)

    def test_rejects_invalid_confidence_below(self):
        with pytest.raises(ValueError, match="Confidence"):
            build_wad_record("W1", "كتب", "meaning", True, confidence=-0.1)

    def test_custom_confidence(self):
        wr = build_wad_record("W1", "كتب", "meaning", True, confidence=0.8)
        assert wr.confidence == 0.8

    def test_wad_record_is_frozen(self):
        wr = build_wad_record("W1", "كتب", "meaning", True)
        with pytest.raises(AttributeError):
            wr.lafz = "changed"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# Mental Meaning tests (Art. 18–23)
# ═══════════════════════════════════════════════════════════════════════


class TestBuildMentalMeaning:
    """build_mental_meaning produces valid MentalMeaningRecord."""

    def test_valid_mental_meaning(self):
        mm = build_mental_meaning(
            meaning_id="MM1",
            content="صورة الإنسان في الذهن",
            source=MentalMeaningSource.PERCEPTION,
        )
        assert isinstance(mm, MentalMeaningRecord)
        assert mm.meaning_id == "MM1"
        assert mm.content == "صورة الإنسان في الذهن"
        assert mm.source == MentalMeaningSource.PERCEPTION
        assert mm.matches_external is True  # default

    def test_rejects_empty_content(self):
        with pytest.raises(ValueError, match="content"):
            build_mental_meaning("MM1", "", MentalMeaningSource.PERCEPTION)

    def test_mental_meaning_is_frozen(self):
        mm = build_mental_meaning("MM1", "content", MentalMeaningSource.PERCEPTION)
        with pytest.raises(AttributeError):
            mm.content = "changed"  # type: ignore[misc]

    def test_may_not_match_external(self):
        """Art. 23 — mental meaning may not match external reality."""
        mm = build_mental_meaning(
            "MM1", "ما ظنه حجرًا",
            MentalMeaningSource.PERCEPTION,
            matches_external=False,
        )
        assert mm.matches_external is False

    def test_all_sources_constructible(self):
        for src in MentalMeaningSource:
            mm = build_mental_meaning("MM1", "content", src)
            assert mm.source == src

    def test_with_source_tasawwur(self):
        mm = build_mental_meaning(
            "MM1", "content", MentalMeaningSource.ABSTRACTION,
            source_tasawwur="TASAWWUR_1",
        )
        assert mm.source_tasawwur == "TASAWWUR_1"


# ═══════════════════════════════════════════════════════════════════════
# Nisba / Ratios tests (Art. 32–35)
# ═══════════════════════════════════════════════════════════════════════


class TestBuildNisba:
    """build_nisba produces valid NisbaRecord."""

    def test_valid_nisba(self):
        nr = build_nisba(
            nisba_id="N1",
            nisba_type=NisbaType.ISNADIYYA,
            first_term="زيد",
            second_term="قائم",
            expression_complete=True,
        )
        assert isinstance(nr, NisbaRecord)
        assert nr.nisba_id == "N1"
        assert nr.nisba_type == NisbaType.ISNADIYYA
        assert nr.first_term == "زيد"
        assert nr.second_term == "قائم"
        assert nr.expression_complete is True

    def test_rejects_empty_first_term(self):
        with pytest.raises(ValueError, match="term"):
            build_nisba("N1", NisbaType.ISNADIYYA, "", "قائم")

    def test_rejects_empty_second_term(self):
        with pytest.raises(ValueError, match="term"):
            build_nisba("N1", NisbaType.ISNADIYYA, "زيد", "")

    def test_nisba_is_frozen(self):
        nr = build_nisba("N1", NisbaType.ISNADIYYA, "زيد", "قائم")
        with pytest.raises(AttributeError):
            nr.first_term = "changed"  # type: ignore[misc]

    def test_all_nisba_types_constructible(self):
        for nt in NisbaType:
            nr = build_nisba("N1", nt, "أ", "ب")
            assert nr.nisba_type == nt

    def test_default_expression_not_complete(self):
        nr = build_nisba("N1", NisbaType.TAQYIDIYYA, "أ", "ب")
        assert nr.expression_complete is False


# ═══════════════════════════════════════════════════════════════════════
# Anti-Jump tests (Art. 40–42)
# ═══════════════════════════════════════════════════════════════════════


class TestCheckWadJump:
    """check_wad_jump detects prohibited jumps."""

    def test_detects_missing_tasawwur(self):
        result = check_wad_jump(
            WadJumpViolation.LAFZ_TO_MEANING_NO_TASAWWUR,
            tasawwur_present=False,
        )
        assert result.detected is True

    def test_no_violation_when_tasawwur_present(self):
        result = check_wad_jump(
            WadJumpViolation.LAFZ_TO_MEANING_NO_TASAWWUR,
            tasawwur_present=True,
        )
        assert result.detected is False

    def test_detects_missing_mental_meaning(self):
        result = check_wad_jump(
            WadJumpViolation.LAFZ_TO_EXTERNAL_NO_MENTAL,
            mental_meaning_present=False,
        )
        assert result.detected is True

    def test_detects_missing_method(self):
        result = check_wad_jump(
            WadJumpViolation.LANGUAGE_TO_JUDGEMENT_NO_METHOD,
            method_present=False,
        )
        assert result.detected is True

    def test_detects_missing_mental_mediation(self):
        result = check_wad_jump(
            WadJumpViolation.WAD_TO_EXTERNAL_DIRECT,
            mental_mediation=False,
        )
        assert result.detected is True

    def test_detects_missing_nisab(self):
        result = check_wad_jump(
            WadJumpViolation.MUFRADAT_TO_EXPRESSION_NO_NISAB,
            nisab_present=False,
        )
        assert result.detected is True

    def test_jump_check_result_is_frozen(self):
        result = check_wad_jump(
            WadJumpViolation.LAFZ_TO_MEANING_NO_TASAWWUR,
            tasawwur_present=True,
        )
        with pytest.raises(AttributeError):
            result.detected = True  # type: ignore[misc]

    def test_jump_check_has_descriptions(self):
        result = check_wad_jump(
            WadJumpViolation.LAFZ_TO_MEANING_NO_TASAWWUR,
            tasawwur_present=True,
        )
        assert result.description
        assert result.description_ar


class TestCheckAllWadJumps:
    """check_all_wad_jumps returns complete results."""

    def test_returns_five_results(self):
        results = check_all_wad_jumps()
        assert len(results) == 5

    def test_all_flags_true_no_violations(self):
        results = check_all_wad_jumps(
            tasawwur_present=True,
            mental_meaning_present=True,
            method_present=True,
            mental_mediation=True,
            nisab_present=True,
        )
        assert all(not r.detected for r in results)

    def test_all_flags_false_all_violations(self):
        results = check_all_wad_jumps(
            tasawwur_present=False,
            mental_meaning_present=False,
            method_present=False,
            mental_mediation=False,
            nisab_present=False,
        )
        assert all(r.detected for r in results)

    def test_each_violation_type_present(self):
        results = check_all_wad_jumps()
        violations = {r.violation for r in results}
        assert violations == set(WadJumpViolation)


# ═══════════════════════════════════════════════════════════════════════
# Chain Validation tests (Art. 43–44)
# ═══════════════════════════════════════════════════════════════════════


class TestValidateWadChain:
    """validate_wad_chain validates T → W → M → R → E."""

    def test_full_valid_chain(self):
        valid, errors = validate_wad_chain(
            tasawwur=True, wad=True, mental_meaning=True,
            nisab=True, expression=True,
        )
        assert valid is True
        assert errors == []

    def test_missing_tasawwur(self):
        valid, errors = validate_wad_chain(
            tasawwur=False, wad=True, mental_meaning=True,
            nisab=True, expression=True,
        )
        assert valid is False
        assert any("Tasawwur" in e for e in errors)

    def test_wad_without_tasawwur(self):
        valid, errors = validate_wad_chain(
            tasawwur=False, wad=True, mental_meaning=False,
            nisab=False, expression=False,
        )
        assert valid is False
        assert any("فرع" in e for e in errors)

    def test_mental_meaning_without_wad(self):
        valid, errors = validate_wad_chain(
            tasawwur=True, wad=False, mental_meaning=True,
            nisab=False, expression=False,
        )
        assert valid is False
        assert any("W" in e for e in errors)

    def test_nisab_without_mental_meaning(self):
        valid, errors = validate_wad_chain(
            tasawwur=True, wad=True, mental_meaning=False,
            nisab=True, expression=False,
        )
        assert valid is False
        assert any("النسب" in e or "Nisab" in e for e in errors)

    def test_expression_without_nisab(self):
        valid, errors = validate_wad_chain(
            tasawwur=True, wad=True, mental_meaning=True,
            nisab=False, expression=True,
        )
        assert valid is False
        assert any("Expression" in e or "التعبير" in e for e in errors)

    def test_partial_chain_valid(self):
        """T + W only, no later stages → valid."""
        valid, errors = validate_wad_chain(
            tasawwur=True, wad=True, mental_meaning=False,
            nisab=False, expression=False,
        )
        assert valid is True


# ═══════════════════════════════════════════════════════════════════════
# Constitution Validation tests (Art. 1–51)
# ═══════════════════════════════════════════════════════════════════════


class TestValidateWadConstitution:
    """validate_wad_constitution returns full validation result."""

    def test_default_is_valid(self):
        result = validate_wad_constitution()
        assert isinstance(result, WadConstitutionResult)
        assert result.valid is True, f"Errors: {result.errors}"
        assert result.errors == ()

    def test_result_is_frozen(self):
        result = validate_wad_constitution()
        with pytest.raises(AttributeError):
            result.valid = False  # type: ignore[misc]

    def test_chain_position(self):
        result = validate_wad_constitution()
        assert result.chain_position == "وضع/لغة/نسب"

    def test_jump_checks_count(self):
        result = validate_wad_constitution()
        assert len(result.jump_checks) == 5

    def test_wad_records_non_empty(self):
        result = validate_wad_constitution()
        assert len(result.wad_records) >= 1

    def test_mental_meanings_non_empty(self):
        result = validate_wad_constitution()
        assert len(result.mental_meanings) >= 1

    def test_nisab_non_empty(self):
        result = validate_wad_constitution()
        assert len(result.nisab) >= 1

    def test_no_jump_violations_in_valid_result(self):
        result = validate_wad_constitution()
        for jc in result.jump_checks:
            assert jc.detected is False, (
                f"Unexpected jump violation: {jc.description}"
            )

    def test_custom_input(self):
        result = validate_wad_constitution(
            lafz="قرأ",
            mental_meaning_content="فعل القراءة",
        )
        assert result.valid is True
        assert result.wad_records[0].lafz == "قرأ"


# ═══════════════════════════════════════════════════════════════════════
# Enum completeness tests
# ═══════════════════════════════════════════════════════════════════════


class TestWadEnums:
    """Enum membership and count tests."""

    def test_wad_element_count(self):
        assert len(WadElement) == 4

    def test_wad_element_names(self):
        names = {e.name for e in WadElement}
        assert names == {"LAFZ", "MEANING", "TAKHSIS", "COMPREHENSIBILITY"}

    def test_mental_meaning_source_count(self):
        assert len(MentalMeaningSource) == 4

    def test_mental_meaning_source_names(self):
        names = {s.name for s in MentalMeaningSource}
        assert names == {"PERCEPTION", "ABSTRACTION", "PRIOR_KNOWLEDGE", "COMPOSITION"}

    def test_expression_mode_count(self):
        assert len(ExpressionMode) == 3

    def test_expression_mode_names(self):
        names = {m.name for m in ExpressionMode}
        assert names == {"LAFZ", "ISHARA", "MITHAL"}

    def test_nisba_type_count(self):
        assert len(NisbaType) == 5

    def test_nisba_type_names(self):
        names = {t.name for t in NisbaType}
        assert names == {
            "ISNADIYYA", "TAQYIDIYYA", "IDAFIYYA",
            "FA3ILIYYA", "MAF3ULIYYA",
        }

    def test_wad_jump_violation_count(self):
        assert len(WadJumpViolation) == 5


# ═══════════════════════════════════════════════════════════════════════
# Constants tests
# ═══════════════════════════════════════════════════════════════════════


class TestWadConstants:
    """Module-level constants tests."""

    def test_governing_chain_length(self):
        assert len(GOVERNING_CHAIN) == 11

    def test_chain_position_in_chain(self):
        assert CHAIN_POSITION in GOVERNING_CHAIN

    def test_chain_position_value(self):
        assert CHAIN_POSITION == "وضع/لغة/نسب"

    def test_expression_preference_starts_with_lafz(self):
        assert EXPRESSION_PREFERENCE_ORDER[0] == ExpressionMode.LAFZ

    def test_expression_preference_length(self):
        assert len(EXPRESSION_PREFERENCE_ORDER) == 3


# ═══════════════════════════════════════════════════════════════════════
# Public API re-export tests
# ═══════════════════════════════════════════════════════════════════════


class TestPublicAPIReExports:
    """All public names accessible from arabic_engine.core."""

    def test_enums_importable_from_core(self):
        import arabic_engine.core as core  # noqa: PLC0415
        for name in [
            "WadElement", "MentalMeaningSource", "ExpressionMode",
            "NisbaType", "WadJumpViolation",
        ]:
            assert hasattr(core, name), f"{name!r} not in core"

    def test_types_importable_from_core(self):
        import arabic_engine.core as core  # noqa: PLC0415
        for name in [
            "WadRecord", "MentalMeaningRecord", "NisbaRecord",
            "WadJumpCheckResult", "WadConstitutionResult",
        ]:
            assert hasattr(core, name), f"{name!r} not in core"

    def test_constitution_importable_from_linkage(self):
        import arabic_engine.linkage.wad_constitution as wc  # noqa: PLC0415
        for name in [
            "build_wad_record", "build_mental_meaning", "build_nisba",
            "check_wad_jump", "check_all_wad_jumps",
            "validate_wad_chain", "validate_wad_constitution",
            "GOVERNING_CHAIN", "CHAIN_POSITION",
            "EXPRESSION_PREFERENCE_ORDER",
        ]:
            assert hasattr(wc, name), f"{name!r} not in wad_constitution"
