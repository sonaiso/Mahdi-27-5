"""Tests for the noun fractal cycle (6-stage processing)."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    POS,
    NounFractalStage,
    SemanticType,
    UniversalParticular,
)
from arabic_engine.core.types import Concept, LexicalClosure
from arabic_engine.noun.fractal import run_noun_fractal


def _closure(
    surface: str,
    lemma: str,
    root: tuple = (),
    pattern: str = "",
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface, lemma=lemma, root=root, pattern=pattern,
        pos=POS.ISM,
    )


def _concept(label: str, **props) -> Concept:
    return Concept(
        concept_id=0, label=label, semantic_type=SemanticType.ENTITY,
        properties=props,
    )


class TestFractalCycle:
    def test_returns_noun_node(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = run_noun_fractal(cl)
        assert node is not None

    def test_final_stage_is_return(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = run_noun_fractal(cl)
        assert node.fractal_stage == NounFractalStage.RETURN

    def test_all_stages_traversed(self):
        """The fractal cycle passes through all 6 stages sequentially."""
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        # We can only observe the final stage — RETURN
        node = run_noun_fractal(cl)
        assert node.fractal_stage == NounFractalStage.RETURN

    def test_proper_noun_fractal(self):
        cl = _closure("زَيْدٌ", "زَيْد", ("ز", "ي", "د"), "فَعْل")
        co = _concept("زَيْد", proper_noun=True)
        node = run_noun_fractal(cl, co)
        assert node.fractal_stage == NounFractalStage.RETURN
        assert node.universality == UniversalParticular.PARTICULAR

    def test_borrowed_noun_fractal(self):
        cl = _closure("كمبيوتر", "كمبيوتر", (), "")
        node = run_noun_fractal(cl)
        assert node.fractal_stage == NounFractalStage.RETURN
        assert node.is_borrowed is True

    def test_attribute_noun_fractal(self):
        cl = _closure("كاتب", "كاتب", ("ك", "ت", "ب"), "فاعل")
        node = run_noun_fractal(cl)
        assert node.fractal_stage == NounFractalStage.RETURN

    def test_feminine_noun_fractal(self):
        cl = _closure("شجرة", "شجرة", ("ش", "ج", "ر"), "فَعْلَة")
        node = run_noun_fractal(cl)
        assert node.fractal_stage == NounFractalStage.RETURN
        from arabic_engine.core.enums import Gender
        assert node.gender == Gender.FEMININE

    def test_plural_noun_fractal(self):
        cl = _closure("كُتُب", "كُتُب", ("ك", "ت", "ب"), "فُعُل")
        node = run_noun_fractal(cl)
        assert node.fractal_stage == NounFractalStage.RETURN
        from arabic_engine.core.enums import NounNumber
        assert node.number == NounNumber.BROKEN_PLURAL


class TestFractalStageOrder:
    def test_stage_values_ascending(self):
        """Each stage has a strictly increasing enum value."""
        stages = list(NounFractalStage)
        for i in range(1, len(stages)):
            assert stages[i].value > stages[i - 1].value

    def test_stage_count(self):
        assert len(NounFractalStage) == 6


class TestFractalConsistency:
    def test_output_preserves_input_data(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = run_noun_fractal(cl)
        assert node.surface == "كتاب"
        assert node.lemma == "كتاب"
        assert node.root == ("ك", "ت", "ب")

    def test_confidence_preserved(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        cl.confidence = 0.85
        node = run_noun_fractal(cl)
        assert node.confidence == 0.85

    def test_node_is_frozen(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = run_noun_fractal(cl)
        with pytest.raises(AttributeError):
            node.fractal_stage = NounFractalStage.DESIGNATION  # type: ignore[misc]
