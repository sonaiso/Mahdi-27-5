"""Tests for verb enums — Module 1."""

from arabic_engine.core.enums import (
    DerivativeType,
    MazidPattern,
    NasikhCategory,
    ThulathiBab,
    VerbAugmentation,
    VerbBaseType,
    VerbCompleteness,
    VerbFractalStage,
    VerbGender,
    VerbNumber,
    VerbPerson,
    VerbTense,
    VerbTransitivity,
    VerbVoice,
)


class TestVerbBaseType:
    def test_members(self):
        assert VerbBaseType.THULATHI is not None
        assert VerbBaseType.RUBAI is not None
        assert len(VerbBaseType) == 2


class TestVerbAugmentation:
    def test_members(self):
        assert VerbAugmentation.MUJARRAD is not None
        assert VerbAugmentation.MAZID is not None
        assert len(VerbAugmentation) == 2


class TestThulathiBab:
    def test_six_gates(self):
        assert len(ThulathiBab) == 6

    def test_gate_names(self):
        expected = {
            "FA3ALA_YAF3ULU", "FA3ALA_YAF3ILU", "FA3ALA_YAF3ALU",
            "FA3ILA_YAF3ALU", "FA3ULA_YAF3ULU", "FA3ILA_YAF3ILU",
        }
        assert {m.name for m in ThulathiBab} == expected


class TestMazidPattern:
    def test_count(self):
        assert len(MazidPattern) == 10

    def test_istaf3ala(self):
        assert MazidPattern.ISTAF3ALA is not None


class TestVerbTense:
    def test_three_tenses(self):
        assert len(VerbTense) == 3
        assert VerbTense.MADI is not None
        assert VerbTense.MUDARI is not None
        assert VerbTense.AMR is not None


class TestVerbTransitivity:
    def test_four_levels(self):
        assert len(VerbTransitivity) == 4
        assert VerbTransitivity.LAZIM is not None
        assert VerbTransitivity.MUTA3ADDI is not None
        assert VerbTransitivity.MUTA3ADDI_LI_ITHNAYN is not None
        assert VerbTransitivity.MUTA3ADDI_LI_THALATHA is not None


class TestVerbCompleteness:
    def test_members(self):
        assert VerbCompleteness.KAMIL is not None
        assert VerbCompleteness.NAQIS is not None


class TestNasikhCategory:
    def test_three_categories(self):
        assert len(NasikhCategory) == 3
        assert NasikhCategory.KANA_WA_AKHAWAT is not None
        assert NasikhCategory.KADA_WA_AKHAWAT is not None
        assert NasikhCategory.ZANNA_WA_AKHAWAT is not None


class TestVerbPerson:
    def test_three_persons(self):
        assert len(VerbPerson) == 3


class TestVerbNumber:
    def test_three_numbers(self):
        assert len(VerbNumber) == 3


class TestVerbGender:
    def test_two_genders(self):
        assert len(VerbGender) == 2


class TestVerbVoice:
    def test_two_voices(self):
        assert len(VerbVoice) == 2


class TestDerivativeType:
    def test_ten_types(self):
        assert len(DerivativeType) == 10
        assert DerivativeType.MASDAR is not None
        assert DerivativeType.ISM_FA3IL is not None
        assert DerivativeType.ISM_TAFDIL is not None


class TestVerbFractalStage:
    def test_six_stages(self):
        assert len(VerbFractalStage) == 6
        names = [s.name for s in VerbFractalStage]
        assert names == [
            "TA3YIN", "HIFDH", "RABT", "HUKM", "INTIQAL", "RADD",
        ]
