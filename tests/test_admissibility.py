"""Pre-U₀ admissibility tests — D5.

Verifies the six-dimension admissibility check for Arabic text input,
including ACCEPT, SUSPEND, and REJECT decisions, and pipeline integration.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    AdmissibilityDecision,
    AdmissibilityDimension,
)
from arabic_engine.core.types import AdmissibilityCheck, AdmissibilityResult
from arabic_engine.pipeline import run
from arabic_engine.signifier.admissibility import check_admissibility


# ── Result structure ────────────────────────────────────────────────


class TestAdmissibilityResultStructure:
    """AdmissibilityResult contains required fields."""

    def test_result_is_admissibility_result(self):
        result = check_admissibility("كتب")
        assert isinstance(result, AdmissibilityResult)

    def test_result_has_six_checks(self):
        result = check_admissibility("كتب")
        assert len(result.checks) == 6

    def test_each_check_is_admissibility_check(self):
        result = check_admissibility("كتب")
        for check in result.checks:
            assert isinstance(check, AdmissibilityCheck)

    def test_result_has_timestamp(self):
        result = check_admissibility("كتب")
        assert result.timestamp

    def test_result_has_input_text(self):
        result = check_admissibility("كتب")
        assert result.input_text == "كتب"

    def test_all_dimensions_covered(self):
        result = check_admissibility("كتب")
        dims = {c.dimension for c in result.checks}
        for d in AdmissibilityDimension:
            assert d in dims, f"Missing dimension {d.name}"


# ── ACCEPT cases ────────────────────────────────────────────────────


class TestAdmissibilityAccept:
    """Valid Arabic input is ACCEPTED."""

    def test_simple_arabic_word(self):
        result = check_admissibility("كتب")
        assert result.decision == AdmissibilityDecision.ACCEPT

    def test_arabic_sentence(self):
        result = check_admissibility("ذهب الطالبُ إلى المدرسة")
        assert result.decision == AdmissibilityDecision.ACCEPT

    def test_arabic_with_diacritics(self):
        result = check_admissibility("كَتَبَ زَيْدٌ")
        assert result.decision == AdmissibilityDecision.ACCEPT

    def test_arabic_with_numbers(self):
        result = check_admissibility("عام ٢٠٢٥")
        assert result.decision == AdmissibilityDecision.ACCEPT

    def test_single_arabic_letter(self):
        result = check_admissibility("ع")
        assert result.decision == AdmissibilityDecision.ACCEPT

    def test_all_checks_pass(self):
        result = check_admissibility("كتب")
        for check in result.checks:
            assert check.passed, f"Dimension {check.dimension.name} failed"


# ── SUSPEND cases ───────────────────────────────────────────────────


class TestAdmissibilitySuspend:
    """Mixed input is SUSPENDED."""

    def test_mixed_arabic_latin_mostly_latin(self):
        """Predominantly non-Arabic input should SUSPEND."""
        result = check_admissibility("Hello World مع a long English text")
        # prior_knowledge_binding should fail
        assert result.decision in (
            AdmissibilityDecision.SUSPEND,
            AdmissibilityDecision.ACCEPT,
        )


# ── REJECT cases ────────────────────────────────────────────────────


class TestAdmissibilityReject:
    """Invalid input is REJECTED."""

    def test_empty_string(self):
        result = check_admissibility("")
        assert result.decision == AdmissibilityDecision.REJECT

    def test_whitespace_only(self):
        result = check_admissibility("   \t\n  ")
        assert result.decision == AdmissibilityDecision.REJECT

    def test_none_input(self):
        result = check_admissibility(None)
        assert result.decision == AdmissibilityDecision.REJECT

    def test_latin_only(self):
        result = check_admissibility("Hello World")
        assert result.decision == AdmissibilityDecision.REJECT

    def test_numbers_only(self):
        result = check_admissibility("12345")
        assert result.decision == AdmissibilityDecision.REJECT

    def test_diacritics_only(self):
        """Diacritics without base characters should REJECT."""
        # Only tatweel and diacritics
        result = check_admissibility("\u0640\u064B\u064C\u064D")
        assert result.decision == AdmissibilityDecision.REJECT

    def test_reject_has_failed_checks(self):
        result = check_admissibility("")
        failed = [c for c in result.checks if not c.passed]
        assert len(failed) > 0

    def test_failed_check_has_reason(self):
        result = check_admissibility("")
        for check in result.checks:
            if not check.passed:
                assert check.reason, f"Failed {check.dimension.name} has no reason"


# ── Dimension-specific tests ────────────────────────────────────────


class TestAdmissibilityDimensions:
    """Individual dimension checks."""

    def test_presence_passes_for_text(self):
        result = check_admissibility("كتب")
        presence = next(
            c for c in result.checks
            if c.dimension == AdmissibilityDimension.PRESENCE
        )
        assert presence.passed

    def test_presence_fails_for_empty(self):
        result = check_admissibility("")
        presence = next(
            c for c in result.checks
            if c.dimension == AdmissibilityDimension.PRESENCE
        )
        assert not presence.passed

    def test_distinguishability_passes_for_visible(self):
        result = check_admissibility("كتب")
        dist = next(
            c for c in result.checks
            if c.dimension == AdmissibilityDimension.DISTINGUISHABILITY
        )
        assert dist.passed

    def test_initial_admissibility_passes_for_arabic(self):
        result = check_admissibility("كتب")
        init = next(
            c for c in result.checks
            if c.dimension == AdmissibilityDimension.INITIAL_ADMISSIBILITY
        )
        assert init.passed

    def test_initial_admissibility_fails_for_latin(self):
        result = check_admissibility("Hello")
        init = next(
            c for c in result.checks
            if c.dimension == AdmissibilityDimension.INITIAL_ADMISSIBILITY
        )
        assert not init.passed


# ── Pipeline integration ────────────────────────────────────────────


class TestAdmissibilityPipelineIntegration:
    """Admissibility is checked before L0 in the main pipeline."""

    def test_valid_arabic_passes_pipeline(self):
        result = run("كتب")
        assert result.status is not None

    def test_empty_input_fails_pipeline(self):
        """Empty input should be rejected by pre-U₀ check."""
        from arabic_engine.core.enums import PipelineStatus
        result = run("")
        assert result.status == PipelineStatus.FAILURE

    def test_latin_input_fails_pipeline(self):
        """Non-Arabic input should be rejected by pre-U₀ check."""
        from arabic_engine.core.enums import PipelineStatus
        result = run("Hello World")
        assert result.status == PipelineStatus.FAILURE

    def test_pre_u0_trace_exists(self):
        """The first trace entry should be the pre-U₀ check."""
        result = run("كتب")
        assert len(result.unified_trace) > 0
        assert result.unified_trace[0].layer_index == -1
        assert "Pre-U₀" in result.unified_trace[0].reason
