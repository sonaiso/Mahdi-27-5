"""Boundary gate tests — SIVP-v1 § A1–A6.

Verifies that the pipeline enforces gate logic between every pair of
adjacent layers, produces unified trace entries, and exposes a coherent
status on every :class:`PipelineResult`.
"""

from __future__ import annotations

from arabic_engine.cognition.inference_rules import InferenceEngine
from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.enums import (
    LayerGateDecision,
    PipelineLayerID,
    PipelineStatus,
    TruthState,
)
from arabic_engine.pipeline import (
    PipelineResult,
    _evaluate_pipeline_gate,
    run,
)

# ── helpers ──────────────────────────────────────────────────────────

def _full_result(sentence: str = "كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ") -> PipelineResult:
    """Return a full pipeline result with world + inference."""
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


# ── A6: PipelineResult carries gate_records, status, unified_trace ──


class TestPipelineResultFields:
    """A6 — PipelineResult includes gate records and unified status."""

    def test_status_is_success_for_valid_input(self):
        result = _full_result()
        assert result.status == PipelineStatus.SUCCESS

    def test_gate_records_non_empty(self):
        result = _full_result()
        assert len(result.gate_records) > 0

    def test_gate_records_count_equals_layer_boundaries(self):
        """Gate count equals number of adjacent layer-pair transitions."""
        result = _full_result()
        expected = len(PipelineLayerID) - 1
        assert len(result.gate_records) == expected

    def test_unified_trace_non_empty(self):
        result = _full_result()
        assert len(result.unified_trace) > 0

    def test_trace_complete_is_true(self):
        result = _full_result()
        assert result.trace_complete is True


# ── A1: Every layer transition goes through a gate ───────────────────


class TestGateEnforcement:
    """A1 — No transition without explicit gate."""

    def test_all_gates_pass_for_valid_input(self):
        result = _full_result()
        for gate in result.gate_records:
            assert gate.decision in (
                LayerGateDecision.PASS,
                LayerGateDecision.COMPLETE,
            )

    def test_each_gate_has_reason(self):
        """B5 — Every gate carries a reason."""
        result = _full_result()
        for gate in result.gate_records:
            assert gate.reason, f"Gate {gate.gate_id} has empty reason"


# ── A2: Unified status determination ─────────────────────────────────


class TestUnifiedStatus:
    """A2 — status is one of SUCCESS / SUSPEND / FAILURE."""

    def test_status_enum_values(self):
        assert set(PipelineStatus) == {
            PipelineStatus.SUCCESS,
            PipelineStatus.SUSPEND,
            PipelineStatus.FAILURE,
        }

    def test_result_status_is_pipeline_status(self):
        result = _full_result()
        assert isinstance(result.status, PipelineStatus)


# ── A4: Jump prevention ─────────────────────────────────────────────


class TestJumpPrevention:
    """A4 — Non-adjacent transitions produce REJECT."""

    def test_adjacent_gate_passes(self):
        gate = _evaluate_pipeline_gate(
            PipelineLayerID.L0_NORMALIZE,
            PipelineLayerID.L1_TOKENIZE,
            "some_output",
        )
        assert gate.decision in (
            LayerGateDecision.PASS,
            LayerGateDecision.COMPLETE,
        )

    def test_skip_gate_rejects(self):
        gate = _evaluate_pipeline_gate(
            PipelineLayerID.L0_NORMALIZE,
            PipelineLayerID.L3_SYNTAX,
            "some_output",
        )
        assert gate.decision == LayerGateDecision.REJECT

    def test_empty_output_suspends(self):
        gate = _evaluate_pipeline_gate(
            PipelineLayerID.L0_NORMALIZE,
            PipelineLayerID.L1_TOKENIZE,
            [],
        )
        assert gate.decision == LayerGateDecision.SUSPEND


# ── B1/B6: Unified trace entries ─────────────────────────────────────


class TestUnifiedTrace:
    """B1/B6 — Every executed layer has a unified trace entry."""

    def test_trace_entries_have_hashes(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.input_hash, f"Missing input_hash on {entry.layer_name}"
            assert entry.output_hash, f"Missing output_hash on {entry.layer_name}"

    def test_trace_entries_have_timestamps(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.timestamp, f"Missing timestamp on {entry.layer_name}"

    def test_trace_entries_have_layer_names(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.layer_name, f"Missing layer_name at index {entry.layer_index}"

    def test_trace_entry_count_equals_layers_executed(self):
        """13 trace entries = 1 pre-U₀ + 11 gates + 1 final layer."""
        result = _full_result()
        assert len(result.unified_trace) == 13


# ── B4: trace_complete flag ──────────────────────────────────────────


class TestTraceComplete:
    """B4 — trace_complete is True only when all layers executed."""

    def test_full_run_is_complete(self):
        result = _full_result()
        assert result.trace_complete is True


# ── B3: trace_back capability ────────────────────────────────────────


class TestTraceBack:
    """B3 — Any judgment can be traced back to L0."""

    def test_trace_chain_is_contiguous(self):
        result = _full_result()
        indices = [e.layer_index for e in result.unified_trace]
        for i in range(len(indices) - 1):
            assert indices[i + 1] >= indices[i], "Trace not ascending"

    def test_trace_starts_at_pre_u0(self):
        """First trace entry is the pre-U₀ admissibility check (index -1)."""
        result = _full_result()
        assert result.unified_trace[0].layer_index == -1


# ── PipelineLayerID completeness ─────────────────────────────────────


class TestPipelineLayerID:
    """PipelineLayerID has all expected layers."""

    def test_layer_count(self):
        assert len(PipelineLayerID) == 12

    def test_first_layer_is_normalize(self):
        assert list(PipelineLayerID)[0] == PipelineLayerID.L0_NORMALIZE

    def test_last_layer_is_world_model(self):
        assert list(PipelineLayerID)[-1] == PipelineLayerID.L10_WORLD_MODEL
