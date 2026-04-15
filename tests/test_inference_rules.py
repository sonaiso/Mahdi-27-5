from __future__ import annotations

from arabic_engine.cognition.inference_rules import (
    InferenceEngine,
    _event_existence_rule,
    _negation_rule,
    _transitivity_rule,
)
from arabic_engine.core.types import Proposition


def _prop(
    subject: str = "زَيْد",
    predicate: str = "كَتَبَ",
    obj: str = "رِسَالَة",
    polarity: bool = True,
) -> Proposition:
    return Proposition(
        subject=subject, predicate=predicate, obj=obj, polarity=polarity,
    )


# ── event_existence_rule ───────────────────────────────────────────


def test_event_existence_fires() -> None:
    result = _event_existence_rule([_prop()])
    assert result is not None
    assert result.rule_name == "event_existence"


def test_event_existence_conclusion_predicate() -> None:
    result = _event_existence_rule([_prop()])
    assert result is not None
    assert result.conclusion.predicate == "وُجِدَ"


def test_event_existence_confidence() -> None:
    result = _event_existence_rule([_prop()])
    assert result is not None
    assert result.confidence == 0.9


def test_event_existence_preserves_time() -> None:
    p = _prop()
    result = _event_existence_rule([p])
    assert result is not None
    assert result.conclusion.time == p.time


def test_event_existence_negative_skipped() -> None:
    result = _event_existence_rule([_prop(polarity=False)])
    assert result is None


# ── transitivity_rule ──────────────────────────────────────────────


def test_transitivity_fires() -> None:
    p1 = _prop(subject="أ", predicate="يعرف", obj="ب")
    p2 = _prop(subject="ب", predicate="يعرف", obj="ج")
    result = _transitivity_rule([p1, p2])
    assert result is not None


def test_transitivity_conclusion() -> None:
    p1 = _prop(subject="أ", predicate="يعرف", obj="ب")
    p2 = _prop(subject="ب", predicate="يعرف", obj="ج")
    result = _transitivity_rule([p1, p2])
    assert result is not None
    assert result.conclusion.subject == "أ"
    assert result.conclusion.obj == "ج"


def test_transitivity_confidence() -> None:
    p1 = _prop(subject="أ", predicate="يعرف", obj="ب")
    p2 = _prop(subject="ب", predicate="يعرف", obj="ج")
    result = _transitivity_rule([p1, p2])
    assert result is not None
    assert result.confidence == 0.85


def test_transitivity_no_match() -> None:
    p1 = _prop(subject="أ", predicate="يعرف", obj="ب")
    p2 = _prop(subject="ج", predicate="يعرف", obj="د")
    result = _transitivity_rule([p1, p2])
    assert result is None


# ── negation_rule ──────────────────────────────────────────────────


def test_negation_fires() -> None:
    p1 = _prop(polarity=True)
    p2 = _prop(polarity=False)
    result = _negation_rule([p1, p2])
    assert result is not None
    assert result.rule_name == "contradiction"


def test_negation_confidence_zero() -> None:
    result = _negation_rule([_prop(polarity=True), _prop(polarity=False)])
    assert result is not None
    assert result.confidence == 0.0


def test_negation_valid_false() -> None:
    result = _negation_rule([_prop(polarity=True), _prop(polarity=False)])
    assert result is not None
    assert result.valid is False


def test_negation_no_match() -> None:
    result = _negation_rule([_prop(polarity=True), _prop(polarity=True)])
    assert result is None


# ── InferenceEngine ────────────────────────────────────────────────


def test_engine_default_rules() -> None:
    engine = InferenceEngine()
    assert len(engine.rules) == 3


def test_engine_run_returns_list() -> None:
    engine = InferenceEngine()
    result = engine.run([_prop()])
    assert isinstance(result, list)


def test_engine_run_empty() -> None:
    engine = InferenceEngine()
    assert engine.run([]) == []


def test_engine_run_fires_event_existence() -> None:
    engine = InferenceEngine()
    results = engine.run([_prop()])
    names = [r.rule_name for r in results]
    assert "event_existence" in names


def test_engine_custom_rules() -> None:
    engine = InferenceEngine(rules=[_event_existence_rule])
    assert len(engine.rules) == 1


def test_engine_run_until_fixed() -> None:
    engine = InferenceEngine()
    results = engine.run_until_fixed([_prop()])
    assert isinstance(results, list)
    assert len(results) >= 1


def test_engine_run_until_fixed_max_iterations() -> None:
    engine = InferenceEngine()
    results = engine.run_until_fixed([_prop()], max_iterations=1)
    assert isinstance(results, list)
