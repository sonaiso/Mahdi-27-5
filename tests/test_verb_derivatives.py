"""Tests for derivative chain builder — Module 6."""

from arabic_engine.core.enums import MazidPattern, ThulathiBab
from arabic_engine.verb import bab_registry
from arabic_engine.verb.derivatives import build


class TestMujarradDerivatives:
    def test_kataba_derivatives(self):
        bab = bab_registry.get_thulathi_bab(ThulathiBab.FA3ALA_YAF3ULU)
        chain = build(("ك", "ت", "ب"), bab)
        assert chain.root == ("ك", "ت", "ب")
        assert chain.bab_id == bab.bab_id
        # Masdar should contain root consonants
        assert "ك" in chain.masdar
        # Active participle (فاعل pattern)
        assert "ك" in chain.ism_fa3il
        # Passive participle (مفعول pattern)
        assert chain.ism_maf3ul != ""
        # Nouns of time/place
        assert chain.ism_zaman != ""
        assert chain.ism_makan != ""
        # Trilateral-specific
        assert chain.ism_haya != ""
        assert chain.ism_ala != ""

    def test_daraba_derivatives(self):
        bab = bab_registry.get_thulathi_bab(ThulathiBab.FA3ALA_YAF3ILU)
        chain = build(("ض", "ر", "ب"), bab)
        assert "ض" in chain.masdar
        assert chain.ism_fa3il != ""


class TestMazidDerivatives:
    def test_af3ala_derivatives(self):
        bab = bab_registry.get_mazid_bab(MazidPattern.AF3ALA)
        chain = build(("خ", "ر", "ج"), bab)
        assert chain.masdar != ""
        assert chain.ism_fa3il != ""
        assert chain.ism_maf3ul != ""
        # Mazid verbs should NOT have ism_haya or ism_ala
        assert chain.ism_haya == ""
        assert chain.ism_ala == ""

    def test_istaf3ala_derivatives(self):
        bab = bab_registry.get_mazid_bab(MazidPattern.ISTAF3ALA)
        chain = build(("خ", "ر", "ج"), bab)
        assert chain.masdar != ""
        assert chain.ism_fa3il != ""
        assert chain.ism_maf3ul != ""


class TestDerivativeChainFrozen:
    def test_immutability(self):
        bab = bab_registry.get_thulathi_bab(ThulathiBab.FA3ALA_YAF3ULU)
        chain = build(("ك", "ت", "ب"), bab)
        try:
            chain.masdar = "changed"  # type: ignore[misc]
            assert False, "Should not allow mutation"
        except AttributeError:
            pass
