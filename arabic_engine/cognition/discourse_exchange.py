"""discourse_exchange — Schema التداول المعرفي بين الذوات العاقلة.

Implements validation for a single inter-agent discourse exchange:

* sender / receiver presence and role fit
* purpose / style coherence
* linguistic carrier integrity (utterance / concept / both)
* reception and post-reception state
* trust-sensitive exchange checks
* transferred knowledge validity checks
* reception consistency checks
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from arabic_engine.core.enums import (
    AuthorityLevel,
    CarrierClass,
    DiscourseGapType,
    DiscourseValidationOutcome,
    ExchangeType,
    GapSeverity,
    InterpretiveOutcomeType,
    PurposeType,
    ReceptionStateType,
    SenderRoleType,
    StyleKind,
    ValidationOutcome,
    ValidationState,
)
from arabic_engine.core.types import (
    DiscourseCarrierRecord,
    DiscourseConceptRecord,
    DiscourseExchangeNode,
    DiscourseExchangeResult,
    DiscourseGapRecord,
    DiscourseUtteranceRecord,
    ExchangePurposeRecord,
    ExchangeStyleRecord,
    InterpretiveOutcomeRecord,
    RationalSelfRecord,
    ReceiverRoleRecord,
    ReceptionRecord,
    ReceptionStateRecord,
    SenderRoleRecord,
    TrustProfileRecord,
)


def _make_gap(
    exchange_id: str, gap_type: DiscourseGapType, detail: str, severity: GapSeverity
) -> DiscourseGapRecord:
    """Build a discourse gap record."""
    return DiscourseGapRecord(
        node_id=f"GAP::{exchange_id}::{gap_type.name}",
        gap_type=gap_type,
        severity=severity,
        detail=detail,
    )


def validate_sender(
    node: DiscourseExchangeNode,
    sender: Optional[RationalSelfRecord],
    role: Optional[SenderRoleRecord],
) -> List[DiscourseGapRecord]:
    """Validate sender closure and sender role compatibility."""
    gaps: List[DiscourseGapRecord] = []
    if sender is None or role is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_SENDER,
                "Missing sender or sender role",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    if node.exchange_type == ExchangeType.TEACHING and role.role_type not in {
        SenderRoleType.TEACHER,
        SenderRoleType.EXPLAINER,
        SenderRoleType.SOURCE,
    }:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.SENDER_PURPOSE_MISMATCH,
                "Invalid sender role for teaching exchange",
                GapSeverity.CRITICAL,
            )
        )

    return gaps


def validate_receiver(
    node: DiscourseExchangeNode,
    receiver: Optional[RationalSelfRecord],
    role: Optional[ReceiverRoleRecord],
) -> List[DiscourseGapRecord]:
    """Validate receiver closure and expected action definition."""
    gaps: List[DiscourseGapRecord] = []
    if receiver is None or role is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_RECEIVER,
                "Missing receiver or receiver role",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    return gaps


def validate_purpose(
    node: DiscourseExchangeNode,
    purpose: Optional[ExchangePurposeRecord],
) -> List[DiscourseGapRecord]:
    """Validate purpose presence and purpose-style compatibility."""
    gaps: List[DiscourseGapRecord] = []
    if purpose is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_PURPOSE,
                "Missing exchange purpose",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    if purpose.purpose_type == PurposeType.PERSUADE and node.style is not None:
        if node.style.style_kind not in {
            StyleKind.ARGUMENT,
            StyleKind.EXPLANATION,
            StyleKind.TESTIMONY,
        }:
            gaps.append(
                _make_gap(
                    node.node_id,
                    DiscourseGapType.INVALID_STYLE_PURPOSE_FIT,
                    "Purpose-style mismatch for persuasion",
                    GapSeverity.MODERATE,
                )
            )

    return gaps


def validate_style(
    node: DiscourseExchangeNode,
    style: Optional[ExchangeStyleRecord],
) -> List[DiscourseGapRecord]:
    """Validate style presence and exchange-type fit."""
    gaps: List[DiscourseGapRecord] = []
    if style is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_STYLE,
                "Missing exchange style",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    if style.style_kind == StyleKind.QUESTION and node.exchange_type not in {
        ExchangeType.QUESTION,
    }:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_STYLE_PURPOSE_FIT,
                "Invalid style for exchange type",
                GapSeverity.CRITICAL,
            )
        )

    return gaps


def validate_carrier(
    node: DiscourseExchangeNode,
    carrier: Optional[DiscourseCarrierRecord],
    utterance: Optional[DiscourseUtteranceRecord],
    concept: Optional[DiscourseConceptRecord],
) -> List[DiscourseGapRecord]:
    """Validate carrier class and attached sub-carrier records."""
    gaps: List[DiscourseGapRecord] = []
    if carrier is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_CARRIER,
                "Missing carrier",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    if carrier.carrier_class not in {
        CarrierClass.UTTERANCE,
        CarrierClass.CONCEPT,
        CarrierClass.BOTH,
    }:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_CARRIER,
                "Invalid carrier class",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    if carrier.carrier_class == CarrierClass.UTTERANCE and utterance is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_CARRIER,
                "Utterance carrier missing utterance",
                GapSeverity.CRITICAL,
            )
        )
    if carrier.carrier_class == CarrierClass.CONCEPT and concept is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_CARRIER,
                "Concept carrier missing concept",
                GapSeverity.CRITICAL,
            )
        )
    if carrier.carrier_class == CarrierClass.BOTH and (utterance is None or concept is None):
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_CARRIER,
                "Both carrier requires utterance and concept",
                GapSeverity.CRITICAL,
            )
        )

    return gaps


def validate_reception(
    node: DiscourseExchangeNode,
    reception: Optional[ReceptionRecord],
    state: Optional[ReceptionStateRecord],
    outcome: Optional[InterpretiveOutcomeRecord],
) -> List[DiscourseGapRecord]:
    """Validate reception closure and presence of state/outcome."""
    gaps: List[DiscourseGapRecord] = []
    if reception is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_RECEPTION,
                "Missing reception",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    if state is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_RECEPTION_STATE,
                "Missing reception state",
                GapSeverity.CRITICAL,
            )
        )

    if outcome is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.RECEPTION_INCONSISTENCY,
                "Missing interpretive outcome",
                GapSeverity.MODERATE,
            )
        )

    return gaps


def validate_trust(
    node: DiscourseExchangeNode, trust: Optional[TrustProfileRecord]
) -> List[DiscourseGapRecord]:
    """Validate trust profile for credibility-sensitive exchange types."""
    if (
        node.exchange_type
        in {ExchangeType.TEACHING, ExchangeType.TESTIMONY, ExchangeType.EXPLANATION}
        and trust is None
    ):
        return [
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_TRUST_PROFILE,
                "Missing trust profile for credibility-sensitive exchange",
                GapSeverity.MODERATE,
            )
        ]
    return []


def validate_knowledge_transfer(
    node: DiscourseExchangeNode, episode: object
) -> List[DiscourseGapRecord]:
    """Validate transferred knowledge is present and epistemically valid."""
    gaps: List[DiscourseGapRecord] = []
    if episode is None:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.MISSING_TRANSFERRED_KNOWLEDGE,
                "Missing transferred knowledge",
                GapSeverity.CRITICAL,
            )
        )
        return gaps

    rank = getattr(episode, "epistemic_rank", None)
    if rank is not None and (
        getattr(rank, "name", "") == ValidationOutcome.REJECTED_METHODOLOGICALLY.name
    ):
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_TRANSFERRED_KNOWLEDGE,
                "Cannot تداول methodologically rejected knowledge",
                GapSeverity.FATAL,
            )
        )

    validation_state = getattr(episode, "validation_state", None)
    if validation_state is not None and validation_state == ValidationState.INVALID:
        gaps.append(
            _make_gap(
                node.node_id,
                DiscourseGapType.INVALID_TRANSFERRED_KNOWLEDGE,
                "Cannot تداول invalid knowledge episode",
                GapSeverity.CRITICAL,
            )
        )

    return gaps


def validate_sender_purpose_fit(
    sender_role: Optional[SenderRoleRecord],
    purpose: Optional[ExchangePurposeRecord],
) -> List[DiscourseGapRecord]:
    """Validate sender authority against directive-like purposes."""
    if sender_role is None or purpose is None:
        return []

    if (
        purpose.purpose_type == PurposeType.REQUEST_ACTION
        and sender_role.authority_level == AuthorityLevel.LOW
    ):
        return [
            DiscourseGapRecord(
                node_id=f"GAP::{sender_role.node_id}::SENDER_PURPOSE_MISMATCH",
                gap_type=DiscourseGapType.SENDER_PURPOSE_MISMATCH,
                severity=GapSeverity.MODERATE,
                detail="Insufficient authority for directive exchange",
            )
        ]

    return []


def validate_reception_consistency(
    state: Optional[ReceptionStateRecord],
    outcome: Optional[InterpretiveOutcomeRecord],
) -> List[DiscourseGapRecord]:
    """Validate consistency between reception state and interpretive outcome."""
    if state is None or outcome is None:
        return []

    if (
        state.state_type == ReceptionStateType.ACCEPTED
        and outcome.outcome_type == InterpretiveOutcomeType.DISTORTED
    ):
        return [
            DiscourseGapRecord(
                node_id=f"GAP::{state.node_id}::RECEPTION_INCONSISTENCY",
                gap_type=DiscourseGapType.RECEPTION_INCONSISTENCY,
                severity=GapSeverity.CRITICAL,
                detail="Acceptance cannot coexist with distorted interpretation without review",
            )
        ]

    return []


def validate_exchange(node: DiscourseExchangeNode) -> DiscourseExchangeResult:
    """Run full discourse exchange validation and return normalized result."""
    gaps: List[DiscourseGapRecord] = []

    gaps.extend(validate_sender(node, node.sender, node.sender_role))
    gaps.extend(validate_receiver(node, node.receiver, node.receiver_role))
    gaps.extend(validate_purpose(node, node.purpose))
    gaps.extend(validate_style(node, node.style))
    gaps.extend(validate_carrier(node, node.carrier, node.utterance, node.concept))
    gaps.extend(
        validate_reception(node, node.reception, node.reception_state, node.interpretive_outcome)
    )
    gaps.extend(validate_trust(node, node.trust_profile))
    gaps.extend(validate_knowledge_transfer(node, node.transferred_knowledge))
    gaps.extend(validate_sender_purpose_fit(node.sender_role, node.purpose))
    gaps.extend(validate_reception_consistency(node.reception_state, node.interpretive_outcome))

    required_missing = {
        DiscourseGapType.MISSING_SENDER,
        DiscourseGapType.MISSING_RECEIVER,
        DiscourseGapType.MISSING_PURPOSE,
        DiscourseGapType.MISSING_STYLE,
        DiscourseGapType.MISSING_CARRIER,
        DiscourseGapType.MISSING_TRANSFERRED_KNOWLEDGE,
        DiscourseGapType.MISSING_RECEPTION,
        DiscourseGapType.MISSING_RECEPTION_STATE,
    }

    gap_types = {g.gap_type for g in gaps}
    if not gaps:
        outcome = DiscourseValidationOutcome.VALID
    elif gap_types & required_missing:
        outcome = DiscourseValidationOutcome.INCOMPLETE
    else:
        outcome = DiscourseValidationOutcome.INVALID

    node.gaps = list(gaps)
    node.validation_outcome = outcome

    return DiscourseExchangeResult(
        exchange_id=node.node_id,
        outcome=outcome,
        gaps=list(gaps),
        status=node.status,
    )


def validate_batch(nodes: Sequence[DiscourseExchangeNode]) -> List[DiscourseExchangeResult]:
    """Validate many exchanges in order."""
    return [validate_exchange(node) for node in nodes]
