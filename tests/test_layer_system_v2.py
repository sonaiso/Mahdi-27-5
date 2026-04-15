"""Comprehensive v2 tests for the strict 7-layer analysis system.

Covers each layer builder, individual assessment functions,
transition gates, the full pipeline, and edge cases for
non-Arabic and diacritic codepoints.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    JudgmentCategory,
    StrictLayerID,
    TransitionGateStatus,
)
from arabic_engine.core.types import (
    AuditoryMinimumRecord,
    GenerativeProfileRecord,
    JudgmentRecordL5,
    LayerTraceRecord,
    MentalFoundationRecord,
    RepresentationRecord,
    RootPattern,
    StructuralProfileRecord,
    Syllable,
    TransformationProfileRecord,
    TransitionGate,
)
from arabic_engine.layers.layer0_mental import (
    assess_difference,
    assess_identity,
    assess_rank,
    assess_reality_match,
    build_mental_foundation,
)
from arabic_engine.layers.layer1_generative import (
    build_generative_profile,
    compute_closure,
    compute_sonority,
    extract_manner,
    extract_place,
    extract_voicedness,
)
from arabic_engine.layers.layer2_auditory import (
    assess_audibility,
    assess_cohesion,
    assess_temporal_span,
    assess_unity,
    build_auditory_minimum,
)
from arabic_engine.layers.layer3_structural import (
    build_structural_profile,
)
from arabic_engine.layers.layer4_transformation import (
    build_transformation_record,
)
from arabic_engine.layers.layer5_judgment import (
    build_judgment,
)
from arabic_engine.layers.layer6_representation import (
    build_representation,
)
from arabic_engine.layers.layer_pipeline import analyze_element, analyze_word
from arabic_engine.layers.transition_rules import (
    gate_0_to_1,
    gate_1_to_2,
    gate_2_to_3,
    gate_3_to_4,
    gate_4_to_5,
    gate_5_to_6,
    validate_full_trace,
)
from arabic_engine.signifier.dmin import DMIN_REGISTRY

# ── Helpers ──────────────────────────────────────────────────────────

KAF = 0x0643  # ك
BA = 0x0628  # ب
FATHA = 0x064E  # َ  (diacritic)
LATIN_A = 0x0041  # A  (non-Arabic)


def _in_unit(value: float) -> bool:
    """Return True when *value* ∈ [0, 1]."""
    return isinstance(value, (int, float)) and 0.0 <= value <= 1.0


# ══════════════════════════════════════════════════════════════════════
# Layer 0 — Mental Foundation
# ══════════════════════════════════════════════════════════════════════


class TestLayer0Mental:
    """Layer 0 builder and sub-assessments."""

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_build_returns_record(self, cp: int) -> None:
        rec = build_mental_foundation(cp)
        assert isinstance(rec, MentalFoundationRecord)

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_scores_in_unit_interval(self, cp: int) -> None:
        rec = build_mental_foundation(cp)
        assert _in_unit(rec.identity_strength)
        assert _in_unit(rec.distinctiveness)
        assert _in_unit(rec.rank_position)
        assert _in_unit(rec.stability_score)
        assert _in_unit(rec.reality_match_score)

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_bool_fields(self, cp: int) -> None:
        rec = build_mental_foundation(cp)
        assert isinstance(rec.is_constitutive, bool)
        assert isinstance(rec.is_dependent, bool)

    def test_identity_known_returns_positive(self) -> None:
        assert assess_identity(KAF) > 0.0

    def test_identity_unknown_returns_zero(self) -> None:
        assert assess_identity(LATIN_A) == 0.0

    def test_difference_known_positive(self) -> None:
        assert 0.0 < assess_difference(KAF) <= 1.0

    def test_rank_known_positive(self) -> None:
        assert assess_rank(KAF) > 0.0

    def test_reality_match_known(self) -> None:
        assert _in_unit(assess_reality_match(KAF))

    def test_transformation_type_is_str(self) -> None:
        rec = build_mental_foundation(KAF)
        assert isinstance(rec.transformation_type, str)

    def test_causal_source_is_str(self) -> None:
        rec = build_mental_foundation(KAF)
        assert isinstance(rec.causal_source, str)


# ══════════════════════════════════════════════════════════════════════
# Layer 1 — Generative Profile
# ══════════════════════════════════════════════════════════════════════


class TestLayer1Generative:
    """Layer 1 builder and sub-extractors."""

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_build_returns_record(self, cp: int) -> None:
        rec = build_generative_profile(cp)
        assert isinstance(rec, GenerativeProfileRecord)

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_voicedness_is_bool(self, cp: int) -> None:
        rec = build_generative_profile(cp)
        assert isinstance(rec.voicedness, bool)

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_place_manner_non_empty(self, cp: int) -> None:
        rec = build_generative_profile(cp)
        assert isinstance(rec.place_class, str) and rec.place_class
        assert isinstance(rec.manner_class, str) and rec.manner_class

    @pytest.mark.parametrize("cp", [KAF, BA])
    def test_closure_sonority_in_unit(self, cp: int) -> None:
        rec = build_generative_profile(cp)
        assert _in_unit(rec.closure_value)
        assert _in_unit(rec.sonority_level)

    def test_extract_voicedness_via_dmin(self) -> None:
        dmin = DMIN_REGISTRY.get(KAF)
        assert dmin is not None
        assert isinstance(extract_voicedness(dmin), bool)

    def test_extract_place_via_dmin(self) -> None:
        dmin = DMIN_REGISTRY.get(KAF)
        assert dmin is not None
        assert isinstance(extract_place(dmin), str)

    def test_extract_manner_via_dmin(self) -> None:
        dmin = DMIN_REGISTRY.get(KAF)
        assert dmin is not None
        assert isinstance(extract_manner(dmin), str)

    def test_compute_closure_via_dmin(self) -> None:
        dmin = DMIN_REGISTRY.get(KAF)
        assert dmin is not None
        assert _in_unit(compute_closure(dmin))

    def test_compute_sonority_via_dmin(self) -> None:
        dmin = DMIN_REGISTRY.get(KAF)
        assert dmin is not None
        assert _in_unit(compute_sonority(dmin))

    def test_nasality_and_continuancy_are_bool(self) -> None:
        rec = build_generative_profile(BA)
        assert isinstance(rec.nasality, bool)
        assert isinstance(rec.continuancy, bool)

    def test_air_pressure_in_unit(self) -> None:
        rec = build_generative_profile(KAF)
        assert _in_unit(rec.air_pressure)


# ══════════════════════════════════════════════════════════════════════
# Layer 2 — Auditory Minimum
# ══════════════════════════════════════════════════════════════════════


class TestLayer2Auditory:
    """Layer 2 builder and sub-assessments."""

    @pytest.fixture()
    def gen_kaf(self) -> GenerativeProfileRecord:
        return build_generative_profile(KAF)

    def test_build_returns_record(self, gen_kaf: GenerativeProfileRecord) -> None:
        rec = build_auditory_minimum(gen_kaf)
        assert isinstance(rec, AuditoryMinimumRecord)

    def test_audibility_in_unit(self, gen_kaf: GenerativeProfileRecord) -> None:
        rec = build_auditory_minimum(gen_kaf)
        assert _in_unit(rec.audibility_score)

    def test_temporal_span_in_unit(self, gen_kaf: GenerativeProfileRecord) -> None:
        rec = build_auditory_minimum(gen_kaf)
        assert _in_unit(rec.temporal_span)

    def test_cohesion_in_unit(self, gen_kaf: GenerativeProfileRecord) -> None:
        rec = build_auditory_minimum(gen_kaf)
        assert _in_unit(rec.cohesion_score)

    def test_unity_in_unit(self, gen_kaf: GenerativeProfileRecord) -> None:
        rec = build_auditory_minimum(gen_kaf)
        assert _in_unit(rec.unity_score)

    def test_phase_count_nonneg(self, gen_kaf: GenerativeProfileRecord) -> None:
        rec = build_auditory_minimum(gen_kaf)
        assert isinstance(rec.phase_count, int)
        assert rec.phase_count >= 0

    def test_assess_audibility_direct(self, gen_kaf: GenerativeProfileRecord) -> None:
        assert _in_unit(assess_audibility(gen_kaf))

    def test_assess_temporal_no_syllable(self) -> None:
        assert _in_unit(assess_temporal_span(None))

    def test_assess_cohesion_direct(self, gen_kaf: GenerativeProfileRecord) -> None:
        assert _in_unit(assess_cohesion(gen_kaf))

    def test_assess_unity_direct(self) -> None:
        assert _in_unit(assess_unity(0.5, 0.5, 0.5))

    def test_with_syllable(self, gen_kaf: GenerativeProfileRecord) -> None:
        syl = Syllable(onset=(KAF,), nucleus=(FATHA,), coda=(), weight=1)
        rec = build_auditory_minimum(gen_kaf, syllable=syl)
        assert isinstance(rec, AuditoryMinimumRecord)
        assert _in_unit(rec.temporal_span)


# ══════════════════════════════════════════════════════════════════════
# Layer 3 — Structural Profile
# ══════════════════════════════════════════════════════════════════════


class TestLayer3Structural:
    """Layer 3 builder output validation."""

    def test_build_returns_record(self) -> None:
        rec = build_structural_profile(KAF, "ك")
        assert isinstance(rec, StructuralProfileRecord)

    def test_syllable_slot_is_str(self) -> None:
        rec = build_structural_profile(KAF, "ك")
        assert isinstance(rec.syllable_slot, str)

    def test_root_slot_is_str(self) -> None:
        rec = build_structural_profile(KAF, "ك")
        assert isinstance(rec.root_slot, str)

    def test_scores_in_unit(self) -> None:
        rec = build_structural_profile(BA, "ب")
        assert _in_unit(rec.constitutiveness_score)
        assert _in_unit(rec.dependency_score)
        assert _in_unit(rec.attachment_score)
        assert _in_unit(rec.augmentation_score)

    def test_fitness_in_unit(self) -> None:
        rec = build_structural_profile(KAF, "ك")
        assert _in_unit(rec.fa_fitness)
        assert _in_unit(rec.ayn_fitness)
        assert _in_unit(rec.lam_fitness)

    def test_with_root_pattern(self) -> None:
        rp = RootPattern(root=("ك", "ت", "ب"), pattern="فَعَلَ")
        rec = build_structural_profile(KAF, "ك", root_pattern=rp)
        assert isinstance(rec, StructuralProfileRecord)


# ══════════════════════════════════════════════════════════════════════
# Layer 4 — Transformation
# ══════════════════════════════════════════════════════════════════════


class TestLayer4Transformation:
    """Layer 4 builder output validation."""

    @pytest.fixture()
    def structural_kaf(self) -> StructuralProfileRecord:
        return build_structural_profile(KAF, "ك")

    def test_build_returns_record(self, structural_kaf: StructuralProfileRecord) -> None:
        rec = build_transformation_record(KAF, structural=structural_kaf)
        assert isinstance(rec, TransformationProfileRecord)

    def test_stability_in_unit(self, structural_kaf: StructuralProfileRecord) -> None:
        rec = build_transformation_record(KAF, structural=structural_kaf)
        assert _in_unit(rec.inflection_stability_score)

    def test_recoverability_in_unit(self, structural_kaf: StructuralProfileRecord) -> None:
        rec = build_transformation_record(KAF, structural=structural_kaf)
        assert _in_unit(rec.recoverability_score)

    def test_presence_bools(self, structural_kaf: StructuralProfileRecord) -> None:
        rec = build_transformation_record(KAF, structural=structural_kaf)
        assert isinstance(rec.surface_presence, bool)
        assert isinstance(rec.underlying_presence, bool)

    def test_confidence_scores_in_unit(self, structural_kaf: StructuralProfileRecord) -> None:
        rec = build_transformation_record(KAF, structural=structural_kaf)
        assert _in_unit(rec.substitution_confidence)
        assert _in_unit(rec.deletion_confidence)
        assert _in_unit(rec.illal_confidence)
        assert _in_unit(rec.idgham_confidence)

    def test_build_without_structural(self) -> None:
        rec = build_transformation_record(KAF)
        assert isinstance(rec, TransformationProfileRecord)


# ══════════════════════════════════════════════════════════════════════
# Layer 5 — Judgment
# ══════════════════════════════════════════════════════════════════════


class TestLayer5Judgment:
    """Layer 5 builder output validation."""

    @pytest.fixture()
    def _records(self) -> tuple[StructuralProfileRecord, TransformationProfileRecord]:
        s = build_structural_profile(KAF, "ك")
        t = build_transformation_record(KAF, structural=s)
        return s, t

    def test_build_returns_record(
        self,
        _records: tuple[StructuralProfileRecord, TransformationProfileRecord],
    ) -> None:
        s, t = _records
        rec = build_judgment(s, t)
        assert isinstance(rec, JudgmentRecordL5)

    def test_category_is_enum(
        self,
        _records: tuple[StructuralProfileRecord, TransformationProfileRecord],
    ) -> None:
        s, t = _records
        rec = build_judgment(s, t)
        assert isinstance(rec.final_judgment, JudgmentCategory)

    def test_confidence_in_unit(
        self,
        _records: tuple[StructuralProfileRecord, TransformationProfileRecord],
    ) -> None:
        s, t = _records
        rec = build_judgment(s, t)
        assert _in_unit(rec.judgment_confidence)

    def test_functional_class_is_str(
        self,
        _records: tuple[StructuralProfileRecord, TransformationProfileRecord],
    ) -> None:
        s, t = _records
        rec = build_judgment(s, t)
        assert isinstance(rec.functional_class, str)

    def test_deictic_relational_identity_in_unit(
        self,
        _records: tuple[StructuralProfileRecord, TransformationProfileRecord],
    ) -> None:
        s, t = _records
        rec = build_judgment(s, t)
        assert _in_unit(rec.deictic_score)
        assert _in_unit(rec.relational_score)
        assert _in_unit(rec.identity_preservation_score)

    @pytest.mark.parametrize("cp,char", [(KAF, "ك"), (BA, "ب")])
    def test_judgment_for_multiple_letters(self, cp: int, char: str) -> None:
        s = build_structural_profile(cp, char)
        t = build_transformation_record(cp, structural=s)
        rec = build_judgment(s, t)
        assert isinstance(rec.final_judgment, JudgmentCategory)


# ══════════════════════════════════════════════════════════════════════
# Layer 6 — Representation
# ══════════════════════════════════════════════════════════════════════


class TestLayer6Representation:
    """Layer 6 builder output validation."""

    @pytest.fixture()
    def _full_stack(self) -> dict:
        m = build_mental_foundation(KAF)
        g = build_generative_profile(KAF)
        a = build_auditory_minimum(g)
        s = build_structural_profile(KAF, "ك")
        t = build_transformation_record(KAF, structural=s)
        j = build_judgment(s, t)
        return {
            "element_id": "U+0643",
            "mental": m,
            "generative": g,
            "auditory": a,
            "structural": s,
            "transformation": t,
            "judgment": j,
        }

    def test_build_returns_record(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert isinstance(rec, RepresentationRecord)

    def test_feature_hash_non_empty(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert isinstance(rec.feature_hash, str)
        assert len(rec.feature_hash) > 0

    def test_entity_id_matches(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert rec.entity_id == "U+0643"

    def test_layer_trace_tuple(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert isinstance(rec.layer_trace, tuple)
        assert all(isinstance(lid, StrictLayerID) for lid in rec.layer_trace)

    def test_validation_status_is_bool(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert isinstance(rec.validation_status, bool)

    def test_confidence_chain_tuple(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert isinstance(rec.confidence_chain, tuple)
        assert all(_in_unit(v) for v in rec.confidence_chain)

    def test_rule_set_tuple(self, _full_stack: dict) -> None:
        rec = build_representation(**_full_stack)
        assert isinstance(rec.rule_set, tuple)
        assert all(isinstance(s, str) for s in rec.rule_set)


# ══════════════════════════════════════════════════════════════════════
# Transition Gates
# ══════════════════════════════════════════════════════════════════════


class TestGates:
    """Each gate function returns a TransitionGate."""

    def test_gate_0_to_1_passed(self) -> None:
        m = build_mental_foundation(KAF)
        g = gate_0_to_1(m)
        assert isinstance(g, TransitionGate)
        assert g.source_layer == StrictLayerID.MENTAL_FOUNDATION
        assert g.target_layer == StrictLayerID.GENERATIVE
        assert g.gate_status == TransitionGateStatus.PASSED

    def test_gate_1_to_2_passed(self) -> None:
        gen = build_generative_profile(KAF)
        g = gate_1_to_2(gen)
        assert isinstance(g, TransitionGate)
        assert g.source_layer == StrictLayerID.GENERATIVE
        assert g.target_layer == StrictLayerID.AUDITORY_MINIMUM
        assert g.gate_status == TransitionGateStatus.PASSED

    def test_gate_2_to_3_passed(self) -> None:
        gen = build_generative_profile(KAF)
        aud = build_auditory_minimum(gen)
        g = gate_2_to_3(aud)
        assert isinstance(g, TransitionGate)
        assert g.source_layer == StrictLayerID.AUDITORY_MINIMUM
        assert g.target_layer == StrictLayerID.STRUCTURAL
        assert g.gate_status == TransitionGateStatus.PASSED

    def test_gate_3_to_4_passed(self) -> None:
        s = build_structural_profile(KAF, "ك")
        g = gate_3_to_4(s)
        assert isinstance(g, TransitionGate)
        assert g.source_layer == StrictLayerID.STRUCTURAL
        assert g.target_layer == StrictLayerID.TRANSFORMATION
        assert g.gate_status == TransitionGateStatus.PASSED

    def test_gate_4_to_5_passed(self) -> None:
        s = build_structural_profile(KAF, "ك")
        t = build_transformation_record(KAF, structural=s)
        g = gate_4_to_5(t)
        assert isinstance(g, TransitionGate)
        assert g.source_layer == StrictLayerID.TRANSFORMATION
        assert g.target_layer == StrictLayerID.HIGHER_FUNCTION
        assert g.gate_status == TransitionGateStatus.PASSED

    def test_gate_5_to_6_passed(self) -> None:
        m = build_mental_foundation(KAF)
        s = build_structural_profile(KAF, "ك")
        t = build_transformation_record(KAF, structural=s)
        j = build_judgment(s, t)
        g = gate_5_to_6(j, m)
        assert isinstance(g, TransitionGate)
        assert g.source_layer == StrictLayerID.HIGHER_FUNCTION
        assert g.target_layer == StrictLayerID.PROGRAMMATIC
        assert g.gate_status == TransitionGateStatus.PASSED

    def test_gate_conditions_met_is_tuple(self) -> None:
        m = build_mental_foundation(KAF)
        g = gate_0_to_1(m)
        assert isinstance(g.conditions_met, tuple)
        assert all(isinstance(c, bool) for c in g.conditions_met)

    def test_gate_failure_reasons_is_tuple(self) -> None:
        m = build_mental_foundation(KAF)
        g = gate_0_to_1(m)
        assert isinstance(g.failure_reasons, tuple)


# ══════════════════════════════════════════════════════════════════════
# Pipeline
# ══════════════════════════════════════════════════════════════════════


class TestPipeline:
    """End-to-end pipeline via analyze_element / analyze_word."""

    def test_analyze_element_kaf(self) -> None:
        trace = analyze_element(KAF, char="ك")
        assert isinstance(trace, LayerTraceRecord)
        assert trace.element_id == "U+0643"
        assert trace.layer_0 is not None
        assert trace.layer_1 is not None
        assert trace.layer_2 is not None
        assert trace.layer_3 is not None
        assert trace.layer_4 is not None
        assert trace.layer_5 is not None
        assert trace.layer_6 is not None

    def test_analyze_element_all_gates_passed(self) -> None:
        trace = analyze_element(KAF, char="ك")
        assert len(trace.gates) == 6
        for g in trace.gates:
            assert g.gate_status == TransitionGateStatus.PASSED
        assert trace.final_gate_status == TransitionGateStatus.PASSED

    def test_analyze_word_ktb(self) -> None:
        traces = analyze_word("كتب")
        assert len(traces) == 3
        for tr in traces:
            assert isinstance(tr, LayerTraceRecord)
            assert tr.final_gate_status == TransitionGateStatus.PASSED
            assert len(tr.gates) == 6

    def test_analyze_word_element_ids(self) -> None:
        traces = analyze_word("كتب")
        ids = [tr.element_id for tr in traces]
        assert ids == ["U+0643", "U+062A", "U+0628"]

    def test_analyze_element_ba(self) -> None:
        trace = analyze_element(BA, char="ب")
        assert trace.final_gate_status == TransitionGateStatus.PASSED
        assert trace.layer_6 is not None


# ══════════════════════════════════════════════════════════════════════
# Transition Rules — validate_full_trace
# ══════════════════════════════════════════════════════════════════════


class TestTransitionRules:
    """validate_full_trace returns True for a fully passed trace."""

    def test_full_trace_valid(self) -> None:
        trace = analyze_element(KAF, char="ك")
        assert validate_full_trace(trace) is True

    def test_full_trace_valid_ba(self) -> None:
        trace = analyze_element(BA, char="ب")
        assert validate_full_trace(trace) is True

    def test_blocked_trace_invalid(self) -> None:
        trace = analyze_element(LATIN_A, char="A")
        assert validate_full_trace(trace) is False

    def test_all_word_traces_valid(self) -> None:
        for tr in analyze_word("كتب"):
            assert validate_full_trace(tr) is True


# ══════════════════════════════════════════════════════════════════════
# Edge Cases
# ══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Non-Arabic codepoints and diacritics."""

    def test_non_arabic_blocked_at_gate0(self) -> None:
        trace = analyze_element(LATIN_A, char="A")
        assert trace.final_gate_status == TransitionGateStatus.BLOCKED
        assert len(trace.gates) >= 1
        assert trace.gates[0].gate_status == TransitionGateStatus.BLOCKED

    def test_non_arabic_mental_zeros(self) -> None:
        rec = build_mental_foundation(LATIN_A)
        assert rec.identity_strength == 0.0
        assert rec.distinctiveness == 0.0
        assert rec.rank_position == 0.0

    def test_diacritic_fatha_passes(self) -> None:
        trace = analyze_element(FATHA, char="َ")
        assert trace.final_gate_status == TransitionGateStatus.PASSED
        assert trace.layer_6 is not None

    def test_diacritic_mental_foundation(self) -> None:
        rec = build_mental_foundation(FATHA)
        assert isinstance(rec, MentalFoundationRecord)
        assert _in_unit(rec.identity_strength)

    def test_non_arabic_layer0_only(self) -> None:
        trace = analyze_element(LATIN_A, char="A")
        assert trace.layer_0 is not None
        assert trace.layer_1 is None
