"""Tests for the full pipeline."""

from __future__ import annotations

from arabic_engine.cognition.inference_rules import InferenceEngine
from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.enums import TruthState, ValidationState
from arabic_engine.pipeline import run, verify_contracts


def _make_pipeline_result(sentence: str = "كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ"):
    """Run the pipeline on a sentence and return the result."""
    world = WorldModel()
    world.add_fact(
        subject="زَيْد",
        predicate="كَتَبَ",
        obj="رِسَالَة",
        truth_state=TruthState.CERTAIN,
        source="witness",
    )
    engine = InferenceEngine()
    return run(sentence, world=world, inference_engine=engine)


class TestContracts:
    """Layer contracts must be satisfied."""

    def test_contracts_pass(self):
        verify_contracts()


class TestPipeline:
    """End-to-end pipeline tests."""

    def test_normalisation_preserves_input(self):
        result = _make_pipeline_result()
        assert result.normalised, "Normalised text should not be empty"

    def test_tokenisation_produces_four_tokens(self):
        result = _make_pipeline_result()
        assert len(result.tokens) == 4

    def test_lexical_closures_match_tokens(self):
        result = _make_pipeline_result()
        assert len(result.closures) == len(result.tokens)

    def test_syntax_nodes_match_tokens(self):
        result = _make_pipeline_result()
        assert len(result.syntax_nodes) == len(result.tokens)

    def test_concepts_generated(self):
        result = _make_pipeline_result()
        assert len(result.concepts) > 0

    def test_dalala_links_generated(self):
        result = _make_pipeline_result()
        assert len(result.dalala_links) > 0

    def test_proposition_fields(self):
        result = _make_pipeline_result()
        p = result.proposition
        assert p.subject == "زَيْد"
        assert p.predicate == "كَتَبَ"
        assert p.obj == "رِسَالَة"

    def test_evaluation_confidence_in_range(self):
        result = _make_pipeline_result()
        assert 0.0 <= result.eval_result.confidence <= 1.0

    def test_inferences_present(self):
        result = _make_pipeline_result()
        assert len(result.inferences) >= 1

    def test_semantic_roles_present(self):
        result = _make_pipeline_result()
        assert result.semantic_roles["event"] == "كَتَبَ"
        assert result.semantic_roles["agent"] == "زَيْد"
        assert result.semantic_roles["patient"] == "رِسَالَة"

    def test_knowledge_episode_and_evaluation_result(self):
        result = _make_pipeline_result()
        assert result.knowledge_episode.episode_id
        assert result.evaluation_result.validation_state == ValidationState.VALID

    def test_world_update_is_validation_gated(self):
        result = _make_pipeline_result()
        assert result.world_update["applied"] is True
        assert isinstance(result.world_update["fact_id"], int)

    def test_explanation_contains_reasoning_keys(self):
        result = _make_pipeline_result()
        assert "why_agent" in result.explanation
        assert "why_judgement" in result.explanation
        assert "why_rank" in result.explanation


class TestGeneralClosure:
    """General closure verification (Chapter 19)."""

    def test_closure_passes(self):
        from arabic_engine.closure import verify_general_closure

        result = verify_general_closure()
        assert result.closed is True, "General closure verification should pass"
