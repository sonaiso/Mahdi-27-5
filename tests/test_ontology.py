from __future__ import annotations

from arabic_engine.core.enums import POS, SemanticType
from arabic_engine.core.types import Concept, LexicalClosure
from arabic_engine.signified.ontology import batch_map, map_concept


def _closure(lemma: str, pos: POS = POS.ISM) -> LexicalClosure:
    return LexicalClosure(
        surface=lemma,
        lemma=lemma,
        root=("x",),
        pattern="فَعَلَ",
        pos=pos,
    )


# ── Known lemma tests ──────────────────────────────────────────────


def test_map_known_verb() -> None:
    c = map_concept(_closure("كَتَبَ", POS.FI3L))
    assert c.concept_id == 101
    assert c.semantic_type == SemanticType.EVENT


def test_map_known_entity_zayd() -> None:
    c = map_concept(_closure("زَيْد"))
    assert c.concept_id == 201
    assert c.semantic_type == SemanticType.ENTITY


def test_map_known_entity_risala() -> None:
    c = map_concept(_closure("رِسَالَة"))
    assert c.concept_id == 301
    assert c.semantic_type == SemanticType.ENTITY


def test_map_known_time_adverb_ams() -> None:
    c = map_concept(_closure("أَمْس"))
    assert c.concept_id == 401
    assert c.semantic_type == SemanticType.ATTRIBUTE


def test_map_known_time_adverb_ghad() -> None:
    c = map_concept(_closure("غَد"))
    assert c.concept_id == 402


# ── Unknown lemma tests ────────────────────────────────────────────


def test_map_unknown_lemma_creates_new_concept() -> None:
    c = map_concept(_closure("مجهول_ontology_test_1"))
    assert isinstance(c, Concept)
    assert c.concept_id > 900


def test_unknown_verb_mapped_as_event() -> None:
    c = map_concept(_closure("مجهول_ontology_test_2", POS.FI3L))
    assert c.semantic_type == SemanticType.EVENT


def test_unknown_noun_mapped_as_entity() -> None:
    c = map_concept(_closure("مجهول_ontology_test_3", POS.ISM))
    assert c.semantic_type == SemanticType.ENTITY


def test_unknown_harf_mapped_as_relation() -> None:
    c = map_concept(_closure("مجهول_ontology_test_4", POS.HARF))
    assert c.semantic_type == SemanticType.RELATION


def test_unknown_sifa_mapped_as_attribute() -> None:
    c = map_concept(_closure("مجهول_ontology_test_5", POS.SIFA))
    assert c.semantic_type == SemanticType.ATTRIBUTE


# ── batch_map tests ────────────────────────────────────────────────


def test_batch_map_returns_list() -> None:
    closures = [_closure("كَتَبَ", POS.FI3L), _closure("زَيْد")]
    result = batch_map(closures)
    assert isinstance(result, list)
    assert len(result) == 2


def test_batch_map_preserves_order() -> None:
    closures = [_closure("كَتَبَ", POS.FI3L), _closure("زَيْد")]
    result = batch_map(closures)
    assert result[0].concept_id == 101
    assert result[1].concept_id == 201


def test_batch_map_empty_list() -> None:
    assert batch_map([]) == []


# ── Label tests ────────────────────────────────────────────────────


def test_concept_has_correct_label() -> None:
    c = map_concept(_closure("كَتَبَ", POS.FI3L))
    assert c.label == "كتابة"


def test_unknown_concept_label_matches_lemma() -> None:
    lemma = "مجهول_ontology_test_6"
    c = map_concept(_closure(lemma))
    assert c.label == lemma
