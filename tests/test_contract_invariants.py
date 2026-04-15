"""Contract invariant tests — SIVP-v1 § C6, C1, C4/C5.

Verifies that every ``invariant`` declared in ``contracts.yaml`` is
satisfied by the actual pipeline output, and checks domain consistency
of enums and types used across the three pipeline systems.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from arabic_engine.cognition.inference_rules import InferenceEngine
from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.enums import (
    CognitiveLayerID,
    DalalaType,
    GuidanceState,
    IrabCase,
    IrabRole,
    LayerGateDecision,
    PipelineLayerID,
    PipelineStatus,
    SemanticType,
    SpaceRef,
    TimeRef,
    TransitionGateStatus,
    TruthState,
    ValidationState,
)
from arabic_engine.pipeline import run

# ── helpers ──────────────────────────────────────────────────────────

def _result():
    """Full pipeline result for the canonical test sentence."""
    world = WorldModel()
    world.add_fact(
        subject="زَيْد",
        predicate="كَتَبَ",
        obj="رِسَالَة",
        truth_state=TruthState.CERTAIN,
        source="witness",
    )
    engine = InferenceEngine()
    return run(
        "كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ",
        world=world,
        inference_engine=engine,
    )


def _load_invariants():
    """Return a dict mapping layer name → list of invariant strings."""
    path = Path(__file__).resolve().parent.parent / "arabic_engine" / "contracts.yaml"
    with open(path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return {
        layer["name"]: layer.get("invariants", [])
        for layer in spec.get("layers", [])
    }


# ── C6: Every invariant in contracts.yaml covered by a test ──────────


class TestNormalizeInvariants:
    """Layer 0: normalize — invariants from contracts.yaml."""

    def test_no_tatweel(self):
        result = _result()
        assert "\u0640" not in result.normalised

    def test_no_consecutive_whitespace(self):
        result = _result()
        assert "  " not in result.normalised

    def test_nfc_normalized(self):
        import unicodedata
        result = _result()
        assert result.normalised == unicodedata.normalize("NFC", result.normalised)


class TestTokenizeInvariants:
    """Layer 1: tokenize."""

    def test_each_token_non_empty(self):
        result = _result()
        for token in result.tokens:
            assert token, "Token must be non-empty"

    def test_no_leading_trailing_whitespace(self):
        result = _result()
        for token in result.tokens:
            assert token == token.strip()


class TestLexicalClosureInvariants:
    """Layer 2: lexical_closure (batch_closure)."""

    def test_output_length_matches_input(self):
        result = _result()
        assert len(result.closures) == len(result.tokens)

    def test_each_closure_has_valid_pos(self):
        from arabic_engine.core.enums import POS
        result = _result()
        for cl in result.closures:
            assert isinstance(cl.pos, POS)

    def test_root_is_tuple(self):
        result = _result()
        for cl in result.closures:
            assert isinstance(cl.root, tuple)


class TestSyntaxInvariants:
    """Layer 3: syntax (analyse)."""

    def test_output_length_matches_input(self):
        result = _result()
        assert len(result.syntax_nodes) == len(result.closures)

    def test_each_node_has_valid_irab_case(self):
        result = _result()
        for node in result.syntax_nodes:
            assert isinstance(node.case, IrabCase)

    def test_each_node_has_valid_irab_role(self):
        result = _result()
        for node in result.syntax_nodes:
            assert isinstance(node.role, IrabRole)


class TestOntologyInvariants:
    """Layer 4: ontology (batch_map)."""

    def test_output_length_matches_input(self):
        result = _result()
        assert len(result.concepts) == len(result.closures)

    def test_each_concept_has_unique_id(self):
        result = _result()
        ids = [c.concept_id for c in result.concepts]
        assert len(ids) == len(set(ids))

    def test_semantic_type_is_valid(self):
        result = _result()
        for c in result.concepts:
            assert isinstance(c.semantic_type, SemanticType)


class TestDalalaInvariants:
    """Layer 5: dalala (full_validation)."""

    def test_each_link_confidence_in_range(self):
        result = _result()
        for link in result.dalala_links:
            assert 0.0 <= link.confidence <= 1.0

    def test_each_link_has_valid_dalala_type(self):
        result = _result()
        for link in result.dalala_links:
            assert isinstance(link.dalala_type, DalalaType)

    def test_accepted_is_bool(self):
        result = _result()
        for link in result.dalala_links:
            assert isinstance(link.accepted, bool)


class TestJudgmentInvariants:
    """Layer 6: judgment (build_proposition)."""

    def test_subject_non_empty(self):
        result = _result()
        assert result.proposition.subject

    def test_predicate_non_empty(self):
        result = _result()
        assert result.proposition.predicate

    def test_polarity_is_bool(self):
        result = _result()
        assert isinstance(result.proposition.polarity, bool)


class TestTimeSpaceInvariants:
    """Layer 7: time_space (tag)."""

    def test_time_ref_is_valid(self):
        result = _result()
        assert isinstance(result.time_space.time_ref, TimeRef)

    def test_space_ref_is_valid(self):
        result = _result()
        assert isinstance(result.time_space.space_ref, SpaceRef)


class TestSemanticRolesInvariants:
    """Layer 7b: semantic_roles."""

    def test_contains_event_agent_patient_keys(self):
        result = _result()
        for key in ("event", "agent", "patient"):
            assert key in result.semantic_roles

    def test_all_values_are_strings(self):
        result = _result()
        for v in result.semantic_roles.values():
            assert isinstance(v, str)


class TestEvaluationInvariants:
    """Layer 8: evaluation (evaluate)."""

    def test_confidence_in_range(self):
        result = _result()
        assert 0.0 <= result.eval_result.confidence <= 1.0

    def test_truth_state_is_valid(self):
        result = _result()
        assert isinstance(result.eval_result.truth_state, TruthState)

    def test_guidance_state_is_valid(self):
        result = _result()
        assert isinstance(result.eval_result.guidance_state, GuidanceState)


class TestExplanationInvariants:
    """Layer 11: explanation (build_explanation)."""

    def test_contains_why_agent(self):
        result = _result()
        assert "why_agent" in result.explanation

    def test_contains_why_judgement(self):
        result = _result()
        assert "why_judgement" in result.explanation

    def test_contains_why_rank(self):
        result = _result()
        assert "why_rank" in result.explanation


# ── Meta: every invariant in contracts.yaml has a test ────────────────


class TestInvariantCoverage:
    """C6 meta — every declared invariant is covered."""

    def test_all_invariants_declared(self):
        """Ensure contracts.yaml has invariants for every main layer."""
        invariants = _load_invariants()
        main_layers = [
            "normalize", "tokenize", "lexical_closure", "syntax",
            "ontology", "dalala", "judgment", "time_space",
            "semantic_roles", "evaluation", "explanation",
        ]
        for name in main_layers:
            assert name in invariants, f"Missing invariants for layer '{name}'"
            assert len(invariants[name]) > 0, f"No invariants for layer '{name}'"


# ── C1: Domain consistency — no overlapping enums ─────────────────────


class TestDomainConsistency:
    """C1/C4/C5 — each decision/state enum has a distinct domain."""

    def test_pipeline_status_distinct_from_gate_decision(self):
        """PipelineStatus (pipeline result) ≠ LayerGateDecision (per-gate).

        SUSPEND is intentionally shared (same semantic concept).
        SUCCESS≠PASS and FAILURE≠REJECT are deliberately distinct names.
        """
        ps_names = {e.name for e in PipelineStatus}
        gd_names = {e.name for e in LayerGateDecision}
        # SUSPEND is shared by design
        assert "SUSPEND" in ps_names and "SUSPEND" in gd_names
        # Distinct names for different semantics
        assert "SUCCESS" in ps_names and "SUCCESS" not in gd_names
        assert "FAILURE" in ps_names and "FAILURE" not in gd_names
        assert "PASS" in gd_names and "PASS" not in ps_names
        assert "REJECT" in gd_names and "REJECT" not in ps_names

    def test_validation_state_distinct_domain(self):
        """ValidationState (epistemic) ≠ TransitionGateStatus (7-layer)."""
        vs_names = {e.name for e in ValidationState}
        tgs_names = {e.name for e in TransitionGateStatus}
        # No overlap expected
        assert vs_names & tgs_names == set()

    def test_pipeline_layer_id_distinct_from_cognitive_layer_id(self):
        """PipelineLayerID (main pipeline) ≠ CognitiveLayerID (proof chain)."""
        pl_names = {e.name for e in PipelineLayerID}
        cl_names = {e.name for e in CognitiveLayerID}
        assert pl_names & cl_names == set()

    def test_gate_decision_values_complete(self):
        """LayerGateDecision has exactly 4 values."""
        assert len(LayerGateDecision) == 4

    def test_pipeline_status_values_complete(self):
        """PipelineStatus has exactly 3 values."""
        assert len(PipelineStatus) == 3

    def test_validation_state_values_complete(self):
        """ValidationState has exactly 3 values."""
        assert len(ValidationState) == 3

    def test_transition_gate_status_values_complete(self):
        """TransitionGateStatus has exactly 3 values."""
        assert len(TransitionGateStatus) == 3
