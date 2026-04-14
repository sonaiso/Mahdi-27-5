"""tests/test_evaluation.py — comprehensive tests for evaluation module.

Covers:
* build_proposition: verb-subject-object extraction, past/present tense
  detection, no verb, no nouns, ISM-only, order preservation.
* evaluate: CERTAIN/PROBABLE/POSSIBLE/DOUBTFUL thresholds, empty links,
  single link, confidence rounding.
"""

from __future__ import annotations

import unittest

from arabic_engine.cognition.evaluation import build_proposition, evaluate
from arabic_engine.core.enums import (
    DalalaType,
    GuidanceState,
    POS,
    SemanticType,
    TimeRef,
    TruthState,
)
from arabic_engine.core.types import (
    Concept,
    DalalaLink,
    EvalResult,
    LexicalClosure,
    Proposition,
)


# ── helpers ─────────────────────────────────────────────────────────

def _closure(lemma: str, pos: POS, pattern: str = "") -> LexicalClosure:
    """Shortcut to build a minimal LexicalClosure."""
    return LexicalClosure(
        surface=lemma,
        lemma=lemma,
        root=(),
        pattern=pattern,
        pos=pos,
    )


def _link(confidence: float) -> DalalaLink:
    """Shortcut to build a DalalaLink with the given confidence."""
    return DalalaLink(
        source_lemma="x",
        target_concept_id=1,
        dalala_type=DalalaType.MUTABAQA,
        accepted=True,
        confidence=confidence,
    )


def _concept(cid: int = 1) -> Concept:
    return Concept(
        concept_id=cid,
        label="test",
        semantic_type=SemanticType.ENTITY,
        properties={},
    )


def _prop(subject="", predicate="", obj="") -> Proposition:
    return Proposition(subject=subject, predicate=predicate, obj=obj)


# ── TestBuildProposition ────────────────────────────────────────────

class TestBuildProposition(unittest.TestCase):
    """Tests for build_proposition()."""

    def test_verb_subject_object(self):
        closures = [
            _closure("كَتَبَ", POS.FI3L, "فَعَلَ"),
            _closure("زَيْد", POS.ISM),
            _closure("كِتَاب", POS.ISM),
        ]
        prop = build_proposition(closures, [_concept()], [])
        self.assertEqual(prop.predicate, "كَتَبَ")
        self.assertEqual(prop.subject, "زَيْد")
        self.assertEqual(prop.obj, "كِتَاب")
        self.assertTrue(prop.polarity)

    def test_past_tense_detection(self):
        closures = [
            _closure("ذَهَبَ", POS.FI3L, "فَعَلَ"),
            _closure("عَلِيّ", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.time, TimeRef.PAST)

    def test_present_tense_detection(self):
        closures = [
            _closure("يَكْتُبُ", POS.FI3L, "يَفْعَلُ"),
            _closure("عَلِيّ", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.time, TimeRef.PRESENT)

    def test_unknown_pattern_leaves_time_unspecified(self):
        closures = [
            _closure("اُكْتُبْ", POS.FI3L, "اُفْعُلْ"),
            _closure("عَلِيّ", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.time, TimeRef.UNSPECIFIED)

    def test_no_verb(self):
        closures = [
            _closure("زَيْد", POS.ISM),
            _closure("طَالِب", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.predicate, "")
        self.assertEqual(prop.subject, "زَيْد")
        self.assertEqual(prop.obj, "طَالِب")

    def test_no_nouns(self):
        closures = [_closure("كَتَبَ", POS.FI3L, "فَعَلَ")]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.predicate, "كَتَبَ")
        self.assertEqual(prop.subject, "")
        self.assertEqual(prop.obj, "")

    def test_empty_closures(self):
        prop = build_proposition([], [], [])
        self.assertEqual(prop.subject, "")
        self.assertEqual(prop.predicate, "")
        self.assertEqual(prop.obj, "")
        self.assertEqual(prop.time, TimeRef.UNSPECIFIED)
        self.assertTrue(prop.polarity)

    def test_ism_only_single(self):
        closures = [_closure("زَيْد", POS.ISM)]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.subject, "زَيْد")
        self.assertEqual(prop.obj, "")
        self.assertEqual(prop.predicate, "")

    def test_order_preserved_verb_after_nouns(self):
        closures = [
            _closure("زَيْد", POS.ISM),
            _closure("كَتَبَ", POS.FI3L, "فَعَلَ"),
            _closure("كِتَاب", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.subject, "زَيْد")
        self.assertEqual(prop.predicate, "كَتَبَ")
        self.assertEqual(prop.obj, "كِتَاب")

    def test_only_first_verb_used(self):
        closures = [
            _closure("كَتَبَ", POS.FI3L, "فَعَلَ"),
            _closure("يَقْرَأُ", POS.FI3L, "يَفْعَلُ"),
            _closure("زَيْد", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.predicate, "كَتَبَ")
        self.assertEqual(prop.time, TimeRef.PAST)

    def test_harf_ignored(self):
        closures = [
            _closure("فِي", POS.HARF),
            _closure("كَتَبَ", POS.FI3L, "فَعَلَ"),
            _closure("زَيْد", POS.ISM),
        ]
        prop = build_proposition(closures, [], [])
        self.assertEqual(prop.predicate, "كَتَبَ")
        self.assertEqual(prop.subject, "زَيْد")


# ── TestEvaluate ────────────────────────────────────────────────────

class TestEvaluate(unittest.TestCase):
    """Tests for evaluate()."""

    def test_certain_threshold(self):
        prop = _prop("s", "p", "o")
        result = evaluate(prop, [_link(0.95)])
        self.assertEqual(result.truth_state, TruthState.CERTAIN)

    def test_certain_exact_boundary(self):
        result = evaluate(_prop(), [_link(0.9)])
        self.assertEqual(result.truth_state, TruthState.CERTAIN)

    def test_probable_threshold(self):
        result = evaluate(_prop(), [_link(0.8)])
        self.assertEqual(result.truth_state, TruthState.PROBABLE)

    def test_probable_exact_boundary(self):
        result = evaluate(_prop(), [_link(0.7)])
        self.assertEqual(result.truth_state, TruthState.PROBABLE)

    def test_possible_threshold(self):
        result = evaluate(_prop(), [_link(0.55)])
        self.assertEqual(result.truth_state, TruthState.POSSIBLE)

    def test_possible_exact_boundary(self):
        result = evaluate(_prop(), [_link(0.4)])
        self.assertEqual(result.truth_state, TruthState.POSSIBLE)

    def test_doubtful_threshold(self):
        result = evaluate(_prop(), [_link(0.2)])
        self.assertEqual(result.truth_state, TruthState.DOUBTFUL)

    def test_empty_links_gives_doubtful(self):
        result = evaluate(_prop(), [])
        self.assertEqual(result.truth_state, TruthState.DOUBTFUL)
        self.assertEqual(result.confidence, 0.0)

    def test_single_link_confidence(self):
        result = evaluate(_prop(), [_link(0.75)])
        self.assertAlmostEqual(result.confidence, 0.75)

    def test_average_confidence_multiple_links(self):
        links = [_link(0.8), _link(0.6)]
        result = evaluate(_prop(), links)
        self.assertAlmostEqual(result.confidence, 0.7)
        self.assertEqual(result.truth_state, TruthState.PROBABLE)

    def test_confidence_rounding(self):
        links = [_link(0.333), _link(0.666), _link(0.777)]
        result = evaluate(_prop(), links)
        expected = round((0.333 + 0.666 + 0.777) / 3, 4)
        self.assertEqual(result.confidence, expected)

    def test_guidance_state_always_not_applicable(self):
        result = evaluate(_prop(), [_link(0.95)])
        self.assertEqual(result.guidance_state, GuidanceState.NOT_APPLICABLE)

    def test_proposition_passed_through(self):
        prop = _prop("subj", "pred", "obj")
        result = evaluate(prop, [_link(0.5)])
        self.assertIs(result.proposition, prop)


if __name__ == "__main__":
    unittest.main()
