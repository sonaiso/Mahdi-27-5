"""Tests for verb analyzer — Module 4."""

from arabic_engine.core.enums import (
    POS,
    NasikhCategory,
    VerbCompleteness,
    VerbTense,
    VerbTransitivity,
    VerbVoice,
)
from arabic_engine.verb.analyzer import analyze


class TestAnalyzeKnownVerb:
    def test_kataba(self):
        profile = analyze("كَتَبَ", pattern="فَعَلَ")
        assert profile is not None
        assert profile.root == ("ك", "ت", "ب")
        assert profile.tense == VerbTense.MADI
        assert profile.voice == VerbVoice.MA3LUM
        assert profile.completeness == VerbCompleteness.KAMIL
        assert profile.nasikh_category is None

    def test_nasara(self):
        profile = analyze("نَصَرَ", pattern="فَعَلَ")
        assert profile is not None
        assert profile.root == ("ن", "ص", "ر")
        assert profile.bab.bab_label == "باب نَصَرَ"

    def test_3alima(self):
        profile = analyze("عَلِمَ", pattern="فَعِلَ")
        assert profile is not None
        assert profile.bab.past_pattern == "فَعِلَ"
        assert profile.tense == VerbTense.MADI

    def test_karuma(self):
        profile = analyze("كَرُمَ", pattern="فَعُلَ")
        assert profile is not None
        assert profile.bab.bab_label == "باب كَرُمَ"
        assert profile.transitivity == VerbTransitivity.LAZIM


class TestAnalyzeNasikh:
    def test_kana(self):
        profile = analyze("كان", pattern="فَعَلَ")
        assert profile is not None
        assert profile.nasikh_category == NasikhCategory.KANA_WA_AKHAWAT
        assert profile.completeness == VerbCompleteness.NAQIS


class TestAnalyzeNonVerb:
    def test_non_fi3l_pos(self):
        result = analyze("زَيْد", pattern="فَعْل", pos=POS.ISM)
        assert result is None

    def test_unknown_surface(self):
        result = analyze("غَرِيب_جِدًّا", pattern="")
        assert result is None


class TestAnalyzePatternFallback:
    def test_fallback_to_pattern(self):
        """When surface is unknown, pattern-based lookup should work."""
        result = analyze("سَمَعَ", pattern="فَعِلَ")
        assert result is not None
        assert result.bab.past_pattern == "فَعِلَ"
