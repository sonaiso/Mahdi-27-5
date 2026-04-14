"""tests/test_epistemic_v1.py — comprehensive tests for epistemic_v1.

Covers:
* CERTAIN valid case
* TRUE_NON_CERTAIN valid case (existence + SCIENTIFIC method)
* Methodological rejection cases (each EPI00x code)
* IMPOSSIBLE case (FORMAL_CONTRADICTION)
* Carrier mismatch cases (UTTERANCE/CONCEPT/BOTH)
* Conflict resolution cases
* InsertionPolicy cases
* Batch ordering
* Concept only / Utterance only / BOTH missing one side
* Full proof path but method_fit mismatch
* Scientific method + existence = TRUE_NON_CERTAIN (not CERTAIN)
* Distinction between REJECTED_METHODOLOGICALLY and IMPOSSIBLE
"""

from __future__ import annotations

import pytest

from arabic_engine.cognition.epistemic_v1 import (
    assign_epistemic_rank,
    derive_insertion_policy,
    resolve_utterance_concept_conflict,
    validate_batch,
    validate_episode,
    validate_linguistic_carrier,
)
from arabic_engine.core.enums import (
    CarrierType,
    ContaminationLevel,
    DecisionCode,
    EpistemicRank,
    GapSeverity,
    InsertionPolicy,
    JudgementType,
    LinkKind,
    MethodFamily,
    ProofPathKind,
    RealityKind,
    SenseModality,
    TraceMode,
    ValidationOutcome,
)
from arabic_engine.core.types import (
    ConceptRecord,
    ConflictRuleRecord,
    JudgementRecord,
    KnowledgeEpisodeInput,
    LinguisticCarrierRecord,
    LinkingTraceRecord,
    MethodRecord,
    OpinionTraceRecord,
    PriorInfoRecord,
    ProofPathRecord,
    RealityAnchorRecord,
    SenseTraceRecord,
    UtteranceRecord,
)

# ── Fixtures / helpers ───────────────────────────────────────────────────────

def _reality(kind: RealityKind = RealityKind.MATERIAL) -> RealityAnchorRecord:
    return RealityAnchorRecord(anchor_id="RA_001", kind=kind, description="test reality")


def _sense() -> SenseTraceRecord:
    return SenseTraceRecord(
        trace_id="ST_001",
        modality=SenseModality.VISUAL,
        mode=TraceMode.DIRECT,
        description="visual direct observation",
    )


def _prior() -> tuple[PriorInfoRecord, ...]:
    return (PriorInfoRecord(info_id="PI_001", content="prior knowledge", source="AX_001"),)


def _linking() -> LinkingTraceRecord:
    return LinkingTraceRecord(link_id="LT_001", kind=LinkKind.CAUSAL, description="causal link")


def _judgement(jtype: JudgementType = JudgementType.EXISTENCE) -> JudgementRecord:
    return JudgementRecord(
        judgement_id="J_001",
        judgement_type=jtype,
        content="test judgement",
    )


def _method(
    family: MethodFamily = MethodFamily.RATIONAL,
    domain_fit: tuple[JudgementType, ...] | None = None,
) -> MethodRecord:
    if domain_fit is None:
        domain_fit = (
            JudgementType.EXISTENCE,
            JudgementType.ESSENCE,
            JudgementType.ATTRIBUTE,
            JudgementType.RELATION,
            JudgementType.INTERPRETIVE,
            JudgementType.FORMAL_CONTRADICTION,
        )
    return MethodRecord(
        method_id="M_001",
        family=family,
        name="rational",
        domain_fit=domain_fit,
    )


def _proof(method_fit: MethodFamily = MethodFamily.RATIONAL) -> ProofPathRecord:
    return ProofPathRecord(
        path_id="PP_001",
        kind=ProofPathKind.DIRECT_PROOF,
        steps=("step 1", "step 2"),
        method_fit=method_fit,
    )


def _carrier(
    ctype: CarrierType = CarrierType.UTTERANCE,
    utterance: UtteranceRecord | None = None,
    concept: ConceptRecord | None = None,
) -> LinguisticCarrierRecord:
    if utterance is None and ctype in (CarrierType.UTTERANCE, CarrierType.BOTH):
        utterance = UtteranceRecord(utterance_id="U_001", text="كتب")
    if concept is None and ctype in (CarrierType.CONCEPT, CarrierType.BOTH):
        concept = ConceptRecord(concept_record_id="C_001", label="writing")
    return LinguisticCarrierRecord(
        carrier_id="CAR_001",
        carrier_type=ctype,
        utterance=utterance,
        concept=concept,
    )


def _conflict_rule(prefer_concept: bool = True) -> ConflictRuleRecord:
    return ConflictRuleRecord(
        rule_id="CR_001",
        prefer_concept=prefer_concept,
        rationale="concept wins by default",
    )


def _full_input(
    episode_id: str = "EP_001",
    jtype: JudgementType = JudgementType.EXISTENCE,
    method_family: MethodFamily = MethodFamily.RATIONAL,
    carrier_type: CarrierType = CarrierType.UTTERANCE,
    **kwargs,
) -> KnowledgeEpisodeInput:
    """Build a fully valid KnowledgeEpisodeInput."""
    return KnowledgeEpisodeInput(
        episode_id=episode_id,
        reality_anchor=kwargs.get("reality_anchor", _reality()),
        sense_trace=kwargs.get("sense_trace", _sense()),
        prior_infos=kwargs.get("prior_infos", _prior()),
        opinion_traces=kwargs.get("opinion_traces", ()),
        linking_trace=kwargs.get("linking_trace", _linking()),
        judgement=kwargs.get("judgement", _judgement(jtype)),
        method=kwargs.get("method", _method(method_family)),
        carrier=kwargs.get("carrier", _carrier(carrier_type)),
        proof_path=kwargs.get("proof_path", _proof(method_family)),
        conflict_rule=kwargs.get("conflict_rule", _conflict_rule()),
    )


# ── 1. CERTAIN valid case ────────────────────────────────────────────────────

class TestCertainCase:
    def test_certain_outcome_and_rank(self):
        result = validate_episode(_full_input(jtype=JudgementType.EXISTENCE))
        assert result.outcome == ValidationOutcome.VALID
        assert result.rank == EpistemicRank.CERTAIN
        assert result.insertion_policy == InsertionPolicy.FOUNDATIONAL
        assert result.codes == ()

    def test_certain_has_no_gaps(self):
        result = validate_episode(_full_input(jtype=JudgementType.EXISTENCE))
        assert result.gaps == ()


# ── 2. TRUE_NON_CERTAIN valid cases ─────────────────────────────────────────

class TestTrueNonCertainCase:
    @pytest.mark.parametrize("jtype", [
        JudgementType.ESSENCE,
        JudgementType.ATTRIBUTE,
        JudgementType.RELATION,
        JudgementType.INTERPRETIVE,
    ])
    def test_non_certain_rank(self, jtype):
        result = validate_episode(_full_input(jtype=jtype))
        assert result.outcome == ValidationOutcome.VALID
        assert result.rank == EpistemicRank.TRUE_NON_CERTAIN
        assert result.insertion_policy == InsertionPolicy.ADMISSIBLE

    def test_scientific_existence_is_true_non_certain(self):
        """Scientific method on existence → TRUE_NON_CERTAIN (not CERTAIN).

        Scientific method is only valid for empirical material inquiry and
        must never ground a CERTAIN judgement on its own.
        """
        inp = _full_input(
            jtype=JudgementType.EXISTENCE,
            method_family=MethodFamily.SCIENTIFIC,
            method=_method(MethodFamily.SCIENTIFIC, (JudgementType.EXISTENCE,)),
            proof_path=_proof(MethodFamily.SCIENTIFIC),
        )
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.VALID
        assert result.rank == EpistemicRank.TRUE_NON_CERTAIN
        assert result.insertion_policy == InsertionPolicy.ADMISSIBLE


# ── 3. Methodological rejection cases ───────────────────────────────────────

class TestMethodologicalRejection:
    def test_missing_reality_anchor(self):
        inp = _full_input(reality_anchor=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI001_MISSING_REALITY in result.codes
        assert result.rank is None
        assert result.insertion_policy == InsertionPolicy.BLOCKED

    def test_missing_sense_trace(self):
        inp = _full_input(sense_trace=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI002_MISSING_SENSE in result.codes

    def test_missing_prior_info(self):
        inp = _full_input(prior_infos=())
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI003_MISSING_PRIOR_INFO in result.codes

    def test_high_opinion_contamination(self):
        opinion = OpinionTraceRecord(
            opinion_id="OP_001",
            description="prior biased opinion",
            contamination_level=ContaminationLevel.HIGH,
        )
        inp = _full_input(opinion_traces=(opinion,))
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI004_OPINION_CONTAMINATION in result.codes

    def test_low_opinion_contamination_accepted(self):
        """LOW contamination must not trigger EPI004."""
        opinion = OpinionTraceRecord(
            opinion_id="OP_001",
            description="mild prior opinion",
            contamination_level=ContaminationLevel.LOW,
        )
        inp = _full_input(opinion_traces=(opinion,))
        result = validate_episode(inp)
        assert DecisionCode.EPI004_OPINION_CONTAMINATION not in result.codes

    def test_missing_linking_trace(self):
        inp = _full_input(linking_trace=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI005_MISSING_LINKING in result.codes

    def test_missing_judgement(self):
        inp = _full_input(judgement=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI006_MISSING_JUDGEMENT in result.codes

    def test_missing_method(self):
        inp = _full_input(method=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI007_MISSING_METHOD in result.codes

    def test_missing_carrier(self):
        inp = _full_input(carrier=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI009_CARRIER_INVALID in result.codes

    def test_missing_proof_path(self):
        inp = _full_input(proof_path=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI010_MISSING_PROOF_PATH in result.codes

    def test_missing_conflict_rule(self):
        inp = _full_input(conflict_rule=None)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert DecisionCode.EPI011_MISSING_CONFLICT_RULE in result.codes

    def test_completely_empty_episode(self):
        """All fields absent → multiple fatal codes."""
        inp = KnowledgeEpisodeInput(episode_id="EP_EMPTY")
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        fatal = {
            DecisionCode.EPI001_MISSING_REALITY,
            DecisionCode.EPI002_MISSING_SENSE,
            DecisionCode.EPI003_MISSING_PRIOR_INFO,
            DecisionCode.EPI005_MISSING_LINKING,
            DecisionCode.EPI006_MISSING_JUDGEMENT,
            DecisionCode.EPI007_MISSING_METHOD,
            DecisionCode.EPI009_CARRIER_INVALID,
            DecisionCode.EPI010_MISSING_PROOF_PATH,
            DecisionCode.EPI011_MISSING_CONFLICT_RULE,
        }
        for code in fatal:
            assert code in result.codes


# ── 4. IMPOSSIBLE case ───────────────────────────────────────────────────────

class TestImpossibleCase:
    def test_formal_contradiction_rank(self):
        inp = _full_input(jtype=JudgementType.FORMAL_CONTRADICTION)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.VALID
        assert result.rank == EpistemicRank.IMPOSSIBLE
        assert result.insertion_policy == InsertionPolicy.BLOCKED

    def test_impossible_vs_rejected_methodologically(self):
        """IMPOSSIBLE is a valid rank; REJECTED_METHODOLOGICALLY is an outcome.

        They must be distinguishable: IMPOSSIBLE has outcome=VALID,
        REJECTED has rank=None.
        """
        impossible = validate_episode(_full_input(jtype=JudgementType.FORMAL_CONTRADICTION))
        rejected = validate_episode(_full_input(reality_anchor=None))

        assert impossible.outcome == ValidationOutcome.VALID
        assert impossible.rank == EpistemicRank.IMPOSSIBLE

        assert rejected.outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY
        assert rejected.rank is None


# ── 5. Method-fit and proof-path mismatch ────────────────────────────────────

class TestMethodFit:
    def test_method_does_not_fit_judgement(self):
        """SCIENTIFIC method has domain_fit = [EXISTENCE]; ESSENCE fails."""
        inp = _full_input(
            jtype=JudgementType.ESSENCE,
            method=_method(MethodFamily.SCIENTIFIC, (JudgementType.EXISTENCE,)),
            proof_path=_proof(MethodFamily.SCIENTIFIC),
        )
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.INVALID
        assert DecisionCode.EPI008_METHOD_FIT_FAILURE in result.codes
        assert result.rank is None

    def test_proof_method_mismatch(self):
        """Full proof path but method_fit=SCIENTIFIC while method is RATIONAL."""
        inp = _full_input(
            proof_path=_proof(MethodFamily.SCIENTIFIC),  # mismatch
        )
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.INVALID
        assert DecisionCode.EPI013_PROOF_METHOD_MISMATCH in result.codes


# ── 6. Carrier mismatch cases ────────────────────────────────────────────────

class TestCarrierValidation:
    def test_utterance_carrier_missing_utterance(self):
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_001",
            carrier_type=CarrierType.UTTERANCE,
            utterance=None,
            concept=None,
        )
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert not valid
        assert DecisionCode.EPI009_CARRIER_INVALID in codes

    def test_concept_carrier_missing_concept(self):
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_001",
            carrier_type=CarrierType.CONCEPT,
            utterance=None,
            concept=None,
        )
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert not valid
        assert DecisionCode.EPI009_CARRIER_INVALID in codes

    def test_concept_only_carrier_valid(self):
        carrier = _carrier(CarrierType.CONCEPT)
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert valid
        assert codes == []

    def test_utterance_only_carrier_valid(self):
        carrier = _carrier(CarrierType.UTTERANCE)
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert valid

    def test_both_carrier_missing_utterance(self):
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_BOTH",
            carrier_type=CarrierType.BOTH,
            utterance=None,
            concept=ConceptRecord(concept_record_id="C_001", label="writing"),
        )
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert not valid
        assert DecisionCode.EPI012_CARRIER_BOTH_MISSING in codes

    def test_both_carrier_missing_concept(self):
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_BOTH",
            carrier_type=CarrierType.BOTH,
            utterance=UtteranceRecord(utterance_id="U_001", text="كتب"),
            concept=None,
        )
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert not valid
        assert DecisionCode.EPI012_CARRIER_BOTH_MISSING in codes

    def test_both_carrier_both_missing(self):
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_BOTH",
            carrier_type=CarrierType.BOTH,
            utterance=None,
            concept=None,
        )
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert not valid
        assert DecisionCode.EPI012_CARRIER_BOTH_MISSING in codes

    def test_both_carrier_fully_present(self):
        carrier = _carrier(CarrierType.BOTH)
        valid, codes, gaps = validate_linguistic_carrier(carrier)
        assert valid

    def test_episode_with_concept_only_carrier(self):
        inp = _full_input(carrier=_carrier(CarrierType.CONCEPT))
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.VALID

    def test_episode_with_utterance_only_carrier(self):
        inp = _full_input(carrier=_carrier(CarrierType.UTTERANCE))
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.VALID


# ── 7. Conflict resolution cases ─────────────────────────────────────────────

class TestConflictResolution:
    def test_concept_wins_by_rule(self):
        carrier = _carrier(CarrierType.BOTH)
        rule = _conflict_rule(prefer_concept=True)
        result = resolve_utterance_concept_conflict(carrier, rule)
        assert result.winner == "concept"
        assert result.rule_applied is rule

    def test_utterance_wins_by_rule(self):
        carrier = _carrier(CarrierType.BOTH)
        rule = _conflict_rule(prefer_concept=False)
        result = resolve_utterance_concept_conflict(carrier, rule)
        assert result.winner == "utterance"

    def test_conflict_resolved_in_full_episode(self):
        """BOTH carrier with differing utterance/concept texts → still VALID."""
        utterance = UtteranceRecord(utterance_id="U_001", text="كتب")
        concept = ConceptRecord(concept_record_id="C_001", label="reading")
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_BOTH",
            carrier_type=CarrierType.BOTH,
            utterance=utterance,
            concept=concept,
        )
        inp = _full_input(carrier=carrier)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.VALID
        assert any("conflict resolved" in m for m in result.messages)

    def test_no_conflict_when_texts_match(self):
        utterance = UtteranceRecord(utterance_id="U_001", text="كتب")
        concept = ConceptRecord(concept_record_id="C_001", label="كتب")
        carrier = LinguisticCarrierRecord(
            carrier_id="CAR_BOTH",
            carrier_type=CarrierType.BOTH,
            utterance=utterance,
            concept=concept,
        )
        inp = _full_input(carrier=carrier)
        result = validate_episode(inp)
        assert result.outcome == ValidationOutcome.VALID
        assert not any("conflict resolved" in m for m in result.messages)


# ── 8. InsertionPolicy cases ─────────────────────────────────────────────────

class TestInsertionPolicy:
    def test_certain_foundational(self):
        policy = derive_insertion_policy(ValidationOutcome.VALID, EpistemicRank.CERTAIN)
        assert policy == InsertionPolicy.FOUNDATIONAL

    def test_true_non_certain_admissible(self):
        policy = derive_insertion_policy(ValidationOutcome.VALID, EpistemicRank.TRUE_NON_CERTAIN)
        assert policy == InsertionPolicy.ADMISSIBLE

    def test_probabilistic_doubt_guarded(self):
        policy = derive_insertion_policy(
            ValidationOutcome.VALID, EpistemicRank.PROBABILISTIC_DOUBT
        )
        assert policy == InsertionPolicy.GUARDED

    def test_impossible_blocked(self):
        policy = derive_insertion_policy(ValidationOutcome.VALID, EpistemicRank.IMPOSSIBLE)
        assert policy == InsertionPolicy.BLOCKED

    def test_invalid_blocked(self):
        policy = derive_insertion_policy(ValidationOutcome.INVALID, None)
        assert policy == InsertionPolicy.BLOCKED

    def test_rejected_blocked(self):
        policy = derive_insertion_policy(
            ValidationOutcome.REJECTED_METHODOLOGICALLY, None
        )
        assert policy == InsertionPolicy.BLOCKED

    def test_pending_guarded(self):
        policy = derive_insertion_policy(ValidationOutcome.PENDING, None)
        assert policy == InsertionPolicy.GUARDED


# ── 9. assign_epistemic_rank unit tests ──────────────────────────────────────

class TestAssignEpistemicRank:
    def test_existence_rational_certain(self):
        rank = assign_epistemic_rank(
            _judgement(JudgementType.EXISTENCE),
            _method(MethodFamily.RATIONAL),
            _proof(MethodFamily.RATIONAL),
        )
        assert rank == EpistemicRank.CERTAIN

    def test_existence_scientific_true_non_certain(self):
        rank = assign_epistemic_rank(
            _judgement(JudgementType.EXISTENCE),
            _method(MethodFamily.SCIENTIFIC, (JudgementType.EXISTENCE,)),
            _proof(MethodFamily.SCIENTIFIC),
        )
        assert rank == EpistemicRank.TRUE_NON_CERTAIN

    def test_essence_true_non_certain(self):
        rank = assign_epistemic_rank(
            _judgement(JudgementType.ESSENCE),
            _method(),
            _proof(),
        )
        assert rank == EpistemicRank.TRUE_NON_CERTAIN

    def test_formal_contradiction_impossible(self):
        rank = assign_epistemic_rank(
            _judgement(JudgementType.FORMAL_CONTRADICTION),
            _method(),
            _proof(),
        )
        assert rank == EpistemicRank.IMPOSSIBLE

    def test_hard_conflict_probabilistic(self):
        rank = assign_epistemic_rank(
            _judgement(JudgementType.EXISTENCE),
            _method(),
            _proof(),
            has_hard_conflict=True,
        )
        assert rank == EpistemicRank.PROBABILISTIC_DOUBT

    def test_empty_proof_steps_probabilistic(self):
        empty_proof = ProofPathRecord(
            path_id="PP_EMPTY",
            kind=ProofPathKind.DIRECT_PROOF,
            steps=(),
            method_fit=MethodFamily.RATIONAL,
        )
        rank = assign_epistemic_rank(
            _judgement(JudgementType.EXISTENCE),
            _method(),
            empty_proof,
        )
        assert rank == EpistemicRank.PROBABILISTIC_DOUBT


# ── 10. Batch validation ordering ────────────────────────────────────────────

class TestValidateBatch:
    def test_batch_preserves_order(self):
        inputs = [
            _full_input(episode_id="EP_A", jtype=JudgementType.EXISTENCE),
            _full_input(episode_id="EP_B", jtype=JudgementType.ESSENCE),
            KnowledgeEpisodeInput(episode_id="EP_C"),  # empty → rejected
        ]
        results = validate_batch(inputs)
        assert len(results) == 3
        assert results[0].episode_id == "EP_A"
        assert results[1].episode_id == "EP_B"
        assert results[2].episode_id == "EP_C"
        assert results[0].rank == EpistemicRank.CERTAIN
        assert results[1].rank == EpistemicRank.TRUE_NON_CERTAIN
        assert results[2].outcome == ValidationOutcome.REJECTED_METHODOLOGICALLY

    def test_batch_empty_sequence(self):
        results = validate_batch([])
        assert results == ()

    def test_batch_returns_tuple(self):
        results = validate_batch([_full_input()])
        assert isinstance(results, tuple)


# ── 11. Gap severity checks ───────────────────────────────────────────────────

class TestGapSeverity:
    def test_missing_reality_is_fatal(self):
        inp = _full_input(reality_anchor=None)
        result = validate_episode(inp)
        fatal_gaps = [g for g in result.gaps if g.severity == GapSeverity.FATAL]
        assert any(g.code == DecisionCode.EPI001_MISSING_REALITY for g in fatal_gaps)

    def test_method_fit_failure_is_critical(self):
        inp = _full_input(
            jtype=JudgementType.ESSENCE,
            method=_method(MethodFamily.SCIENTIFIC, (JudgementType.EXISTENCE,)),
            proof_path=_proof(MethodFamily.SCIENTIFIC),
        )
        result = validate_episode(inp)
        critical_gaps = [g for g in result.gaps if g.severity == GapSeverity.CRITICAL]
        assert len(critical_gaps) >= 1


# ── 12. EpistemicRank is four-level only ─────────────────────────────────────

class TestEpistemicRankStructure:
    def test_rank_has_exactly_four_members(self):
        members = list(EpistemicRank)
        assert len(members) == 4

    def test_rank_members_are_correct(self):
        names = {m.name for m in EpistemicRank}
        assert names == {"CERTAIN", "TRUE_NON_CERTAIN", "PROBABILISTIC_DOUBT", "IMPOSSIBLE"}

    def test_rejected_methodologically_not_in_rank(self):
        rank_names = {m.name for m in EpistemicRank}
        assert "REJECTED_METHODOLOGICALLY" not in rank_names

    def test_validation_outcome_has_rejected_methodologically(self):
        from arabic_engine.core.enums import ValidationOutcome
        names = {m.name for m in ValidationOutcome}
        assert "REJECTED_METHODOLOGICALLY" in names


# ── 13. DecisionCode completeness ────────────────────────────────────────────

class TestDecisionCodes:
    def test_all_expected_codes_exist(self):
        expected = {
            "EPI001_MISSING_REALITY",
            "EPI002_MISSING_SENSE",
            "EPI003_MISSING_PRIOR_INFO",
            "EPI004_OPINION_CONTAMINATION",
            "EPI005_MISSING_LINKING",
            "EPI006_MISSING_JUDGEMENT",
            "EPI007_MISSING_METHOD",
            "EPI008_METHOD_FIT_FAILURE",
            "EPI009_CARRIER_INVALID",
            "EPI010_MISSING_PROOF_PATH",
            "EPI011_MISSING_CONFLICT_RULE",
            "EPI012_CARRIER_BOTH_MISSING",
            "EPI013_PROOF_METHOD_MISMATCH",
            "EPI014_UTTERANCE_CONCEPT_CONFLICT",
        }
        from arabic_engine.core.enums import DecisionCode
        actual = {m.name for m in DecisionCode}
        assert expected <= actual
