"""Tests for noun signification (mutābaqa / taḍammun / iltizām)."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    Definiteness,
    DerivationStatus,
    Gender,
    GenderBasis,
    NounKind,
    NounNumber,
    SemanticType,
    UniversalParticular,
)
from arabic_engine.core.types import Concept, NounNode, NounSignification
from arabic_engine.noun.signification import build_noun_signification


def _node(**overrides) -> NounNode:
    defaults = dict(
        surface="إنسان", lemma="إنسان", root=("ا", "ن", "س"),
        pattern="", noun_kind=NounKind.SPECIES,
        universality=UniversalParticular.UNIVERSAL,
        gender=Gender.MASCULINE, gender_basis=GenderBasis.LEXICAL,
        number=NounNumber.SINGULAR, definiteness=Definiteness.INDEFINITE,
        derivation=DerivationStatus.RIGID,
    )
    defaults.update(overrides)
    return NounNode(**defaults)


def _concept(label: str = "إنسان") -> Concept:
    return Concept(
        concept_id=100, label=label,
        semantic_type=SemanticType.ENTITY,
    )


class TestMutabaqa:
    def test_proper_noun_mutabaqa(self):
        node = _node(noun_kind=NounKind.PROPER, lemma="زيد")
        sig = build_noun_signification(node, _concept("زيد"))
        assert sig.mutabaqa_target == "proper:زيد"

    def test_genus_mutabaqa(self):
        node = _node(noun_kind=NounKind.GENUS)
        sig = build_noun_signification(node, _concept())
        assert sig.mutabaqa_target.startswith("genus:")

    def test_species_mutabaqa(self):
        node = _node(noun_kind=NounKind.SPECIES)
        sig = build_noun_signification(node, _concept())
        assert sig.mutabaqa_target.startswith("species:")

    def test_individual_mutabaqa(self):
        node = _node(noun_kind=NounKind.INDIVIDUAL)
        sig = build_noun_signification(node, _concept())
        assert sig.mutabaqa_target.startswith("individual:")

    def test_attribute_mutabaqa(self):
        node = _node(noun_kind=NounKind.ATTRIBUTE)
        sig = build_noun_signification(node, _concept())
        assert sig.mutabaqa_target.startswith("attribute:")

    def test_entity_mutabaqa(self):
        node = _node(noun_kind=NounKind.ENTITY)
        sig = build_noun_signification(node, _concept())
        assert sig.mutabaqa_target.startswith("entity:")


class TestTadammun:
    def test_contains_number(self):
        node = _node(number=NounNumber.DUAL)
        sig = build_noun_signification(node, _concept())
        assert "number:DUAL" in sig.tadammun_parts

    def test_contains_gender(self):
        node = _node(gender=Gender.FEMININE)
        sig = build_noun_signification(node, _concept())
        assert "gender:FEMININE" in sig.tadammun_parts

    def test_contains_definiteness(self):
        node = _node(definiteness=Definiteness.DEFINITE_ARTICLE)
        sig = build_noun_signification(node, _concept())
        assert "definiteness:DEFINITE_ARTICLE" in sig.tadammun_parts

    def test_universal_scope(self):
        node = _node(universality=UniversalParticular.UNIVERSAL)
        sig = build_noun_signification(node, _concept())
        assert "universal_scope" in sig.tadammun_parts

    def test_particular_scope(self):
        node = _node(universality=UniversalParticular.PARTICULAR)
        sig = build_noun_signification(node, _concept())
        assert "particular_scope" in sig.tadammun_parts


class TestIltizam:
    def test_genus_entailments(self):
        node = _node(noun_kind=NounKind.GENUS)
        sig = build_noun_signification(node, _concept())
        assert "entails_species_membership" in sig.iltizam_entailments
        assert "entails_individual_instances" in sig.iltizam_entailments

    def test_species_entailments(self):
        node = _node(noun_kind=NounKind.SPECIES)
        sig = build_noun_signification(node, _concept())
        assert "entails_genus_membership" in sig.iltizam_entailments
        assert "entails_shared_essence" in sig.iltizam_entailments

    def test_individual_entailments(self):
        node = _node(noun_kind=NounKind.INDIVIDUAL)
        sig = build_noun_signification(node, _concept())
        assert "entails_unique_reference" in sig.iltizam_entailments
        assert "entails_species_membership" in sig.iltizam_entailments

    def test_attribute_entailments(self):
        node = _node(noun_kind=NounKind.ATTRIBUTE)
        sig = build_noun_signification(node, _concept())
        assert "entails_qualified_subject" in sig.iltizam_entailments


class TestReferentialStatus:
    def test_proper_noun_specific(self):
        node = _node(noun_kind=NounKind.PROPER)
        sig = build_noun_signification(node, _concept())
        assert sig.referential_status == "specific_referent"

    def test_individual_specific(self):
        node = _node(noun_kind=NounKind.INDIVIDUAL)
        sig = build_noun_signification(node, _concept())
        assert sig.referential_status == "specific_referent"

    def test_universal_generic(self):
        node = _node(
            noun_kind=NounKind.GENUS,
            universality=UniversalParticular.UNIVERSAL,
        )
        sig = build_noun_signification(node, _concept())
        assert sig.referential_status == "generic_referent"

    def test_particular_non_specific(self):
        node = _node(
            noun_kind=NounKind.ENTITY,
            universality=UniversalParticular.PARTICULAR,
        )
        sig = build_noun_signification(node, _concept())
        assert sig.referential_status == "non_specific_referent"


class TestNounSignificationFrozen:
    def test_signification_is_frozen(self):
        node = _node()
        sig = build_noun_signification(node, _concept())
        assert isinstance(sig, NounSignification)
        # NounSignification is frozen
        with pytest.raises(AttributeError):
            sig.mutabaqa_target = "changed"  # type: ignore[misc]
