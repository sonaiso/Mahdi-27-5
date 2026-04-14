"""Tests for arabic_engine.signified.ontology — concept mapping."""

from __future__ import annotations

from arabic_engine.core.enums import POS, SemanticType
from arabic_engine.core.types import Concept, LexicalClosure
from arabic_engine.signified.ontology import batch_map, map_concept

# ── helpers ──────────────────────────────────────────────────────────────


def _make_closure(
    lemma: str = "كَتَبَ",
    pos: POS = POS.FI3L,
    surface: str = "كَتَبَ",
    root: tuple[str, ...] = ("ك", "ت", "ب"),
    pattern: str = "فَعَلَ",
) -> LexicalClosure:
    """Return a minimal LexicalClosure for testing."""
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=root,
        pattern=pattern,
        pos=pos,
    )


# ── TestMapConcept ───────────────────────────────────────────────────────


class TestMapConcept:
    """Tests for map_concept()."""

    def test_known_lemma_returns_db_concept(self):
        """A lemma present in _CONCEPT_DB returns the pre-registered concept."""
        closure = _make_closure(lemma="كَتَبَ", pos=POS.FI3L)
        concept = map_concept(closure)
        assert concept.concept_id == 101
        assert concept.label == "كتابة"
        assert concept.semantic_type == SemanticType.EVENT

    def test_known_entity_zayd(self):
        """'زَيْد' maps to a known entity concept."""
        closure = _make_closure(lemma="زَيْد", pos=POS.ISM)
        concept = map_concept(closure)
        assert concept.concept_id == 201
        assert concept.semantic_type == SemanticType.ENTITY
        assert concept.properties.get("proper_noun") is True

    def test_known_entity_risala(self):
        """'رِسَالَة' maps to a known entity concept."""
        closure = _make_closure(lemma="رِسَالَة", pos=POS.ISM)
        concept = map_concept(closure)
        assert concept.concept_id == 301
        assert concept.semantic_type == SemanticType.ENTITY

    def test_known_time_adverb_ams(self):
        """'أَمْس' maps to a known attribute concept."""
        closure = _make_closure(lemma="أَمْس", pos=POS.ZARF)
        concept = map_concept(closure)
        assert concept.concept_id == 401
        assert concept.semantic_type == SemanticType.ATTRIBUTE

    def test_known_time_adverb_ghad(self):
        """'غَد' maps to a known attribute concept."""
        closure = _make_closure(lemma="غَد", pos=POS.ZARF)
        concept = map_concept(closure)
        assert concept.concept_id == 402
        assert concept.properties.get("time_ref") == "future"

    def test_unknown_lemma_auto_generates(self):
        """An unknown lemma auto-generates a new concept."""
        closure = _make_closure(lemma="شَرِبَ", pos=POS.FI3L)
        concept = map_concept(closure)
        assert concept.concept_id > 900
        assert concept.label == "شَرِبَ"
        assert concept.semantic_type == SemanticType.EVENT

    def test_unknown_ism_maps_to_entity(self):
        """An unknown ISM lemma auto-maps to ENTITY."""
        closure = _make_closure(lemma="بَيْت", pos=POS.ISM)
        concept = map_concept(closure)
        assert concept.semantic_type == SemanticType.ENTITY

    def test_unknown_sifa_maps_to_attribute(self):
        """An unknown SIFA lemma auto-maps to ATTRIBUTE."""
        closure = _make_closure(lemma="كَبِير", pos=POS.SIFA)
        concept = map_concept(closure)
        assert concept.semantic_type == SemanticType.ATTRIBUTE

    def test_unknown_harf_maps_to_relation(self):
        """An unknown HARF lemma auto-maps to RELATION."""
        closure = _make_closure(lemma="فِي", pos=POS.HARF)
        concept = map_concept(closure)
        assert concept.semantic_type == SemanticType.RELATION

    def test_unknown_zarf_maps_to_attribute(self):
        """An unknown ZARF lemma auto-maps to ATTRIBUTE."""
        closure = _make_closure(lemma="هُنَا", pos=POS.ZARF)
        concept = map_concept(closure)
        assert concept.semantic_type == SemanticType.ATTRIBUTE

    def test_unknown_pos_defaults_to_entity(self):
        """A POS not in _POS_TO_STYPE defaults to ENTITY."""
        closure = _make_closure(lemma="شَيْء", pos=POS.UNKNOWN)
        concept = map_concept(closure)
        assert concept.semantic_type == SemanticType.ENTITY

    def test_auto_generated_ids_increment(self):
        """Successive unknown lookups produce distinct auto-incremented IDs."""
        c1 = map_concept(_make_closure(lemma="أَوَّلٌ", pos=POS.ISM))
        c2 = map_concept(_make_closure(lemma="ثَانٍ", pos=POS.ISM))
        assert c2.concept_id > c1.concept_id

    def test_returns_concept_type(self):
        """map_concept always returns a Concept instance."""
        concept = map_concept(_make_closure())
        assert isinstance(concept, Concept)


# ── TestBatchMap ─────────────────────────────────────────────────────────


class TestBatchMap:
    """Tests for batch_map()."""

    def test_empty_list(self):
        """batch_map of an empty list returns an empty list."""
        assert batch_map([]) == []

    def test_single_closure(self):
        """batch_map of one closure returns one concept."""
        closures = [_make_closure(lemma="كَتَبَ")]
        result = batch_map(closures)
        assert len(result) == 1
        assert result[0].label == "كتابة"

    def test_preserves_order(self):
        """batch_map preserves input order."""
        closures = [
            _make_closure(lemma="كَتَبَ", pos=POS.FI3L),
            _make_closure(lemma="زَيْد", pos=POS.ISM),
            _make_closure(lemma="رِسَالَة", pos=POS.ISM),
        ]
        result = batch_map(closures)
        assert len(result) == 3
        assert result[0].concept_id == 101  # كَتَبَ
        assert result[1].concept_id == 201  # زَيْد
        assert result[2].concept_id == 301  # رِسَالَة

    def test_mixed_known_unknown(self):
        """batch_map handles a mix of known and unknown lemmas."""
        closures = [
            _make_closure(lemma="كَتَبَ", pos=POS.FI3L),
            _make_closure(lemma="مَجْهُول", pos=POS.ISM),
        ]
        result = batch_map(closures)
        assert result[0].concept_id == 101
        assert result[1].concept_id > 900

    def test_all_results_are_concepts(self):
        """Every element of batch_map output is a Concept."""
        closures = [
            _make_closure(lemma="أ", pos=POS.ISM),
            _make_closure(lemma="ب", pos=POS.FI3L),
        ]
        for c in batch_map(closures):
            assert isinstance(c, Concept)
