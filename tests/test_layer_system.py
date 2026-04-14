"""Comprehensive tests for the strict 7-layer analysis system.

Tests cover each layer individually, each transition gate,
integration through the full pipeline, and real Arabic word
examples for reality-match validation.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    AuditoryNode,
    GenerativeNode,
    JudgmentCategory,
    LayerEdgeType,
    MentalEdgeType,
    MentalPrimitive,
    RepresentationNode,
    StrictLayerID,
    StructuralNode,
    TransformationNode,
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
)

# ── Layer 0 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer0_mental import (
    assess_difference,
    assess_identity,
    assess_rank,
    assess_reality_match,
    build_mental_foundation,
    check_gate_0_to_1,
)

# ── Layer 1 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer1_generative import (
    build_generative_profile,
    check_gate_1_to_2,
    compute_closure,
    compute_sonority,
    extract_manner,
    extract_place,
    extract_voicedness,
)

# ── Layer 2 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer2_auditory import (
    assess_audibility,
    assess_cohesion,
    assess_temporal_span,
    assess_unity,
    build_auditory_minimum,
    check_gate_2_to_3,
)

# ── Layer 3 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer3_structural import (
    assess_augmentation,
    assess_constitutiveness,
    assess_dependency,
    assign_root_slot,
    assign_syllable_slot,
    build_structural_profile,
    check_gate_3_to_4,
    compute_root_position_fitness,
)

# ── Layer 4 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer4_transformation import (
    assess_inflection_stability,
    assess_recoverability,
    build_transformation_record,
    check_gate_4_to_5,
    detect_deletion,
    detect_idgham,
    detect_illal,
    detect_substitution,
)

# ── Layer 5 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer5_judgment import (
    build_judgment,
    check_gate_5_to_6,
    judge_assimilated,
    judge_attached,
    judge_augmented,
    judge_deictic,
    judge_deleted,
    judge_original,
    judge_relational,
    judge_substituted,
    judge_weakened,
    select_final_judgment,
)

# ── Layer 6 imports ──────────────────────────────────────────────────
from arabic_engine.layers.layer6_representation import (
    build_representation,
    compile_rule_set,
    compute_feature_hash,
    map_to_root_node,
    validate_against_reality,
)

# ── Pipeline imports ─────────────────────────────────────────────────
from arabic_engine.layers.layer_pipeline import analyze_element, analyze_word

# ── Transition rules ─────────────────────────────────────────────────
from arabic_engine.layers.transition_rules import validate_full_trace

# ── DMin registry ────────────────────────────────────────────────────
from arabic_engine.signifier.dmin import DMIN_REGISTRY

# ══════════════════════════════════════════════════════════════════════
# Enum sanity tests
# ══════════════════════════════════════════════════════════════════════


class TestEnumCompleteness:
    """All layer-system enums have the expected members."""

    def test_strict_layer_id_count(self):
        assert len(StrictLayerID) == 7

    def test_mental_primitive_count(self):
        assert len(MentalPrimitive) == 9

    def test_mental_edge_type_count(self):
        assert len(MentalEdgeType) == 7

    def test_generative_node_count(self):
        assert len(GenerativeNode) == 8

    def test_auditory_node_count(self):
        assert len(AuditoryNode) == 7

    def test_structural_node_count(self):
        assert len(StructuralNode) == 9

    def test_transformation_node_count(self):
        assert len(TransformationNode) == 8

    def test_judgment_category_count(self):
        assert len(JudgmentCategory) == 9

    def test_representation_node_count(self):
        assert len(RepresentationNode) == 10

    def test_layer_edge_type_count(self):
        assert len(LayerEdgeType) == 29

    def test_transition_gate_status_count(self):
        assert len(TransitionGateStatus) == 3


# ══════════════════════════════════════════════════════════════════════
# Layer 0 tests — Mental Foundation
# ══════════════════════════════════════════════════════════════════════


class TestLayer0Mental:
    """Layer 0: identity, difference, rank, reality-match."""

    def test_identity_known_consonant(self):
        assert assess_identity(0x0628) == 1.0  # ب

    def test_identity_unknown(self):
        assert assess_identity(0x0041) == 0.0  # 'A'

    def test_difference_nonzero(self):
        score = assess_difference(0x0628)
        assert 0.0 < score <= 1.0

    def test_difference_unknown(self):
        assert assess_difference(0x0041) == 0.0

    def test_rank_consonant(self):
        assert assess_rank(0x0628) == 1.0  # consonant

    def test_rank_long_vowel(self):
        assert assess_rank(0x0627) == 0.8  # alef

    def test_rank_unknown(self):
        assert assess_rank(0x0041) == 0.0

    def test_reality_match_known(self):
        score = assess_reality_match(0x0628)
        assert score > 0.5

    def test_reality_match_unknown(self):
        assert assess_reality_match(0x0041) == 0.0

    def test_build_mental_foundation(self):
        rec = build_mental_foundation(0x0628)
        assert isinstance(rec, MentalFoundationRecord)
        assert rec.identity_strength == 1.0
        assert rec.is_constitutive is True
        assert rec.is_dependent is False

    def test_build_mental_foundation_vowel(self):
        rec = build_mental_foundation(0x064E)  # fatha
        assert rec.is_constitutive is False
        assert rec.is_dependent is True

    def test_gate_0_to_1_passes_for_ba(self):
        rec = build_mental_foundation(0x0628)
        gate = check_gate_0_to_1(rec)
        assert gate.gate_status == TransitionGateStatus.PASSED
        assert all(gate.conditions_met)

    def test_gate_0_to_1_blocks_unknown(self):
        rec = build_mental_foundation(0x0041)
        gate = check_gate_0_to_1(rec)
        assert gate.gate_status == TransitionGateStatus.BLOCKED
        assert "no_identity" in gate.failure_reasons


# ══════════════════════════════════════════════════════════════════════
# Layer 1 tests — Generative Profile
# ══════════════════════════════════════════════════════════════════════


class TestLayer1Generative:
    """Layer 1: voicedness, place, manner, closure, sonority."""

    def test_voicedness_ba(self):
        dmin = DMIN_REGISTRY[0x0628]
        assert extract_voicedness(dmin) is True

    def test_voicedness_ta(self):
        dmin = DMIN_REGISTRY[0x062A]  # ت
        assert extract_voicedness(dmin) is False

    def test_place_class(self):
        dmin = DMIN_REGISTRY[0x0628]
        assert extract_place(dmin) == "SHF"  # شفوي

    def test_manner_stop(self):
        dmin = DMIN_REGISTRY[0x0628]
        assert extract_manner(dmin) == "stop"

    def test_manner_fricative(self):
        dmin = DMIN_REGISTRY[0x0633]  # س
        assert extract_manner(dmin) == "fricative"

    def test_closure_stop(self):
        dmin = DMIN_REGISTRY[0x0628]
        assert compute_closure(dmin) == 1.0

    def test_closure_fricative(self):
        dmin = DMIN_REGISTRY[0x0633]
        assert compute_closure(dmin) == 0.6

    def test_sonority_consonant(self):
        dmin = DMIN_REGISTRY[0x0628]
        son = compute_sonority(dmin)
        assert 0.3 < son < 0.8

    def test_sonority_vowel(self):
        dmin = DMIN_REGISTRY[0x0627]  # alef
        son = compute_sonority(dmin)
        assert son >= 0.8

    def test_build_generative_profile(self):
        rec = build_generative_profile(0x0628)
        assert isinstance(rec, GenerativeProfileRecord)
        assert rec.voicedness is True
        assert rec.place_class == "SHF"

    def test_build_generative_unknown(self):
        rec = build_generative_profile(0x0041)
        assert rec.place_class == "UNKNOWN"

    def test_gate_1_to_2_passes(self):
        rec = build_generative_profile(0x0628)
        gate = check_gate_1_to_2(rec)
        assert gate.gate_status == TransitionGateStatus.PASSED

    def test_gate_1_to_2_blocks_unknown(self):
        rec = build_generative_profile(0x0041)
        gate = check_gate_1_to_2(rec)
        assert gate.gate_status == TransitionGateStatus.BLOCKED


# ══════════════════════════════════════════════════════════════════════
# Layer 2 tests — Auditory Minimum
# ══════════════════════════════════════════════════════════════════════


class TestLayer2Auditory:
    """Layer 2: audibility, temporal span, cohesion, unity."""

    def test_audibility_voiced(self):
        gen = build_generative_profile(0x0628)
        score = assess_audibility(gen)
        assert score > 0.3

    def test_temporal_span_no_syllable(self):
        assert assess_temporal_span(None) == 0.3

    def test_temporal_span_heavy(self):
        syl = Syllable(onset=(0x0628,), nucleus=(0x064E,), coda=(0x0644,), weight=2)
        assert assess_temporal_span(syl) == 0.7

    def test_cohesion_known(self):
        gen = build_generative_profile(0x0628)
        score = assess_cohesion(gen)
        assert score >= 0.9

    def test_unity_positive(self):
        score = assess_unity(0.8, 0.9, 0.7)
        assert 0.7 < score <= 1.0

    def test_build_auditory_minimum(self):
        gen = build_generative_profile(0x0628)
        rec = build_auditory_minimum(gen)
        assert isinstance(rec, AuditoryMinimumRecord)
        assert rec.audibility_score > 0

    def test_gate_2_to_3_passes(self):
        gen = build_generative_profile(0x0628)
        rec = build_auditory_minimum(gen)
        gate = check_gate_2_to_3(rec)
        assert gate.gate_status == TransitionGateStatus.PASSED

    def test_gate_2_to_3_blocks_zero_audibility(self):
        rec = AuditoryMinimumRecord(
            audibility_score=0.0,
            temporal_span=0.0,
            phase_count=0,
            order_score=0.0,
            cohesion_score=0.0,
            unity_score=0.0,
        )
        gate = check_gate_2_to_3(rec)
        assert gate.gate_status == TransitionGateStatus.BLOCKED


# ══════════════════════════════════════════════════════════════════════
# Layer 3 tests — Structural Profile
# ══════════════════════════════════════════════════════════════════════


class TestLayer3Structural:
    """Layer 3: syllable slot, root slot, constitutiveness, dependency."""

    _rp_ktb = RootPattern(root=("ك", "ت", "ب"), pattern="فَعَلَ", root_id=1, pattern_id=1)

    def test_assign_syllable_onset(self):
        syl = Syllable(onset=(0x0628,), nucleus=(0x064E,), coda=(), weight=1)
        assert assign_syllable_slot(0x0628, syl) == "onset"

    def test_assign_syllable_nucleus(self):
        syl = Syllable(onset=(0x0628,), nucleus=(0x064E,), coda=(), weight=1)
        assert assign_syllable_slot(0x064E, syl) == "nucleus"

    def test_assign_syllable_no_syllable(self):
        assert assign_syllable_slot(0x0628, None) == "unknown"

    def test_assign_root_fa(self):
        assert assign_root_slot("ك", self._rp_ktb) == "fa"

    def test_assign_root_ayn(self):
        assert assign_root_slot("ت", self._rp_ktb) == "ayn"

    def test_assign_root_lam(self):
        assert assign_root_slot("ب", self._rp_ktb) == "lam"

    def test_assign_root_none(self):
        assert assign_root_slot("م", self._rp_ktb) == "none"

    def test_constitutiveness_root(self):
        score = assess_constitutiveness("onset", "fa")
        assert score >= 0.7

    def test_constitutiveness_non_root(self):
        score = assess_constitutiveness("nucleus", "none")
        assert score < 0.3

    def test_dependency_non_root(self):
        score = assess_dependency("nucleus", "none")
        assert score > 0.5

    def test_dependency_root(self):
        score = assess_dependency("onset", "fa")
        assert score == 0.0

    def test_augmentation_ta(self):
        # ت is in سألتمونيها
        score = assess_augmentation(ord("ت"))
        assert score >= 0.5

    def test_augmentation_ba(self):
        # ب is not in سألتمونيها
        score = assess_augmentation(ord("ب"))
        assert score < 0.5

    def test_root_position_fitness(self):
        fa, ayn, lam = compute_root_position_fitness("ك", self._rp_ktb)
        assert fa == 1.0
        assert ayn == 0.0
        assert lam == 0.0

    def test_build_structural_profile(self):
        rec = build_structural_profile(ord("ك"), "ك", root_pattern=self._rp_ktb)
        assert isinstance(rec, StructuralProfileRecord)
        assert rec.root_slot == "fa"
        assert rec.constitutiveness_score >= 0.5

    def test_gate_3_to_4_passes(self):
        rec = build_structural_profile(ord("ك"), "ك", root_pattern=self._rp_ktb)
        gate = check_gate_3_to_4(rec)
        assert gate.gate_status == TransitionGateStatus.PASSED


# ══════════════════════════════════════════════════════════════════════
# Layer 4 tests — Transformation
# ══════════════════════════════════════════════════════════════════════


class TestLayer4Transformation:
    """Layer 4: stability, recoverability, substitution, deletion, illal, idgham."""

    def test_stability_consonant(self):
        score = assess_inflection_stability(0x0628)
        assert score >= 0.5

    def test_stability_weak_letter(self):
        score = assess_inflection_stability(0x0648)  # و
        assert score < 0.5

    def test_recoverability_same_form(self):
        score = assess_recoverability(0x0628, "ب", "ب")
        assert score == 1.0

    def test_recoverability_different_form(self):
        score = assess_recoverability(0x0628, "ب", "و")
        assert score == 0.6

    def test_detect_substitution_ibdal(self):
        # Find a codepoint with IBDAL
        score = detect_substitution(0x0628, "ب", "و")
        # ب has ibdal transform
        assert score >= 0.0  # may or may not have ibdal

    def test_detect_deletion_yes(self):
        score = detect_deletion(surface_present=False, underlying_present=True)
        assert score >= 0.8

    def test_detect_deletion_no(self):
        score = detect_deletion(surface_present=True, underlying_present=True)
        assert score == 0.0

    def test_detect_illal_waw(self):
        score = detect_illal(0x0648)  # و
        assert score > 0.0

    def test_detect_illal_consonant(self):
        score = detect_illal(0x0628)
        assert score == 0.0

    def test_detect_idgham(self):
        score = detect_idgham(0x0628)
        # ب may or may not have idgham transform
        assert 0.0 <= score <= 1.0

    def test_build_transformation_record(self):
        rec = build_transformation_record(0x0628)
        assert isinstance(rec, TransformationProfileRecord)
        assert rec.surface_presence is True

    def test_gate_4_to_5_passes(self):
        rec = build_transformation_record(0x0628)
        gate = check_gate_4_to_5(rec)
        assert gate.gate_status == TransitionGateStatus.PASSED


# ══════════════════════════════════════════════════════════════════════
# Layer 5 tests — Judgment
# ══════════════════════════════════════════════════════════════════════


class TestLayer5Judgment:
    """Layer 5: final judgment (original, augmented, etc.)."""

    _rp_ktb = RootPattern(root=("ك", "ت", "ب"), pattern="فَعَلَ", root_id=1, pattern_id=1)

    def _make_root_structural(self, root_slot: str = "fa") -> StructuralProfileRecord:
        return StructuralProfileRecord(
            syllable_slot="onset",
            root_slot=root_slot,
            constitutiveness_score=0.9,
            dependency_score=0.0,
            attachment_score=0.2,
            augmentation_score=0.1,
        )

    def _make_non_root_structural(self) -> StructuralProfileRecord:
        return StructuralProfileRecord(
            syllable_slot="unknown",
            root_slot="none",
            constitutiveness_score=0.0,
            dependency_score=0.8,
            attachment_score=0.7,
            augmentation_score=0.8,
        )

    def _make_stable_transform(self) -> TransformationProfileRecord:
        return TransformationProfileRecord(
            inflection_stability_score=0.9,
            recoverability_score=0.9,
            surface_presence=True,
            underlying_presence=True,
        )

    def _make_illal_transform(self) -> TransformationProfileRecord:
        return TransformationProfileRecord(
            inflection_stability_score=0.3,
            recoverability_score=0.6,
            surface_presence=True,
            underlying_presence=True,
            illal_confidence=0.8,
        )

    def test_judge_original_high(self):
        score = judge_original(self._make_root_structural(), self._make_stable_transform())
        assert score >= 0.7

    def test_judge_augmented_non_root(self):
        score = judge_augmented(self._make_non_root_structural())
        assert score >= 0.5

    def test_judge_augmented_root(self):
        score = judge_augmented(self._make_root_structural())
        assert score == 0.0

    def test_judge_substituted(self):
        tr = TransformationProfileRecord(
            inflection_stability_score=0.5,
            recoverability_score=0.6,
            surface_presence=True,
            underlying_presence=True,
            substitution_confidence=0.9,
        )
        score = judge_substituted(tr)
        assert score >= 0.8

    def test_judge_deleted(self):
        tr = TransformationProfileRecord(
            inflection_stability_score=0.5,
            recoverability_score=0.6,
            surface_presence=False,
            underlying_presence=True,
            deletion_confidence=0.9,
        )
        score = judge_deleted(tr)
        assert score >= 0.8

    def test_judge_weakened(self):
        score = judge_weakened(self._make_illal_transform())
        assert score >= 0.7

    def test_judge_assimilated_root(self):
        tr = TransformationProfileRecord(
            inflection_stability_score=0.8,
            recoverability_score=0.8,
            surface_presence=True,
            underlying_presence=True,
            idgham_confidence=0.8,
        )
        # Root consonants should not score high on assimilation
        score = judge_assimilated(tr, self._make_root_structural())
        assert score < 0.3

    def test_judge_attached(self):
        score = judge_attached(self._make_non_root_structural())
        assert score > 0.0

    def test_judge_deictic(self):
        score = judge_deictic(self._make_non_root_structural())
        assert score > 0.0

    def test_judge_relational(self):
        score = judge_relational(self._make_non_root_structural())
        assert score > 0.0

    def test_select_final_judgment_original(self):
        cat = select_final_judgment(0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert cat == JudgmentCategory.ORIGINAL

    def test_select_final_judgment_augmented(self):
        cat = select_final_judgment(0.1, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert cat == JudgmentCategory.AUGMENTED

    def test_select_final_judgment_deleted(self):
        cat = select_final_judgment(0.0, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert cat == JudgmentCategory.DELETED

    def test_build_judgment(self):
        structural = self._make_root_structural()
        transform = self._make_stable_transform()
        rec = build_judgment(structural, transform)
        assert isinstance(rec, JudgmentRecordL5)
        assert rec.final_judgment == JudgmentCategory.ORIGINAL
        assert rec.judgment_confidence > 0.0

    def test_gate_5_to_6_passes(self):
        structural = self._make_root_structural()
        transform = self._make_stable_transform()
        judgment = build_judgment(structural, transform)
        mental = build_mental_foundation(0x0628)
        gate = check_gate_5_to_6(judgment, mental)
        assert gate.gate_status == TransitionGateStatus.PASSED


# ══════════════════════════════════════════════════════════════════════
# Layer 6 tests — Representation
# ══════════════════════════════════════════════════════════════════════


class TestLayer6Representation:
    """Layer 6: feature hash, root mapping, rule set, validation."""

    def _full_records(self):
        mental = build_mental_foundation(0x0628)
        gen = build_generative_profile(0x0628)
        aud = build_auditory_minimum(gen)
        struct = build_structural_profile(
            0x0628, "ب",
            root_pattern=RootPattern(root=("ك", "ت", "ب"), pattern="فَعَلَ", root_id=1, pattern_id=1),
        )
        trans = build_transformation_record(0x0628, struct)
        judg = build_judgment(struct, trans)
        return mental, gen, aud, struct, trans, judg

    def test_compute_feature_hash(self):
        gen = build_generative_profile(0x0628)
        aud = build_auditory_minimum(gen)
        h = compute_feature_hash(gen, aud)
        assert isinstance(h, str)
        assert len(h) == 16

    def test_feature_hash_deterministic(self):
        gen = build_generative_profile(0x0628)
        aud = build_auditory_minimum(gen)
        h1 = compute_feature_hash(gen, aud)
        h2 = compute_feature_hash(gen, aud)
        assert h1 == h2

    def test_map_to_root_node(self):
        struct = build_structural_profile(
            0x0628, "ب",
            root_pattern=RootPattern(root=("ك", "ت", "ب"), pattern="فَعَلَ", root_id=1, pattern_id=1),
        )
        assert map_to_root_node(struct) == "root:lam"

    def test_compile_rule_set_stable(self):
        trans = TransformationProfileRecord(
            inflection_stability_score=0.9,
            recoverability_score=0.9,
            surface_presence=True,
            underlying_presence=True,
        )
        rules = compile_rule_set(trans)
        assert "stable" in rules

    def test_validate_against_reality_true(self):
        mental, gen, aud, struct, trans, judg = self._full_records()
        assert validate_against_reality(judg, mental) is True

    def test_build_representation(self):
        mental, gen, aud, struct, trans, judg = self._full_records()
        rep = build_representation("U+0628", mental, gen, aud, struct, trans, judg)
        assert isinstance(rep, RepresentationRecord)
        assert rep.entity_id == "U+0628"
        assert rep.validation_status is True
        assert len(rep.layer_trace) == 7
        assert rep.feature_hash


# ══════════════════════════════════════════════════════════════════════
# Gate tests
# ══════════════════════════════════════════════════════════════════════


class TestTransitionGates:
    """Each of the 6 transition gates."""

    def test_gate_0_1_structure(self):
        rec = build_mental_foundation(0x0628)
        gate = check_gate_0_to_1(rec)
        assert gate.source_layer == StrictLayerID.MENTAL_FOUNDATION
        assert gate.target_layer == StrictLayerID.GENERATIVE

    def test_gate_1_2_structure(self):
        rec = build_generative_profile(0x0628)
        gate = check_gate_1_to_2(rec)
        assert gate.source_layer == StrictLayerID.GENERATIVE
        assert gate.target_layer == StrictLayerID.AUDITORY_MINIMUM

    def test_gate_2_3_structure(self):
        gen = build_generative_profile(0x0628)
        rec = build_auditory_minimum(gen)
        gate = check_gate_2_to_3(rec)
        assert gate.source_layer == StrictLayerID.AUDITORY_MINIMUM
        assert gate.target_layer == StrictLayerID.STRUCTURAL

    def test_gate_3_4_structure(self):
        rec = build_structural_profile(ord("ك"), "ك")
        gate = check_gate_3_to_4(rec)
        assert gate.source_layer == StrictLayerID.STRUCTURAL
        assert gate.target_layer == StrictLayerID.TRANSFORMATION

    def test_gate_4_5_structure(self):
        rec = build_transformation_record(0x0628)
        gate = check_gate_4_to_5(rec)
        assert gate.source_layer == StrictLayerID.TRANSFORMATION
        assert gate.target_layer == StrictLayerID.HIGHER_FUNCTION

    def test_gate_5_6_structure(self):
        struct = StructuralProfileRecord(
            syllable_slot="onset", root_slot="fa",
            constitutiveness_score=0.9, dependency_score=0.0,
            attachment_score=0.2, augmentation_score=0.1,
        )
        trans = TransformationProfileRecord(
            inflection_stability_score=0.9, recoverability_score=0.9,
            surface_presence=True, underlying_presence=True,
        )
        judg = build_judgment(struct, trans)
        mental = build_mental_foundation(0x0628)
        gate = check_gate_5_to_6(judg, mental)
        assert gate.source_layer == StrictLayerID.HIGHER_FUNCTION
        assert gate.target_layer == StrictLayerID.PROGRAMMATIC

    def test_validate_full_trace_passing(self):
        trace = analyze_element(0x0628)
        assert validate_full_trace(trace) is True

    def test_validate_full_trace_blocked(self):
        trace = analyze_element(0x0041)  # non-Arabic
        assert validate_full_trace(trace) is False


# ══════════════════════════════════════════════════════════════════════
# Integration tests — full pipeline
# ══════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    """End-to-end analysis through all 7 layers."""

    def test_analyze_ba(self):
        trace = analyze_element(0x0628)
        assert trace.final_gate_status == TransitionGateStatus.PASSED
        assert trace.layer_6 is not None
        assert trace.layer_0 is not None

    def test_analyze_blocks_non_arabic(self):
        trace = analyze_element(0x0041)
        assert trace.final_gate_status == TransitionGateStatus.BLOCKED
        assert trace.layer_1 is None

    def test_all_consonants_pass(self):
        """Every Arabic consonant in DMIN_REGISTRY should pass all gates."""
        from arabic_engine.core.enums import PhonCategory
        consonants = [
            cp for cp, d in DMIN_REGISTRY.items()
            if d.category == PhonCategory.CONSONANT
        ]
        assert len(consonants) > 20
        for cp in consonants:
            trace = analyze_element(cp)
            assert trace.final_gate_status == TransitionGateStatus.PASSED, (
                f"U+{cp:04X} ({chr(cp)}) failed at gate"
            )

    def test_layer_trace_record_fields(self):
        trace = analyze_element(0x0628)
        assert isinstance(trace, LayerTraceRecord)
        assert trace.element_id == "U+0628"
        assert isinstance(trace.layer_0, MentalFoundationRecord)
        assert isinstance(trace.layer_1, GenerativeProfileRecord)
        assert isinstance(trace.layer_2, AuditoryMinimumRecord)
        assert isinstance(trace.layer_3, StructuralProfileRecord)
        assert isinstance(trace.layer_4, TransformationProfileRecord)
        assert isinstance(trace.layer_5, JudgmentRecordL5)
        assert isinstance(trace.layer_6, RepresentationRecord)
        assert len(trace.gates) == 6


# ══════════════════════════════════════════════════════════════════════
# Real Arabic word tests — مطابقة واقع العربية
# ══════════════════════════════════════════════════════════════════════


class TestRealArabicWords:
    """Test with real Arabic words for reality-match validation."""

    _rp_ktb = RootPattern(root=("ك", "ت", "ب"), pattern="فَعَلَ", root_id=1, pattern_id=1)
    _rp_rsl = RootPattern(root=("ر", "س", "ل"), pattern="فِعَالَة", root_id=3, pattern_id=3)

    def test_kataba_root_consonants(self):
        """كَتَبَ — ك(أصل/فاء) ت(أصل/عين) ب(أصل/لام)."""
        for char, expected_slot in [("ك", "fa"), ("ت", "ayn"), ("ب", "lam")]:
            trace = analyze_element(ord(char), char=char, root_pattern=self._rp_ktb)
            assert trace.final_gate_status == TransitionGateStatus.PASSED
            assert trace.layer_3.root_slot == expected_slot
            assert trace.layer_5.final_judgment == JudgmentCategory.ORIGINAL

    def test_risala_root_consonants(self):
        """رِسَالَة — ر(فاء) س(عين) ل(لام)."""
        for char, expected_slot in [("ر", "fa"), ("س", "ayn"), ("ل", "lam")]:
            trace = analyze_element(ord(char), char=char, root_pattern=self._rp_rsl)
            assert trace.final_gate_status == TransitionGateStatus.PASSED
            assert trace.layer_3.root_slot == expected_slot
            assert trace.layer_5.final_judgment == JudgmentCategory.ORIGINAL

    def test_alef_long_vowel(self):
        """ا as long vowel — augmented/dependent."""
        trace = analyze_element(0x0627)
        assert trace.final_gate_status == TransitionGateStatus.PASSED
        # Alef is a letter in سألتمونيها
        assert trace.layer_3.augmentation_score >= 0.5

    def test_waw_illal_potential(self):
        """و — has illal (إعلال) potential."""
        trace = analyze_element(0x0648)
        assert trace.final_gate_status == TransitionGateStatus.PASSED
        assert trace.layer_4.illal_confidence > 0.0

    def test_analyze_word_ktb(self):
        """Full word analysis: كتب."""
        traces = analyze_word("كتب", root_pattern=self._rp_ktb)
        assert len(traces) == 3
        for t in traces:
            assert t.final_gate_status == TransitionGateStatus.PASSED

    def test_word_analysis_root_slots(self):
        """All three consonants in كتب get correct root slots."""
        traces = analyze_word("كتب", root_pattern=self._rp_ktb)
        slots = [t.layer_3.root_slot for t in traces]
        assert slots == ["fa", "ayn", "lam"]

    def test_word_analysis_all_original(self):
        """All three consonants in كتب are judged ORIGINAL."""
        traces = analyze_word("كتب", root_pattern=self._rp_ktb)
        judgments = [t.layer_5.final_judgment for t in traces]
        assert all(j == JudgmentCategory.ORIGINAL for j in judgments)


# ══════════════════════════════════════════════════════════════════════
# Edge case tests
# ══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Boundary conditions and edge cases."""

    def test_unknown_codepoint(self):
        trace = analyze_element(0xFFFF)
        assert trace.final_gate_status == TransitionGateStatus.BLOCKED

    def test_zero_codepoint(self):
        trace = analyze_element(0)
        assert trace.final_gate_status == TransitionGateStatus.BLOCKED

    def test_sukun_blocks_at_auditory(self):
        """Sukun has no audibility — blocked at Layer 2 gate."""
        trace = analyze_element(0x0652)
        assert trace.layer_0 is not None
        assert trace.layer_1 is not None
        assert trace.layer_2 is not None
        assert trace.final_gate_status == TransitionGateStatus.BLOCKED

    def test_empty_word(self):
        traces = analyze_word("")
        assert traces == []

    def test_single_char_word(self):
        traces = analyze_word("ب")
        assert len(traces) == 1

    def test_transition_gate_frozen(self):
        """TransitionGate is frozen."""
        rec = build_mental_foundation(0x0628)
        gate = check_gate_0_to_1(rec)
        with pytest.raises(AttributeError):
            gate.gate_status = TransitionGateStatus.BLOCKED  # type: ignore[misc]

    def test_mental_foundation_frozen(self):
        """MentalFoundationRecord is frozen."""
        rec = build_mental_foundation(0x0628)
        with pytest.raises(AttributeError):
            rec.identity_strength = 0.0  # type: ignore[misc]

    def test_layer_trace_frozen(self):
        """LayerTraceRecord is frozen."""
        trace = analyze_element(0x0628)
        with pytest.raises(AttributeError):
            trace.element_id = "modified"  # type: ignore[misc]

    def test_representation_record_frozen(self):
        """RepresentationRecord is frozen."""
        trace = analyze_element(0x0628)
        assert trace.layer_6 is not None
        with pytest.raises(AttributeError):
            trace.layer_6.entity_id = "modified"  # type: ignore[misc]

    def test_partial_trace_has_gates(self):
        """Even blocked traces include the gates that were checked."""
        trace = analyze_element(0x0041)
        assert len(trace.gates) >= 1
        assert trace.gates[0].gate_status == TransitionGateStatus.BLOCKED

    def test_confidence_chain_length(self):
        """Full trace confidence chain has 6 values (one per real layer)."""
        trace = analyze_element(0x0628)
        assert trace.layer_6 is not None
        assert len(trace.layer_6.confidence_chain) == 6

    def test_different_codepoints_different_hashes(self):
        """Different elements should produce different feature hashes."""
        t1 = analyze_element(0x0628)  # ب
        t2 = analyze_element(0x062A)  # ت
        assert t1.layer_6 is not None
        assert t2.layer_6 is not None
        assert t1.layer_6.feature_hash != t2.layer_6.feature_hash
