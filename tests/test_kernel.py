"""Tests for the Kernel-14 primitives."""

from __future__ import annotations

import pytest

from arabic_engine.core.kernel import (
    KernelEdge,
    KernelGraph,
    KernelLabel,
    KernelNode,
    KernelRelation,
    derive_discourse_exchange,
    derive_knowledge_episode,
    derive_linguistic_profile,
    derive_reusable_model,
    derive_utterance_from_carrier,
    validate_kernel_graph,
)


def _node(node_id: str, node_label: KernelLabel, **fields: object) -> KernelNode:
    return KernelNode(node_id=node_id, label=node_label, fields=fields)


def test_validate_kernel_graph_accepts_minimal_valid_graph() -> None:
    self_node = _node("n1", KernelLabel.SELF, self_id="SELF_001", name="self")
    concept = _node("n2", KernelLabel.CONCEPT, concept_id="CONCEPT_001", label="c")
    edge = KernelEdge(source_id="n1", relation=KernelRelation.KNOWS, target_id="n2")
    result = validate_kernel_graph(KernelGraph(nodes=(self_node, concept), edges=(edge,)))
    assert result.valid is True
    assert result.errors == ()


def test_validate_kernel_graph_rejects_missing_required_fields() -> None:
    self_node = _node("n1", KernelLabel.SELF, self_id="SELF_001")
    result = validate_kernel_graph(KernelGraph(nodes=(self_node,), edges=()))
    assert result.valid is False
    assert any("missing required fields" in err for err in result.errors)


def test_validate_kernel_graph_rejects_relation_label_mismatch() -> None:
    reality = _node("n1", KernelLabel.REALITY, reality_id="R1", kind="material")
    sense = _node("n2", KernelLabel.SENSE, sense_id="S1", modality="visual")
    edge = KernelEdge(source_id="n1", relation=KernelRelation.KNOWS, target_id="n2")
    result = validate_kernel_graph(KernelGraph(nodes=(reality, sense), edges=(edge,)))
    assert result.valid is False
    assert any("Self->Concept" in err and "Reality->Sense" in err for err in result.errors)


def test_validate_kernel_graph_accepts_model_has_state() -> None:
    model = _node("m1", KernelLabel.MODEL, model_id="MODEL_1", name="seed-model")
    state = _node("s1", KernelLabel.STATE, state_id="STATE_1", state_type="validated")
    edge = KernelEdge(source_id="m1", relation=KernelRelation.HAS_STATE, target_id="s1")
    result = validate_kernel_graph(KernelGraph(nodes=(model, state), edges=(edge,)))
    assert result.valid is True


def test_kernel_derivations() -> None:
    carrier = _node("carrier", KernelLabel.CARRIER, carrier_id="C1", carrier_type="both")
    method = _node("method", KernelLabel.METHOD, method_id="M1", family="rational")
    concept = _node("concept", KernelLabel.CONCEPT, concept_id="K1", label="label")
    reality = _node("reality", KernelLabel.REALITY, reality_id="R1", kind="material")
    sense = _node("sense", KernelLabel.SENSE, sense_id="S1", modality="visual")
    prior = _node("prior", KernelLabel.PRIOR_INFO, prior_info_id="P1", source="seed")
    link = _node("link", KernelLabel.LINK, link_id="L1", link_kind="causal")
    judgement = _node(
        "judgement",
        KernelLabel.JUDGEMENT,
        judgement_id="J1",
        judgement_type="existence",
    )
    exchange = _node(
        "exchange",
        KernelLabel.EXCHANGE,
        exchange_id="E1",
        exchange_type="report",
    )
    self_node = _node("self", KernelLabel.SELF, self_id="SELF_1", name="self")
    state = _node("state", KernelLabel.STATE, state_id="ST1", state_type="validated")
    model = _node("model", KernelLabel.MODEL, model_id="MODEL_1", name="model")

    utterance = derive_utterance_from_carrier(carrier, text="نص")
    profile = derive_linguistic_profile(method, carrier, concept)
    episode = derive_knowledge_episode(reality, sense, prior, link, judgement)
    discourse = derive_discourse_exchange(exchange, carrier, self_node, state)
    reusable = derive_reusable_model(model, state, pattern_count=2)

    assert utterance.carrier_id == "C1"
    assert profile.signature == "M1|C1|K1"
    assert episode.reality_id == "R1"
    assert discourse.exchange_id == "E1"
    assert reusable.model_id == "MODEL_1"


def test_derive_reusable_model_requires_repetition() -> None:
    model = _node("model", KernelLabel.MODEL, model_id="MODEL_1", name="model")
    state = _node("state", KernelLabel.STATE, state_id="ST1", state_type="validated")
    with pytest.raises(ValueError, match="pattern_count >= 2"):
        derive_reusable_model(model, state, pattern_count=1)
