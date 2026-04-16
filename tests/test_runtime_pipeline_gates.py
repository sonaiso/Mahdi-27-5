"""Runtime pipeline gate tests — anti-jump and stage gate enforcement.

Verifies that the operational pipeline (Utterance → Judgement) enforces
sequential stage execution, records gate decisions, and handles errors
gracefully.
"""

from __future__ import annotations

from arabic_engine.runtime_pipeline import (
    PipelineStage,
    RuntimeState,
    _stage_gate,
    run_pipeline,
)

# ── Stage gate enforcement ──────────────────────────────────────────


class TestStageGate:
    """Anti-jump enforcement in the runtime pipeline."""

    def test_first_stage_always_allowed(self):
        state = RuntimeState(raw_text="test")
        assert _stage_gate(state, PipelineStage.UTTERANCE) is True

    def test_second_stage_requires_first(self):
        state = RuntimeState(raw_text="test")
        assert _stage_gate(state, PipelineStage.CONCEPT) is False

    def test_second_stage_allowed_after_first_completed(self):
        state = RuntimeState(raw_text="test")
        state.completed_stages.append("UTTERANCE")
        assert _stage_gate(state, PipelineStage.CONCEPT) is True

    def test_jump_rejected(self):
        """Cannot jump from UTTERANCE to AXIS (skipping CONCEPT)."""
        state = RuntimeState(raw_text="test")
        state.completed_stages.append("UTTERANCE")
        # AXIS requires CONCEPT as predecessor
        assert _stage_gate(state, PipelineStage.AXIS) is False

    def test_rejected_gate_records_decision(self):
        state = RuntimeState(raw_text="test")
        _stage_gate(state, PipelineStage.CONCEPT)
        assert len(state.stage_decisions) == 1
        assert state.stage_decisions[0]["decision"] == "REJECT"
        assert "UTTERANCE" in state.stage_decisions[0]["reason"]


# ── Full pipeline gate records ──────────────────────────────────────


class TestPipelineGateRecords:
    """run_pipeline records gate decisions for every stage."""

    def test_completed_stages_count(self):
        result = run_pipeline("ذهب الطالبُ إلى المدرسة")
        assert len(result.completed_stages) == 8

    def test_completed_stages_order(self):
        result = run_pipeline("ذهب الطالبُ إلى المدرسة")
        expected = [s.name for s in PipelineStage]
        assert result.completed_stages == expected

    def test_all_stage_decisions_pass(self):
        result = run_pipeline("ذهب الطالبُ إلى المدرسة")
        for decision in result.stage_decisions:
            assert decision["decision"] == "PASS"

    def test_stage_decisions_count_matches_stages(self):
        result = run_pipeline("ذهب الطالبُ إلى المدرسة")
        assert len(result.stage_decisions) == 8

    def test_empty_input_still_records_decisions(self):
        result = run_pipeline("")
        assert len(result.stage_decisions) > 0

    def test_stage_decision_has_reason(self):
        result = run_pipeline("كتب")
        for decision in result.stage_decisions:
            assert decision["reason"], f"Missing reason for {decision['stage']}"

    def test_stage_decision_has_stage_name(self):
        result = run_pipeline("كتب")
        for decision in result.stage_decisions:
            assert decision["stage"], "Missing stage name"


# ── Trace integrity ─────────────────────────────────────────────────


class TestRuntimeTraceIntegrity:
    """Every stage appends trace entries."""

    def test_trace_has_8_entries(self):
        result = run_pipeline("ذهب الطالبُ إلى المدرسة")
        assert len(result.trace) == 8

    def test_each_trace_has_stage(self):
        result = run_pipeline("كتب")
        for entry in result.trace:
            assert isinstance(entry.stage, PipelineStage)

    def test_each_trace_has_input_summary(self):
        result = run_pipeline("كتب")
        for entry in result.trace:
            assert entry.input_summary
