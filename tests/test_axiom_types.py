"""Tests for the axiom types: ZeroSlotRecord, TriadicBlockRecord, LayerPromotionRule.

Validates that the three new dataclasses faithfully encode axioms A1–A4:

    A1. ∃z (ZeroSlot(z) ∧ Fillable(z))
    A2. ∀z (ZeroSlot(z) ∧ Fillable(z) → ∃x Occupies(x,z))
    A3. CompleteDistinction(x,y) → ∃t ≠ x,y   (MinimalCompleteDistinction = 3)
    A4. Complete(x ∈ L_n) → RequiresHigherContext(x)
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    CellType,
    ConditionToken,
    OntologicalLayer,
    SlotState,
)
from arabic_engine.core.types import (
    LayerPromotionRule,
    TriadicBlockRecord,
    ZeroSlotRecord,
)

# ═══════════════════════════════════════════════════════════════════════
# ZeroSlotRecord — A1 / A2
# ═══════════════════════════════════════════════════════════════════════

class TestZeroSlotRecordConstruction:
    """Basic construction and field access."""

    def test_create_empty_slot(self):
        z = ZeroSlotRecord(
            slot_id="ZS_001",
            label="فتحة فارغة",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        assert z.slot_id == "ZS_001"
        assert z.state is SlotState.EMPTY
        assert z.layer is OntologicalLayer.CELL

    def test_create_occupied_slot(self):
        z = ZeroSlotRecord(
            slot_id="ZS_002",
            label="خانة مشغولة",
            state=SlotState.OCCUPIED,
            layer=OntologicalLayer.CELL,
            occupant_id="AE_002",
        )
        assert z.occupant_id == "AE_002"

    def test_defaults(self):
        z = ZeroSlotRecord(
            slot_id="ZS_003",
            label="test",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        assert z.occupant_id is None
        assert z.parent_cell is None
        assert z.constraint_token is None
        assert z.notes == ""

    def test_optional_fields(self):
        z = ZeroSlotRecord(
            slot_id="ZS_004",
            label="constrained slot",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.SYLLABLE,
            parent_cell=CellType.C_ROOT_PLAIN,
            constraint_token=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            notes="linked to root consonant",
        )
        assert z.parent_cell is CellType.C_ROOT_PLAIN
        assert z.constraint_token is ConditionToken.DEEP_STRUCTURE_PRESERVED

    def test_frozen(self):
        z = ZeroSlotRecord(
            slot_id="ZS_005",
            label="frozen",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        with pytest.raises((AttributeError, TypeError)):
            z.state = SlotState.OCCUPIED  # type: ignore[misc]


class TestZeroSlotRecordAxioms:
    """A1 / A2 / C1 / C2 — structural zero-slot semantics."""

    def test_a1_fillable_when_empty(self):
        z = ZeroSlotRecord(
            slot_id="ZS_A1", label="a1", state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        assert z.is_fillable is True

    def test_a1_fillable_when_occupied(self):
        z = ZeroSlotRecord(
            slot_id="ZS_A1b", label="a1b", state=SlotState.OCCUPIED,
            layer=OntologicalLayer.CELL, occupant_id="X",
        )
        assert z.is_fillable is True  # occupied is not blocked

    def test_a1_not_fillable_when_blocked(self):
        z = ZeroSlotRecord(
            slot_id="ZS_BLK", label="blocked", state=SlotState.BLOCKED,
            layer=OntologicalLayer.CELL,
        )
        assert z.is_fillable is False

    def test_a2_is_occupied(self):
        z = ZeroSlotRecord(
            slot_id="ZS_A2", label="a2", state=SlotState.OCCUPIED,
            layer=OntologicalLayer.CELL, occupant_id="AE_001",
        )
        assert z.is_occupied is True

    def test_a2_not_occupied_when_empty(self):
        z = ZeroSlotRecord(
            slot_id="ZS_A2b", label="a2b", state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        assert z.is_occupied is False

    def test_a2_not_occupied_without_occupant_id(self):
        z = ZeroSlotRecord(
            slot_id="ZS_A2c", label="a2c", state=SlotState.OCCUPIED,
            layer=OntologicalLayer.CELL,
        )
        assert z.is_occupied is False

    def test_c1_zero_is_empty_not_nothing(self):
        z = ZeroSlotRecord(
            slot_id="ZS_C1", label="c1", state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        assert z.is_zero is True
        assert z.is_fillable is True

    def test_c1_occupied_is_not_zero(self):
        z = ZeroSlotRecord(
            slot_id="ZS_C1b", label="c1b", state=SlotState.OCCUPIED,
            layer=OntologicalLayer.CELL, occupant_id="X",
        )
        assert z.is_zero is False


# ═══════════════════════════════════════════════════════════════════════
# TriadicBlockRecord — A3
# ═══════════════════════════════════════════════════════════════════════

class TestTriadicBlockRecordConstruction:
    """Basic construction and field access."""

    def test_create_block(self):
        b = TriadicBlockRecord(
            block_id="TB_001",
            apex="C_ROOT_PLAIN",
            left="D_FATHA",
            right="D_SUKUN",
            layer=OntologicalLayer.CELL,
        )
        assert b.block_id == "TB_001"
        assert b.apex == "C_ROOT_PLAIN"
        assert b.left == "D_FATHA"
        assert b.right == "D_SUKUN"

    def test_defaults(self):
        b = TriadicBlockRecord(
            block_id="TB_002",
            apex="A", left="B", right="C",
            layer=OntologicalLayer.TRANSITION,
        )
        assert b.complete is True
        assert b.governing_transition is None
        assert b.notes == ""

    def test_with_governing_transition(self):
        b = TriadicBlockRecord(
            block_id="TB_003",
            apex="apex", left="left", right="right",
            layer=OntologicalLayer.CELL,
            governing_transition="TR_001",
        )
        assert b.governing_transition == "TR_001"

    def test_frozen(self):
        b = TriadicBlockRecord(
            block_id="TB_004",
            apex="A", left="B", right="C",
            layer=OntologicalLayer.CELL,
        )
        with pytest.raises((AttributeError, TypeError)):
            b.apex = "X"  # type: ignore[misc]


class TestTriadicBlockRecordAxioms:
    """A3 / C3 — triadic distinction semantics."""

    def test_a3_members_triple(self):
        b = TriadicBlockRecord(
            block_id="TB_A3", apex="t", left="x", right="y",
            layer=OntologicalLayer.CELL,
        )
        assert b.members == ("t", "x", "y")
        assert len(b.members) == 3

    def test_a3_not_degenerate_when_all_distinct(self):
        b = TriadicBlockRecord(
            block_id="TB_OK", apex="A", left="B", right="C",
            layer=OntologicalLayer.CELL,
        )
        assert b.is_degenerate is False

    def test_a3_degenerate_when_apex_equals_left(self):
        b = TriadicBlockRecord(
            block_id="TB_DG1", apex="X", left="X", right="Y",
            layer=OntologicalLayer.CELL,
        )
        assert b.is_degenerate is True

    def test_a3_degenerate_when_apex_equals_right(self):
        b = TriadicBlockRecord(
            block_id="TB_DG2", apex="X", left="Y", right="X",
            layer=OntologicalLayer.CELL,
        )
        assert b.is_degenerate is True

    def test_a3_degenerate_when_left_equals_right(self):
        b = TriadicBlockRecord(
            block_id="TB_DG3", apex="Z", left="X", right="X",
            layer=OntologicalLayer.CELL,
        )
        assert b.is_degenerate is True

    def test_c3_incomplete_pair_is_degenerate(self):
        # A pair-only relation (left == right) yields incomplete rank judgment
        b = TriadicBlockRecord(
            block_id="TB_C3", apex="A", left="B", right="B",
            layer=OntologicalLayer.CELL, complete=False,
        )
        assert b.is_degenerate is True
        assert b.complete is False


# ═══════════════════════════════════════════════════════════════════════
# LayerPromotionRule — A4
# ═══════════════════════════════════════════════════════════════════════

class TestLayerPromotionRuleConstruction:
    """Basic construction and field access."""

    def test_create_rule(self):
        r = LayerPromotionRule(
            rule_id="LP_001",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            description="cell → transition promotion",
        )
        assert r.rule_id == "LP_001"
        assert r.source_layer is OntologicalLayer.CELL
        assert r.target_layer is OntologicalLayer.TRANSITION

    def test_defaults(self):
        r = LayerPromotionRule(
            rule_id="LP_002",
            source_layer=OntologicalLayer.TRANSITION,
            target_layer=OntologicalLayer.SYLLABLE,
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="transition → syllable",
        )
        assert r.requires_completeness is True
        assert r.notes == ""

    def test_frozen(self):
        r = LayerPromotionRule(
            rule_id="LP_003",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            description="frozen test",
        )
        with pytest.raises((AttributeError, TypeError)):
            r.source_layer = OntologicalLayer.SYLLABLE  # type: ignore[misc]


class TestLayerPromotionRuleAxioms:
    """A4 / C4 — layer promotion semantics."""

    def test_a4_valid_promotion_upward(self):
        r = LayerPromotionRule(
            rule_id="LP_A4a",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            description="valid promotion",
        )
        assert r.is_valid is True

    def test_a4_invalid_promotion_same_layer(self):
        r = LayerPromotionRule(
            rule_id="LP_A4b",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.CELL,
            condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            description="same layer — invalid",
        )
        assert r.is_valid is False

    def test_a4_invalid_promotion_downward(self):
        r = LayerPromotionRule(
            rule_id="LP_A4c",
            source_layer=OntologicalLayer.SYLLABLE,
            target_layer=OntologicalLayer.CELL,
            condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            description="downward — invalid",
        )
        assert r.is_valid is False

    def test_a4_layer_gap_one(self):
        r = LayerPromotionRule(
            rule_id="LP_GAP1",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
            description="gap=1",
        )
        assert r.layer_gap == 1

    def test_a4_layer_gap_multi(self):
        r = LayerPromotionRule(
            rule_id="LP_GAP3",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.ROOT,
            condition=ConditionToken.ROOT_SLOTS_IDENTIFIED_INDEPENDENTLY,
            description="cell → root (gap=3)",
        )
        assert r.layer_gap == 3

    def test_a4_full_chain_is_valid(self):
        """Verify the full ontological chain: cell → transition → syllable → root → pattern."""
        layers = list(OntologicalLayer)
        for i in range(len(layers) - 1):
            r = LayerPromotionRule(
                rule_id=f"LP_CHAIN_{i}",
                source_layer=layers[i],
                target_layer=layers[i + 1],
                condition=ConditionToken.DEEP_STRUCTURE_PRESERVED,
                description=f"{layers[i].name} → {layers[i+1].name}",
            )
            assert r.is_valid is True
            assert r.layer_gap == 1


# ═══════════════════════════════════════════════════════════════════════
# Enum tests — SlotState / OntologicalLayer
# ═══════════════════════════════════════════════════════════════════════

class TestNewEnums:
    def test_slot_state_has_three_members(self):
        assert len(SlotState) == 3

    def test_slot_state_values(self):
        assert SlotState.EMPTY in SlotState
        assert SlotState.OCCUPIED in SlotState
        assert SlotState.BLOCKED in SlotState

    def test_ontological_layer_has_five_members(self):
        assert len(OntologicalLayer) == 5

    def test_ontological_layer_order(self):
        layers = list(OntologicalLayer)
        assert layers[0] is OntologicalLayer.CELL
        assert layers[1] is OntologicalLayer.TRANSITION
        assert layers[2] is OntologicalLayer.SYLLABLE
        assert layers[3] is OntologicalLayer.ROOT
        assert layers[4] is OntologicalLayer.PATTERN

    def test_ontological_layer_ascending_values(self):
        layers = list(OntologicalLayer)
        for i in range(len(layers) - 1):
            assert layers[i].value < layers[i + 1].value
