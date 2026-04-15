from __future__ import annotations

from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.enums import TruthState, ValidationState
from arabic_engine.core.types import Proposition, WorldFact

# ── add_fact ───────────────────────────────────────────────────────


def test_add_fact_returns_world_fact() -> None:
    wm = WorldModel()
    f = wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة")
    assert isinstance(f, WorldFact)


def test_add_fact_increments_id() -> None:
    wm = WorldModel()
    f1 = wm.add_fact("أ", "ب", "ج")
    f2 = wm.add_fact("د", "هـ", "و")
    assert f1.fact_id != f2.fact_id


def test_add_fact_default_truth_state() -> None:
    wm = WorldModel()
    f = wm.add_fact("أ", "ب", "ج")
    assert f.truth_state == TruthState.CERTAIN


def test_add_fact_custom_truth_state() -> None:
    wm = WorldModel()
    f = wm.add_fact("أ", "ب", "ج", truth_state=TruthState.PROBABLE)
    assert f.truth_state == TruthState.PROBABLE


# ── lookup ─────────────────────────────────────────────────────────


def test_lookup_by_subject() -> None:
    wm = WorldModel()
    wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة")
    results = wm.lookup("زَيْد")
    assert len(results) >= 1
    assert results[0].subject == "زَيْد"


def test_lookup_by_subject_empty() -> None:
    wm = WorldModel()
    assert wm.lookup("لا_يوجد") == []


def test_lookup_with_predicate_filter() -> None:
    wm = WorldModel()
    wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة")
    wm.add_fact("زَيْد", "قَرَأَ", "كِتَاب")
    results = wm.lookup("زَيْد", predicate="كَتَبَ")
    assert len(results) == 1
    assert results[0].predicate == "كَتَبَ"


def test_lookup_predicate_no_match() -> None:
    wm = WorldModel()
    wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة")
    assert wm.lookup("زَيْد", predicate="ذَهَبَ") == []


# ── matches ────────────────────────────────────────────────────────


def test_matches_found() -> None:
    wm = WorldModel()
    wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة")
    p = Proposition(subject="زَيْد", predicate="كَتَبَ", obj="رِسَالَة")
    result = wm.matches(p)
    assert result is not None
    assert isinstance(result, WorldFact)


def test_matches_not_found() -> None:
    wm = WorldModel()
    p = Proposition(subject="غريب", predicate="فَعَلَ", obj="شيء")
    assert wm.matches(p) is None


def test_matches_requires_obj_match() -> None:
    wm = WorldModel()
    wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة")
    p = Proposition(subject="زَيْد", predicate="كَتَبَ", obj="كِتَاب")
    assert wm.matches(p) is None


# ── confidence_adjustment ──────────────────────────────────────────


def test_confidence_certain() -> None:
    wm = WorldModel()
    wm.add_fact("أ", "ب", "ج", truth_state=TruthState.CERTAIN)
    p = Proposition(subject="أ", predicate="ب", obj="ج")
    assert wm.confidence_adjustment(p) == 1.0


def test_confidence_probable() -> None:
    wm = WorldModel()
    wm.add_fact("أ", "ب", "ج", truth_state=TruthState.PROBABLE)
    p = Proposition(subject="أ", predicate="ب", obj="ج")
    assert wm.confidence_adjustment(p) == 0.8


def test_confidence_false() -> None:
    wm = WorldModel()
    wm.add_fact("أ", "ب", "ج", truth_state=TruthState.FALSE)
    p = Proposition(subject="أ", predicate="ب", obj="ج")
    assert wm.confidence_adjustment(p) == 0.1


def test_confidence_no_match() -> None:
    wm = WorldModel()
    p = Proposition(subject="غريب", predicate="ب", obj="ج")
    assert wm.confidence_adjustment(p) == 0.5


def test_confidence_other_state() -> None:
    wm = WorldModel()
    wm.add_fact("أ", "ب", "ج", truth_state=TruthState.POSSIBLE)
    p = Proposition(subject="أ", predicate="ب", obj="ج")
    assert wm.confidence_adjustment(p) == 0.5


# ── apply_validated_proposition ────────────────────────────────────


def test_apply_validated_valid() -> None:
    wm = WorldModel()
    p = Proposition(subject="أ", predicate="ب", obj="ج")
    result = wm.apply_validated_proposition(p, ValidationState.VALID)
    assert result["applied"] is True
    assert isinstance(result["fact_id"], int)


def test_apply_validated_invalid() -> None:
    wm = WorldModel()
    p = Proposition(subject="أ", predicate="ب", obj="ج")
    result = wm.apply_validated_proposition(p, ValidationState.INVALID)
    assert result["applied"] is False
    assert result["fact_id"] is None


# ── all_facts ──────────────────────────────────────────────────────


def test_all_facts_empty() -> None:
    wm = WorldModel()
    assert wm.all_facts == []


def test_all_facts_after_add() -> None:
    wm = WorldModel()
    wm.add_fact("أ", "ب", "ج")
    wm.add_fact("د", "هـ", "و")
    assert len(wm.all_facts) == 2
