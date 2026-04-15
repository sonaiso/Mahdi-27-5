"""Trace integrity tests — B1/B2/B3.

Verifies trace completeness, replay determinism, timestamp ordering,
suspend/failure reasoning, and hash consistency across the pipeline.
"""

from __future__ import annotations

from arabic_engine.cognition.inference_rules import InferenceEngine
from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.enums import (
    LayerGateDecision,
    PipelineStatus,
    TruthState,
)
from arabic_engine.core.types import DecisionTrace
from arabic_engine.pipeline import (
    partial_replay_from_trace,
    replay_from_trace,
    run,
)


def _full_result(sentence: str = "كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ"):
    """Build a full pipeline result with world + inference."""
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


# ── B1: DecisionTrace now has integrity fields ──────────────────────


class TestDecisionTraceFields:
    """B1 — DecisionTrace includes input_hash, output_hash, timestamp."""

    def test_input_hash_field_exists(self):
        dt = DecisionTrace(
            trace_id="t1",
            stage=__import__(
                "arabic_engine.core.enums", fromlist=["ActivationStage"]
            ).ActivationStage.SIGNAL,
            decision_type="test",
            input_hash="abc123",
        )
        assert dt.input_hash == "abc123"

    def test_output_hash_field_exists(self):
        dt = DecisionTrace(
            trace_id="t1",
            stage=__import__(
                "arabic_engine.core.enums", fromlist=["ActivationStage"]
            ).ActivationStage.SIGNAL,
            decision_type="test",
            output_hash="def456",
        )
        assert dt.output_hash == "def456"

    def test_timestamp_field_exists(self):
        dt = DecisionTrace(
            trace_id="t1",
            stage=__import__(
                "arabic_engine.core.enums", fromlist=["ActivationStage"]
            ).ActivationStage.SIGNAL,
            decision_type="test",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert dt.timestamp == "2026-01-01T00:00:00Z"

    def test_reason_field_exists(self):
        dt = DecisionTrace(
            trace_id="t1",
            stage=__import__(
                "arabic_engine.core.enums", fromlist=["ActivationStage"]
            ).ActivationStage.SIGNAL,
            decision_type="test",
            reason="pruned below threshold",
        )
        assert dt.reason == "pruned below threshold"

    def test_evidence_field_exists(self):
        dt = DecisionTrace(
            trace_id="t1",
            stage=__import__(
                "arabic_engine.core.enums", fromlist=["ActivationStage"]
            ).ActivationStage.SIGNAL,
            decision_type="test",
            evidence=("ev1", "ev2"),
        )
        assert dt.evidence == ("ev1", "ev2")

    def test_defaults_are_empty(self):
        dt = DecisionTrace(
            trace_id="t1",
            stage=__import__(
                "arabic_engine.core.enums", fromlist=["ActivationStage"]
            ).ActivationStage.SIGNAL,
            decision_type="test",
        )
        assert dt.input_hash == ""
        assert dt.output_hash == ""
        assert dt.timestamp == ""
        assert dt.reason == ""
        assert dt.evidence == ()


# ── Trace completeness ──────────────────────────────────────────────


class TestTraceCompleteness:
    """Every pipeline layer produces a trace entry."""

    def test_every_trace_has_input_hash(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.input_hash, (
                f"Missing input_hash at layer {entry.layer_name}"
            )

    def test_every_trace_has_output_hash(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.output_hash, (
                f"Missing output_hash at layer {entry.layer_name}"
            )

    def test_every_trace_has_timestamp(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.timestamp, (
                f"Missing timestamp at layer {entry.layer_name}"
            )

    def test_every_trace_has_layer_name(self):
        result = _full_result()
        for entry in result.unified_trace:
            assert entry.layer_name

    def test_suspend_entries_have_reason(self):
        """Any SUSPEND trace entry must carry a non-empty reason."""
        result = _full_result()
        for entry in result.unified_trace:
            if entry.state == LayerGateDecision.SUSPEND:
                assert entry.reason, (
                    f"SUSPEND at {entry.layer_name} has empty reason"
                )


# ── Timestamp ordering ──────────────────────────────────────────────


class TestTimestampOrdering:
    """Timestamps increase (or remain equal) across layers."""

    def test_timestamps_non_decreasing(self):
        result = _full_result()
        timestamps = [e.timestamp for e in result.unified_trace]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], (
                f"Timestamp regression between layer {i} and {i + 1}"
            )


# ── Replay determinism ──────────────────────────────────────────────


class TestReplayDeterminism:
    """Same input produces identical hashes on replay."""

    def test_full_replay_reproduces(self):
        result = _full_result()
        report = replay_from_trace(
            result.unified_trace,
            result.raw,
            world=WorldModel(),
        )
        # Most layers should match (world model may vary)
        assert report["matched"] > 0

    def test_same_input_produces_same_hashes(self):
        """Two independent runs produce identical trace hashes."""
        r1 = run("كتب")
        r2 = run("كتب")
        for e1, e2 in zip(r1.unified_trace, r2.unified_trace):
            assert e1.output_hash == e2.output_hash, (
                f"Hash mismatch at {e1.layer_name}: "
                f"{e1.output_hash} != {e2.output_hash}"
            )


# ── Partial replay ──────────────────────────────────────────────────


class TestPartialReplay:
    """partial_replay_from_trace works on layer ranges."""

    def test_partial_replay_returns_report(self):
        result = run("كتب")
        report = partial_replay_from_trace(
            result.unified_trace,
            result.raw,
            start_layer=0,
            end_layer=3,
        )
        assert isinstance(report, dict)
        assert "matched" in report
        assert "range" in report

    def test_partial_replay_range_is_correct(self):
        result = run("كتب")
        report = partial_replay_from_trace(
            result.unified_trace,
            result.raw,
            start_layer=0,
            end_layer=3,
        )
        assert report["range"] == (0, 3)

    def test_partial_replay_filters_layers(self):
        result = run("كتب")
        full_report = replay_from_trace(result.unified_trace, result.raw)
        partial_report = partial_replay_from_trace(
            result.unified_trace,
            result.raw,
            start_layer=0,
            end_layer=3,
        )
        assert len(partial_report["details"]) <= len(full_report["details"])

    def test_partial_replay_default_end_covers_all(self):
        result = run("كتب")
        report = partial_replay_from_trace(
            result.unified_trace,
            result.raw,
        )
        assert report["matched"] > 0


# ── Hash consistency ────────────────────────────────────────────────


class TestHashConsistency:
    """Hash values are stable and consistent."""

    def test_hash_is_sha256_length(self):
        result = run("كتب")
        for entry in result.unified_trace:
            assert len(entry.input_hash) == 64
            assert len(entry.output_hash) == 64

    def test_different_inputs_produce_different_hashes(self):
        r1 = run("كتب")
        r2 = run("ذهب")
        # At least the first layer (L0 normalize) should differ
        assert r1.unified_trace[0].input_hash != r2.unified_trace[0].input_hash
