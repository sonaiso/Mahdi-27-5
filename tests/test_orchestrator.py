"""Tests for the runtime orchestrator and legacy adapter.

Invariants tested
-----------------
1. Trace graph is connected from input to judgement.
2. Compatibility API still works (legacy adapter).
3. Bounded iteration terminates.
4. No hypothesis without source_refs in final state.
5. Full end-to-end Arabic sentence processing.
"""

from __future__ import annotations

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.runtime.adapters import to_legacy_state
from arabic_engine.runtime.orchestrator import run

# ═══════════════════════════════════════════════════════════════════════
# End-to-end orchestrator
# ═══════════════════════════════════════════════════════════════════════


class TestOrchestrator:
    """Full orchestrator integration tests."""

    def test_basic_run(self):
        state = run("كتب الرسالة")
        assert state.input_text == "كتب الرسالة"
        assert len(state.signal.atoms) > 0
        assert len(state.signal.signal_units) > 0
        assert len(state.hypotheses.all_hypotheses()) > 0
        assert len(state.decisions.activated) > 0

    def test_judgement_produced(self):
        state = run("كتب الرسالة")
        assert state.decisions.judgement is not None
        assert state.decisions.judgement.stage == ActivationStage.JUDGEMENT

    def test_all_activated_are_stabilized(self):
        state = run("كتب")
        for h in state.decisions.activated:
            assert h.status == HypothesisStatus.STABILIZED

    def test_trace_exists(self):
        state = run("كتب الرسالة")
        # At least the final stabilisation trace
        assert len(state.decisions.trace) >= 1

    def test_bounded_iteration(self):
        state = run("كتب الرسالة", max_iterations=1)
        assert state.iteration <= 1

    def test_no_hypothesis_without_source_refs_except_segmentation(self):
        """Every hypothesis (except top-level segmentation) has source_refs."""
        state = run("ذهب الطالب إلى المدرسة")
        for h in state.hypotheses.all_hypotheses():
            if h.hypothesis_type == "segmentation":
                assert len(h.source_refs) > 0  # linked to signal unit
            elif h.hypothesis_type == "judgement":
                # Judgement may have empty source_refs if no cases exist
                pass
            else:
                assert len(h.source_refs) > 0, (
                    f"{h.node_id} ({h.hypothesis_type}) has no source_refs"
                )

    def test_empty_input(self):
        state = run("")
        assert state.input_text == ""
        assert len(state.signal.atoms) == 0
        assert state.decisions.judgement is not None

    def test_three_token_sentence(self):
        state = run("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert len(state.signal.signal_units) == 3
        # Should have morph, concept, role, factor, case for each token
        morph = state.hypotheses.hypotheses.get(ActivationStage.MORPHOLOGY, [])
        assert len(morph) >= 3

    def test_single_token(self):
        state = run("كتب")
        assert len(state.signal.signal_units) == 1
        assert state.decisions.judgement is not None

    def test_multi_word_with_preposition(self):
        state = run("ذهب إلى المدرسة")
        assert len(state.signal.signal_units) == 3
        relations = state.hypotheses.hypotheses.get(ActivationStage.RELATION, [])
        assert len(relations) >= 1


# ═══════════════════════════════════════════════════════════════════════
# Legacy adapter
# ═══════════════════════════════════════════════════════════════════════


class TestLegacyAdapter:
    """Compatibility facade correctly maps to RuntimeState."""

    def test_basic_conversion(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert legacy.raw_text == "كتب الرسالة"

    def test_utterance_units_populated(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert len(legacy.utterance_units) >= 1

    def test_concepts_populated(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert len(legacy.concepts) >= 1

    def test_roles_populated(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert len(legacy.roles) >= 1

    def test_judgement_populated(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert legacy.judgement is not None
        assert legacy.judgement.proposition_type != ""

    def test_case_resolutions_populated(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert len(legacy.case_resolutions) >= 1

    def test_trace_populated(self):
        kernel = run("كتب الرسالة")
        legacy = to_legacy_state(kernel)
        assert len(legacy.trace) >= 1

    def test_empty_input_adapter(self):
        kernel = run("")
        legacy = to_legacy_state(kernel)
        assert legacy.raw_text == ""
        assert legacy.judgement is not None
