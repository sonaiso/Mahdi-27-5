"""Tests for bāb registry — Module 3."""

from arabic_engine.core.enums import (
    MazidPattern,
    ThulathiBab,
    VerbAugmentation,
    VerbBaseType,
)
from arabic_engine.verb import bab_registry


class TestThulathiBabs:
    def test_six_gates_exist(self):
        babs = bab_registry.all_thulathi_babs()
        assert len(babs) == 6

    def test_each_gate_is_mujarrad(self):
        for bab in bab_registry.all_thulathi_babs():
            assert bab.augmentation == VerbAugmentation.MUJARRAD
            assert bab.base_type == VerbBaseType.THULATHI

    def test_get_bab_nasara(self):
        bab = bab_registry.get_thulathi_bab(ThulathiBab.FA3ALA_YAF3ULU)
        assert bab.past_pattern == "فَعَلَ"
        assert bab.present_pattern == "يَفْعُلُ"
        assert bab.bab_label == "باب نَصَرَ"

    def test_get_bab_3alima(self):
        bab = bab_registry.get_thulathi_bab(ThulathiBab.FA3ILA_YAF3ALU)
        assert bab.past_pattern == "فَعِلَ"
        assert bab.present_pattern == "يَفْعَلُ"

    def test_unique_bab_ids(self):
        ids = [b.bab_id for b in bab_registry.all_thulathi_babs()]
        assert len(ids) == len(set(ids))


class TestMazidBabs:
    def test_ten_patterns_exist(self):
        babs = bab_registry.all_mazid_babs()
        assert len(babs) == 10

    def test_each_pattern_is_mazid(self):
        for bab in bab_registry.all_mazid_babs():
            assert bab.augmentation == VerbAugmentation.MAZID

    def test_istaf3ala(self):
        bab = bab_registry.get_mazid_bab(MazidPattern.ISTAF3ALA)
        assert bab.past_pattern == "اِسْتَفْعَلَ"
        assert bab.present_pattern == "يَسْتَفْعِلُ"
        assert bab.masdar_pattern == "اِسْتِفْعَال"

    def test_af3ala(self):
        bab = bab_registry.get_mazid_bab(MazidPattern.AF3ALA)
        assert bab.semantic_tendency == "تعدية / سببية"


class TestLookup:
    def test_lookup_kataba(self):
        result = bab_registry.lookup_verb("كَتَبَ")
        assert result is not None
        root, bab = result
        assert root == ("ك", "ت", "ب")
        assert bab.bab_label == "باب نَصَرَ"

    def test_lookup_unknown(self):
        assert bab_registry.lookup_verb("شَيْء_غَرِيب") is None


class TestFindBabById:
    def test_find_existing(self):
        bab = bab_registry.find_bab_by_id(1)
        assert bab is not None
        assert bab.bab_label == "باب نَصَرَ"

    def test_find_mazid(self):
        bab = bab_registry.find_bab_by_id(19)
        assert bab is not None
        assert bab.past_pattern == "اِسْتَفْعَلَ"

    def test_find_nonexistent(self):
        assert bab_registry.find_bab_by_id(999) is None


class TestMatchPattern:
    def test_match_fa3ala_yaf3ulu(self):
        bab = bab_registry.match_pattern("فَعَلَ", "يَفْعُلُ")
        assert bab is not None
        assert bab.bab_id == 1

    def test_match_mazid(self):
        bab = bab_registry.match_pattern("اِسْتَفْعَلَ", "يَسْتَفْعِلُ")
        assert bab is not None
        assert bab.bab_id == 19

    def test_match_none(self):
        assert bab_registry.match_pattern("xxx", "yyy") is None
