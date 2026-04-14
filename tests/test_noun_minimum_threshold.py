"""Tests for validate_noun_completeness (minimum complete threshold)."""

from __future__ import annotations

from arabic_engine.core.enums import (
    CompoundType,
    Definiteness,
    DerivationStatus,
    Gender,
    GenderBasis,
    NounKind,
    NounNumber,
    UniversalParticular,
)
from arabic_engine.core.types import NounNode
from arabic_engine.noun.constitution import validate_noun_completeness


def _node(**overrides) -> NounNode:
    defaults = dict(
        surface="كتاب", lemma="كتاب", root=("ك", "ت", "ب"),
        pattern="فِعال", noun_kind=NounKind.ENTITY,
        universality=UniversalParticular.PARTICULAR,
        gender=Gender.MASCULINE, gender_basis=GenderBasis.LEXICAL,
        number=NounNumber.SINGULAR, definiteness=Definiteness.INDEFINITE,
        derivation=DerivationStatus.RIGID,
    )
    defaults.update(overrides)
    return NounNode(**defaults)


class TestCompleteNoun:
    def test_standard_noun_is_complete(self):
        assert validate_noun_completeness(_node()) is True

    def test_proper_noun_is_complete(self):
        node = _node(
            surface="زيد", lemma="زيد",
            noun_kind=NounKind.PROPER,
            definiteness=Definiteness.DEFINITE_PROPER,
        )
        assert validate_noun_completeness(node) is True

    def test_borrowed_without_root_is_complete(self):
        node = _node(
            surface="كمبيوتر", lemma="كمبيوتر",
            root=(), noun_kind=NounKind.BORROWED,
            is_borrowed=True,
        )
        assert validate_noun_completeness(node) is True

    def test_compound_without_root_is_complete(self):
        node = _node(
            surface="بعلبك", lemma="بعلبك",
            root=(), noun_kind=NounKind.COMPOUND,
            compound_type=CompoundType.BLEND,
        )
        assert validate_noun_completeness(node) is True


class TestIncompleteNoun:
    def test_empty_surface_fails(self):
        assert validate_noun_completeness(_node(surface="")) is False

    def test_empty_lemma_fails(self):
        assert validate_noun_completeness(_node(lemma="")) is False

    def test_no_root_and_not_borrowed_fails(self):
        assert validate_noun_completeness(_node(root=())) is False


class TestEdgeCases:
    def test_feminine_noun_is_complete(self):
        node = _node(gender=Gender.FEMININE, gender_basis=GenderBasis.REAL)
        assert validate_noun_completeness(node) is True

    def test_dual_number_is_complete(self):
        node = _node(number=NounNumber.DUAL)
        assert validate_noun_completeness(node) is True

    def test_broken_plural_is_complete(self):
        node = _node(number=NounNumber.BROKEN_PLURAL)
        assert validate_noun_completeness(node) is True

    def test_definite_article_is_complete(self):
        node = _node(definiteness=Definiteness.DEFINITE_ARTICLE)
        assert validate_noun_completeness(node) is True

    def test_all_noun_kinds_complete(self):
        for kind in NounKind:
            extras = {}
            if kind == NounKind.BORROWED:
                extras = {"root": (), "is_borrowed": True}
            elif kind == NounKind.COMPOUND:
                extras = {"root": (), "compound_type": CompoundType.BLEND}
            node = _node(noun_kind=kind, **extras)
            assert validate_noun_completeness(node) is True, f"Failed for {kind.name}"
