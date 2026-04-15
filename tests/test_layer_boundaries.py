"""Tests for layer boundaries — اختبارات الحدود بين الطبقات.

Verifies that the output of each layer matches the input contract
of the next layer, ensuring the ascending closure principle is maintained.
"""

from __future__ import annotations

from arabic_engine.cognition.evaluation import build_proposition, evaluate
from arabic_engine.core.enums import (
    DiacriticConsistency,
    EpicLayerID,
)
from arabic_engine.core.types import LayerTrace
from arabic_engine.diacritics.analyzer import analyze as diac_analyze
from arabic_engine.linkage.dalala import full_validation
from arabic_engine.morphology.engine import analyze as morph_analyze
from arabic_engine.signified.ontology import batch_map
from arabic_engine.signifier.root_pattern import batch_closure
from arabic_engine.signifier.unicode_norm import normalize, tokenize
from arabic_engine.syllables.segmenter import segment
from arabic_engine.syntax.syntax import analyse as syn_analyse


class TestE1ToE2Boundary:
    """E1 (Unicode) → E2 (Diacritics): normalized text feeds diacritic analysis."""

    def test_normalized_text_analyzable(self) -> None:
        """Normalized text should be analyzable by diacritic layer."""
        text = "كَتَبَ زَيْدٌ الرِّسَالَةَ"
        normalized = normalize(text)
        tokens = tokenize(normalized)
        for token in tokens:
            result = diac_analyze(token)
            assert result.token == token
            assert isinstance(result.consistency, DiacriticConsistency)


class TestE2ToE3Boundary:
    """E2 (Diacritics) → E3 (Syllables): diacritic analysis feeds syllabification."""

    def test_voweled_token_segmentable(self) -> None:
        """Voweled token from diacritic analysis should be segmentable."""
        token = "كَتَبَ"
        diac = diac_analyze(token)
        assert diac.is_fully_voweled
        syl = segment(token)
        assert syl.is_valid
        assert len(syl.pattern.syllables) > 0


class TestE3ToE4Boundary:
    """E3 (Syllables) → E4 (Morphology): syllabic analysis feeds morphology."""

    def test_segmented_word_analyzable(self) -> None:
        """Segmented word should be analyzable by morphology."""
        word = "كَتَبَ"
        syl = segment(word)
        assert syl.is_valid
        morph = morph_analyze(word)
        assert isinstance(morph, dict)
        assert "root" in morph


class TestE4ToE5Boundary:
    """E4 (Morphology) → E5 (Syntax): morphological output feeds syntax."""

    def test_closures_parseable(self) -> None:
        """LexicalClosures from morphological layer should be parseable by syntax."""
        text = "كَتَبَ زَيْدٌ"
        normalized = normalize(text)
        tokens = tokenize(normalized)
        closures = batch_closure(tokens)
        nodes = syn_analyse(closures)
        assert len(nodes) == len(closures)


class TestE5ToE6Boundary:
    """E5 (Syntax) → E6 (Semantics): syntax output feeds semantic mapping."""

    def test_closures_to_concepts(self) -> None:
        """Closures should be mappable to concepts."""
        text = "كَتَبَ زَيْدٌ"
        normalized = normalize(text)
        tokens = tokenize(normalized)
        closures = batch_closure(tokens)
        concepts = batch_map(closures)
        assert len(concepts) == len(closures)


class TestE6ToE7Boundary:
    """E6 (Semantics) → E7 (Cognition): semantic output feeds cognition."""

    def test_concepts_and_links_build_proposition(self) -> None:
        """Concepts and dalala links should produce a valid proposition."""
        text = "كَتَبَ زَيْدٌ الرِّسَالَةَ"
        normalized = normalize(text)
        tokens = tokenize(normalized)
        closures = batch_closure(tokens)
        concepts = batch_map(closures)
        links = full_validation(closures, concepts)
        proposition = build_proposition(closures, concepts, links)
        assert proposition.subject != ""
        assert proposition.predicate != ""


class TestE7ToE8Boundary:
    """E7 (Cognition) → E8 (Judgement): cognitive output feeds judgement."""

    def test_proposition_evaluatable(self) -> None:
        """Proposition from cognition should be evaluatable."""
        text = "كَتَبَ زَيْدٌ الرِّسَالَةَ"
        normalized = normalize(text)
        tokens = tokenize(normalized)
        closures = batch_closure(tokens)
        concepts = batch_map(closures)
        links = full_validation(closures, concepts)
        proposition = build_proposition(closures, concepts, links)
        eval_result = evaluate(proposition, links)
        assert 0 <= eval_result.confidence <= 1


class TestEpicLayerIDEnum:
    """Tests for EpicLayerID enum."""

    def test_all_epic_layers_exist(self) -> None:
        """All 8 epic layers should exist."""
        expected = ["UNICODE", "DIACRITICS", "SYLLABLES", "MORPHOLOGY",
                    "SYNTAX", "SEMANTICS", "COGNITION", "JUDGEMENT"]
        for name in expected:
            assert hasattr(EpicLayerID, name)

    def test_epic_layer_count(self) -> None:
        """There should be exactly 8 epic layers."""
        assert len(list(EpicLayerID)) == 8


class TestLayerTrace:
    """Tests for the unified LayerTrace type."""

    def test_create_trace(self) -> None:
        """LayerTrace should be constructible."""
        trace = LayerTrace(
            layer_id="E1",
            layer_name="Unicode",
            input_hash="abc123",
            input_summary="كَتَبَ",
            output_summary="كَتَبَ (normalized)",
            rules_applied=("NFC", "remove_tatweel"),
            confidence=1.0,
            duration_ms=0.5,
            timestamp="2026-04-15T20:00:00Z",
        )
        assert trace.layer_id == "E1"
        assert trace.confidence == 1.0
        assert len(trace.rules_applied) == 2

    def test_trace_is_frozen(self) -> None:
        """LayerTrace should be immutable."""
        trace = LayerTrace(
            layer_id="E2",
            layer_name="Diacritics",
            input_hash="def456",
            input_summary="test",
            output_summary="test",
            rules_applied=(),
            confidence=0.9,
            duration_ms=1.0,
            timestamp="2026-01-01T00:00:00Z",
        )
        try:
            trace.confidence = 0.5  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass
