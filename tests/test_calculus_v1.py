"""Tests for the Axiomatic Arabic Structural Calculus v1.

Covers:
  * New enums: OntologicalMode, TriadType, RankType
  * New types: StructuralSlot, VocalicZero, TriadRecord, RankDecision
  * Five laws: Rank, Decision, Limit/Capacity, Prior Constraint, Promotion
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    ConditionToken,
    OntologicalLayer,
    OntologicalMode,
    RankType,
    TriadType,
)
from arabic_engine.core.laws import (
    apply_decision_rule,
    check_rank_comparable,
    classify_rank,
    has_interpretation,
    next_promotion_layer,
    validate_triad_typed,
)
from arabic_engine.core.types import (
    RankDecision,
    StructuralSlot,
    TriadRecord,
    VocalicZero,
)

# ═══════════════════════════════════════════════════════════════════════
# New Enums
# ═══════════════════════════════════════════════════════════════════════

class TestOntologicalMode:
    def test_has_six_members(self):
        assert len(OntologicalMode) == 6

    def test_all_values(self):
        expected = {"SLOT", "UNIT", "MODIFIER", "COMPOSITE", "STRUCTURE", "CONSTRAINT"}
        assert {m.name for m in OntologicalMode} == expected


class TestTriadType:
    def test_has_three_members(self):
        assert len(TriadType) == 3

    def test_all_values(self):
        expected = {"DISTINCTIVE", "HIERARCHICAL", "GENERATIVE"}
        assert {t.name for t in TriadType} == expected


class TestRankType:
    def test_has_three_members(self):
        assert len(RankType) == 3

    def test_all_values(self):
        expected = {"LIMITAL", "CAPACITIVE", "TRANSITIONAL"}
        assert {r.name for r in RankType} == expected


# ═══════════════════════════════════════════════════════════════════════
# StructuralSlot
# ═══════════════════════════════════════════════════════════════════════

class TestStructuralSlotConstruction:
    def test_create_empty_slot(self):
        s = StructuralSlot(
            slot_id="SS_001",
            label="structural zero",
            layer=OntologicalLayer.CELL,
        )
        assert s.slot_id == "SS_001"
        assert s.mode is OntologicalMode.SLOT
        assert s.fillable is True
        assert s.is_empty is True

    def test_create_occupied_slot(self):
        s = StructuralSlot(
            slot_id="SS_002",
            label="filled slot",
            layer=OntologicalLayer.CELL,
            occupant_id="AE_001",
        )
        assert s.is_occupied is True
        assert s.is_empty is False

    def test_frozen(self):
        s = StructuralSlot(slot_id="SS_003", label="x", layer=OntologicalLayer.CELL)
        with pytest.raises((AttributeError, TypeError)):
            s.fillable = False  # type: ignore[misc]

    def test_with_constraint(self):
        s = StructuralSlot(
            slot_id="SS_004",
            label="constrained",
            layer=OntologicalLayer.SYLLABLE,
            constraint=ConditionToken.DEEP_STRUCTURE_PRESERVED,
        )
        assert s.constraint is ConditionToken.DEEP_STRUCTURE_PRESERVED

    def test_mode_always_slot(self):
        s = StructuralSlot(slot_id="SS_005", label="x", layer=OntologicalLayer.CELL)
        assert s.mode is OntologicalMode.SLOT


# ═══════════════════════════════════════════════════════════════════════
# VocalicZero
# ═══════════════════════════════════════════════════════════════════════

class TestVocalicZeroConstruction:
    def test_create(self):
        v = VocalicZero(zero_id="VZ_001", host_slot_id="SS_001")
        assert v.zero_id == "VZ_001"
        assert v.host_slot_id == "SS_001"
        assert v.mode is OntologicalMode.MODIFIER
        assert v.layer is OntologicalLayer.CELL

    def test_is_not_structural_zero(self):
        v = VocalicZero(zero_id="VZ_002", host_slot_id="SS_001")
        assert v.is_structural_zero is False

    def test_is_vocalic_zero(self):
        v = VocalicZero(zero_id="VZ_003", host_slot_id="SS_001")
        assert v.is_vocalic_zero is True

    def test_frozen(self):
        v = VocalicZero(zero_id="VZ_004", host_slot_id="SS_001")
        with pytest.raises((AttributeError, TypeError)):
            v.explicit = False  # type: ignore[misc]

    def test_explicit_default(self):
        v = VocalicZero(zero_id="VZ_005", host_slot_id="SS_001")
        assert v.explicit is True

    def test_implicit_sukun(self):
        v = VocalicZero(zero_id="VZ_006", host_slot_id="SS_001", explicit=False)
        assert v.explicit is False


# ═══════════════════════════════════════════════════════════════════════
# TriadRecord
# ═══════════════════════════════════════════════════════════════════════

class TestTriadRecordConstruction:
    def test_create_distinctive(self):
        t = TriadRecord(
            triad_id="TD_001",
            triad_type=TriadType.DISTINCTIVE,
            node_a="prev",
            node_b="center",
            node_c="next",
        )
        assert t.triad_type is TriadType.DISTINCTIVE
        assert t.members == ("prev", "center", "next")

    def test_create_hierarchical(self):
        t = TriadRecord(
            triad_id="TD_002",
            triad_type=TriadType.HIERARCHICAL,
            node_a="apex",
            node_b="left",
            node_c="right",
        )
        assert t.triad_type is TriadType.HIERARCHICAL

    def test_create_generative(self):
        t = TriadRecord(
            triad_id="TD_003",
            triad_type=TriadType.GENERATIVE,
            node_a="base",
            node_b="motion",
            node_c="constraint",
        )
        assert t.triad_type is TriadType.GENERATIVE

    def test_non_degenerate(self):
        t = TriadRecord(
            triad_id="TD_004",
            triad_type=TriadType.DISTINCTIVE,
            node_a="A", node_b="B", node_c="C",
        )
        assert t.is_degenerate is False

    def test_degenerate_ab(self):
        t = TriadRecord(
            triad_id="TD_005",
            triad_type=TriadType.DISTINCTIVE,
            node_a="X", node_b="X", node_c="Y",
        )
        assert t.is_degenerate is True

    def test_degenerate_ac(self):
        t = TriadRecord(
            triad_id="TD_006",
            triad_type=TriadType.DISTINCTIVE,
            node_a="X", node_b="Y", node_c="X",
        )
        assert t.is_degenerate is True

    def test_degenerate_bc(self):
        t = TriadRecord(
            triad_id="TD_007",
            triad_type=TriadType.DISTINCTIVE,
            node_a="Z", node_b="X", node_c="X",
        )
        assert t.is_degenerate is True

    def test_has_decision_rule_false(self):
        t = TriadRecord(
            triad_id="TD_008",
            triad_type=TriadType.GENERATIVE,
            node_a="A", node_b="B", node_c="C",
        )
        assert t.has_decision_rule is False

    def test_has_decision_rule_true(self):
        t = TriadRecord(
            triad_id="TD_009",
            triad_type=TriadType.GENERATIVE,
            node_a="A", node_b="B", node_c="C",
            decision_rule="J_phonological",
        )
        assert t.has_decision_rule is True

    def test_frozen(self):
        t = TriadRecord(
            triad_id="TD_010",
            triad_type=TriadType.DISTINCTIVE,
            node_a="A", node_b="B", node_c="C",
        )
        with pytest.raises((AttributeError, TypeError)):
            t.triad_type = TriadType.HIERARCHICAL  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# RankDecision
# ═══════════════════════════════════════════════════════════════════════

class TestRankDecisionConstruction:
    def test_create_limital(self):
        r = RankDecision(
            decision_id="RD_001",
            element_id="AE_001",
            limit_score=0.9,
            capacity_score=0.2,
            rank_type=RankType.LIMITAL,
        )
        assert r.is_limital is True
        assert r.is_capacitive is False
        assert r.is_transitional is False

    def test_create_capacitive(self):
        r = RankDecision(
            decision_id="RD_002",
            element_id="AE_002",
            limit_score=0.1,
            capacity_score=0.8,
            rank_type=RankType.CAPACITIVE,
        )
        assert r.is_capacitive is True

    def test_create_transitional(self):
        r = RankDecision(
            decision_id="RD_003",
            element_id="AE_003",
            limit_score=0.5,
            capacity_score=0.5,
            rank_type=RankType.TRANSITIONAL,
        )
        assert r.is_transitional is True

    def test_has_interpretation_default(self):
        r = RankDecision(
            decision_id="RD_004",
            element_id="AE_004",
            limit_score=0.5,
            capacity_score=0.5,
            rank_type=RankType.TRANSITIONAL,
        )
        assert r.has_interpretation is True  # omega defaults to 1.0

    def test_no_interpretation_when_omega_zero(self):
        r = RankDecision(
            decision_id="RD_005",
            element_id="AE_005",
            limit_score=0.5,
            capacity_score=0.5,
            rank_type=RankType.TRANSITIONAL,
            omega=0.0,
        )
        assert r.has_interpretation is False

    def test_requires_promotion_false(self):
        r = RankDecision(
            decision_id="RD_006",
            element_id="AE_006",
            limit_score=0.5,
            capacity_score=0.5,
            rank_type=RankType.TRANSITIONAL,
        )
        assert r.requires_promotion is False

    def test_requires_promotion_true(self):
        r = RankDecision(
            decision_id="RD_007",
            element_id="AE_007",
            limit_score=0.5,
            capacity_score=0.5,
            rank_type=RankType.TRANSITIONAL,
            promotion_target=OntologicalLayer.SYLLABLE,
        )
        assert r.requires_promotion is True

    def test_frozen(self):
        r = RankDecision(
            decision_id="RD_008",
            element_id="AE_008",
            limit_score=0.5,
            capacity_score=0.5,
            rank_type=RankType.TRANSITIONAL,
        )
        with pytest.raises((AttributeError, TypeError)):
            r.rank_type = RankType.LIMITAL  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# Law 1 — Rank Law
# ═══════════════════════════════════════════════════════════════════════

class TestLaw1RankComparable:
    def test_same_mode_comparable(self):
        assert check_rank_comparable(OntologicalMode.UNIT, OntologicalMode.UNIT) is True

    def test_different_mode_not_comparable(self):
        assert check_rank_comparable(OntologicalMode.SLOT, OntologicalMode.UNIT) is False

    def test_slot_vs_modifier(self):
        assert check_rank_comparable(OntologicalMode.SLOT, OntologicalMode.MODIFIER) is False

    def test_composite_vs_structure(self):
        assert check_rank_comparable(OntologicalMode.COMPOSITE, OntologicalMode.STRUCTURE) is False

    def test_all_modes_self_comparable(self):
        for mode in OntologicalMode:
            assert check_rank_comparable(mode, mode) is True


# ═══════════════════════════════════════════════════════════════════════
# Law 2 — Description-to-Decision
# ═══════════════════════════════════════════════════════════════════════

class TestLaw2DecisionRule:
    def test_simple_transform(self):
        desc = {"weight": 3, "voiced": True}
        rules = {
            "weight": lambda w: "heavy" if w >= 2 else "light",
            "voiced": lambda v: "majhur" if v else "mahmous",
        }
        result = apply_decision_rule(desc, rules)
        assert result == {"weight": "heavy", "voiced": "majhur"}

    def test_empty_rule_set(self):
        result = apply_decision_rule({"a": 1}, {})
        assert result == {}

    def test_missing_key_raises(self):
        with pytest.raises(KeyError):
            apply_decision_rule({}, {"missing": lambda x: x})

    def test_single_rule(self):
        desc = {"economy": 0.8}
        rules = {"economy": lambda e: "high" if e > 0.5 else "low"}
        assert apply_decision_rule(desc, rules) == {"economy": "high"}


# ═══════════════════════════════════════════════════════════════════════
# Law 3 — Limit and Capacity
# ═══════════════════════════════════════════════════════════════════════

class TestLaw3ClassifyRank:
    def test_limital(self):
        assert classify_rank(0.9, 0.2) is RankType.LIMITAL

    def test_capacitive(self):
        assert classify_rank(0.1, 0.8) is RankType.CAPACITIVE

    def test_transitional_equal(self):
        assert classify_rank(0.5, 0.5) is RankType.TRANSITIONAL

    def test_transitional_within_threshold(self):
        assert classify_rank(0.5, 0.6, threshold=0.3) is RankType.TRANSITIONAL

    def test_custom_threshold(self):
        assert classify_rank(0.6, 0.5, threshold=0.05) is RankType.LIMITAL

    def test_zero_scores(self):
        assert classify_rank(0.0, 0.0) is RankType.TRANSITIONAL

    def test_daad_example(self):
        # ض — high limit (emphatic closure), low capacity
        assert classify_rank(0.85, 0.15) is RankType.LIMITAL

    def test_alif_example(self):
        # ا — low limit, high capacity (carrier)
        assert classify_rank(0.1, 0.9) is RankType.CAPACITIVE

    def test_waw_example(self):
        # و — balanced (semi-vowel / glide)
        assert classify_rank(0.45, 0.55) is RankType.TRANSITIONAL


# ═══════════════════════════════════════════════════════════════════════
# Law 4 — Prior Constraint
# ═══════════════════════════════════════════════════════════════════════

class TestLaw4PriorConstraint:
    def test_omega_zero_no_interpretation(self):
        assert has_interpretation(0.0) is False

    def test_omega_positive(self):
        assert has_interpretation(1.0) is True

    def test_omega_negative(self):
        assert has_interpretation(-0.5) is True

    def test_omega_small(self):
        assert has_interpretation(0.001) is True


# ═══════════════════════════════════════════════════════════════════════
# Law 5 — Layer Promotion
# ═══════════════════════════════════════════════════════════════════════

class TestLaw5LayerPromotion:
    def test_cell_promotes_to_transition(self):
        assert next_promotion_layer(OntologicalLayer.CELL) is OntologicalLayer.TRANSITION

    def test_transition_promotes_to_syllable(self):
        assert next_promotion_layer(OntologicalLayer.TRANSITION) is OntologicalLayer.SYLLABLE

    def test_syllable_promotes_to_root(self):
        assert next_promotion_layer(OntologicalLayer.SYLLABLE) is OntologicalLayer.ROOT

    def test_root_promotes_to_pattern(self):
        assert next_promotion_layer(OntologicalLayer.ROOT) is OntologicalLayer.PATTERN

    def test_pattern_is_top(self):
        assert next_promotion_layer(OntologicalLayer.PATTERN) is None

    def test_full_chain(self):
        layer = OntologicalLayer.CELL
        chain = [layer]
        while (next_layer := next_promotion_layer(layer)) is not None:
            chain.append(next_layer)
            layer = next_layer
        assert chain == list(OntologicalLayer)


# ═══════════════════════════════════════════════════════════════════════
# Triad Type Validation
# ═══════════════════════════════════════════════════════════════════════

class TestTriadTypeValidation:
    def test_valid_distinctive(self):
        assert validate_triad_typed(TriadType.DISTINCTIVE, "A", "B", "C") is True

    def test_valid_hierarchical(self):
        assert validate_triad_typed(TriadType.HIERARCHICAL, "apex", "left", "right") is True

    def test_valid_generative(self):
        assert validate_triad_typed(TriadType.GENERATIVE, "base", "motion", "constraint") is True

    def test_degenerate_fails(self):
        assert validate_triad_typed(TriadType.DISTINCTIVE, "A", "A", "B") is False

    def test_all_same_fails(self):
        assert validate_triad_typed(TriadType.DISTINCTIVE, "X", "X", "X") is False
