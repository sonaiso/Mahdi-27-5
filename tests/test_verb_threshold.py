"""Tests for verb threshold validator — Module 5."""

from arabic_engine.core.enums import POS, VerbTense
from arabic_engine.verb.threshold import validate
from arabic_engine.verb import bab_registry


class TestFullThreshold:
    def test_complete_verb(self):
        lookup = bab_registry.lookup_verb("كَتَبَ")
        assert lookup is not None
        root, bab = lookup
        result = validate(
            surface="كَتَبَ",
            pos=POS.FI3L,
            root=root,
            pattern="فَعَلَ",
            tense=VerbTense.MADI,
            bab=bab,
        )
        assert result.has_thubut is True
        assert result.has_hadd is True
        assert result.has_imtidad is True
        assert result.has_muqawwim is True
        assert result.has_3alaqa_binaya is True
        assert result.has_intizam is True
        assert result.has_wahda is True
        assert result.has_qabiliyyat_ta3yin is True
        assert result.is_complete is True


class TestIncompleteThreshold:
    def test_no_tense(self):
        result = validate(
            surface="كَتَبَ",
            pos=POS.FI3L,
            root=("ك", "ت", "ب"),
            pattern="فَعَلَ",
            tense=None,
            bab=None,
        )
        assert result.has_thubut is False
        assert result.is_complete is False

    def test_non_verb_pos(self):
        result = validate(
            surface="كِتَاب",
            pos=POS.ISM,
            root=("ك", "ت", "ب"),
            pattern="فِعَال",
            tense=VerbTense.MADI,
            bab=None,
        )
        assert result.has_hadd is False
        assert result.is_complete is False

    def test_no_bab(self):
        result = validate(
            surface="كَتَبَ",
            pos=POS.FI3L,
            root=("ك", "ت", "ب"),
            pattern="فَعَلَ",
            tense=VerbTense.MADI,
            bab=None,
        )
        assert result.has_intizam is False
        assert result.has_qabiliyyat_ta3yin is False
        assert result.is_complete is False

    def test_multiword_surface(self):
        result = validate(
            surface="ما زال",
            pos=POS.FI3L,
            root=("ز", "و", "ل"),
            pattern="فَعَلَ",
            tense=VerbTense.MADI,
            bab=None,
        )
        assert result.has_wahda is False


class TestThresholdProperty:
    def test_is_complete_property(self):
        """is_complete is a derived property, not stored."""
        from arabic_engine.core.types import VerbMinimalThreshold
        t = VerbMinimalThreshold(
            has_thubut=True, has_hadd=True, has_imtidad=True,
            has_muqawwim=True, has_3alaqa_binaya=True,
            has_intizam=True, has_wahda=True, has_qabiliyyat_ta3yin=True,
        )
        assert t.is_complete is True
