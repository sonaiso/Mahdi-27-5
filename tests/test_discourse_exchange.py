"""Tests for discourse_exchange schema and validators."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from arabic_engine.cognition.discourse_exchange import (
    validate_batch,
    validate_carrier,
    validate_exchange,
    validate_knowledge_transfer,
    validate_purpose,
    validate_receiver,
    validate_reception,
    validate_reception_consistency,
    validate_sender,
    validate_sender_purpose_fit,
    validate_style,
    validate_trust,
)
from arabic_engine.core.enums import (
    AuthorityLevel,
    CarrierClass,
    DalaalaKind,
    DiscourseGapType,
    DiscourseValidationOutcome,
    ExchangePurposeType,
    ExchangeStatus,
    ExchangeStyleType,
    ExchangeType,
    ExplicitnessLevel,
    GapSeverity,
    InterpretiveOutcomeType,
    PurposeType,
    RationalSelfKind,
    ReceiverExpectedAction,
    ReceiverRoleType,
    ReceiverState,
    ReceptionMode,
    ReceptionStateType,
    SenderRoleType,
    StyleKind,
    TrustBasis,
    TrustLevel,
    UtteranceMode,
    ValidationState,
)
from arabic_engine.core.types import (
    DiscourseCarrierRecord,
    DiscourseConceptRecord,
    DiscourseExchangeNode,
    DiscourseGapRecord,
    DiscourseUtteranceRecord,
    ExchangePurposeRecord,
    ExchangeStyleRecord,
    InterpretiveOutcomeRecord,
    KnowledgeEpisodeNode,
    RationalSelfRecord,
    ReceiverRoleRecord,
    ReceptionRecord,
    ReceptionStateRecord,
    SenderRoleRecord,
    TrustProfileRecord,
)


@pytest.mark.parametrize(
    ("enum_cls", "member_names"),
    [
        (
            ExchangeType,
            {
                "REPORT",
                "TEACHING",
                "QUESTION",
                "ANSWER",
                "COMMAND",
                "WARNING",
                "PERSUASION",
                "NEGOTIATION",
                "TESTIMONY",
                "EXPLANATION",
            },
        ),
        (
            ExchangePurposeType,
            {
                "INFORM",
                "TEACH",
                "VERIFY",
                "GUIDE",
                "BIND",
                "PERSUADE",
                "WARN",
                "REQUEST",
                "TEST",
                "PRESERVE_KNOWLEDGE",
            },
        ),
        (
            ExchangeStyleType,
            {
                "KHABARI",
                "INSHAI",
                "EXPLANATORY",
                "ARGUMENTATIVE",
                "DIRECTIVE",
                "INTERROGATIVE",
                "PEDAGOGICAL",
                "TESTIMONIAL",
            },
        ),
        (
            ExchangeStatus,
            {
                "DRAFTED",
                "TRANSMITTED",
                "RECEIVED",
                "INTERPRETED",
                "ACCEPTED",
                "REJECTED",
                "SUSPENDED",
            },
        ),
        (RationalSelfKind, {"INDIVIDUAL", "COLLECTIVE", "INSTITUTIONAL", "MODELED_AGENT"}),
        (
            SenderRoleType,
            {"SOURCE", "EXPLAINER", "WITNESS", "TEACHER", "COMMANDER", "QUESTIONER", "INTERPRETER"},
        ),
        (AuthorityLevel, {"LOW", "MEDIUM", "HIGH"}),
        (
            ReceiverRoleType,
            {"LISTENER", "LEARNER", "EXAMINER", "ADDRESSEE", "RESPONDENT", "EVALUATOR"},
        ),
        (ReceiverExpectedAction, {"UNDERSTAND", "VERIFY", "ACT", "ANSWER", "PRESERVE", "RELAY"}),
        (
            PurposeType,
            {
                "INFORM",
                "INSTRUCT",
                "PERSUADE",
                "TEST",
                "QUERY",
                "PRESERVE",
                "REFUTE",
                "WARN",
                "REQUEST_ACTION",
                "CLARIFY",
            },
        ),
        (ExplicitnessLevel, {"DIRECT", "SEMI_DIRECT", "IMPLICIT"}),
        (
            StyleKind,
            {
                "KHABAR",
                "INSHA",
                "QUESTION",
                "ANSWER",
                "COMMAND",
                "PROHIBITION",
                "EXPLANATION",
                "ARGUMENT",
                "TESTIMONY",
                "SYMBOLIC",
            },
        ),
        (
            UtteranceMode,
            {"STATEMENT", "QUESTION", "COMMAND", "REPORT", "EXPLANATION", "DIALOGUE_TURN"},
        ),
        (DalaalaKind, {"MUTABAQA", "TADHAMMUN", "ILTIZAM", "ISHARA"}),
        (ReceptionMode, {"HEARD", "READ", "OBSERVED", "INFERRED", "RECALLED"}),
        (ReceiverState, {"OPEN", "RESISTANT", "BIASED", "UNCERTAIN", "ATTENTIVE"}),
        (
            ReceptionStateType,
            {
                "RECEIVED",
                "UNDERSTOOD",
                "MISUNDERSTOOD",
                "ACCEPTED",
                "REJECTED",
                "SUSPENDED",
                "PARTIALLY_UNDERSTOOD",
            },
        ),
        (TrustLevel, {"LOW", "MEDIUM", "HIGH"}),
        (TrustBasis, {"EXPERTISE", "AUTHORITY", "FAMILIARITY", "TESTIMONY_CHAIN", "NONE"}),
        (
            InterpretiveOutcomeType,
            {"ALIGNED", "NARROWED", "EXPANDED", "DISTORTED", "CONFLICTING", "UNRESOLVED"},
        ),
        (
            DiscourseGapType,
            {
                "MISSING_SENDER",
                "MISSING_RECEIVER",
                "MISSING_PURPOSE",
                "MISSING_STYLE",
                "INVALID_STYLE_PURPOSE_FIT",
                "MISSING_CARRIER",
                "INVALID_CARRIER",
                "MISSING_RECEPTION",
                "MISSING_RECEPTION_STATE",
                "MISSING_TRANSFERRED_KNOWLEDGE",
                "INVALID_TRANSFERRED_KNOWLEDGE",
                "MISSING_TRUST_PROFILE",
                "RECEPTION_INCONSISTENCY",
                "SENDER_PURPOSE_MISMATCH",
            },
        ),
        (DiscourseValidationOutcome, {"VALID", "INVALID", "INCOMPLETE"}),
    ],
)
def test_discourse_enum_completeness(enum_cls, member_names):
    assert {m.name for m in enum_cls} == member_names


@pytest.mark.parametrize(
    "factory",
    [
        lambda: RationalSelfRecord("S1", RationalSelfKind.INDIVIDUAL, "full", "ar"),
        lambda: SenderRoleRecord("SR1", SenderRoleType.SOURCE, AuthorityLevel.HIGH),
        lambda: ReceiverRoleRecord(
            "RR1", ReceiverRoleType.LISTENER, ReceiverExpectedAction.UNDERSTAND
        ),
        lambda: ExchangePurposeRecord("P1", PurposeType.INFORM, "share fact"),
        lambda: ExchangeStyleRecord("ST1", StyleKind.EXPLANATION, ExplicitnessLevel.DIRECT),
        lambda: DiscourseCarrierRecord("C1", CarrierClass.UTTERANCE),
        lambda: DiscourseUtteranceRecord("U1", "نَصّ", UtteranceMode.STATEMENT, "direct"),
        lambda: DiscourseConceptRecord("CO1", "مفهوم", DalaalaKind.MUTABAQA, "general"),
        lambda: ReceptionRecord("R1", ReceptionMode.HEARD, ReceiverState.OPEN),
        lambda: ReceptionStateRecord("RS1", ReceptionStateType.UNDERSTOOD, "clear"),
        lambda: TrustProfileRecord("T1", TrustLevel.HIGH, TrustBasis.EXPERTISE),
        lambda: InterpretiveOutcomeRecord("IO1", InterpretiveOutcomeType.ALIGNED),
        lambda: DiscourseGapRecord("G1", DiscourseGapType.MISSING_STYLE, GapSeverity.MODERATE, "x"),
    ],
)
def test_discourse_records_are_frozen(factory):
    item = factory()
    with pytest.raises(FrozenInstanceError):
        item.node_id = "X"  # type: ignore[misc]


def _valid_exchange() -> DiscourseExchangeNode:
    sender = RationalSelfRecord("S1", RationalSelfKind.INDIVIDUAL, "full", "ar")
    receiver = RationalSelfRecord("S2", RationalSelfKind.INDIVIDUAL, "full", "ar")

    episode = KnowledgeEpisodeNode(
        node_id="KE1",
        domain_profile="general",
        judgement_type="existence",
        method_family="aqli",
        carrier_type="both",
        validation_state=ValidationState.VALID,
    )

    return DiscourseExchangeNode(
        node_id="DX1",
        exchange_type=ExchangeType.TEACHING,
        purpose_class="teach",
        style_class="pedagogical",
        carrier_type="both",
        status=ExchangeStatus.RECEIVED,
        sender=sender,
        sender_role=SenderRoleRecord("SR1", SenderRoleType.TEACHER, AuthorityLevel.HIGH),
        receiver=receiver,
        receiver_role=ReceiverRoleRecord(
            "RR1", ReceiverRoleType.LEARNER, ReceiverExpectedAction.UNDERSTAND
        ),
        purpose=ExchangePurposeRecord("P1", PurposeType.INSTRUCT, "teach concept"),
        style=ExchangeStyleRecord("ST1", StyleKind.EXPLANATION, ExplicitnessLevel.DIRECT),
        carrier=DiscourseCarrierRecord("C1", CarrierClass.BOTH),
        utterance=DiscourseUtteranceRecord("U1", "هٰذا بَيَانٌ", UtteranceMode.EXPLANATION, "direct"),
        concept=DiscourseConceptRecord("CO1", "مفهوم", DalaalaKind.MUTABAQA, "general"),
        transferred_knowledge=episode,
        reception=ReceptionRecord("R1", ReceptionMode.HEARD, ReceiverState.ATTENTIVE),
        reception_state=ReceptionStateRecord("RS1", ReceptionStateType.UNDERSTOOD, "coherent"),
        trust_profile=TrustProfileRecord("T1", TrustLevel.HIGH, TrustBasis.EXPERTISE),
        interpretive_outcome=InterpretiveOutcomeRecord("IO1", InterpretiveOutcomeType.ALIGNED),
    )


def test_discourse_exchange_node_mutable_fields():
    node = _valid_exchange()
    node.validation_outcome = DiscourseValidationOutcome.INVALID
    node.gaps.append(
        DiscourseGapRecord("G2", DiscourseGapType.MISSING_STYLE, GapSeverity.MODERATE, "x")
    )
    assert node.validation_outcome == DiscourseValidationOutcome.INVALID
    assert len(node.gaps) == 1


@pytest.mark.parametrize(
    ("role_type", "has_gap"),
    [
        (SenderRoleType.TEACHER, False),
        (SenderRoleType.EXPLAINER, False),
        (SenderRoleType.SOURCE, False),
        (SenderRoleType.WITNESS, True),
    ],
)
def test_validate_sender_role_fit(role_type, has_gap):
    node = _valid_exchange()
    node.sender_role = SenderRoleRecord("SRX", role_type, AuthorityLevel.HIGH)
    gaps = validate_sender(node, node.sender, node.sender_role)
    assert any(g.gap_type == DiscourseGapType.SENDER_PURPOSE_MISMATCH for g in gaps) is has_gap


def test_validate_sender_missing_sender():
    node = _valid_exchange()
    gaps = validate_sender(node, None, node.sender_role)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_SENDER


def test_validate_receiver_ok():
    node = _valid_exchange()
    assert validate_receiver(node, node.receiver, node.receiver_role) == []


def test_validate_receiver_missing_receiver():
    node = _valid_exchange()
    gaps = validate_receiver(node, None, node.receiver_role)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_RECEIVER


def test_validate_purpose_missing():
    node = _valid_exchange()
    gaps = validate_purpose(node, None)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_PURPOSE


def test_validate_purpose_style_mismatch_on_persuade():
    node = _valid_exchange()
    node.purpose = ExchangePurposeRecord("P2", PurposeType.PERSUADE, "convince")
    node.style = ExchangeStyleRecord("ST2", StyleKind.COMMAND, ExplicitnessLevel.DIRECT)
    gaps = validate_purpose(node, node.purpose)
    assert any(g.gap_type == DiscourseGapType.INVALID_STYLE_PURPOSE_FIT for g in gaps)


def test_validate_style_missing():
    node = _valid_exchange()
    gaps = validate_style(node, None)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_STYLE


def test_validate_style_question_invalid_for_non_question_exchange():
    node = _valid_exchange()
    node.exchange_type = ExchangeType.EXPLANATION
    node.style = ExchangeStyleRecord("STQ", StyleKind.QUESTION, ExplicitnessLevel.DIRECT)
    gaps = validate_style(node, node.style)
    assert any(g.gap_type == DiscourseGapType.INVALID_STYLE_PURPOSE_FIT for g in gaps)


@pytest.mark.parametrize(
    ("carrier_class", "utterance", "concept", "ok"),
    [
        (
            CarrierClass.UTTERANCE,
            DiscourseUtteranceRecord("U", "نَصّ", UtteranceMode.STATEMENT, "direct"),
            None,
            True,
        ),
        (CarrierClass.UTTERANCE, None, None, False),
        (
            CarrierClass.CONCEPT,
            None,
            DiscourseConceptRecord("C", "x", DalaalaKind.MUTABAQA, "g"),
            True,
        ),
        (CarrierClass.CONCEPT, None, None, False),
        (
            CarrierClass.BOTH,
            DiscourseUtteranceRecord("U", "نَصّ", UtteranceMode.STATEMENT, "direct"),
            DiscourseConceptRecord("C", "x", DalaalaKind.MUTABAQA, "g"),
            True,
        ),
        (
            CarrierClass.BOTH,
            DiscourseUtteranceRecord("U", "نَصّ", UtteranceMode.STATEMENT, "direct"),
            None,
            False,
        ),
    ],
)
def test_validate_carrier_cases(carrier_class, utterance, concept, ok):
    node = _valid_exchange()
    carrier = DiscourseCarrierRecord("CX", carrier_class)
    gaps = validate_carrier(node, carrier, utterance, concept)
    assert (gaps == []) is ok


def test_validate_carrier_missing_carrier():
    node = _valid_exchange()
    gaps = validate_carrier(node, None, node.utterance, node.concept)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_CARRIER


def test_validate_reception_missing_reception():
    node = _valid_exchange()
    gaps = validate_reception(node, None, node.reception_state, node.interpretive_outcome)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_RECEPTION


def test_validate_reception_missing_state():
    node = _valid_exchange()
    gaps = validate_reception(node, node.reception, None, node.interpretive_outcome)
    assert any(g.gap_type == DiscourseGapType.MISSING_RECEPTION_STATE for g in gaps)


def test_validate_reception_missing_outcome_warns():
    node = _valid_exchange()
    gaps = validate_reception(node, node.reception, node.reception_state, None)
    assert any(g.gap_type == DiscourseGapType.RECEPTION_INCONSISTENCY for g in gaps)


@pytest.mark.parametrize(
    ("exchange_type", "has_trust", "expect_gap"),
    [
        (ExchangeType.TEACHING, True, False),
        (ExchangeType.TEACHING, False, True),
        (ExchangeType.TESTIMONY, False, True),
        (ExchangeType.EXPLANATION, False, True),
        (ExchangeType.REPORT, False, False),
    ],
)
def test_validate_trust(exchange_type, has_trust, expect_gap):
    node = _valid_exchange()
    node.exchange_type = exchange_type
    trust = node.trust_profile if has_trust else None
    gaps = validate_trust(node, trust)
    assert (any(g.gap_type == DiscourseGapType.MISSING_TRUST_PROFILE for g in gaps)) is expect_gap


def test_validate_knowledge_transfer_missing():
    node = _valid_exchange()
    gaps = validate_knowledge_transfer(node, None)
    assert gaps[0].gap_type == DiscourseGapType.MISSING_TRANSFERRED_KNOWLEDGE


def test_validate_knowledge_transfer_invalid_state():
    node = _valid_exchange()
    episode = KnowledgeEpisodeNode(
        node_id="KE2",
        domain_profile="d",
        judgement_type="j",
        method_family="m",
        carrier_type="c",
        validation_state=ValidationState.INVALID,
    )
    gaps = validate_knowledge_transfer(node, episode)
    assert any(g.gap_type == DiscourseGapType.INVALID_TRANSFERRED_KNOWLEDGE for g in gaps)


def test_validate_knowledge_transfer_with_rejected_rank():
    node = _valid_exchange()

    class _RejectedRank:
        name = "REJECTED_METHODOLOGICALLY"

    class _Episode:
        epistemic_rank = _RejectedRank()
        validation_state = ValidationState.VALID

    gaps = validate_knowledge_transfer(node, _Episode())
    assert any(g.gap_type == DiscourseGapType.INVALID_TRANSFERRED_KNOWLEDGE for g in gaps)


def test_validate_sender_purpose_fit_low_authority_directive():
    sender_role = SenderRoleRecord("SR2", SenderRoleType.COMMANDER, AuthorityLevel.LOW)
    purpose = ExchangePurposeRecord("P3", PurposeType.REQUEST_ACTION, "act now")
    gaps = validate_sender_purpose_fit(sender_role, purpose)
    assert gaps and gaps[0].gap_type == DiscourseGapType.SENDER_PURPOSE_MISMATCH


def test_validate_sender_purpose_fit_ok():
    sender_role = SenderRoleRecord("SR2", SenderRoleType.COMMANDER, AuthorityLevel.HIGH)
    purpose = ExchangePurposeRecord("P3", PurposeType.REQUEST_ACTION, "act now")
    assert validate_sender_purpose_fit(sender_role, purpose) == []


def test_validate_reception_consistency_invalid_combo():
    state = ReceptionStateRecord("RS2", ReceptionStateType.ACCEPTED, "ok")
    outcome = InterpretiveOutcomeRecord("IO2", InterpretiveOutcomeType.DISTORTED)
    gaps = validate_reception_consistency(state, outcome)
    assert gaps and gaps[0].gap_type == DiscourseGapType.RECEPTION_INCONSISTENCY


def test_validate_reception_consistency_ok_combo():
    state = ReceptionStateRecord("RS2", ReceptionStateType.ACCEPTED, "ok")
    outcome = InterpretiveOutcomeRecord("IO2", InterpretiveOutcomeType.ALIGNED)
    assert validate_reception_consistency(state, outcome) == []


def test_validate_exchange_valid():
    node = _valid_exchange()
    result = validate_exchange(node)
    assert result.outcome == DiscourseValidationOutcome.VALID
    assert result.gaps == []
    assert node.validation_outcome == DiscourseValidationOutcome.VALID


@pytest.mark.parametrize(
    ("mutator", "expected_gap"),
    [
        (lambda n: setattr(n, "sender", None), DiscourseGapType.MISSING_SENDER),
        (lambda n: setattr(n, "receiver", None), DiscourseGapType.MISSING_RECEIVER),
        (lambda n: setattr(n, "purpose", None), DiscourseGapType.MISSING_PURPOSE),
        (lambda n: setattr(n, "style", None), DiscourseGapType.MISSING_STYLE),
        (lambda n: setattr(n, "carrier", None), DiscourseGapType.MISSING_CARRIER),
        (
            lambda n: setattr(n, "transferred_knowledge", None),
            DiscourseGapType.MISSING_TRANSFERRED_KNOWLEDGE,
        ),
        (lambda n: setattr(n, "reception", None), DiscourseGapType.MISSING_RECEPTION),
        (lambda n: setattr(n, "reception_state", None), DiscourseGapType.MISSING_RECEPTION_STATE),
    ],
)
def test_validate_exchange_required_closure_gaps(mutator, expected_gap):
    node = _valid_exchange()
    mutator(node)
    result = validate_exchange(node)
    assert any(g.gap_type == expected_gap for g in result.gaps)
    assert result.outcome == DiscourseValidationOutcome.INCOMPLETE


def test_validate_exchange_marks_invalid_without_required_missing():
    node = _valid_exchange()
    node.exchange_type = ExchangeType.EXPLANATION
    node.style = ExchangeStyleRecord("STX", StyleKind.QUESTION, ExplicitnessLevel.DIRECT)
    result = validate_exchange(node)
    assert result.outcome == DiscourseValidationOutcome.INVALID


def test_validate_batch_preserves_order():
    valid = _valid_exchange()
    invalid = _valid_exchange()
    invalid.sender = None
    results = validate_batch([valid, invalid])
    assert [r.exchange_id for r in results] == ["DX1", "DX1"]
    assert results[0].outcome == DiscourseValidationOutcome.VALID
    assert results[1].outcome == DiscourseValidationOutcome.INCOMPLETE


def test_validate_batch_empty():
    assert validate_batch([]) == []
