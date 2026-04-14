"""Tests for the transition engine — قانون الانتقال بين الخانات."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    FunctionRole,
    PhonCategory,
    PhonTransform,
    SyllablePosition,
    TransitionCondition,
    TransitionLaw,
    TransitionType,
)
from arabic_engine.core.types import TransitionContext, TransitionResult, TransitionRule
from arabic_engine.signifier.dmin import lookup
from arabic_engine.signifier.transition import (
    TRANSITION_MATRIX,
    TRANSITION_PRIORITY,
    apply_best_transition,
    find_applicable_rules,
    format_matrix_table,
    stability_check,
)

# ── Helpers ──────────────────────────────────────────────────────────

def _ctx(
    position: SyllablePosition = SyllablePosition.ONSET,
    function_role: FunctionRole = FunctionRole.ROOT_RADICAL,
    left=None,
    right=None,
    economy: float = 0.0,
    pattern: str = "",
    architecture: str = "",
) -> TransitionContext:
    return TransitionContext(
        position=position,
        function_role=function_role,
        left_neighbor=left,
        right_neighbor=right,
        pattern=pattern,
        economy_pressure=economy,
        architecture=architecture,
    )


# ── New enum presence ────────────────────────────────────────────────

class TestNewEnums:
    """Verify all new enumerations are present and complete."""

    def test_transition_type_has_four_values(self):
        assert len(TransitionType) == 4
        assert TransitionType.FUNCTIONAL
        assert TransitionType.RANK
        assert TransitionType.CONTEXTUAL
        assert TransitionType.MORPHO_STRUCTURAL

    def test_transition_law_has_seven_values(self):
        assert len(TransitionLaw) == 7
        assert TransitionLaw.ITLAL
        assert TransitionLaw.IDGHAM
        assert TransitionLaw.IBDAL
        assert TransitionLaw.HADHF
        assert TransitionLaw.WAQF
        assert TransitionLaw.ZIYADA
        assert TransitionLaw.INZILAQ

    def test_transition_condition_has_five_values(self):
        assert len(TransitionCondition) == 5
        assert TransitionCondition.STRUCTURAL_VALIDITY
        assert TransitionCondition.PHONETIC_BALANCE
        assert TransitionCondition.ROOT_PRESERVATION
        assert TransitionCondition.FUNCTION_PRESERVATION
        assert TransitionCondition.NON_CONTRADICTION

    def test_syllable_position_has_four_values(self):
        assert len(SyllablePosition) == 4

    def test_function_role_has_seven_values(self):
        assert len(FunctionRole) == 7


# ── TransitionMatrix structure ───────────────────────────────────────

class TestTransitionMatrix:
    """The TRANSITION_MATRIX must satisfy structural invariants."""

    def test_matrix_is_non_empty(self):
        assert len(TRANSITION_MATRIX) > 0

    def test_all_rules_are_transition_rule_instances(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule, TransitionRule)

    def test_all_laws_covered(self):
        laws_in_matrix = {rule.law for rule in TRANSITION_MATRIX}
        # All seven laws must appear at least once
        for law in TransitionLaw:
            assert law in laws_in_matrix, f"{law.name} missing from matrix"

    def test_all_transition_types_covered(self):
        types_in_matrix = {rule.transition_type for rule in TRANSITION_MATRIX}
        for tt in TransitionType:
            assert tt in types_in_matrix, f"{tt.name} missing from matrix"

    def test_each_rule_has_non_empty_conditions(self):
        for rule in TRANSITION_MATRIX:
            assert len(rule.conditions) >= 1, f"Rule {rule.law.name} has no conditions"

    def test_each_rule_has_example(self):
        for rule in TRANSITION_MATRIX:
            assert rule.example, f"Rule {rule.law.name} has no example"

    def test_each_rule_has_description_ar(self):
        for rule in TRANSITION_MATRIX:
            assert rule.description_ar, f"Rule {rule.law.name} has empty description_ar"

    def test_priorities_are_positive_integers(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.priority, int) and rule.priority >= 1

    def test_from_category_none_or_phon_category(self):
        for rule in TRANSITION_MATRIX:
            assert rule.from_category is None or isinstance(
                rule.from_category, PhonCategory
            )

    def test_to_category_is_phon_category(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.to_category, PhonCategory)

    def test_resulting_transform_is_phon_transform(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.resulting_transform, PhonTransform)


# ── Priority list ────────────────────────────────────────────────────

class TestPriorityList:
    def test_priority_list_has_seven_steps(self):
        assert len(TRANSITION_PRIORITY) == 7

    def test_root_preservation_is_first(self):
        first = TRANSITION_PRIORITY[0]
        assert "Root preservation" in first or "الجذر" in first or "Root" in first

    def test_deletion_is_last(self):
        last = TRANSITION_PRIORITY[-1]
        assert "Deletion" in last or "الحذف" in last or "last resort" in last


# ── Stability check ──────────────────────────────────────────────────

class TestStabilityCheck:
    """stability_check returns True for stable elements, False for transitioning."""

    def test_plain_consonant_is_stable(self):
        ba = lookup(0x0628)  # ب — no ITLAL feature
        ctx = _ctx()
        assert stability_check(ba, ctx) is True

    def test_waw_under_zero_economy_is_stable(self):
        waw = lookup(0x0648)  # و — has ITLAL
        ctx = _ctx(economy=0.0)
        assert stability_check(waw, ctx) is True

    def test_waw_under_high_economy_pressure_triggers_transition(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.9)
        assert stability_check(waw, ctx) is False

    def test_ya_under_moderate_economy_in_onset_is_stable(self):
        ya = lookup(0x064A)  # ي
        ctx = _ctx(position=SyllablePosition.ONSET, economy=0.3)
        assert stability_check(ya, ctx) is True

    def test_ya_under_moderate_economy_in_coda_triggers_transition(self):
        ya = lookup(0x064A)
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.3)
        assert stability_check(ya, ctx) is False

    def test_gemination_triggered_by_identical_left_neighbour(self):
        dal = lookup(0x062F)  # د — has SHADID
        ctx = _ctx(left=dal)
        # The element itself is a SHADID, and left neighbour is identical → unstable
        assert stability_check(dal, ctx) is False

    def test_dissimilar_left_neighbour_does_not_trigger_gemination(self):
        dal = lookup(0x062F)  # د
        ba = lookup(0x0628)   # ب
        ctx = _ctx(left=ba)
        assert stability_check(dal, ctx) is True

    def test_tanwin_at_coda_with_high_economy_triggers_waqf(self):
        tanwin = lookup(0x064C)  # ٌ تنوين ضم
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.9)
        assert stability_check(tanwin, ctx) is False

    def test_tanwin_at_onset_with_high_economy_is_stable(self):
        tanwin = lookup(0x064C)
        ctx = _ctx(position=SyllablePosition.ONSET, economy=0.9)
        assert stability_check(tanwin, ctx) is True


# ── find_applicable_rules ────────────────────────────────────────────

class TestFindApplicableRules:
    """find_applicable_rules returns the correct subset of rules."""

    def test_no_rules_for_plain_consonant_no_economy(self):
        ba = lookup(0x0628)   # ب — no ITLAL, no identical neighbour
        ctx = _ctx()
        rules = find_applicable_rules(ba, ctx)
        # Idgham requires identical neighbour → shouldn't match
        # Hadhf/Waqf require economy >= 0.5 → shouldn't match
        for rule in rules:
            assert rule.law not in (TransitionLaw.HADHF, TransitionLaw.WAQF)

    def test_itlal_rule_matches_waw(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.0)
        rules = find_applicable_rules(waw, ctx)
        laws = {r.law for r in rules}
        assert TransitionLaw.ITLAL in laws or TransitionLaw.INZILAQ in laws

    def test_hadhf_rules_require_economy_threshold(self):
        waw = lookup(0x0648)
        ctx_low = _ctx(economy=0.3)
        ctx_high = _ctx(economy=0.7)
        low_rules = {r.law for r in find_applicable_rules(waw, ctx_low)}
        high_rules = {r.law for r in find_applicable_rules(waw, ctx_high)}
        assert TransitionLaw.HADHF not in low_rules
        assert TransitionLaw.HADHF in high_rules

    def test_idgham_rule_requires_identical_neighbour(self):
        dal = lookup(0x062F)  # د
        # With identical left neighbour
        ctx_with = _ctx(left=dal)
        ctx_without = _ctx()
        with_rules = {r.law for r in find_applicable_rules(dal, ctx_with)}
        without_rules = {r.law for r in find_applicable_rules(dal, ctx_without)}
        assert TransitionLaw.IDGHAM in with_rules
        assert TransitionLaw.IDGHAM not in without_rules

    def test_waqf_requires_economy_threshold(self):
        tanwin = lookup(0x064C)  # ٌ
        ctx_low = _ctx(economy=0.2, position=SyllablePosition.CODA)
        ctx_high = _ctx(economy=0.9, position=SyllablePosition.CODA)
        low = {r.law for r in find_applicable_rules(tanwin, ctx_low)}
        high = {r.law for r in find_applicable_rules(tanwin, ctx_high)}
        assert TransitionLaw.WAQF not in low
        assert TransitionLaw.WAQF in high

    def test_rules_sorted_by_priority_ascending(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.8)
        rules = find_applicable_rules(waw, ctx)
        priorities = [r.priority for r in rules]
        assert priorities == sorted(priorities)

    def test_ziyada_rule_matches_sin(self):
        sin = lookup(0x0633)  # س — SHADID feature
        ctx = _ctx(function_role=FunctionRole.AUGMENT, architecture="مزيد")
        rules = find_applicable_rules(sin, ctx)
        laws = {r.law for r in rules}
        assert TransitionLaw.ZIYADA in laws


# ── apply_best_transition ────────────────────────────────────────────

class TestApplyBestTransition:
    """apply_best_transition implements the ArgMin optimality criterion."""

    def test_stable_element_returns_stable_result(self):
        ba = lookup(0x0628)
        ctx = _ctx()
        result = apply_best_transition(ba, ctx)
        assert isinstance(result, TransitionResult)
        assert result.stable is True
        assert result.applied_rule is None
        assert result.total_cost == 0.0

    def test_stable_result_preserves_source_unicode(self):
        ba = lookup(0x0628)
        ctx = _ctx()
        result = apply_best_transition(ba, ctx)
        assert result.source_unicode == 0x0628

    def test_stable_result_surface_form_matches_char(self):
        ba = lookup(0x0628)
        ctx = _ctx()
        result = apply_best_transition(ba, ctx)
        assert result.surface_form == "ب"

    def test_waw_high_economy_triggers_transition(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.9)
        result = apply_best_transition(waw, ctx)
        assert result.stable is False
        assert result.applied_rule is not None
        assert result.total_cost > 0.0

    def test_transition_result_has_positive_costs(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.9)
        result = apply_best_transition(waw, ctx)
        assert result.loss_root >= 0.0
        assert result.loss_pattern >= 0.0
        assert result.phonetic_burden >= 0.0

    def test_total_cost_equals_sum_of_parts(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.9)
        result = apply_best_transition(waw, ctx)
        expected = result.loss_root + result.loss_pattern + result.phonetic_burden
        assert abs(result.total_cost - expected) < 1e-9

    def test_gemination_transition_shadda_category(self):
        dal = lookup(0x062F)  # د with identical left neighbour
        ctx = _ctx(left=dal)
        result = apply_best_transition(dal, ctx)
        assert result.stable is False
        assert result.target_category is PhonCategory.SHADDA

    def test_tanwin_waqf_transitions_to_sukun(self):
        tanwin = lookup(0x064C)  # ٌ
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.9)
        result = apply_best_transition(tanwin, ctx)
        assert result.stable is False
        assert result.target_category is PhonCategory.SUKUN

    def test_deletion_surface_form_is_empty(self):
        waw = lookup(0x0648)
        # Very high economy + CODA position forces HADHF
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.95)
        result = apply_best_transition(waw, ctx)
        if result.target_category is PhonCategory.SPECIAL_MARK:
            assert result.surface_form == ""

    def test_notes_field_is_string(self):
        ba = lookup(0x0628)
        ctx = _ctx()
        result = apply_best_transition(ba, ctx)
        assert isinstance(result.notes, str)

    def test_conditions_met_is_frozenset(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.8)
        result = apply_best_transition(waw, ctx)
        assert isinstance(result.conditions_met, frozenset)

    def test_applied_rule_law_is_transition_law(self):
        dal = lookup(0x062F)
        ctx = _ctx(left=dal)
        result = apply_best_transition(dal, ctx)
        if result.applied_rule is not None:
            assert isinstance(result.applied_rule.law, TransitionLaw)


# ── format_matrix_table ──────────────────────────────────────────────

class TestFormatMatrixTable:
    def test_returns_string(self):
        table = format_matrix_table()
        assert isinstance(table, str)

    def test_table_has_header(self):
        table = format_matrix_table()
        assert "القانون" in table or "law" in table.lower()

    def test_table_has_one_row_per_rule(self):
        table = format_matrix_table()
        # Every rule index should appear
        for i in range(1, len(TRANSITION_MATRIX) + 1):
            assert str(i) in table

    def test_table_contains_itlal(self):
        table = format_matrix_table()
        assert "ITLAL" in table

    def test_table_contains_idgham(self):
        table = format_matrix_table()
        assert "IDGHAM" in table


# ── TransitionRule dataclass ─────────────────────────────────────────

class TestTransitionRuleDataclass:
    def test_rule_is_frozen(self):
        rule = TRANSITION_MATRIX[0]
        with pytest.raises((AttributeError, TypeError)):
            rule.priority = 99  # type: ignore[misc]

    def test_required_features_is_frozenset(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.required_features, frozenset)

    def test_conditions_is_frozenset(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.conditions, frozenset)


# ── Integration: seven canonical linguistic examples ─────────────────

class TestCanonicalExamples:
    """Spot-check the seven canonical examples from the theoretical framework."""

    def test_madd_rule_exists_for_waw(self):
        """يَقُولُ — و transitions into long-vowel nucleus via ITLAL."""
        itlal_rules = [
            r for r in TRANSITION_MATRIX
            if r.law is TransitionLaw.ITLAL
            and (r.from_category is None or r.from_category is PhonCategory.SEMI_VOWEL)
        ]
        assert len(itlal_rules) >= 1
        assert any(r.resulting_transform is PhonTransform.MADD for r in itlal_rules)

    def test_shadda_rule_exists_for_geminate_dal(self):
        """مَدَّ / رَدَّ — two identical consonants collapse to Shadda."""
        idgham_rules = [r for r in TRANSITION_MATRIX if r.law is TransitionLaw.IDGHAM]
        assert any(r.to_category is PhonCategory.SHADDA for r in idgham_rules)

    def test_ziyada_rule_for_sin(self):
        """اسْتَخْرَجَ — س/ت re-slotted as augment."""
        sin = lookup(0x0633)
        ctx = _ctx(function_role=FunctionRole.AUGMENT, architecture="مزيد")
        rules = find_applicable_rules(sin, ctx)
        assert any(r.law is TransitionLaw.ZIYADA for r in rules)

    def test_waqf_tanwin_fath(self):
        """كِتَابًا → كِتَابَا or كِتَابْ at pause."""
        tanwin = lookup(0x064B)  # ً تنوين فتح
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.9)
        rules = find_applicable_rules(tanwin, ctx)
        assert any(r.law is TransitionLaw.WAQF for r in rules)

    def test_hadhf_for_ya_in_jussive(self):
        """يَقُلْ (مجزوم) — ي deleted from surface."""
        ya = lookup(0x064A)
        ctx = _ctx(
            position=SyllablePosition.CODA,
            function_role=FunctionRole.VOWEL_CARRIER,
            economy=0.8,
        )
        rules = find_applicable_rules(ya, ctx)
        assert any(r.law is TransitionLaw.HADHF for r in rules)

    def test_ibdal_rule_exists_for_hamza(self):
        """تسهيل الهمزة — ء substituted by adjacent sound."""
        ibdal_rules = [
            r for r in TRANSITION_MATRIX
            if r.law is TransitionLaw.IBDAL
            and (r.from_category is None or r.from_category is PhonCategory.CONSONANT)
        ]
        assert len(ibdal_rules) >= 1

    def test_inzilaq_rule_for_waw_semi_vowel(self):
        """مَوْعِد — و stays semi-consonantal via INZILAQ."""
        inzilaq_rules = [r for r in TRANSITION_MATRIX if r.law is TransitionLaw.INZILAQ]
        assert len(inzilaq_rules) >= 1
        assert any(
            r.from_category is PhonCategory.SEMI_VOWEL for r in inzilaq_rules
        )
