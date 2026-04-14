"""Tests for core/calculus.py — الحساب البنيوي التأسيسي.

Week 2 acceptance criteria — the test passes iff:

    1. A zero-slot can be occupied → ``occupy_zero_slot``
    2. An essence–condition pair can be validated → ``validate``
    3. An element can be promoted between layers → ``promote``
    4. Three elements can be composed into a non-degenerate triad → ``compose``
    5. Inference can be invoked on a proposition → ``infer``
    6. The full chain ``slot → occupy → validate → promote → infer`` works

Transition condition:
    The end-to-end scenario at the bottom of this file must pass.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.calculus import (
    compose,
    infer,
    occupy_structural_slot,
    occupy_zero_slot,
    promote,
    validate,
)
from arabic_engine.core.enums import (
    ConditionToken,
    OntologicalLayer,
    SlotState,
    TriadType,
)
from arabic_engine.core.types import (
    EssenceConditionPair,
    LayerPromotionRule,
    StructuralSlot,
    ZeroSlotRecord,
)

# ═══════════════════════════════════════════════════════════════════════
# occupy_zero_slot
# ═══════════════════════════════════════════════════════════════════════


class TestOccupyZeroSlot:
    """Tests for ``occupy_zero_slot``."""

    def _empty_slot(self) -> ZeroSlotRecord:
        return ZeroSlotRecord(
            slot_id="ZS_T01",
            label="test-slot",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )

    def test_fill_empty_slot(self) -> None:
        slot = self._empty_slot()
        filled = occupy_zero_slot(slot, "ELEM_001")
        assert filled.state is SlotState.OCCUPIED
        assert filled.occupant_id == "ELEM_001"

    def test_original_unchanged(self) -> None:
        slot = self._empty_slot()
        occupy_zero_slot(slot, "ELEM_001")
        assert slot.state is SlotState.EMPTY
        assert slot.occupant_id is None

    def test_filled_is_fillable_true(self) -> None:
        """After occupation, is_fillable is still True because
        is_fillable means 'not BLOCKED', not 'can accept new occupant'."""
        slot = self._empty_slot()
        filled = occupy_zero_slot(slot, "ELEM_001")
        assert filled.is_occupied is True
        assert filled.is_fillable is True  # is_fillable means not BLOCKED

    def test_blocked_slot_raises(self) -> None:
        slot = ZeroSlotRecord(
            slot_id="ZS_BLK",
            label="blocked",
            state=SlotState.BLOCKED,
            layer=OntologicalLayer.CELL,
        )
        with pytest.raises(ValueError, match="BLOCKED"):
            occupy_zero_slot(slot, "ELEM_002")

    def test_already_occupied_raises(self) -> None:
        slot = self._empty_slot()
        filled = occupy_zero_slot(slot, "ELEM_001")
        with pytest.raises(ValueError, match="already OCCUPIED"):
            occupy_zero_slot(filled, "ELEM_002")

    def test_preserves_other_fields(self) -> None:
        slot = ZeroSlotRecord(
            slot_id="ZS_FULL",
            label="full-test",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.TRANSITION,
            notes="keep me",
        )
        filled = occupy_zero_slot(slot, "ELEM_003")
        assert filled.slot_id == "ZS_FULL"
        assert filled.label == "full-test"
        assert filled.layer is OntologicalLayer.TRANSITION
        assert filled.notes == "keep me"


# ═══════════════════════════════════════════════════════════════════════
# occupy_structural_slot
# ═══════════════════════════════════════════════════════════════════════


class TestOccupyStructuralSlot:
    """Tests for ``occupy_structural_slot``."""

    def _empty_slot(self) -> StructuralSlot:
        return StructuralSlot(
            slot_id="SS_T01",
            label="struct-test",
            layer=OntologicalLayer.CELL,
        )

    def test_fill_empty_slot(self) -> None:
        slot = self._empty_slot()
        filled = occupy_structural_slot(slot, "VAL_001")
        assert filled.is_occupied is True
        assert filled.occupant_id == "VAL_001"

    def test_not_fillable_raises(self) -> None:
        slot = StructuralSlot(
            slot_id="SS_NF",
            label="not-fillable",
            layer=OntologicalLayer.CELL,
            fillable=False,
        )
        with pytest.raises(ValueError, match="not fillable"):
            occupy_structural_slot(slot, "VAL_002")

    def test_already_occupied_raises(self) -> None:
        slot = self._empty_slot()
        filled = occupy_structural_slot(slot, "VAL_001")
        with pytest.raises(ValueError, match="already occupied"):
            occupy_structural_slot(filled, "VAL_002")


# ═══════════════════════════════════════════════════════════════════════
# validate
# ═══════════════════════════════════════════════════════════════════════


class TestValidate:
    """Tests for ``validate``."""

    def test_no_constraint_always_valid(self) -> None:
        pair = EssenceConditionPair(
            element_id="E001",
            slot="S1",
            value="V1",
        )
        assert validate(pair) is True

    def test_constraint_met(self) -> None:
        pair = EssenceConditionPair(
            element_id="E002",
            slot="S1",
            value="V1",
            constraint=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
        )
        ctx = frozenset({ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING})
        assert validate(pair, context_tokens=ctx) is True

    def test_constraint_not_met(self) -> None:
        pair = EssenceConditionPair(
            element_id="E003",
            slot="S1",
            value="V1",
            constraint=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
        )
        ctx = frozenset({ConditionToken.COMPRESSION_ALLOWED})
        assert validate(pair, context_tokens=ctx) is False

    def test_constraint_no_context(self) -> None:
        pair = EssenceConditionPair(
            element_id="E004",
            slot="S1",
            value="V1",
            constraint=ConditionToken.COMPRESSION_ALLOWED,
        )
        assert validate(pair) is False  # no context provided

    def test_constraint_empty_context(self) -> None:
        pair = EssenceConditionPair(
            element_id="E005",
            slot="S1",
            value="V1",
            constraint=ConditionToken.COMPRESSION_ALLOWED,
        )
        assert validate(pair, context_tokens=frozenset()) is False


# ═══════════════════════════════════════════════════════════════════════
# promote
# ═══════════════════════════════════════════════════════════════════════


class TestPromote:
    """Tests for ``promote``."""

    def test_cell_to_transition(self) -> None:
        rule = LayerPromotionRule(
            rule_id="LP_001",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="CELL → TRANSITION",
        )
        result = promote(OntologicalLayer.CELL, rule)
        assert result is OntologicalLayer.TRANSITION

    def test_transition_to_syllable(self) -> None:
        rule = LayerPromotionRule(
            rule_id="LP_002",
            source_layer=OntologicalLayer.TRANSITION,
            target_layer=OntologicalLayer.SYLLABLE,
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="TRANSITION → SYLLABLE",
        )
        result = promote(OntologicalLayer.TRANSITION, rule)
        assert result is OntologicalLayer.SYLLABLE

    def test_full_promotion_chain(self) -> None:
        """CELL → TRANSITION → SYLLABLE → ROOT → PATTERN."""
        layers = list(OntologicalLayer)
        current = layers[0]  # CELL
        for i in range(len(layers) - 1):
            rule = LayerPromotionRule(
                rule_id=f"LP_{i+1:03d}",
                source_layer=layers[i],
                target_layer=layers[i + 1],
                condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
                description=f"{layers[i].name} → {layers[i+1].name}",
            )
            current = promote(current, rule)
        assert current is OntologicalLayer.PATTERN

    def test_wrong_source_raises(self) -> None:
        rule = LayerPromotionRule(
            rule_id="LP_BAD",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="CELL → TRANSITION",
        )
        with pytest.raises(ValueError, match="does not match"):
            promote(OntologicalLayer.SYLLABLE, rule)

    def test_invalid_rule_raises(self) -> None:
        rule = LayerPromotionRule(
            rule_id="LP_INV",
            source_layer=OntologicalLayer.SYLLABLE,
            target_layer=OntologicalLayer.CELL,  # downward = invalid
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="invalid",
        )
        with pytest.raises(ValueError, match="invalid"):
            promote(OntologicalLayer.SYLLABLE, rule)


# ═══════════════════════════════════════════════════════════════════════
# compose
# ═══════════════════════════════════════════════════════════════════════


class TestCompose:
    """Tests for ``compose``."""

    def test_basic_composition(self) -> None:
        triad = compose("slot_1", "value_1", "constraint_1")
        assert triad.node_a == "slot_1"
        assert triad.node_b == "value_1"
        assert triad.node_c == "constraint_1"

    def test_non_degenerate(self) -> None:
        triad = compose("A", "B", "C")
        assert triad.is_degenerate is False

    def test_degenerate_raises(self) -> None:
        with pytest.raises(ValueError, match="Degenerate"):
            compose("A", "A", "B")

    def test_all_same_raises(self) -> None:
        with pytest.raises(ValueError, match="Degenerate"):
            compose("X", "X", "X")

    def test_custom_type(self) -> None:
        triad = compose(
            "apex", "left", "right",
            triad_type=TriadType.HIERARCHICAL,
        )
        assert triad.triad_type is TriadType.HIERARCHICAL

    def test_custom_layer(self) -> None:
        triad = compose(
            "A", "B", "C",
            layer=OntologicalLayer.ROOT,
        )
        assert triad.layer is OntologicalLayer.ROOT

    def test_members_property(self) -> None:
        triad = compose("A", "B", "C")
        assert triad.members == ("A", "B", "C")


# ═══════════════════════════════════════════════════════════════════════
# infer
# ═══════════════════════════════════════════════════════════════════════


class TestInfer:
    """Tests for ``infer``."""

    def test_with_mock_engine(self) -> None:
        class MockEngine:
            def run(self, propositions):
                return [{"derived": True}]

        results = infer([], MockEngine())
        assert len(results) == 1
        assert results[0]["derived"] is True

    def test_engine_without_run_raises(self) -> None:
        with pytest.raises(TypeError, match="run"):
            infer([], object())  # type: ignore[arg-type]

    def test_empty_result(self) -> None:
        class EmptyEngine:
            def run(self, propositions):
                return []

        assert infer([], EmptyEngine()) == []


# ═══════════════════════════════════════════════════════════════════════
# End-to-end scenario — شرط الانتقال
# ═══════════════════════════════════════════════════════════════════════


class TestEndToEndScenario:
    """Full chain: slot → occupy → validate → promote → compose → infer.

    This is the Week 2 transition condition: this test MUST pass before
    proceeding to Week 3.
    """

    def test_full_chain(self) -> None:
        # 1. Create an empty zero-slot
        slot = ZeroSlotRecord(
            slot_id="ZS_E2E",
            label="end-to-end slot",
            state=SlotState.EMPTY,
            layer=OntologicalLayer.CELL,
        )
        assert slot.is_zero

        # 2. Occupy the slot (A2)
        filled = occupy_zero_slot(slot, "LETTER_BA")
        assert filled.is_occupied
        assert filled.occupant_id == "LETTER_BA"

        # 3. Build an essence–condition pair and validate (A6)
        pair = EssenceConditionPair(
            element_id="LETTER_BA",
            slot=filled.slot_id,
            value="ba",
            constraint=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            layer=OntologicalLayer.CELL,
        )
        ctx = frozenset({ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING})
        assert validate(pair, context_tokens=ctx)

        # 4. Promote from CELL to TRANSITION (A4)
        rule = LayerPromotionRule(
            rule_id="LP_E2E",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="CELL → TRANSITION for end-to-end test",
        )
        new_layer = promote(OntologicalLayer.CELL, rule)
        assert new_layer is OntologicalLayer.TRANSITION

        # 5. Compose a triad (A3)
        triad = compose(
            "SLOT_ZS_E2E",
            "VALUE_BA",
            "COND_OPEN_SYLLABLE",
            triad_id="TD_E2E",
            triad_type=TriadType.GENERATIVE,
            layer=new_layer,
        )
        assert not triad.is_degenerate
        assert triad.layer is OntologicalLayer.TRANSITION

        # 6. Infer (wrapper test)
        class SimpleEngine:
            def run(self, propositions):
                return [{"rule": "transitivity", "derived": True}]

        results = infer([], SimpleEngine())
        assert len(results) >= 1

    def test_blocked_slot_stops_chain(self) -> None:
        """If the slot is BLOCKED, the entire chain must fail at step 2."""
        slot = ZeroSlotRecord(
            slot_id="ZS_BLK_E2E",
            label="blocked",
            state=SlotState.BLOCKED,
            layer=OntologicalLayer.CELL,
        )
        with pytest.raises(ValueError):
            occupy_zero_slot(slot, "LETTER_BA")

    def test_constraint_failure_stops_chain(self) -> None:
        """If the constraint is not met, validation fails at step 3."""
        pair = EssenceConditionPair(
            element_id="LETTER_BA",
            slot="ZS_E2E",
            value="ba",
            constraint=ConditionToken.COMPRESSION_ALLOWED,
            layer=OntologicalLayer.CELL,
        )
        # Wrong context
        ctx = frozenset({ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING})
        assert validate(pair, context_tokens=ctx) is False

    def test_wrong_layer_stops_chain(self) -> None:
        """If promote is called with wrong layer, it fails at step 4."""
        rule = LayerPromotionRule(
            rule_id="LP_WRONG",
            source_layer=OntologicalLayer.CELL,
            target_layer=OntologicalLayer.TRANSITION,
            condition=ConditionToken.SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING,
            description="CELL → TRANSITION",
        )
        with pytest.raises(ValueError):
            promote(OntologicalLayer.ROOT, rule)
