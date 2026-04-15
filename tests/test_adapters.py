"""Tests for arabic_engine/runtime/adapters.py."""

from __future__ import annotations

from arabic_engine.core.enums import ActivationStage
from arabic_engine.core.trace import (
    DecisionState,
    HypothesisState,
    KernelRuntimeState,
)
from arabic_engine.core.types import DecisionTrace, HypothesisNode
from arabic_engine.runtime.adapters import to_legacy_state
from arabic_engine.runtime_pipeline import RuntimeState


def _hypothesis(
    node_id: str = "h1",
    hypothesis_type: str = "test",
    stage: ActivationStage = ActivationStage.SIGNAL,
    payload: tuple = (),
) -> HypothesisNode:
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type=hypothesis_type,
        stage=stage,
        confidence=0.9,
        payload=payload,
    )


def _kernel(**kwargs) -> KernelRuntimeState:
    return KernelRuntimeState(**kwargs)


# ── basic conversion ────────────────────────────────────────────────


def test_empty_kernel_returns_runtime_state():
    result = to_legacy_state(_kernel())
    assert isinstance(result, RuntimeState)


def test_preserves_input_text():
    result = to_legacy_state(_kernel(input_text="بسم الله"))
    assert result.raw_text == "بسم الله"


def test_empty_kernel_has_empty_lists():
    result = to_legacy_state(_kernel())
    assert result.utterance_units == []
    assert result.concepts == []
    assert result.axes == []
    assert result.relations == []
    assert result.roles == []


def test_empty_kernel_no_judgement():
    result = to_legacy_state(_kernel())
    assert result.judgement is None


# ── hypothesis stage mapping ────────────────────────────────────────


def test_signal_hypotheses_map_to_utterances():
    hs = HypothesisState()
    hs.add_hypothesis(
        _hypothesis(
            hypothesis_type="segmentation",
            stage=ActivationStage.SIGNAL,
            payload=(("token_text", "كتب"),),
        )
    )
    kernel = _kernel()
    kernel.hypotheses = hs
    result = to_legacy_state(kernel)
    assert len(result.utterance_units) == 1


def test_concept_hypotheses_map():
    hs = HypothesisState()
    hs.add_hypothesis(
        _hypothesis(
            hypothesis_type="concept",
            stage=ActivationStage.CONCEPT,
            payload=(("label", "كتاب"), ("semantic_type", "entity")),
        )
    )
    kernel = _kernel()
    kernel.hypotheses = hs
    result = to_legacy_state(kernel)
    assert len(result.concepts) == 1


def test_axis_hypotheses_map():
    hs = HypothesisState()
    hs.add_hypothesis(
        _hypothesis(
            hypothesis_type="axis",
            stage=ActivationStage.AXIS,
            payload=(("axis_name", "temporal"), ("axis_value", "past")),
        )
    )
    kernel = _kernel()
    kernel.hypotheses = hs
    result = to_legacy_state(kernel)
    assert len(result.axes) == 1


def test_relation_hypotheses_map():
    hs = HypothesisState()
    hs.add_hypothesis(
        _hypothesis(
            hypothesis_type="relation",
            stage=ActivationStage.RELATION,
            payload=(
                ("relation_type", "agent"),
                ("source_label", "كاتب"),
                ("target_label", "كتاب"),
            ),
        )
    )
    kernel = _kernel()
    kernel.hypotheses = hs
    result = to_legacy_state(kernel)
    assert len(result.relations) == 1


def test_role_hypotheses_map():
    hs = HypothesisState()
    hs.add_hypothesis(
        _hypothesis(
            hypothesis_type="role",
            stage=ActivationStage.ROLE,
            payload=(("token_label", "الطالب"), ("role", "فاعل")),
        )
    )
    kernel = _kernel()
    kernel.hypotheses = hs
    result = to_legacy_state(kernel)
    assert len(result.roles) == 1


def test_traces_mapped():
    dt = DecisionTrace(
        trace_id="t1",
        stage=ActivationStage.SIGNAL,
        decision_type="prune",
        input_refs=("ref1",),
        output_refs=("ref2",),
        applied_rules=("rule1",),
        justification="test",
    )
    ds = DecisionState()
    ds.trace.append(dt)
    kernel = _kernel()
    kernel.decisions = ds
    result = to_legacy_state(kernel)
    assert len(result.trace) >= 1
