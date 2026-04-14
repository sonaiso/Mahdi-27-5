"""Tests for noun-related enums (Phase 1).

Validates completeness, non-overlap, and correctness of all noun enums
added by the Noun Fractal Constitution.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    CompoundType,
    Definiteness,
    DerivationStatus,
    Gender,
    GenderBasis,
    NounFractalStage,
    NounKind,
    NounNumber,
    ProperNounType,
    UniversalParticular,
)


class TestGender:
    def test_members(self):
        assert set(Gender) == {
            Gender.MASCULINE, Gender.FEMININE, Gender.DUAL_GENDER,
        }

    def test_values_unique(self):
        values = [m.value for m in Gender]
        assert len(values) == len(set(values))


class TestGenderBasis:
    def test_members(self):
        assert set(GenderBasis) == {
            GenderBasis.REAL, GenderBasis.METAPHORICAL,
            GenderBasis.LEXICAL, GenderBasis.SEMANTIC,
        }

    def test_values_unique(self):
        values = [m.value for m in GenderBasis]
        assert len(values) == len(set(values))


class TestNounNumber:
    def test_members(self):
        expected = {
            NounNumber.SINGULAR, NounNumber.DUAL,
            NounNumber.SOUND_MASC_PLURAL, NounNumber.SOUND_FEM_PLURAL,
            NounNumber.BROKEN_PLURAL, NounNumber.COLLECTIVE_NOUN,
            NounNumber.GENUS_NOUN, NounNumber.NUMERAL,
        }
        assert set(NounNumber) == expected

    def test_count(self):
        assert len(NounNumber) == 8


class TestDefiniteness:
    def test_members(self):
        expected = {
            Definiteness.DEFINITE_ARTICLE,
            Definiteness.DEFINITE_PROPER,
            Definiteness.DEFINITE_PRONOUN,
            Definiteness.DEFINITE_DEMONSTRATIVE,
            Definiteness.DEFINITE_RELATIVE,
            Definiteness.DEFINITE_ANNEXATION,
            Definiteness.DEFINITE_VOCATIVE,
            Definiteness.INDEFINITE,
        }
        assert set(Definiteness) == expected

    def test_count(self):
        assert len(Definiteness) == 8


class TestNounKind:
    def test_members(self):
        expected = {
            NounKind.ENTITY, NounKind.ATTRIBUTE, NounKind.PROPER,
            NounKind.GENUS, NounKind.SPECIES, NounKind.INDIVIDUAL,
            NounKind.NUMERAL, NounKind.COMPOUND, NounKind.BORROWED,
        }
        assert set(NounKind) == expected

    def test_count(self):
        assert len(NounKind) == 9


class TestUniversalParticular:
    def test_members(self):
        assert set(UniversalParticular) == {
            UniversalParticular.UNIVERSAL,
            UniversalParticular.PARTICULAR,
        }


class TestProperNounType:
    def test_members(self):
        expected = {
            ProperNounType.PERSONAL, ProperNounType.PLACE,
            ProperNounType.TIME, ProperNounType.TRANSFERRED,
            ProperNounType.COMPOUND, ProperNounType.NICKNAME,
            ProperNounType.PATRONYMIC, ProperNounType.COINED,
            ProperNounType.BORROWED,
        }
        assert set(ProperNounType) == expected

    def test_count(self):
        assert len(ProperNounType) == 9


class TestCompoundType:
    def test_members(self):
        assert set(CompoundType) == {
            CompoundType.ANNEXATION,
            CompoundType.BLEND,
            CompoundType.PREDICATIVE,
        }


class TestDerivationStatus:
    def test_members(self):
        assert set(DerivationStatus) == {
            DerivationStatus.RIGID,
            DerivationStatus.DERIVED,
        }


class TestNounFractalStage:
    def test_members(self):
        expected = {
            NounFractalStage.DESIGNATION,
            NounFractalStage.PRESERVATION,
            NounFractalStage.LINKAGE,
            NounFractalStage.JUDGMENT,
            NounFractalStage.TRANSITION,
            NounFractalStage.RETURN,
        }
        assert set(NounFractalStage) == expected

    def test_count(self):
        assert len(NounFractalStage) == 6

    def test_cycle_order(self):
        """The fractal stages have a natural ordering."""
        stages = list(NounFractalStage)
        names = [s.name for s in stages]
        assert names == [
            "DESIGNATION", "PRESERVATION", "LINKAGE",
            "JUDGMENT", "TRANSITION", "RETURN",
        ]


class TestNoEnumOverlap:
    """Ensure no two noun enums share the same name or purpose."""

    def test_noun_kind_vs_semantic_type(self):
        """NounKind is finer-grained than SemanticType."""
        from arabic_engine.core.enums import SemanticType
        noun_names = {m.name for m in NounKind}
        semantic_names = {m.name for m in SemanticType}
        # ENTITY and ATTRIBUTE appear in both but serve different layers
        overlap = noun_names & semantic_names
        assert overlap == {"ENTITY", "ATTRIBUTE"}
