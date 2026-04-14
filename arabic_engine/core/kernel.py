"""Kernel 14 — minimal epistemic core primitives.

This module defines the canonical 14-node epistemic kernel used as the
foundational source for higher-level derived structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class KernelLabel(Enum):
    """Canonical kernel node labels (exactly 14)."""

    SELF = "Self"
    REALITY = "Reality"
    SENSE = "Sense"
    PRIOR_INFO = "PriorInfo"
    LINK = "Link"
    CONCEPT = "Concept"
    JUDGEMENT = "Judgement"
    METHOD = "Method"
    PROOF = "Proof"
    CARRIER = "Carrier"
    EXCHANGE = "Exchange"
    MODEL = "Model"
    CONSTRAINT = "Constraint"
    STATE = "State"


class KernelRelation(Enum):
    """Core kernel relationships only."""

    KNOWS = "KNOWS"
    EMITS = "EMITS"
    RECEIVES = "RECEIVES"
    IS_SENSED_AS = "IS_SENSED_AS"
    IS_INTERPRETED_WITH = "IS_INTERPRETED_WITH"
    ARE_BOUND_BY = "ARE_BOUND_BY"
    YIELDS = "YIELDS"
    IS_JUDGED_AS = "IS_JUDGED_AS"
    IS_EVALUATED_BY = "IS_EVALUATED_BY"
    IS_JUSTIFIED_BY = "IS_JUSTIFIED_BY"
    IS_LIMITED_BY = "IS_LIMITED_BY"
    HAS_STATE = "HAS_STATE"
    ARE_CARRIED_BY = "ARE_CARRIED_BY"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    INVOLVES = "INVOLVES"
    FORMS = "FORMS"
    # ── Rational Self Ontology v1 extensions ─────────────────────
    DESIGNATES = "DESIGNATES"          # Self → LexemeNode
    INTENDS_COMPOSITION = "INTENDS_COMPOSITION"  # Self → CompositionReadyNode


KERNEL_REQUIRED_FIELDS: dict[KernelLabel, frozenset[str]] = {
    KernelLabel.SELF: frozenset({"self_id", "name"}),
    KernelLabel.REALITY: frozenset({"reality_id", "kind"}),
    KernelLabel.SENSE: frozenset({"sense_id", "modality"}),
    KernelLabel.PRIOR_INFO: frozenset({"prior_info_id", "source"}),
    KernelLabel.LINK: frozenset({"link_id", "link_kind"}),
    KernelLabel.CONCEPT: frozenset({"concept_id", "label"}),
    KernelLabel.JUDGEMENT: frozenset({"judgement_id", "judgement_type"}),
    KernelLabel.METHOD: frozenset({"method_id", "family"}),
    KernelLabel.PROOF: frozenset({"proof_id", "proof_kind"}),
    KernelLabel.CARRIER: frozenset({"carrier_id", "carrier_type"}),
    KernelLabel.EXCHANGE: frozenset({"exchange_id", "exchange_type"}),
    KernelLabel.MODEL: frozenset({"model_id", "name"}),
    KernelLabel.CONSTRAINT: frozenset({"constraint_id", "constraint_type"}),
    KernelLabel.STATE: frozenset({"state_id", "state_type"}),
}


KERNEL_RELATION_PAIRS: dict[KernelRelation, tuple[tuple[KernelLabel, KernelLabel], ...]] = {
    KernelRelation.KNOWS: ((KernelLabel.SELF, KernelLabel.CONCEPT),),
    KernelRelation.EMITS: ((KernelLabel.SELF, KernelLabel.CARRIER),),
    KernelRelation.RECEIVES: ((KernelLabel.SELF, KernelLabel.CARRIER),),
    KernelRelation.IS_SENSED_AS: ((KernelLabel.REALITY, KernelLabel.SENSE),),
    KernelRelation.IS_INTERPRETED_WITH: ((KernelLabel.SENSE, KernelLabel.PRIOR_INFO),),
    KernelRelation.ARE_BOUND_BY: ((KernelLabel.PRIOR_INFO, KernelLabel.LINK),),
    KernelRelation.YIELDS: ((KernelLabel.LINK, KernelLabel.CONCEPT),),
    KernelRelation.IS_JUDGED_AS: ((KernelLabel.CONCEPT, KernelLabel.JUDGEMENT),),
    KernelRelation.IS_EVALUATED_BY: ((KernelLabel.JUDGEMENT, KernelLabel.METHOD),),
    KernelRelation.IS_JUSTIFIED_BY: ((KernelLabel.JUDGEMENT, KernelLabel.PROOF),),
    KernelRelation.IS_LIMITED_BY: ((KernelLabel.JUDGEMENT, KernelLabel.CONSTRAINT),),
    KernelRelation.HAS_STATE: (
        (KernelLabel.JUDGEMENT, KernelLabel.STATE),
        (KernelLabel.MODEL, KernelLabel.STATE),
    ),
    KernelRelation.ARE_CARRIED_BY: ((KernelLabel.CONCEPT, KernelLabel.CARRIER),),
    KernelRelation.PARTICIPATES_IN: ((KernelLabel.CARRIER, KernelLabel.EXCHANGE),),
    KernelRelation.INVOLVES: ((KernelLabel.EXCHANGE, KernelLabel.SELF),),
    KernelRelation.FORMS: ((KernelLabel.EXCHANGE, KernelLabel.MODEL),),
    # ── Rational Self Ontology v1 extensions ─────────────────────
    # DESIGNATES: Self designates (perceives / names) a lexeme
    KernelRelation.DESIGNATES: ((KernelLabel.SELF, KernelLabel.CONCEPT),),
    # INTENDS_COMPOSITION: Self intends to compose lexemes
    KernelRelation.INTENDS_COMPOSITION: ((KernelLabel.SELF, KernelLabel.CONCEPT),),
}


@dataclass(frozen=True)
class KernelNode:
    """A minimal kernel node."""

    node_id: str
    label: KernelLabel
    fields: dict[str, Any]


@dataclass(frozen=True)
class KernelEdge:
    """A minimal kernel edge."""

    source_id: str
    relation: KernelRelation
    target_id: str


@dataclass(frozen=True)
class KernelGraph:
    """A minimal kernel graph payload."""

    nodes: tuple[KernelNode, ...]
    edges: tuple[KernelEdge, ...]


@dataclass(frozen=True)
class KernelValidationResult:
    """Validation result for a kernel graph."""

    valid: bool
    errors: tuple[str, ...]


@dataclass(frozen=True)
class KernelUtterance:
    """Derived utterance (from Carrier)."""

    utterance_id: str
    carrier_id: str
    text: str


@dataclass(frozen=True)
class KernelLinguisticProfile:
    """Derived linguistic profile (from Method + Carrier + Concept)."""

    profile_id: str
    method_id: str
    carrier_id: str
    concept_id: str
    signature: str


@dataclass(frozen=True)
class KernelKnowledgeEpisode:
    """Derived knowledge episode (from Reality + Sense + PriorInfo + Link + Judgement)."""

    episode_id: str
    reality_id: str
    sense_id: str
    prior_info_id: str
    link_id: str
    judgement_id: str


@dataclass(frozen=True)
class KernelDiscourseExchange:
    """Derived discourse exchange (from Exchange + Carrier + Self + State)."""

    discourse_id: str
    exchange_id: str
    carrier_id: str
    self_id: str
    state_id: str


@dataclass(frozen=True)
class KernelReusableModel:
    """Derived reusable model (from Model + State + repeated validated patterns)."""

    reusable_model_id: str
    model_id: str
    state_id: str
    pattern_count: int


def validate_kernel_graph(graph: KernelGraph) -> KernelValidationResult:
    """Validate minimal kernel constraints and relation compatibility."""
    errors: list[str] = []
    node_by_id = {node.node_id: node for node in graph.nodes}

    for node in graph.nodes:
        required = KERNEL_REQUIRED_FIELDS[node.label]
        missing = sorted(field for field in required if field not in node.fields)
        if missing:
            missing_fields = ", ".join(missing)
            errors.append(
                "Node "
                f"{node.node_id} ({node.label.value}) "
                f"missing required fields: {missing_fields}"
            )

    for edge in graph.edges:
        source = node_by_id.get(edge.source_id)
        target = node_by_id.get(edge.target_id)
        if source is None or target is None:
            errors.append(
                f"Edge {edge.relation.value} references unknown node(s): "
                f"{edge.source_id} -> {edge.target_id}"
            )
            continue
        expected_pairs = KERNEL_RELATION_PAIRS[edge.relation]
        if (source.label, target.label) not in expected_pairs:
            expected = ", ".join(f"{s.value}->{t.value}" for s, t in expected_pairs)
            errors.append(
                f"Edge {edge.relation.value} expects one of [{expected}], got "
                f"{source.label.value}->{target.label.value}"
            )

    return KernelValidationResult(valid=not errors, errors=tuple(errors))


def derive_utterance_from_carrier(carrier: KernelNode, text: str) -> KernelUtterance:
    """Derive an Utterance from a Carrier node."""
    if carrier.label is not KernelLabel.CARRIER:
        raise ValueError("Utterance can only be derived from a Carrier node.")
    carrier_id = str(carrier.fields["carrier_id"])
    return KernelUtterance(
        utterance_id=f"utterance::{carrier_id}",
        carrier_id=carrier_id,
        text=text,
    )


def derive_linguistic_profile(
    method: KernelNode,
    carrier: KernelNode,
    concept: KernelNode,
) -> KernelLinguisticProfile:
    """Derive a LinguisticProfile from Method + Carrier + Concept."""
    if method.label is not KernelLabel.METHOD:
        raise ValueError("Expected Method node.")
    if carrier.label is not KernelLabel.CARRIER:
        raise ValueError("Expected Carrier node.")
    if concept.label is not KernelLabel.CONCEPT:
        raise ValueError("Expected Concept node.")

    method_id = str(method.fields["method_id"])
    carrier_id = str(carrier.fields["carrier_id"])
    concept_id = str(concept.fields["concept_id"])
    return KernelLinguisticProfile(
        profile_id=f"profile::{method_id}::{carrier_id}::{concept_id}",
        method_id=method_id,
        carrier_id=carrier_id,
        concept_id=concept_id,
        signature=f"{method_id}|{carrier_id}|{concept_id}",
    )


def derive_knowledge_episode(
    reality: KernelNode,
    sense: KernelNode,
    prior_info: KernelNode,
    link: KernelNode,
    judgement: KernelNode,
) -> KernelKnowledgeEpisode:
    """Derive a KnowledgeEpisode from Reality + Sense + PriorInfo + Link + Judgement."""
    expected = (
        (reality, KernelLabel.REALITY),
        (sense, KernelLabel.SENSE),
        (prior_info, KernelLabel.PRIOR_INFO),
        (link, KernelLabel.LINK),
        (judgement, KernelLabel.JUDGEMENT),
    )
    for node, label in expected:
        if node.label is not label:
            raise ValueError(f"Expected {label.value} node.")

    reality_id = str(reality.fields["reality_id"])
    sense_id = str(sense.fields["sense_id"])
    prior_info_id = str(prior_info.fields["prior_info_id"])
    link_id = str(link.fields["link_id"])
    judgement_id = str(judgement.fields["judgement_id"])
    return KernelKnowledgeEpisode(
        episode_id=f"episode::{reality_id}::{sense_id}::{judgement_id}",
        reality_id=reality_id,
        sense_id=sense_id,
        prior_info_id=prior_info_id,
        link_id=link_id,
        judgement_id=judgement_id,
    )


def derive_discourse_exchange(
    exchange: KernelNode,
    carrier: KernelNode,
    self_node: KernelNode,
    state: KernelNode,
) -> KernelDiscourseExchange:
    """Derive a DiscourseExchange from Exchange + Carrier + Self + State."""
    if exchange.label is not KernelLabel.EXCHANGE:
        raise ValueError("Expected Exchange node.")
    if carrier.label is not KernelLabel.CARRIER:
        raise ValueError("Expected Carrier node.")
    if self_node.label is not KernelLabel.SELF:
        raise ValueError("Expected Self node.")
    if state.label is not KernelLabel.STATE:
        raise ValueError("Expected State node.")

    exchange_id = str(exchange.fields["exchange_id"])
    carrier_id = str(carrier.fields["carrier_id"])
    self_id = str(self_node.fields["self_id"])
    state_id = str(state.fields["state_id"])
    return KernelDiscourseExchange(
        discourse_id=f"discourse::{exchange_id}::{self_id}",
        exchange_id=exchange_id,
        carrier_id=carrier_id,
        self_id=self_id,
        state_id=state_id,
    )


def derive_reusable_model(
    model: KernelNode,
    state: KernelNode,
    pattern_count: int,
) -> KernelReusableModel:
    """Derive a ReusableModel from Model + State + repeated validated patterns."""
    if model.label is not KernelLabel.MODEL:
        raise ValueError("Expected Model node.")
    if state.label is not KernelLabel.STATE:
        raise ValueError("Expected State node.")
    if pattern_count < 2:
        raise ValueError(
            "Reusable model requires repeated validated patterns (pattern_count >= 2)."
        )

    model_id = str(model.fields["model_id"])
    state_id = str(state.fields["state_id"])
    return KernelReusableModel(
        reusable_model_id=f"reusable::{model_id}",
        model_id=model_id,
        state_id=state_id,
        pattern_count=pattern_count,
    )
