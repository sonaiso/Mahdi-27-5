"""Tests for the functional transition loader and Condition DSL."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    CellType,
    ConditionToken,
    EvidenceType,
    FuncTransitionClass,
    ReversibleValue,
)
from arabic_engine.core.types import FunctionalTransitionRecord
from arabic_engine.signifier.functional_transition import (
    CONDITION_TOKEN_MAP,
    by_class,
    by_source,
    by_target,
    load_seed_dataset,
    parse_condition,
)

# ── New enum completeness ────────────────────────────────────────────

class TestNewEnums:
    def test_cell_type_has_28_members(self):
        assert len(CellType) == 28

    def test_func_transition_class_has_seven_members(self):
        assert len(FuncTransitionClass) == 7

    def test_evidence_type_has_six_members(self):
        assert len(EvidenceType) == 6

    def test_reversible_value_has_three_members(self):
        assert len(ReversibleValue) == 3

    def test_condition_token_is_non_empty(self):
        assert len(ConditionToken) >= 50

    def test_cell_type_contains_consonants(self):
        assert CellType.C_ROOT_PLAIN in CellType
        assert CellType.C_AUGMENTATIVE in CellType
        assert CellType.C_GLIDE_BACK in CellType
        assert CellType.C_GLIDE_FRONT in CellType

    def test_cell_type_contains_long_vowels(self):
        assert CellType.V_LONG_A in CellType
        assert CellType.V_LONG_W in CellType
        assert CellType.V_LONG_Y in CellType

    def test_cell_type_contains_diacritics(self):
        for name in (
            "D_FATHA", "D_DAMMA", "D_KASRA", "D_SUKUN",
            "D_SHADDA", "D_TANWEEN_FATH", "D_TANWEEN_DAMM", "D_TANWEEN_KASR",
        ):
            assert CellType[name] in CellType

    def test_cell_type_contains_meta_cells(self):
        for name in (
            "CELL_ILLA", "CELL_IMPLICIT", "CELL_WAQF_COMPRESSED",
            "CELL_EXISTENTIAL", "CELL_EXISTENTIAL_TEMPORAL",
            "CELL_EVENT_SOURCE", "CELL_EVENT_TEMPORAL",
            "CELL_CAUSAL_INTERNAL", "CELL_CAUSAL_EXTERNAL",
        ):
            assert CellType[name] in CellType


# ── CONDITION_TOKEN_MAP ──────────────────────────────────────────────

class TestConditionTokenMap:
    def test_map_covers_all_tokens(self):
        assert set(CONDITION_TOKEN_MAP.values()) == set(ConditionToken)

    def test_map_keys_are_lowercase(self):
        for key in CONDITION_TOKEN_MAP:
            assert key == key.lower()

    def test_map_size_equals_enum_size(self):
        assert len(CONDITION_TOKEN_MAP) == len(ConditionToken)


# ── parse_condition ──────────────────────────────────────────────────

class TestParseCondition:
    def test_known_lowercase(self):
        assert parse_condition("glide_loses_consonantal_load") is (
            ConditionToken.GLIDE_LOSES_CONSONANTAL_LOAD
        )

    def test_known_uppercase(self):
        assert parse_condition("PAUSE_MODE_ENABLED") is ConditionToken.PAUSE_MODE_ENABLED

    def test_known_mixed_case(self):
        assert parse_condition("Word_Final_Position") is ConditionToken.WORD_FINAL_POSITION

    def test_normalises_hyphens(self):
        # hyphens replaced by underscores
        assert parse_condition("pause-mode-enabled") is ConditionToken.PAUSE_MODE_ENABLED

    def test_strips_leading_trailing_whitespace(self):
        assert parse_condition("  fatha_extended  ") is ConditionToken.FATHA_EXTENDED

    def test_unknown_token_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown condition token"):
            parse_condition("completely_nonexistent_condition")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_condition("")


# ── load_seed_dataset ────────────────────────────────────────────────

class TestLoadSeedDataset:
    @pytest.fixture(scope="class")
    def records(self):
        return load_seed_dataset()

    def test_returns_list(self, records):
        assert isinstance(records, list)

    def test_has_33_records(self, records):
        assert len(records) == 33

    def test_all_records_are_functional_transition_record(self, records):
        for r in records:
            assert isinstance(r, FunctionalTransitionRecord)

    def test_ids_are_unique(self, records):
        ids = [r.transition_id for r in records]
        assert len(ids) == len(set(ids))

    def test_ids_match_tr_pattern(self, records):
        import re
        pattern = re.compile(r"^TR_\d{3}$")
        for r in records:
            assert pattern.match(r.transition_id), f"Bad ID: {r.transition_id}"

    def test_records_sorted_by_id(self, records):
        ids = [r.transition_id for r in records]
        assert ids == sorted(ids)

    def test_priority_in_range(self, records):
        for r in records:
            assert 1 <= r.priority <= 5

    def test_source_cell_is_cell_type(self, records):
        for r in records:
            assert isinstance(r.source_cell, CellType)

    def test_target_cell_is_cell_type(self, records):
        for r in records:
            assert isinstance(r.target_cell, CellType)

    def test_transition_class_is_func_transition_class(self, records):
        for r in records:
            assert isinstance(r.transition_class, FuncTransitionClass)

    def test_reversible_is_reversible_value(self, records):
        for r in records:
            assert isinstance(r.reversible, ReversibleValue)

    def test_preconditions_are_frozensets(self, records):
        for r in records:
            assert isinstance(r.preconditions, frozenset)

    def test_preconditions_contain_condition_tokens(self, records):
        for r in records:
            for c in r.preconditions:
                assert isinstance(c, ConditionToken)

    def test_blocking_conditions_are_frozensets(self, records):
        for r in records:
            assert isinstance(r.blocking_conditions, frozenset)

    def test_blocking_conditions_contain_condition_tokens(self, records):
        for r in records:
            for c in r.blocking_conditions:
                assert isinstance(c, ConditionToken)

    def test_all_preconditions_non_empty(self, records):
        for r in records:
            assert len(r.preconditions) >= 1, f"{r.transition_id} has no preconditions"

    def test_evidence_type_is_none_or_evidence_type(self, records):
        for r in records:
            assert r.evidence_type is None or isinstance(r.evidence_type, EvidenceType)

    def test_surface_form_non_empty(self, records):
        for r in records:
            assert r.surface_form, f"{r.transition_id} has empty surface_form"

    def test_deep_form_non_empty(self, records):
        for r in records:
            assert r.deep_form, f"{r.transition_id} has empty deep_form"

    def test_record_is_frozen(self, records):
        r = records[0]
        with pytest.raises((AttributeError, TypeError)):
            r.priority = 99  # type: ignore[misc]


# ── Spot-checks on specific records ─────────────────────────────────

class TestSpecificRecords:
    @pytest.fixture(scope="class")
    def by_id(self):
        return {r.transition_id: r for r in load_seed_dataset()}

    def test_tr001_glide_back_to_long_w(self, by_id):
        r = by_id["TR_001"]
        assert r.source_cell is CellType.C_GLIDE_BACK
        assert r.target_cell is CellType.V_LONG_W
        assert r.transition_class is FuncTransitionClass.PHONOLOGICAL
        assert r.priority == 1
        assert r.reversible is ReversibleValue.CONDITIONAL
        assert ConditionToken.GLIDE_LOSES_CONSONANTAL_LOAD in r.preconditions
        assert ConditionToken.SEGMENT_REQUIRED_AS_EXPLICIT_ONSET in r.blocking_conditions

    def test_tr009_gemination(self, by_id):
        r = by_id["TR_009"]
        assert r.source_cell is CellType.C_ROOT_PLAIN
        assert r.target_cell is CellType.D_SHADDA
        assert ConditionToken.TWO_IDENTICAL_CONSONANTS_IN_SEQUENCE in r.preconditions
        assert ConditionToken.IDENTITY_NOT_PROVEN in r.blocking_conditions
        assert r.reversible is ReversibleValue.YES

    def test_tr023_waqf_fatha(self, by_id):
        r = by_id["TR_023"]
        assert r.source_cell is CellType.D_FATHA
        assert r.target_cell is CellType.CELL_WAQF_COMPRESSED
        assert r.transition_class is FuncTransitionClass.ORTHOGRAPHIC
        assert ConditionToken.PAUSE_MODE_ENABLED in r.preconditions
        assert ConditionToken.WORD_FINAL_POSITION in r.preconditions

    def test_tr030_event_temporalization(self, by_id):
        r = by_id["TR_030"]
        assert r.source_cell is CellType.CELL_EVENT_SOURCE
        assert r.target_cell is CellType.CELL_EVENT_TEMPORAL
        assert r.transition_class is FuncTransitionClass.TEMPORAL
        assert ConditionToken.ABSTRACT_EVENT_LINKED_TO_TIME_REFERENCE in r.preconditions

    def test_tr032_existential_temporal(self, by_id):
        r = by_id["TR_032"]
        assert r.source_cell is CellType.CELL_EXISTENTIAL
        assert r.target_cell is CellType.CELL_EXISTENTIAL_TEMPORAL
        assert r.transition_class is FuncTransitionClass.EXISTENTIAL
        assert ConditionToken.TEMPORAL_OPERATOR_APPLIED in r.preconditions


# ── Filter helpers ────────────────────────────────────────────────────

class TestFilterHelpers:
    @pytest.fixture(scope="class")
    def records(self):
        return load_seed_dataset()

    def test_by_source_returns_subset(self, records):
        subset = by_source(records, CellType.D_SUKUN)
        assert all(r.source_cell is CellType.D_SUKUN for r in subset)
        assert len(subset) >= 3  # TR_015, TR_016, TR_017 at minimum

    def test_by_target_returns_subset(self, records):
        subset = by_target(records, CellType.D_SHADDA)
        assert all(r.target_cell is CellType.D_SHADDA for r in subset)
        assert len(subset) >= 3  # TR_009, TR_010, TR_011 at minimum

    def test_by_class_phonological(self, records):
        subset = by_class(records, FuncTransitionClass.PHONOLOGICAL)
        assert all(r.transition_class is FuncTransitionClass.PHONOLOGICAL for r in subset)
        assert len(subset) >= 1

    def test_by_class_causal(self, records):
        subset = by_class(records, FuncTransitionClass.CAUSAL)
        assert len(subset) >= 2  # TR_028, TR_029 at minimum

    def test_by_class_existential(self, records):
        subset = by_class(records, FuncTransitionClass.EXISTENTIAL)
        assert len(subset) >= 2  # TR_032, TR_033 at minimum

    def test_by_class_abstractive(self, records):
        subset = by_class(records, FuncTransitionClass.ABSTRACTIVE)
        assert len(subset) >= 1  # TR_031 at minimum

    def test_by_source_empty_for_unknown_cell(self, records):
        subset = by_source(records, CellType.V_LONG_A)
        assert subset == []

    def test_filter_returns_list(self, records):
        result = by_source(records, CellType.C_GLIDE_BACK)
        assert isinstance(result, list)

    def test_all_classes_covered(self, records):
        covered = {r.transition_class for r in records}
        for cls in FuncTransitionClass:
            assert cls in covered, f"{cls.name} missing from seed dataset"
