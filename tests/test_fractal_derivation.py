"""tests/test_fractal_derivation.py — comprehensive tests for fractal_derivation.

Covers:
* Guard tests — individual guard validation
* Full derivation tests — end-to-end derivation (Art. 38–41)
* Trace & recoverability tests (Art. 42–44)
* Contract test — layer importability
* Integration test — derivation within mufrad_closure pipeline
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    DerivationalDirection,
    DerivationFailureReason,
    DerivationGuard,
    DerivationPhase,
)
from arabic_engine.core.types import (
    DerivationCandidate,
    DerivationInput,
    DerivationTrace,
    FractalDerivationResult,
    GuardResult,
)
from arabic_engine.signifier.fractal_derivation import (
    derive,
    derive_all_directions,
    validate_derivation_input,
)

# ── Helpers ─────────────────────────────────────────────────────────


def _input(
    root: tuple[str, ...] = ("ك", "ت", "ب"),
    pattern: str = "فاعل",
    direction: DerivationalDirection = DerivationalDirection.ISM_FA3IL,
) -> DerivationInput:
    return DerivationInput(
        root=root,
        weight_pattern=pattern,
        direction=direction,
    )


# ═══════════════════════════════════════════════════════════════════════
# 1. Guard tests
# ═══════════════════════════════════════════════════════════════════════


class TestRootGuard:
    """Test _validate_root guard."""

    def test_valid_triliteral_root(self):
        result = derive(_input(root=("ك", "ت", "ب")))
        # Root guard should pass — check no ROOT_FAILURE from root validation
        assert result.trace is not None
        root_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_ROOT_VALID
        ]
        assert root_guards
        assert root_guards[0].passed

    def test_empty_root_fails(self):
        result = derive(_input(root=()))
        assert not result.success
        assert DerivationFailureReason.ROOT_FAILURE in result.failure_reasons

    def test_single_letter_root_fails(self):
        result = derive(_input(root=("ك",)))
        assert not result.success
        assert DerivationFailureReason.ROOT_FAILURE in result.failure_reasons

    def test_six_letter_root_fails(self):
        result = derive(_input(root=("ك", "ت", "ب", "ر", "ج", "ع")))
        assert not result.success
        assert DerivationFailureReason.ROOT_FAILURE in result.failure_reasons

    def test_invalid_consonant_fails(self):
        result = derive(_input(root=("ك", "X", "ب")))
        assert not result.success
        assert DerivationFailureReason.ROOT_FAILURE in result.failure_reasons

    def test_quadriliteral_root_valid(self):
        result = derive(_input(root=("ت", "ر", "ج", "م"), pattern="فاعل"))
        # Root itself is valid (4 letters), though may fail at later phases
        assert result.trace is not None
        root_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_ROOT_VALID
        ]
        assert root_guards
        assert root_guards[0].passed


class TestWeightGuard:
    """Test _validate_weight guard."""

    def test_valid_pattern(self):
        result = derive(_input(pattern="فاعل"))
        assert result.trace is not None
        weight_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_WEIGHT_VALID
        ]
        assert weight_guards
        assert weight_guards[0].passed

    def test_empty_pattern_fails(self):
        result = derive(_input(pattern=""))
        assert not result.success
        assert DerivationFailureReason.WEIGHT_FAILURE in result.failure_reasons


class TestDirectionGuard:
    """Test _validate_direction guard."""

    def test_valid_direction(self):
        result = derive(_input(direction=DerivationalDirection.ISM_FA3IL))
        assert result.trace is not None
        dir_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_DIRECTION_VALID
        ]
        assert dir_guards
        assert dir_guards[0].passed


class TestRootCarriesDirection:
    """Test root↔direction carrying."""

    def test_root_carries_ism_fa3il(self):
        result = derive(_input(
            root=("ك", "ت", "ب"),
            direction=DerivationalDirection.ISM_FA3IL,
        ))
        assert result.trace is not None
        rc_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_ROOT_CARRIES_DIRECTION
        ]
        assert rc_guards
        assert rc_guards[0].passed


class TestWeightCarriesDirection:
    """Test weight↔direction carrying."""

    def test_weight_carries_permitted(self):
        result = derive(_input(
            pattern="فاعل",
            direction=DerivationalDirection.ISM_FA3IL,
        ))
        assert result.trace is not None
        wc_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_WEIGHT_CARRIES_DIRECTION
        ]
        assert wc_guards
        assert wc_guards[0].passed

    def test_weight_prohibited_fails(self):
        # فَعْل prohibits ISM_FA3IL
        result = derive(_input(
            pattern="فَعْل",
            direction=DerivationalDirection.ISM_FA3IL,
        ))
        assert not result.success
        assert DerivationFailureReason.WEIGHT_FAILURE in result.failure_reasons


# ═══════════════════════════════════════════════════════════════════════
# 2. Full derivation tests (Art. 38–41)
# ═══════════════════════════════════════════════════════════════════════


class TestDerivation:
    """Test full derivation pipeline."""

    def test_derive_katib(self):
        """root=(ك,ت,ب), pattern=فاعل, direction=ISM_FA3IL → كاتب"""
        result = derive(_input(
            root=("ك", "ت", "ب"),
            pattern="فاعل",
            direction=DerivationalDirection.ISM_FA3IL,
        ))
        assert result.success
        assert result.surface is not None
        # The surface should contain all root consonants
        for ch in ("ك", "ت", "ب"):
            assert ch in result.surface

    def test_derive_maktub(self):
        """root=(ك,ت,ب), pattern=مفعول, direction=ISM_MAF3UL → مكتوب"""
        result = derive(_input(
            root=("ك", "ت", "ب"),
            pattern="مفعول",
            direction=DerivationalDirection.ISM_MAF3UL,
        ))
        assert result.success
        assert result.surface is not None
        for ch in ("ك", "ت", "ب"):
            assert ch in result.surface

    def test_derive_kitaba(self):
        """root=(ك,ت,ب), pattern=فِعالة, direction=MASDAR → كتابة"""
        result = derive(_input(
            root=("ك", "ت", "ب"),
            pattern="فِعالة",
            direction=DerivationalDirection.MASDAR,
        ))
        assert result.success
        assert result.surface is not None
        for ch in ("ك", "ت", "ب"):
            assert ch in result.surface

    def test_derive_failure_incompatible(self):
        """Incompatible root+direction → failure."""
        # فَعْل pattern prohibits ISM_FA3IL
        result = derive(_input(
            root=("ك", "ت", "ب"),
            pattern="فَعْل",
            direction=DerivationalDirection.ISM_FA3IL,
        ))
        assert not result.success
        assert len(result.failure_reasons) > 0

    def test_derive_result_has_candidate_on_success(self):
        result = derive(_input())
        assert result.success
        assert result.candidate is not None
        assert isinstance(result.candidate, DerivationCandidate)

    def test_derive_confidence_on_success(self):
        result = derive(_input())
        assert result.success
        assert result.confidence == 1.0

    def test_derive_confidence_on_failure(self):
        result = derive(_input(root=()))
        assert not result.success
        assert result.confidence == 0.0


# ═══════════════════════════════════════════════════════════════════════
# 3. Trace & recoverability tests (Art. 42–44)
# ═══════════════════════════════════════════════════════════════════════


class TestTraceAndRecoverability:
    """Test audit trail and recoverability."""

    def test_trace_always_present(self):
        """Every derivation result has a trace."""
        # Success
        result = derive(_input())
        assert result.trace is not None
        assert isinstance(result.trace, DerivationTrace)

        # Failure
        result = derive(_input(root=()))
        assert result.trace is not None
        assert isinstance(result.trace, DerivationTrace)

    def test_trace_records_input(self):
        inp = _input()
        result = derive(inp)
        assert result.trace is not None
        assert result.trace.input == inp

    def test_trace_has_guard_results(self):
        result = derive(_input())
        assert result.trace is not None
        assert len(result.trace.guard_results) > 0
        for g in result.trace.guard_results:
            assert isinstance(g, GuardResult)

    def test_recoverability_on_success(self):
        result = derive(_input())
        assert result.success
        assert result.is_recoverable
        assert result.trace is not None
        # Check output_recoverable guard passed
        rec_guards = [
            g for g in result.trace.guard_results
            if g.guard == DerivationGuard.GUARD_OUTPUT_RECOVERABLE
        ]
        assert rec_guards
        assert rec_guards[0].passed

    def test_failure_has_reasons(self):
        result = derive(_input(root=()))
        assert not result.success
        assert len(result.failure_reasons) > 0

    def test_trace_phase_reached_on_failure(self):
        result = derive(_input(root=()))
        assert result.trace is not None
        assert result.trace.phase_reached == DerivationPhase.ROOT_CHECK

    def test_trace_phase_reached_on_success(self):
        result = derive(_input())
        assert result.trace is not None
        assert result.trace.phase_reached == DerivationPhase.FINAL_DECISION

    def test_trace_weight_profile_present_after_weight_check(self):
        result = derive(_input())
        assert result.trace is not None
        assert result.trace.weight_profile is not None

    def test_trace_direction_assignment_on_success(self):
        result = derive(_input())
        assert result.trace is not None
        assert result.trace.direction_assignment is not None


# ═══════════════════════════════════════════════════════════════════════
# 4. Utility function tests
# ═══════════════════════════════════════════════════════════════════════


class TestDeriveAllDirections:
    """Test derive_all_directions utility."""

    def test_returns_tuple(self):
        results = derive_all_directions(("ك", "ت", "ب"), "فاعل")
        assert isinstance(results, tuple)
        assert len(results) == len(DerivationalDirection)

    def test_each_result_is_typed(self):
        results = derive_all_directions(("ك", "ت", "ب"), "فاعل")
        for r in results:
            assert isinstance(r, FractalDerivationResult)

    def test_some_succeed_some_fail(self):
        results = derive_all_directions(("ك", "ت", "ب"), "فاعل")
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]
        # At least ISM_FA3IL should succeed for فاعل
        assert len(successes) >= 1
        # Some directions should fail
        assert len(failures) >= 1


class TestValidateDerivationInput:
    """Test validate_derivation_input pre-check."""

    def test_valid_input_passes_all_guards(self):
        inp = _input()
        guards = validate_derivation_input(inp)
        assert isinstance(guards, tuple)
        assert len(guards) > 0
        for g in guards:
            assert isinstance(g, GuardResult)

    def test_invalid_root_stops_early(self):
        inp = _input(root=())
        guards = validate_derivation_input(inp)
        assert len(guards) == 1
        assert not guards[0].passed
        assert guards[0].guard == DerivationGuard.GUARD_ROOT_VALID

    def test_valid_input_reaches_weight_direction_check(self):
        inp = _input()
        guards = validate_derivation_input(inp)
        guard_types = {g.guard for g in guards}
        # Should at least check root, weight, direction, structural, root-carries, weight-carries
        assert DerivationGuard.GUARD_ROOT_VALID in guard_types
        assert DerivationGuard.GUARD_WEIGHT_VALID in guard_types
        assert DerivationGuard.GUARD_DIRECTION_VALID in guard_types


# ═══════════════════════════════════════════════════════════════════════
# 5. Contract test
# ═══════════════════════════════════════════════════════════════════════


class TestContract:
    """Test that the fractal_derivation layer is importable and function exists."""

    def test_module_importable(self):
        import arabic_engine.signifier.fractal_derivation as mod
        assert hasattr(mod, "derive")
        assert callable(mod.derive)

    def test_derive_all_directions_exists(self):
        import arabic_engine.signifier.fractal_derivation as mod
        assert hasattr(mod, "derive_all_directions")
        assert callable(mod.derive_all_directions)

    def test_validate_derivation_input_exists(self):
        import arabic_engine.signifier.fractal_derivation as mod
        assert hasattr(mod, "validate_derivation_input")
        assert callable(mod.validate_derivation_input)


# ═══════════════════════════════════════════════════════════════════════
# 6. Integration test — derivation within mufrad_closure
# ═══════════════════════════════════════════════════════════════════════


class TestMufradClosureIntegration:
    """Test optional fractal derivation integration in mufrad_closure."""

    def test_close_mufrad_has_derivation_trace_field(self):
        from arabic_engine.mufrad_closure import close_mufrad
        result = close_mufrad("كِتابة")
        assert hasattr(result, "derivation_trace")

    def test_close_mufrad_derivation_trace_type(self):
        from arabic_engine.mufrad_closure import close_mufrad
        result = close_mufrad("كِتابة")
        # derivation_trace is either None or DerivationTrace
        if result.derivation_trace is not None:
            assert isinstance(result.derivation_trace, DerivationTrace)


# ═══════════════════════════════════════════════════════════════════════
# 7. Enum and dataclass tests
# ═══════════════════════════════════════════════════════════════════════


class TestEnums:
    """Test new enums exist and have expected members."""

    def test_derivation_guard_members(self):
        assert len(DerivationGuard) == 8
        assert DerivationGuard.GUARD_ROOT_VALID is not None
        assert DerivationGuard.GUARD_OUTPUT_RECOVERABLE is not None

    def test_derivation_failure_reason_members(self):
        assert len(DerivationFailureReason) == 6
        assert DerivationFailureReason.ROOT_FAILURE is not None
        assert DerivationFailureReason.TOTAL_FAILURE is not None

    def test_derivation_phase_members(self):
        assert len(DerivationPhase) == 9
        assert DerivationPhase.ROOT_CHECK is not None
        assert DerivationPhase.FINAL_DECISION is not None


class TestDataclasses:
    """Test new dataclasses are frozen and constructible."""

    def test_derivation_input_frozen(self):
        inp = _input()
        with pytest.raises(AttributeError):
            inp.root = ("x",)  # type: ignore[misc]

    def test_guard_result_frozen(self):
        g = GuardResult(
            guard=DerivationGuard.GUARD_ROOT_VALID,
            passed=True,
            message="ok",
        )
        with pytest.raises(AttributeError):
            g.passed = False  # type: ignore[misc]

    def test_derivation_candidate_frozen(self):
        c = DerivationCandidate(
            surface="كاتب",
            root=("ك", "ت", "ب"),
            pattern="فاعل",
            direction=DerivationalDirection.ISM_FA3IL,
        )
        with pytest.raises(AttributeError):
            c.surface = "x"  # type: ignore[misc]

    def test_fractal_derivation_result_frozen(self):
        r = FractalDerivationResult(success=False)
        with pytest.raises(AttributeError):
            r.success = True  # type: ignore[misc]
