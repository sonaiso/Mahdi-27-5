"""Comprehensive tests for arabic_engine.closure — General Closure (Ch. 19)."""

from __future__ import annotations

from unittest.mock import patch

from arabic_engine.closure import (
    ClosureStatus,
    ClosureVerdict,
    GeneralClosureResult,
    _check_dalala_types,
    _check_decomposability,
    _check_explanation_closure,
    _check_inference_closure,
    _check_irab_closure,
    _check_layer_chain_sync,
    _check_mantuq_boundary,
    _check_masdar_closure,
    _check_module_exists,
    _check_no_contradiction,
    _check_phonological_closure,
    _check_pos_minimality,
    _check_propositional_closure,
    _check_semantic_roles_closure,
    _check_time_space_closure,
    format_closure_report,
    verify_general_closure,
)

# ── GeneralClosureResult property tests ─────────────────────────────


class TestGeneralClosureResult:
    """Test GeneralClosureResult.closed property and to_dict()."""

    def test_closed_when_all_pass(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
        )
        assert result.closed is True

    def test_not_closed_when_verdict_open(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.OPEN, "fail", "فشل"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
        )
        assert result.closed is False

    def test_not_closed_when_ascending_invalid(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=False,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
        )
        assert result.closed is False

    def test_not_closed_when_contradiction(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=False,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
        )
        assert result.closed is False

    def test_not_closed_when_not_decomposable(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=False,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
        )
        assert result.closed is False

    def test_not_closed_when_boundary_unclear(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=False,
            layer_chain_synced=True,
        )
        assert result.closed is False

    def test_not_closed_when_chain_not_synced(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=False,
        )
        assert result.closed is False

    def test_closed_with_empty_verdicts(self):
        result = GeneralClosureResult(
            verdicts=[],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
        )
        # Empty verdicts means all() returns True vacuously
        assert result.closed is True

    def test_to_dict_keys(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
            layer_chain_synced=True,
            timestamp="2026-01-01T00:00:00+00:00",
        )
        d = result.to_dict()
        assert "closed" in d
        assert "timestamp" in d
        assert "summary" in d
        assert "verdicts" in d
        assert "structural_checks" in d
        assert d["closed"] is True
        assert d["summary"] == "1/1 layer checks passed"

    def test_to_dict_verdict_structure(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
                ClosureVerdict("b", "ب", ClosureStatus.OPEN, "fail", "فشل"),
            ],
        )
        d = result.to_dict()
        assert len(d["verdicts"]) == 2
        assert d["verdicts"][0]["status"] == "CLOSED"
        assert d["verdicts"][1]["status"] == "OPEN"
        assert d["summary"] == "1/2 layer checks passed"


# ── Individual closure check tests ──────────────────────────────────


class TestCheckModuleExists:
    """Test _check_module_exists for various layer configurations."""

    def test_valid_function_layer(self):
        layer = {
            "name": "normalize",
            "name_ar": "الذرة اليونيكودية",
            "module": "arabic_engine.signifier.unicode_norm",
            "function": "normalize",
            "symbol": "U₀",
        }
        verdict = _check_module_exists(layer)
        assert verdict.status == ClosureStatus.CLOSED

    def test_valid_class_method_layer(self):
        layer = {
            "name": "inference",
            "name_ar": "الاستدلال",
            "module": "arabic_engine.cognition.inference_rules",
            "function": "InferenceEngine.run",
            "symbol": "ℳ⁺_min/inference",
        }
        verdict = _check_module_exists(layer)
        assert verdict.status == ClosureStatus.CLOSED

    def test_missing_module(self):
        layer = {
            "name": "fake",
            "name_ar": "وهمي",
            "module": "arabic_engine.nonexistent_module",
            "function": "fake_fn",
            "symbol": "X",
        }
        verdict = _check_module_exists(layer)
        assert verdict.status == ClosureStatus.OPEN
        assert "not importable" in verdict.justification

    def test_missing_function(self):
        layer = {
            "name": "fake",
            "name_ar": "وهمي",
            "module": "arabic_engine.signifier.unicode_norm",
            "function": "nonexistent_function",
            "symbol": "X",
        }
        verdict = _check_module_exists(layer)
        assert verdict.status == ClosureStatus.OPEN
        assert "not found" in verdict.justification

    def test_missing_class(self):
        layer = {
            "name": "fake",
            "name_ar": "وهمي",
            "module": "arabic_engine.cognition.inference_rules",
            "function": "NonexistentClass.run",
            "symbol": "X",
        }
        verdict = _check_module_exists(layer)
        assert verdict.status == ClosureStatus.OPEN
        assert "not found" in verdict.justification


class TestCheckPosMinimality:
    def test_pos_ternary_present(self):
        verdict = _check_pos_minimality()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "pos_classification"


class TestCheckIrabClosure:
    def test_irab_minimally_complete(self):
        verdict = _check_irab_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "irab_system"


class TestCheckDalalaTypes:
    def test_dalala_types_present(self):
        verdict = _check_dalala_types()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "dalala_types"


class TestCheckPropositionalClosure:
    def test_propositional_complete(self):
        verdict = _check_propositional_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "propositional"


class TestCheckTimeSpaceClosure:
    def test_time_space_complete(self):
        verdict = _check_time_space_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "time_space"


class TestCheckInferenceClosure:
    def test_inference_has_rules(self):
        verdict = _check_inference_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "inference"


class TestCheckPhonologicalClosure:
    def test_phonological_closed(self):
        verdict = _check_phonological_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "phonological"

    def test_phonological_missing_syllabify(self):
        with patch("importlib.import_module") as mock_import:
            # Return a module without syllabify
            mock_mod = type("FakeMod", (), {})()
            mock_import.return_value = mock_mod
            verdict = _check_phonological_closure()
            assert verdict.status == ClosureStatus.OPEN


class TestCheckSemanticRolesClosure:
    def test_semantic_roles_closed(self):
        verdict = _check_semantic_roles_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "semantic_roles"


class TestCheckMasdarClosure:
    def test_masdar_closed(self):
        verdict = _check_masdar_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "masdar"


class TestCheckExplanationClosure:
    def test_explanation_closed(self):
        verdict = _check_explanation_closure()
        assert verdict.status == ClosureStatus.CLOSED
        assert verdict.layer_name == "explanation"


# ── Structural check tests ──────────────────────────────────────────


class TestCheckNoContradiction:
    def test_all_closed_passes(self):
        verdicts = [
            ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ClosureVerdict("b", "ب", ClosureStatus.CLOSED, "ok", "حسن"),
        ]
        assert _check_no_contradiction(verdicts) is True

    def test_all_open_passes(self):
        verdicts = [
            ClosureVerdict("a", "أ", ClosureStatus.OPEN, "fail", "فشل"),
            ClosureVerdict("b", "ب", ClosureStatus.OPEN, "fail", "فشل"),
        ]
        # All open is technically consistent (no CLOSED above OPEN)
        assert _check_no_contradiction(verdicts) is True

    def test_open_then_closed_fails(self):
        verdicts = [
            ClosureVerdict("a", "أ", ClosureStatus.OPEN, "fail", "فشل"),
            ClosureVerdict("b", "ب", ClosureStatus.CLOSED, "ok", "حسن"),
        ]
        # CLOSED above OPEN = contradiction
        assert _check_no_contradiction(verdicts) is False

    def test_closed_then_open_passes(self):
        verdicts = [
            ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ClosureVerdict("b", "ب", ClosureStatus.OPEN, "fail", "فشل"),
        ]
        # OPEN at top only — no contradiction
        assert _check_no_contradiction(verdicts) is True

    def test_empty_verdicts(self):
        assert _check_no_contradiction([]) is True


class TestCheckDecomposability:
    def test_decomposability_passes(self):
        assert _check_decomposability() is True


class TestCheckMantuqBoundary:
    def test_boundary_clear(self):
        assert _check_mantuq_boundary() is True


class TestCheckLayerChainSync:
    def test_chain_synced(self):
        assert _check_layer_chain_sync() is True


# ── Full verification tests ─────────────────────────────────────────


class TestVerifyGeneralClosure:
    """Test the main verify_general_closure orchestrator."""

    def test_full_closure_passes(self):
        result = verify_general_closure()
        assert result.closed is True

    def test_all_verdicts_closed(self):
        result = verify_general_closure()
        for v in result.verdicts:
            assert v.status == ClosureStatus.CLOSED, (
                f"Verdict '{v.layer_name}' is OPEN: {v.justification}"
            )

    def test_structural_flags_all_true(self):
        result = verify_general_closure()
        assert result.ascending_order_valid is True
        assert result.no_contradiction is True
        assert result.decomposable is True
        assert result.mantuq_boundary_clear is True
        assert result.layer_chain_synced is True

    def test_timestamp_set(self):
        result = verify_general_closure()
        assert result.timestamp != ""
        assert "T" in result.timestamp  # ISO format

    def test_selective_layer_checks_only(self):
        result = verify_general_closure(
            include_layer_checks=True,
            include_structural_checks=False,
        )
        assert len(result.verdicts) > 0
        # Structural checks not run, so they remain at default False
        assert result.ascending_order_valid is False
        assert result.closed is False  # structural flags are False

    def test_selective_structural_checks_only(self):
        result = verify_general_closure(
            include_layer_checks=False,
            include_structural_checks=True,
        )
        assert len(result.verdicts) == 0
        assert result.ascending_order_valid is True
        assert result.decomposable is True
        # With no verdicts and all structural True, closed should be True
        assert result.closed is True


# ── Format report tests ─────────────────────────────────────────────


class TestFormatClosureReport:
    def test_report_contains_header(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "General Manṭūq Closure Verification" in report

    def test_report_contains_timestamp(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "Timestamp:" in report

    def test_report_contains_summary_count(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        # Should contain a "N/N passed" line
        assert "passed" in report

    def test_report_contains_structural_checks(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "Ascending order" in report
        assert "No contradiction" in report
        assert "Decomposability" in report
        assert "Manṭūq boundary" in report
        assert "Layer-chain sync" in report

    def test_report_closed_verdict(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "Closed_Mantūq(L*) = TRUE" in report

    def test_report_open_verdict(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.OPEN, "fail", "فشل"),
            ],
        )
        report = format_closure_report(result)
        assert "Closed_Mantūq(L*) = FALSE" in report
        assert "Gaps in:" in report
