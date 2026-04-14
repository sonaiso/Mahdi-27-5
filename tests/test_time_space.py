"""Comprehensive tests for arabic_engine.cognition.time_space."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import POS, SpaceRef, TimeRef
from arabic_engine.core.types import LexicalClosure, Proposition, TimeSpaceTag
from arabic_engine.cognition.time_space import detect_time, detect_space, tag


# ── helpers ──────────────────────────────────────────────────────────

def _cl(
    surface: str = "",
    lemma: str = "",
    pattern: str = "",
    pos: POS = POS.ISM,
) -> LexicalClosure:
    """Build a minimal LexicalClosure for testing."""
    return LexicalClosure(
        surface=surface,
        lemma=lemma or surface,
        root=(),
        pattern=pattern,
        pos=pos,
    )


# ── TestDetectTime ───────────────────────────────────────────────────

class TestDetectTime:
    """Tests for detect_time()."""

    # -- temporal adverbs --

    def test_adverb_ams_past(self):
        closures = [_cl(surface="أمس", lemma="أمس", pos=POS.ZARF)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PAST
        assert detail == "أمس"

    def test_adverb_ams_diacritised_past(self):
        closures = [_cl(surface="أَمْس", lemma="أَمْس", pos=POS.ZARF)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PAST

    def test_adverb_alyawm_present(self):
        closures = [_cl(surface="اليوم", lemma="اليوم", pos=POS.ZARF)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PRESENT
        assert detail == "اليوم"

    def test_adverb_alyawm_diacritised_present(self):
        closures = [_cl(surface="الْيَوْمَ", lemma="الْيَوْمَ", pos=POS.ZARF)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PRESENT

    def test_adverb_ghadan_future(self):
        closures = [_cl(surface="غدا", lemma="غدا", pos=POS.ZARF)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.FUTURE
        assert detail == "غدا"

    def test_adverb_ghadan_diacritised_future(self):
        closures = [_cl(surface="غَدًا", lemma="غَدًا", pos=POS.ZARF)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.FUTURE

    # -- verb morphology --

    def test_verb_past_pattern_fa3ala(self):
        closures = [_cl(surface="كَتَبَ", pattern="فَعَلَ", pos=POS.FI3L)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PAST
        assert detail == "كَتَبَ"

    def test_verb_past_pattern_ifta3ala(self):
        closures = [_cl(surface="اِجْتَهَدَ", pattern="اِفْتَعَلَ", pos=POS.FI3L)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PAST

    def test_verb_present_pattern_yaf3alu(self):
        closures = [_cl(surface="يَكْتُبُ", pattern="يَفْعَلُ", pos=POS.FI3L)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PRESENT
        assert detail == "يَكْتُبُ"

    def test_verb_present_pattern_yaf3ilu(self):
        closures = [_cl(surface="يَجْلِسُ", pattern="يَفْعِلُ", pos=POS.FI3L)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.PRESENT

    # -- future markers --

    def test_future_marker_sa(self):
        closures = [
            _cl(surface="سَ", pos=POS.HARF),
            _cl(surface="يَكْتُبُ", pattern="يَفْعَلُ", pos=POS.FI3L),
        ]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.FUTURE
        assert detail == "سَ"

    def test_future_marker_sawfa(self):
        closures = [
            _cl(surface="سَوْفَ", pos=POS.HARF),
            _cl(surface="يَذْهَبُ", pattern="يَفْعَلُ", pos=POS.FI3L),
        ]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.FUTURE
        assert detail == "سَوْفَ"

    # -- no signal --

    def test_no_time_signal(self):
        closures = [_cl(surface="كِتَاب", pos=POS.ISM)]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.UNSPECIFIED
        assert detail == ""

    def test_empty_closures(self):
        ref, detail = detect_time([])
        assert ref is TimeRef.UNSPECIFIED
        assert detail == ""

    # -- priority: adverb > verb --

    def test_adverb_takes_priority_over_verb(self):
        closures = [
            _cl(surface="كَتَبَ", pattern="فَعَلَ", pos=POS.FI3L),
            _cl(surface="غدا", lemma="غدا", pos=POS.ZARF),
        ]
        ref, detail = detect_time(closures)
        assert ref is TimeRef.FUTURE
        assert detail == "غدا"


# ── TestDetectSpace ──────────────────────────────────────────────────

class TestDetectSpace:
    """Tests for detect_space()."""

    def test_huna_here(self):
        closures = [_cl(surface="هنا", lemma="هنا")]
        ref, detail = detect_space(closures)
        assert ref is SpaceRef.HERE
        assert detail == "هنا"

    def test_huna_diacritised_here(self):
        closures = [_cl(surface="هُنَا", lemma="هُنَا")]
        ref, detail = detect_space(closures)
        assert ref is SpaceRef.HERE

    def test_hunaka_there(self):
        closures = [_cl(surface="هناك", lemma="هناك")]
        ref, detail = detect_space(closures)
        assert ref is SpaceRef.THERE
        assert detail == "هناك"

    def test_hunaka_diacritised_there(self):
        closures = [_cl(surface="هُنَاكَ", lemma="هُنَاكَ")]
        ref, detail = detect_space(closures)
        assert ref is SpaceRef.THERE

    def test_no_spatial_marker(self):
        closures = [_cl(surface="بيت", lemma="بيت")]
        ref, detail = detect_space(closures)
        assert ref is SpaceRef.UNSPECIFIED
        assert detail == ""

    def test_empty_closures(self):
        ref, detail = detect_space([])
        assert ref is SpaceRef.UNSPECIFIED
        assert detail == ""


# ── TestTag ──────────────────────────────────────────────────────────

class TestTag:
    """Tests for tag()."""

    def test_combined_time_and_space(self):
        closures = [
            _cl(surface="أمس", lemma="أمس", pos=POS.ZARF),
            _cl(surface="هنا", lemma="هنا"),
        ]
        result = tag(closures)
        assert isinstance(result, TimeSpaceTag)
        assert result.time_ref is TimeRef.PAST
        assert result.space_ref is SpaceRef.HERE
        assert result.time_detail == "أمس"
        assert result.space_detail == "هنا"

    def test_proposition_updated_in_place(self):
        closures = [
            _cl(surface="غدا", lemma="غدا", pos=POS.ZARF),
            _cl(surface="هناك", lemma="هناك"),
        ]
        prop = Proposition(subject="أ", predicate="ب", obj="ج")
        assert prop.time is TimeRef.UNSPECIFIED
        assert prop.space is SpaceRef.UNSPECIFIED

        result = tag(closures, proposition=prop)

        assert prop.time is TimeRef.FUTURE
        assert prop.space is SpaceRef.THERE
        assert result.time_ref is prop.time
        assert result.space_ref is prop.space

    def test_no_proposition(self):
        closures = [_cl(surface="كَتَبَ", pattern="فَعَلَ", pos=POS.FI3L)]
        result = tag(closures, proposition=None)
        assert result.time_ref is TimeRef.PAST
        assert result.space_ref is SpaceRef.UNSPECIFIED

    def test_empty_closures(self):
        result = tag([])
        assert result.time_ref is TimeRef.UNSPECIFIED
        assert result.space_ref is SpaceRef.UNSPECIFIED
        assert result.time_detail == ""
        assert result.space_detail == ""
