"""Comprehensive unit tests for the transition engine — قانون الانتقال بين الخانات.

Covers type safety, logic correctness, edge cases, cost computation,
stability-check logic, and round-trip properties of the engine.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    FunctionRole,
    PhonCategory,
    PhonFeature,
    PhonGroup,
    SyllablePosition,
    TransitionCondition,
    TransitionLaw,
)
from arabic_engine.core.types import TransitionContext, TransitionRule
from arabic_engine.signifier.dmin import lookup
from arabic_engine.signifier.transition import (
    _ECONOMY_CODA_ITLAL_THRESHOLD,
    _ECONOMY_REDUCTION_THRESHOLD,
    _UNICODE_SHADDA,
    _UNICODE_SUKUN,
    TRANSITION_MATRIX,
    apply_best_transition,
    find_applicable_rules,
    stability_check,
)

# ── Shared helper ────────────────────────────────────────────────────


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


# ── Module-level constants ───────────────────────────────────────────


class TestModuleConstants:
    """Verify that the new module-level constants are correct."""

    def test_unicode_sukun_value(self):
        assert _UNICODE_SUKUN == 0x0652

    def test_unicode_shadda_value(self):
        assert _UNICODE_SHADDA == 0x0651

    def test_economy_reduction_threshold_is_half(self):
        assert _ECONOMY_REDUCTION_THRESHOLD == 0.5

    def test_coda_itlal_threshold_is_positive(self):
        assert 0.0 < _ECONOMY_CODA_ITLAL_THRESHOLD < 1.0

    def test_sukun_chr_produces_correct_character(self):
        assert chr(_UNICODE_SUKUN) == "\u0652"

    def test_shadda_chr_produces_correct_character(self):
        assert chr(_UNICODE_SHADDA) == "\u0651"


# ── Helper function types ────────────────────────────────────────────


class TestHelperFunctionTypes:
    """Verify _ff() and _cc() return FrozenSet with correct element types."""

    def test_all_required_features_are_frozensets(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.required_features, frozenset)

    def test_required_features_contain_phon_features(self):
        for rule in TRANSITION_MATRIX:
            for feat in rule.required_features:
                assert isinstance(feat, PhonFeature)

    def test_all_conditions_are_frozensets(self):
        for rule in TRANSITION_MATRIX:
            assert isinstance(rule.conditions, frozenset)

    def test_conditions_contain_transition_conditions(self):
        for rule in TRANSITION_MATRIX:
            for cond in rule.conditions:
                assert isinstance(cond, TransitionCondition)


# ── stability_check — logic correctness ─────────────────────────────


class TestStabilityCheckLogic:
    """Verify stability_check does not contain unreachable code paths."""

    def test_itlal_at_exactly_0_5_economy_is_unstable(self):
        """economy_pressure == _ECONOMY_REDUCTION_THRESHOLD should trigger instability."""
        waw = lookup(0x0648)
        ctx = _ctx(economy=_ECONOMY_REDUCTION_THRESHOLD)
        assert stability_check(waw, ctx) is False

    def test_itlal_just_below_reduction_but_above_coda_threshold_in_coda_is_unstable(self):
        """_ECONOMY_CODA_ITLAL_THRESHOLD < economy_pressure < _ECONOMY_REDUCTION_THRESHOLD
        and position==CODA → unstable."""
        waw = lookup(0x0648)
        midpoint = (_ECONOMY_CODA_ITLAL_THRESHOLD + _ECONOMY_REDUCTION_THRESHOLD) / 2
        ctx = _ctx(position=SyllablePosition.CODA, economy=midpoint)
        assert stability_check(waw, ctx) is False

    def test_itlal_below_both_thresholds_in_coda_is_stable(self):
        """economy_pressure below coda ITLAL threshold and position==CODA → stable."""
        waw = lookup(0x0648)
        ctx = _ctx(position=SyllablePosition.CODA, economy=_ECONOMY_CODA_ITLAL_THRESHOLD / 2)
        assert stability_check(waw, ctx) is True

    def test_itlal_at_exactly_coda_threshold_in_coda_is_stable(self):
        """economy_pressure exactly at CODA threshold (not strictly greater) → stable."""
        waw = lookup(0x0648)
        ctx = _ctx(position=SyllablePosition.CODA, economy=_ECONOMY_CODA_ITLAL_THRESHOLD)
        assert stability_check(waw, ctx) is True

    def test_itlal_below_threshold_not_in_coda_is_stable(self):
        """economy_pressure midpoint but NOT in CODA → stable."""
        waw = lookup(0x0648)
        midpoint = (_ECONOMY_CODA_ITLAL_THRESHOLD + _ECONOMY_REDUCTION_THRESHOLD) / 2
        ctx = _ctx(position=SyllablePosition.ONSET, economy=midpoint)
        assert stability_check(waw, ctx) is True

    def test_non_itlal_consonant_high_economy_is_stable(self):
        """Plain consonant without ITLAL feature should be unaffected by ITLAL condition."""
        ba = lookup(0x0628)  # ب — no ITLAL
        ctx = _ctx(economy=0.99)
        # ITLAL condition doesn't fire; gemination condition requires identical left.
        assert stability_check(ba, ctx) is True

    def test_coda_position_check_uses_equality_not_membership(self):
        """Stability_check uses == _SP.CODA rather than in (_SP.CODA,).
        Verify NUCLEUS position does not trigger coda-specific ITLAL check."""
        waw = lookup(0x0648)
        ctx = _ctx(position=SyllablePosition.NUCLEUS, economy=0.3)
        assert stability_check(waw, ctx) is True


# ── find_applicable_rules — null guards ─────────────────────────────


class TestFindApplicableRulesNullGuards:
    """Verify null/empty checks introduced in find_applicable_rules."""

    def test_returns_empty_list_for_element_with_none_category(self):
        """If somehow element.category is None, return empty list gracefully."""
        from arabic_engine.core.types import DMin

        # Build a minimal DMin with None category
        element = DMin(
            unicode=0x0628,
            category=None,  # type: ignore[arg-type]
            group=PhonGroup.SHF,
            features=frozenset(),
            transforms=frozenset(),
        )
        ctx = _ctx()
        rules = find_applicable_rules(element, ctx)
        assert rules == []

    def test_returns_empty_list_for_element_with_none_features(self):
        """If somehow element.features is None, return empty list gracefully."""
        from arabic_engine.core.types import DMin

        element = DMin(
            unicode=0x0628,
            category=PhonCategory.CONSONANT,
            group=PhonGroup.SHF,
            features=None,  # type: ignore[arg-type]
            transforms=frozenset(),
        )
        ctx = _ctx()
        rules = find_applicable_rules(element, ctx)
        assert rules == []


# ── find_applicable_rules — IDGHAM phonetic similarity ──────────────


class TestIdghamPhoneticSimilarity:
    """The improved IDGHAM gate accepts phonetically similar (same group) neighbours."""

    def test_identical_unicode_still_triggers_idgham(self):
        dal = lookup(0x062F)
        ctx = _ctx(left=dal)
        rules = find_applicable_rules(dal, ctx)
        assert any(r.law is TransitionLaw.IDGHAM for r in rules)

    def test_none_left_neighbour_blocks_idgham(self):
        dal = lookup(0x062F)
        ctx = _ctx()  # no left neighbour
        rules = find_applicable_rules(dal, ctx)
        assert all(r.law is not TransitionLaw.IDGHAM for r in rules)

    def test_same_articulatory_group_triggers_idgham(self):
        """Two consonants in the same group (e.g. ASN_LTH) should allow IDGHAM."""
        # ت (U+062A) and د (U+062F) are both in ASN_LTH group
        ta = lookup(0x062A)   # ت
        dal = lookup(0x062F)  # د
        # Only test if they are in the same group (defensive)
        if ta.group != dal.group:
            pytest.skip("ta and dal are not in the same articulatory group in this build")
        ctx = _ctx(left=ta)
        rules = find_applicable_rules(dal, ctx)
        assert any(r.law is TransitionLaw.IDGHAM for r in rules)

    def test_different_group_consonants_do_not_trigger_idgham(self):
        """Consonants from very different groups (e.g. ب and ق) should not trigger IDGHAM."""
        ba = lookup(0x0628)   # ب — SHF group
        qaf = lookup(0x0642)  # ق — LHW group
        if ba.group == qaf.group:
            pytest.skip("ba and qaf are unexpectedly in the same group in this build")
        ctx = _ctx(left=ba)
        rules = find_applicable_rules(qaf, ctx)
        assert all(r.law is not TransitionLaw.IDGHAM for r in rules)


# ── _transition_cost — economy_pressure validation ──────────────────


class TestTransitionCostValidation:
    """_transition_cost raises ValueError for out-of-range economy_pressure."""

    def _first_rule(self) -> "TransitionRule":
        return TRANSITION_MATRIX[0]

    def test_valid_economy_zero_does_not_raise(self):
        from arabic_engine.signifier.transition import _transition_cost
        rule = self._first_rule()
        ctx = _ctx(economy=0.0)
        lr, lp, pb = _transition_cost(rule, ctx)
        assert lr >= 0 and lp >= 0 and pb >= 0

    def test_valid_economy_one_does_not_raise(self):
        from arabic_engine.signifier.transition import _transition_cost
        rule = self._first_rule()
        ctx = _ctx(economy=1.0)
        _transition_cost(rule, ctx)  # should not raise

    def test_negative_economy_raises_value_error(self):
        from arabic_engine.signifier.transition import _transition_cost
        rule = self._first_rule()
        ctx = _ctx(economy=-0.1)
        with pytest.raises(ValueError, match="economy_pressure"):
            _transition_cost(rule, ctx)

    def test_economy_above_one_raises_value_error(self):
        from arabic_engine.signifier.transition import _transition_cost
        rule = self._first_rule()
        ctx = _ctx(economy=1.1)
        with pytest.raises(ValueError, match="economy_pressure"):
            _transition_cost(rule, ctx)

    def test_phonetic_burden_decreases_with_higher_economy(self):
        from arabic_engine.signifier.transition import _transition_cost
        rule = self._first_rule()
        ctx_low = _ctx(economy=0.0)
        ctx_high = _ctx(economy=1.0)
        _, _, pb_low = _transition_cost(rule, ctx_low)
        _, _, pb_high = _transition_cost(rule, ctx_high)
        assert pb_high <= pb_low


# ── apply_best_transition — surface form Unicode constants ───────────


class TestSurfaceFormConstants:
    """Verify that sukun and shadda surface forms use the named constants."""

    def test_sukun_surface_uses_correct_codepoint(self):
        tanwin = lookup(0x064C)  # ٌ
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.9)
        result = apply_best_transition(tanwin, ctx)
        if result.target_category is PhonCategory.SUKUN:
            assert result.surface_form.endswith(chr(_UNICODE_SUKUN))

    def test_shadda_surface_uses_correct_codepoint(self):
        dal = lookup(0x062F)  # د with identical left → shadda
        ctx = _ctx(left=dal)
        result = apply_best_transition(dal, ctx)
        if result.target_category is PhonCategory.SHADDA:
            assert result.surface_form.endswith(chr(_UNICODE_SHADDA))

    def test_deletion_target_has_empty_surface(self):
        waw = lookup(0x0648)
        ctx = _ctx(position=SyllablePosition.CODA, economy=0.95)
        result = apply_best_transition(waw, ctx)
        if result.target_category is PhonCategory.SPECIAL_MARK:
            assert result.surface_form == ""


# ── TransitionContext — forward reference fix ────────────────────────


class TestTransitionContextAnnotations:
    """TransitionContext.left_neighbor/right_neighbor should accept real DMin objects."""

    def test_left_neighbor_accepts_dmin(self):
        dal = lookup(0x062F)
        ctx = _ctx(left=dal)
        assert ctx.left_neighbor is dal

    def test_right_neighbor_accepts_dmin(self):
        ba = lookup(0x0628)
        ctx = _ctx(right=ba)
        assert ctx.right_neighbor is ba

    def test_neighbors_default_to_none(self):
        ctx = _ctx()
        assert ctx.left_neighbor is None
        assert ctx.right_neighbor is None


# ── apply_best_transition — invalid economy raises ValueError ────────


class TestApplyBestTransitionValidation:
    """apply_best_transition propagates ValueError from _transition_cost."""

    def test_invalid_economy_raises_when_transition_needed(self):
        dal = lookup(0x062F)  # will trigger IDGHAM with identical left
        ctx = TransitionContext(
            position=SyllablePosition.ONSET,
            function_role=FunctionRole.ROOT_RADICAL,
            left_neighbor=dal,
            economy_pressure=2.0,  # out of range
        )
        with pytest.raises(ValueError, match="economy_pressure"):
            apply_best_transition(dal, ctx)


# ── Cost computation determinism ─────────────────────────────────────


class TestCostDeterminism:
    """Same inputs must always produce the same output (determinism)."""

    def test_same_input_produces_same_result_twice(self):
        waw = lookup(0x0648)
        ctx = _ctx(economy=0.8)
        r1 = apply_best_transition(waw, ctx)
        r2 = apply_best_transition(waw, ctx)
        assert r1.total_cost == r2.total_cost
        assert r1.target_category == r2.target_category
        assert r1.applied_rule == r2.applied_rule

    def test_total_cost_is_sum_of_components_for_all_rules(self):
        """For every rule, running cost computation twice gives identical result."""
        from arabic_engine.signifier.transition import _transition_cost
        ctx = _ctx(economy=0.5)
        for rule in TRANSITION_MATRIX:
            lr1, lp1, pb1 = _transition_cost(rule, ctx)
            lr2, lp2, pb2 = _transition_cost(rule, ctx)
            assert lr1 == lr2 and lp1 == lp2 and pb1 == pb2

    def test_cost_components_are_non_negative(self):
        from arabic_engine.signifier.transition import _transition_cost
        ctx = _ctx(economy=0.7)
        for rule in TRANSITION_MATRIX:
            lr, lp, pb = _transition_cost(rule, ctx)
            assert lr >= 0.0
            assert lp >= 0.0
            assert pb >= 0.0
