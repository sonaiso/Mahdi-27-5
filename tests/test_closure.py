"""Tests for arabic_engine.closure — General Closure verification."""

from __future__ import annotations

from arabic_engine.closure import (
    ClosureStatus,
    ClosureVerdict,
    GeneralClosureResult,
    _check_ascending_order,
    _check_dalala_types,
    _check_decomposability,
    _check_inference_closure,
    _check_irab_closure,
    _check_mantuq_boundary,
    _check_module_exists,
    _check_no_contradiction,
    _check_pos_minimality,
    _check_propositional_closure,
    _check_time_space_closure,
    format_closure_report,
    verify_general_closure,
)

# ── ClosureStatus ───────────────────────────────────────────────────────


class TestClosureStatus:
    """Tests for the ClosureStatus enum."""

    def test_has_closed(self):
        assert hasattr(ClosureStatus, "CLOSED")

    def test_has_open(self):
        assert hasattr(ClosureStatus, "OPEN")

    def test_exactly_two_members(self):
        assert len(ClosureStatus) == 2


# ── ClosureVerdict ──────────────────────────────────────────────────────


class TestClosureVerdict:
    """Tests for the ClosureVerdict dataclass."""

    def test_creation(self):
        v = ClosureVerdict(
            layer_name="test",
            layer_name_ar="اختبار",
            status=ClosureStatus.CLOSED,
            justification="ok",
            justification_ar="حسن",
        )
        assert v.layer_name == "test"
        assert v.status == ClosureStatus.CLOSED

    def test_open_verdict(self):
        v = ClosureVerdict(
            layer_name="gap",
            layer_name_ar="فجوة",
            status=ClosureStatus.OPEN,
            justification="missing module",
            justification_ar="وحدة ناقصة",
        )
        assert v.status == ClosureStatus.OPEN


# ── GeneralClosureResult ────────────────────────────────────────────────


class TestGeneralClosureResult:
    """Tests for the GeneralClosureResult dataclass."""

    def test_defaults(self):
        r = GeneralClosureResult()
        assert r.verdicts == []
        assert r.ascending_order_valid is False
        assert r.no_contradiction is False
        assert r.decomposable is False
        assert r.mantuq_boundary_clear is False

    def test_closed_when_all_pass(self):
        r = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
        )
        assert r.closed is True

    def test_not_closed_when_verdict_open(self):
        r = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.OPEN, "gap", "فجوة"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
        )
        assert r.closed is False

    def test_not_closed_when_ascending_false(self):
        r = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=False,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
        )
        assert r.closed is False

    def test_not_closed_when_no_contradiction_false(self):
        r = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=False,
            decomposable=True,
            mantuq_boundary_clear=True,
        )
        assert r.closed is False

    def test_not_closed_when_decomposable_false(self):
        r = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=False,
            mantuq_boundary_clear=True,
        )
        assert r.closed is False

    def test_not_closed_when_boundary_false(self):
        r = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=False,
        )
        assert r.closed is False

    def test_empty_verdicts_all_true_is_closed(self):
        r = GeneralClosureResult(
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
        )
        assert r.closed is True


# ── _check_module_exists ────────────────────────────────────────────────


class TestCheckModuleExists:
    """Tests for _check_module_exists."""

    def test_valid_module_and_function(self):
        layer = {
            "symbol": "test",
            "name": "test_layer",
            "name_ar": "اختبار",
            "module": "json",
            "function": "dumps",
        }
        v = _check_module_exists(layer)
        assert v.status == ClosureStatus.CLOSED

    def test_invalid_module(self):
        layer = {
            "symbol": "test",
            "name": "test_layer",
            "name_ar": "اختبار",
            "module": "totally.nonexistent.module",
            "function": "foo",
        }
        v = _check_module_exists(layer)
        assert v.status == ClosureStatus.OPEN
        assert "not importable" in v.justification

    def test_invalid_function(self):
        layer = {
            "symbol": "test",
            "name": "test_layer",
            "name_ar": "اختبار",
            "module": "json",
            "function": "this_does_not_exist",
        }
        v = _check_module_exists(layer)
        assert v.status == ClosureStatus.OPEN
        assert "not found" in v.justification

    def test_class_method_valid(self):
        layer = {
            "symbol": "test",
            "name": "test_layer",
            "name_ar": "اختبار",
            "module": "json",
            "function": "JSONDecoder.decode",
        }
        v = _check_module_exists(layer)
        assert v.status == ClosureStatus.CLOSED

    def test_class_method_invalid_class(self):
        layer = {
            "symbol": "test",
            "name": "test_layer",
            "name_ar": "اختبار",
            "module": "json",
            "function": "NonExistentClass.method",
        }
        v = _check_module_exists(layer)
        assert v.status == ClosureStatus.OPEN
        assert "not found" in v.justification


# ── Domain-specific checks ──────────────────────────────────────────────


class TestDomainChecks:
    """Tests for domain-specific closure checks."""

    def test_pos_minimality_closed(self):
        v = _check_pos_minimality()
        assert v.status == ClosureStatus.CLOSED

    def test_irab_closure_closed(self):
        v = _check_irab_closure()
        assert v.status == ClosureStatus.CLOSED

    def test_dalala_types_closed(self):
        v = _check_dalala_types()
        assert v.status == ClosureStatus.CLOSED

    def test_propositional_closure_closed(self):
        v = _check_propositional_closure()
        assert v.status == ClosureStatus.CLOSED

    def test_time_space_closure_closed(self):
        v = _check_time_space_closure()
        assert v.status == ClosureStatus.CLOSED

    def test_inference_closure_closed(self):
        v = _check_inference_closure()
        assert v.status == ClosureStatus.CLOSED

    def test_pos_minimality_verdict_has_layer_name(self):
        v = _check_pos_minimality()
        assert v.layer_name == "pos_classification"

    def test_irab_verdict_has_layer_name(self):
        v = _check_irab_closure()
        assert v.layer_name == "irab_system"

    def test_dalala_verdict_has_layer_name(self):
        v = _check_dalala_types()
        assert v.layer_name == "dalala_types"

    def test_propositional_verdict_has_layer_name(self):
        v = _check_propositional_closure()
        assert v.layer_name == "propositional"

    def test_time_space_verdict_has_layer_name(self):
        v = _check_time_space_closure()
        assert v.layer_name == "time_space"

    def test_inference_verdict_has_layer_name(self):
        v = _check_inference_closure()
        assert v.layer_name == "inference"


# ── Structural checks ──────────────────────────────────────────────────


class TestStructuralChecks:
    """Tests for aggregate structural checks."""

    def test_ascending_order_valid(self):
        assert _check_ascending_order() is True

    def test_decomposability_valid(self):
        assert _check_decomposability() is True

    def test_mantuq_boundary_clear(self):
        assert _check_mantuq_boundary() is True

    def test_no_contradiction_all_closed(self):
        verdicts = [
            ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ClosureVerdict("b", "ب", ClosureStatus.CLOSED, "ok", "حسن"),
        ]
        assert _check_no_contradiction(verdicts) is True

    def test_no_contradiction_has_open(self):
        verdicts = [
            ClosureVerdict("a", "أ", ClosureStatus.CLOSED, "ok", "حسن"),
            ClosureVerdict("b", "ب", ClosureStatus.OPEN, "gap", "فجوة"),
        ]
        assert _check_no_contradiction(verdicts) is False

    def test_no_contradiction_empty(self):
        assert _check_no_contradiction([]) is True


# ── verify_general_closure ──────────────────────────────────────────────


class TestVerifyGeneralClosure:
    """Tests for verify_general_closure — the main entry point."""

    def test_returns_general_closure_result(self):
        result = verify_general_closure()
        assert isinstance(result, GeneralClosureResult)

    def test_overall_closed(self):
        result = verify_general_closure()
        assert result.closed is True

    def test_verdicts_non_empty(self):
        result = verify_general_closure()
        assert len(result.verdicts) > 0

    def test_all_verdicts_closed(self):
        result = verify_general_closure()
        for v in result.verdicts:
            assert v.status == ClosureStatus.CLOSED, (
                f"Layer '{v.layer_name}' is OPEN: {v.justification}"
            )

    def test_ascending_order_valid(self):
        result = verify_general_closure()
        assert result.ascending_order_valid is True

    def test_no_contradiction(self):
        result = verify_general_closure()
        assert result.no_contradiction is True

    def test_decomposable(self):
        result = verify_general_closure()
        assert result.decomposable is True

    def test_mantuq_boundary_clear(self):
        result = verify_general_closure()
        assert result.mantuq_boundary_clear is True


# ── format_closure_report ───────────────────────────────────────────────


class TestFormatClosureReport:
    """Tests for format_closure_report."""

    def test_returns_string(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert isinstance(report, str)

    def test_report_contains_header(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "الإقفال العام للمنطوق" in report

    def test_report_contains_layer_checks(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "Layer-Local Closure Checks" in report

    def test_report_contains_structural_checks(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "Structural Checks" in report

    def test_report_contains_final_verdict(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "Final Verdict" in report

    def test_closed_report_contains_true(self):
        result = verify_general_closure()
        report = format_closure_report(result)
        assert "TRUE" in report

    def test_open_report_contains_false(self):
        """A report with an OPEN verdict should say FALSE."""
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("gap", "فجوة", ClosureStatus.OPEN, "missing", "ناقص"),
            ],
        )
        report = format_closure_report(result)
        assert "FALSE" in report

    def test_open_report_lists_gaps(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("gap", "فجوة", ClosureStatus.OPEN, "missing", "ناقص"),
            ],
        )
        report = format_closure_report(result)
        assert "فجوة" in report

    def test_checkmark_for_closed(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("ok", "حسن", ClosureStatus.CLOSED, "ok", "حسن"),
            ],
            ascending_order_valid=True,
            no_contradiction=True,
            decomposable=True,
            mantuq_boundary_clear=True,
        )
        report = format_closure_report(result)
        assert "✓" in report

    def test_cross_for_open(self):
        result = GeneralClosureResult(
            verdicts=[
                ClosureVerdict("gap", "فجوة", ClosureStatus.OPEN, "gap", "فجوة"),
            ],
        )
        report = format_closure_report(result)
        assert "✗" in report
