"""Tests for Unicode as Cognitive Input Proof v1.

Invariants tested
-----------------
1. The cognitive chain processes all 8 layers for valid Arabic input.
2. Gate decisions enforce minimum completeness thresholds.
3. Jump violations are correctly detected and prevented.
4. The formal proof verifies all 5 premises + conclusion.
5. Empty input is handled gracefully.
6. All new types are correctly structured.
"""

from __future__ import annotations

from arabic_engine.cognitive_input.chain import run_cognitive_chain
from arabic_engine.cognitive_input.gate import (
    detect_jump_violations,
    evaluate_gate,
    is_valid_transition,
)
from arabic_engine.cognitive_input.proof import (
    ProofConditionStatus,
    format_proof_report,
    verify_unicode_cognitive_proof,
)
from arabic_engine.core.enums import CognitiveLayerID, LayerGateDecision

# ═══════════════════════════════════════════════════════════════════════
# Gate logic tests
# ═══════════════════════════════════════════════════════════════════════


class TestEvaluateGate:
    """evaluate_gate() produces correct decisions."""

    def test_pass_when_complete_above_threshold(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=True,
            completeness=0.8,
            has_blocker=False,
        )
        assert gate.decision == LayerGateDecision.PASS

    def test_reject_when_no_membership(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=False,
            completeness=1.0,
            has_blocker=False,
        )
        assert gate.decision == LayerGateDecision.REJECT

    def test_reject_when_blocker_present(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=True,
            completeness=1.0,
            has_blocker=True,
        )
        assert gate.decision == LayerGateDecision.REJECT

    def test_suspend_when_below_threshold(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=True,
            completeness=0.2,
            has_blocker=False,
        )
        assert gate.decision == LayerGateDecision.SUSPEND

    def test_complete_when_perfect_score(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=True,
            completeness=1.0,
            has_blocker=False,
        )
        assert gate.decision == LayerGateDecision.COMPLETE

    def test_custom_threshold(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=True,
            completeness=0.9,
            has_blocker=False,
            threshold=0.95,
        )
        assert gate.decision == LayerGateDecision.SUSPEND

    def test_gate_has_id(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.UNICODE_RAW,
            to_layer=CognitiveLayerID.ATOMIZED,
            membership=True,
            completeness=1.0,
            has_blocker=False,
        )
        assert gate.gate_id == "G_UNICODE_RAW_to_ATOMIZED"

    def test_gate_preserves_evidence(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.UNICODE_RAW,
            to_layer=CognitiveLayerID.ATOMIZED,
            membership=True,
            completeness=1.0,
            has_blocker=False,
            evidence=("e1", "e2"),
        )
        assert gate.evidence == ("e1", "e2")

    def test_gate_has_reason(self):
        gate = evaluate_gate(
            from_layer=CognitiveLayerID.ATOMIZED,
            to_layer=CognitiveLayerID.DIFFERENTIATED,
            membership=True,
            completeness=0.8,
            has_blocker=False,
        )
        assert gate.reason != ""


class TestIsValidTransition:
    """is_valid_transition() enforces adjacency."""

    def test_adjacent_is_valid(self):
        assert is_valid_transition(
            CognitiveLayerID.UNICODE_RAW,
            CognitiveLayerID.ATOMIZED,
        )

    def test_skip_one_is_invalid(self):
        assert not is_valid_transition(
            CognitiveLayerID.UNICODE_RAW,
            CognitiveLayerID.DIFFERENTIATED,
        )

    def test_backward_is_invalid(self):
        assert not is_valid_transition(
            CognitiveLayerID.ATOMIZED,
            CognitiveLayerID.UNICODE_RAW,
        )

    def test_same_layer_is_invalid(self):
        assert not is_valid_transition(
            CognitiveLayerID.ATOMIZED,
            CognitiveLayerID.ATOMIZED,
        )

    def test_last_transition_valid(self):
        assert is_valid_transition(
            CognitiveLayerID.SEMANTIC_SUBJECT,
            CognitiveLayerID.JUDGEMENT_READY,
        )


class TestDetectJumpViolations:
    """detect_jump_violations() catches illegal jumps."""

    def test_no_violation_for_adjacent(self):
        violations = detect_jump_violations(
            CognitiveLayerID.UNICODE_RAW,
            CognitiveLayerID.ATOMIZED,
        )
        assert violations == []

    def test_violation_for_skip(self):
        violations = detect_jump_violations(
            CognitiveLayerID.UNICODE_RAW,
            CognitiveLayerID.JUDGEMENT_READY,
        )
        assert len(violations) == 1
        assert "ATOMIZED" in violations[0]

    def test_violation_for_backward(self):
        violations = detect_jump_violations(
            CognitiveLayerID.NORMALIZED,
            CognitiveLayerID.UNICODE_RAW,
        )
        assert len(violations) == 1
        assert "Backward" in violations[0]

    def test_unicode_to_concept_is_violation(self):
        violations = detect_jump_violations(
            CognitiveLayerID.UNICODE_RAW,
            CognitiveLayerID.DISCIPLINED_CONCEPTION,
        )
        assert len(violations) == 1

    def test_normalization_to_judgement_is_violation(self):
        violations = detect_jump_violations(
            CognitiveLayerID.NORMALIZED,
            CognitiveLayerID.JUDGEMENT_READY,
        )
        assert len(violations) == 1

    def test_initial_conception_to_judgement_is_violation(self):
        violations = detect_jump_violations(
            CognitiveLayerID.INITIAL_CONCEPTION,
            CognitiveLayerID.JUDGEMENT_READY,
        )
        assert len(violations) == 1


# ═══════════════════════════════════════════════════════════════════════
# Cognitive chain tests
# ═══════════════════════════════════════════════════════════════════════


class TestRunCognitiveChain:
    """run_cognitive_chain() processes text through all layers."""

    def test_chain_completes_for_arabic(self):
        result = run_cognitive_chain("كتب الرسالة")
        assert result.is_complete
        assert result.final_layer == CognitiveLayerID.JUDGEMENT_READY

    def test_chain_has_eight_layer_results(self):
        result = run_cognitive_chain("ذهب")
        assert len(result.layer_results) == 8

    def test_chain_has_eight_gates(self):
        result = run_cognitive_chain("ذهب")
        assert len(result.gates) == 8

    def test_chain_preserves_source_text(self):
        text = "كَتَبَ"
        result = run_cognitive_chain(text)
        assert result.source_text == text

    def test_chain_no_jump_violations(self):
        result = run_cognitive_chain("كتب")
        assert result.jump_violations == ()

    def test_chain_empty_input(self):
        result = run_cognitive_chain("")
        assert not result.is_complete

    def test_chain_all_gates_pass_or_complete(self):
        result = run_cognitive_chain("كتب")
        for lr in result.layer_results:
            assert lr.gate.decision in (
                LayerGateDecision.PASS,
                LayerGateDecision.COMPLETE,
            )

    def test_chain_layers_in_order(self):
        result = run_cognitive_chain("كتب")
        expected = [
            CognitiveLayerID.ATOMIZED,
            CognitiveLayerID.DIFFERENTIATED,
            CognitiveLayerID.NORMALIZED,
            CognitiveLayerID.DESIGNATED,
            CognitiveLayerID.INITIAL_CONCEPTION,
            CognitiveLayerID.DISCIPLINED_CONCEPTION,
            CognitiveLayerID.SEMANTIC_SUBJECT,
            CognitiveLayerID.JUDGEMENT_READY,
        ]
        actual = [lr.layer for lr in result.layer_results]
        assert actual == expected

    def test_chain_with_diacritics(self):
        result = run_cognitive_chain("كَتَبَ المُعَلِّمُ الدَّرسَ")
        assert result.is_complete
        assert result.final_layer == CognitiveLayerID.JUDGEMENT_READY

    def test_chain_single_char(self):
        result = run_cognitive_chain("ك")
        assert result.is_complete

    def test_chain_completeness_scores_non_negative(self):
        result = run_cognitive_chain("كتب")
        for lr in result.layer_results:
            assert lr.completeness >= 0.0

    def test_chain_membership_true_for_valid_input(self):
        result = run_cognitive_chain("كتب")
        for lr in result.layer_results:
            assert lr.membership is True


# ═══════════════════════════════════════════════════════════════════════
# Proof verification tests
# ═══════════════════════════════════════════════════════════════════════


class TestVerifyProof:
    """verify_unicode_cognitive_proof() verifies all premises."""

    def test_all_conditions_pass(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        assert result.all_passed

    def test_premise_count(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        # 5 premises + 1 conclusion + 5 jump checks = 11
        assert len(result.conditions) == 11

    def test_premise_1_unicode_capturable(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        p1 = result.conditions[0]
        assert p1.condition_id == "P1"
        assert p1.status == ProofConditionStatus.VERIFIED

    def test_premise_2_not_complete_meaning(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        p2 = result.conditions[1]
        assert p2.condition_id == "P2"
        assert p2.status == ProofConditionStatus.VERIFIED

    def test_premise_3_cognitive_input(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        p3 = result.conditions[2]
        assert p3.condition_id == "P3"
        assert p3.status == ProofConditionStatus.VERIFIED

    def test_premise_4_rerationalisation(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        p4 = result.conditions[3]
        assert p4.condition_id == "P4"
        assert p4.status == ProofConditionStatus.VERIFIED

    def test_premise_5_no_jumping(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        p5 = result.conditions[4]
        assert p5.condition_id == "P5"
        assert p5.status == ProofConditionStatus.VERIFIED

    def test_conclusion(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        conclusion = result.conditions[5]
        assert conclusion.condition_id == "CONCLUSION"
        assert conclusion.status == ProofConditionStatus.VERIFIED

    def test_jump_violation_checks_verified(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        jump_conditions = [
            c for c in result.conditions if c.condition_id.startswith("JUMP_")
        ]
        assert len(jump_conditions) == 5
        for jc in jump_conditions:
            assert jc.status == ProofConditionStatus.VERIFIED

    def test_summary_contains_verified(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        assert "VERIFIED" in result.summary

    def test_arabic_summary(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        assert "مُحقَّق" in result.summary_ar

    def test_with_different_text(self):
        result = verify_unicode_cognitive_proof("ذهب الطالبُ إلى المدرسة")
        assert result.all_passed


class TestFormatProofReport:
    """format_proof_report() produces readable output."""

    def test_report_not_empty(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        report = format_proof_report(result)
        assert len(report) > 0

    def test_report_has_header(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        report = format_proof_report(result)
        assert "Unicode as Cognitive Input" in report

    def test_report_has_arabic(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        report = format_proof_report(result)
        assert "إثبات اليونيكود" in report

    def test_report_shows_all_conditions(self):
        result = verify_unicode_cognitive_proof("كَتَبَ")
        report = format_proof_report(result)
        assert "P1" in report
        assert "P2" in report
        assert "P3" in report
        assert "P4" in report
        assert "P5" in report
        assert "CONCLUSION" in report


# ═══════════════════════════════════════════════════════════════════════
# Type structure tests
# ═══════════════════════════════════════════════════════════════════════


class TestCognitiveLayerID:
    """CognitiveLayerID enum has all 9 values."""

    def test_nine_members(self):
        assert len(CognitiveLayerID) == 9

    def test_order_preserved(self):
        members = list(CognitiveLayerID)
        assert members[0] == CognitiveLayerID.UNICODE_RAW
        assert members[-1] == CognitiveLayerID.JUDGEMENT_READY

    def test_all_names_present(self):
        names = {m.name for m in CognitiveLayerID}
        expected = {
            "UNICODE_RAW", "ATOMIZED", "DIFFERENTIATED", "NORMALIZED",
            "DESIGNATED", "INITIAL_CONCEPTION", "DISCIPLINED_CONCEPTION",
            "SEMANTIC_SUBJECT", "JUDGEMENT_READY",
        }
        assert names == expected


class TestLayerGateDecision:
    """LayerGateDecision enum has 4 values."""

    def test_four_members(self):
        assert len(LayerGateDecision) == 4

    def test_all_values(self):
        names = {m.name for m in LayerGateDecision}
        assert names == {"PASS", "REJECT", "SUSPEND", "COMPLETE"}


class TestNewTypeImports:
    """All new types are importable from core."""

    def test_import_from_core(self):
        from arabic_engine.core import (
            AtomizedInput,
            CognitiveChainResult,
            CognitiveGateRecord,
            CognitiveLayerID,
            CognitiveLayerResult,
            DesignatedUnit,
            DifferentiatedUnit,
            DisciplinedConceptionRecord,
            InitialConceptionRecord,
            JudgementReadyInput,
            LayerGateDecision,
            NormalizedUnit,
            SemanticSubject,
        )
        # Verify they are all dataclasses or enums
        assert hasattr(AtomizedInput, "__dataclass_fields__")
        assert hasattr(CognitiveChainResult, "__dataclass_fields__")
        assert hasattr(CognitiveGateRecord, "__dataclass_fields__")
        assert hasattr(CognitiveLayerResult, "__dataclass_fields__")
        assert hasattr(DesignatedUnit, "__dataclass_fields__")
        assert hasattr(DifferentiatedUnit, "__dataclass_fields__")
        assert hasattr(DisciplinedConceptionRecord, "__dataclass_fields__")
        assert hasattr(InitialConceptionRecord, "__dataclass_fields__")
        assert hasattr(JudgementReadyInput, "__dataclass_fields__")
        assert hasattr(NormalizedUnit, "__dataclass_fields__")
        assert hasattr(SemanticSubject, "__dataclass_fields__")
        # Enums
        assert hasattr(CognitiveLayerID, "UNICODE_RAW")
        assert hasattr(LayerGateDecision, "PASS")


class TestCognitiveInputPackageImport:
    """The cognitive_input package is importable."""

    def test_package_import(self):
        import arabic_engine.cognitive_input
        assert hasattr(arabic_engine.cognitive_input, "run_cognitive_chain")
        assert hasattr(arabic_engine.cognitive_input, "evaluate_gate")
        assert hasattr(arabic_engine.cognitive_input, "verify_unicode_cognitive_proof")
