"""Tests for nāsikh verb system — Module 7."""

from arabic_engine.core.enums import NasikhCategory
from arabic_engine.verb.nasikh import (
    all_kada,
    all_kana,
    all_zanna,
    classify,
    is_nasikh,
)


class TestKanaFamily:
    def test_kana_classified(self):
        profile = classify("كان")
        assert profile is not None
        assert profile.category == NasikhCategory.KANA_WA_AKHAWAT
        assert profile.epistemic_function == "ربط زمني حكمي"

    def test_asbaha(self):
        profile = classify("أصبح")
        assert profile is not None
        assert profile.category == NasikhCategory.KANA_WA_AKHAWAT

    def test_laysa(self):
        profile = classify("ليس")
        assert profile is not None
        assert profile.category == NasikhCategory.KANA_WA_AKHAWAT

    def test_kana_family_count(self):
        members = all_kana()
        assert len(members) >= 10


class TestKadaFamily:
    def test_kada_classified(self):
        profile = classify("كاد")
        assert profile is not None
        assert profile.category == NasikhCategory.KADA_WA_AKHAWAT

    def test_3asa(self):
        profile = classify("عسى")
        assert profile is not None
        assert profile.category == NasikhCategory.KADA_WA_AKHAWAT

    def test_kada_family_count(self):
        members = all_kada()
        assert len(members) >= 5


class TestZannaFamily:
    def test_zanna_classified(self):
        profile = classify("ظنّ")
        assert profile is not None
        assert profile.category == NasikhCategory.ZANNA_WA_AKHAWAT
        assert "اعتقاد" in profile.epistemic_function

    def test_3alima(self):
        profile = classify("علم")
        assert profile is not None
        assert profile.category == NasikhCategory.ZANNA_WA_AKHAWAT

    def test_zanna_family_count(self):
        members = all_zanna()
        assert len(members) >= 10


class TestIsNasikh:
    def test_kana_is_nasikh(self):
        assert is_nasikh("كان") is True

    def test_kataba_not_nasikh(self):
        assert is_nasikh("كَتَبَ") is False

    def test_unknown_not_nasikh(self):
        assert is_nasikh("شَيْء") is False


class TestNonNasikh:
    def test_classify_returns_none(self):
        assert classify("كَتَبَ") is None
