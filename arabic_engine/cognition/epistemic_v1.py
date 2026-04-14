"""epistemic_v1 — المنهج العقلي: التحقق من الخبرة المعرفية

Python is the *source of truth* for all validation logic.  The Cypher files
in ``db/`` mirror these checks but do not re-define them independently.

Core methodological rule (النبهاني):
    A valid cognitive episode must be grounded in:
    1. RealityAnchor  — مرساة الواقع
    2. SenseTrace     — الأثر الحسي
    3. PriorInfo      — المعلومات السابقة (at least one)
    4. LinkingTrace   — أثر الربط

    Prior *opinion* must be excluded (ContaminationLevel < HIGH).

    Judgement on *existence* (EXISTENCE) with a grounded proof → CERTAIN.
    Judgement on *essence / attribute / relation / interpretive* → TRUE_NON_CERTAIN.
    Methodological rejection is modelled as :class:`ValidationOutcome`,
    NOT as a member of :class:`EpistemicRank`.

    Scientific method is only valid for empirical material inquiry and must
    never be treated as the universal basis of knowledge.

Public API
----------
* :func:`validate_episode`
* :func:`assign_epistemic_rank`
* :func:`derive_insertion_policy`
* :func:`validate_linguistic_carrier`
* :func:`resolve_utterance_concept_conflict`
* :func:`validate_batch`
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from arabic_engine.core.enums import (
    CarrierType,
    ContaminationLevel,
    DecisionCode,
    EpistemicRank,
    GapSeverity,
    InsertionPolicy,
    JudgementType,
    MethodFamily,
    RealityKind,
    ValidationOutcome,
)
from arabic_engine.core.types import (
    ConflictResolutionResult,
    ConflictRuleRecord,
    GapRecord,
    JudgementRecord,
    KnowledgeEpisodeInput,
    LinguisticCarrierRecord,
    MethodRecord,
    ProofPathRecord,
    ValidationResult,
)

# ── Internal helpers ────────────────────────────────────────────────────────

_OPINION_REJECT_THRESHOLD = ContaminationLevel.HIGH

# Methods that are only valid for EXISTENCE judgements on MATERIAL reality
_EMPIRICAL_ONLY_METHODS = {MethodFamily.SCIENTIFIC}

# JudgementTypes where CERTAIN rank is reachable
_EXISTENCE_TYPES = {JudgementType.EXISTENCE}

# JudgementTypes where TRUE_NON_CERTAIN is the ceiling
_NON_CERTAIN_TYPES = {
    JudgementType.ESSENCE,
    JudgementType.ATTRIBUTE,
    JudgementType.RELATION,
    JudgementType.INTERPRETIVE,
}


def _make_gap(
    code: DecisionCode,
    severity: GapSeverity,
    description: str,
    episode_id: Optional[str] = None,
) -> GapRecord:
    prefix = f"{episode_id}::" if episode_id else ""
    return GapRecord(
        gap_id=f"{prefix}GAP_{code.name}",
        code=code,
        severity=severity,
        description=description,
    )


# ── validate_linguistic_carrier ─────────────────────────────────────────────

def validate_linguistic_carrier(
    carrier: LinguisticCarrierRecord,
) -> Tuple[bool, List[DecisionCode], List[GapRecord]]:
    """التحقق من الحامل اللغوي — validate the linguistic transport record.

    Rules:
    * UTTERANCE type → ``utterance`` must not be None.
    * CONCEPT type → ``concept`` must not be None.
    * BOTH type → both ``utterance`` and ``concept`` must not be None.

    Parameters
    ----------
    carrier:
        The :class:`~arabic_engine.core.types.LinguisticCarrierRecord` to
        validate.

    Returns
    -------
    tuple[bool, list[DecisionCode], list[GapRecord]]
        A 3-tuple ``(valid, codes, gaps)`` where ``valid`` is ``True`` only
        when all rules pass, ``codes`` is the list of triggered
        :class:`DecisionCode` values, and ``gaps`` is the corresponding list
        of :class:`GapRecord` instances.
    """
    codes: List[DecisionCode] = []
    gaps: List[GapRecord] = []

    if carrier.carrier_type == CarrierType.UTTERANCE:
        if carrier.utterance is None:
            codes.append(DecisionCode.EPI009_CARRIER_INVALID)
            gaps.append(_make_gap(
                DecisionCode.EPI009_CARRIER_INVALID,
                GapSeverity.CRITICAL,
                "CarrierType.UTTERANCE requires utterance to be present",
            ))
    elif carrier.carrier_type == CarrierType.CONCEPT:
        if carrier.concept is None:
            codes.append(DecisionCode.EPI009_CARRIER_INVALID)
            gaps.append(_make_gap(
                DecisionCode.EPI009_CARRIER_INVALID,
                GapSeverity.CRITICAL,
                "CarrierType.CONCEPT requires concept to be present",
            ))
    else:  # BOTH
        missing: List[str] = []
        if carrier.utterance is None:
            missing.append("utterance")
        if carrier.concept is None:
            missing.append("concept")
        if missing:
            codes.append(DecisionCode.EPI012_CARRIER_BOTH_MISSING)
            gaps.append(_make_gap(
                DecisionCode.EPI012_CARRIER_BOTH_MISSING,
                GapSeverity.FATAL,
                f"CarrierType.BOTH requires both carriers; missing: {', '.join(missing)}",
            ))

    return (len(codes) == 0, codes, gaps)


# ── resolve_utterance_concept_conflict ──────────────────────────────────────

def resolve_utterance_concept_conflict(
    carrier: LinguisticCarrierRecord,
    conflict_rule: ConflictRuleRecord,
) -> ConflictResolutionResult:
    """حل التعارض بين المنطوق والمفهوم — resolve an utterance/concept conflict.

    If ``conflict_rule.prefer_concept`` is True the concept wins; otherwise
    the utterance wins.

    Parameters
    ----------
    carrier:
        A linguistic carrier with ``carrier_type == CarrierType.BOTH``.
    conflict_rule:
        The rule dictating which carrier has precedence.

    Returns
    -------
    :class:`ConflictResolutionResult`
        A record with ``winner`` set to ``"concept"`` or ``"utterance"``,
        ``rule_applied`` set to ``conflict_rule``, and a human-readable
        ``rationale`` string.
    """
    winner = "concept" if conflict_rule.prefer_concept else "utterance"
    return ConflictResolutionResult(
        winner=winner,
        rule_applied=conflict_rule,
        rationale=(
            f"Rule '{conflict_rule.rule_id}' applied: "
            f"{'concept' if conflict_rule.prefer_concept else 'utterance'} "
            f"takes precedence. {conflict_rule.rationale}"
        ),
    )


# ── assign_epistemic_rank ───────────────────────────────────────────────────

def assign_epistemic_rank(
    judgement: JudgementRecord,
    method: MethodRecord,
    proof_path: ProofPathRecord,
    has_hard_conflict: bool = False,
) -> EpistemicRank:
    """تحديد الرتبة الإبستيمية — assign the epistemic rank to a valid episode.

    Ranking rules:
    * ``FORMAL_CONTRADICTION`` → :attr:`EpistemicRank.IMPOSSIBLE`
    * ``EXISTENCE`` + valid proof path + no hard conflict → :attr:`EpistemicRank.CERTAIN`
      (unless method is SCIENTIFIC, which caps at TRUE_NON_CERTAIN even for existence)
    * Essence / attribute / relation / interpretive → :attr:`EpistemicRank.TRUE_NON_CERTAIN`
    * Incomplete proof or unresolved conflict → :attr:`EpistemicRank.PROBABILISTIC_DOUBT`

    Parameters
    ----------
    judgement:
        The output judgement of the episode.
    method:
        The epistemological method applied.
    proof_path:
        The proof path for the judgement.
    has_hard_conflict:
        True if a hard (unresolved) conflict was detected.

    Returns
    -------
    :class:`EpistemicRank`
        The assigned rank — one of :attr:`EpistemicRank.CERTAIN`,
        :attr:`EpistemicRank.TRUE_NON_CERTAIN`,
        :attr:`EpistemicRank.PROBABILISTIC_DOUBT`, or
        :attr:`EpistemicRank.IMPOSSIBLE`.
    """
    jtype = judgement.judgement_type

    if jtype == JudgementType.FORMAL_CONTRADICTION:
        return EpistemicRank.IMPOSSIBLE

    if has_hard_conflict or not proof_path.steps:
        return EpistemicRank.PROBABILISTIC_DOUBT

    if jtype in _EXISTENCE_TYPES:
        # Scientific method is only valid for empirical material inquiry;
        # it cannot ground a CERTAIN judgement on its own.
        if method.family in _EMPIRICAL_ONLY_METHODS:
            return EpistemicRank.TRUE_NON_CERTAIN
        return EpistemicRank.CERTAIN

    if jtype in _NON_CERTAIN_TYPES:
        return EpistemicRank.TRUE_NON_CERTAIN

    return EpistemicRank.PROBABILISTIC_DOUBT


# ── derive_insertion_policy ─────────────────────────────────────────────────

def derive_insertion_policy(
    outcome: ValidationOutcome,
    rank: EpistemicRank | None,
) -> InsertionPolicy:
    """اشتقاق سياسة الإدخال — derive the insertion policy from outcome and rank.

    Rules:
    * REJECTED_METHODOLOGICALLY or INVALID → BLOCKED
    * PENDING → GUARDED
    * VALID + CERTAIN → FOUNDATIONAL
    * VALID + TRUE_NON_CERTAIN → ADMISSIBLE
    * VALID + PROBABILISTIC_DOUBT → GUARDED
    * VALID + IMPOSSIBLE → BLOCKED

    Parameters
    ----------
    outcome:
        The validation outcome.
    rank:
        The epistemic rank (may be None if episode was rejected).

    Returns
    -------
    :class:`InsertionPolicy`
        The policy — :attr:`InsertionPolicy.FOUNDATIONAL` for certain
        knowledge, :attr:`InsertionPolicy.ADMISSIBLE` for non-certain,
        :attr:`InsertionPolicy.GUARDED` for doubtful or pending, and
        :attr:`InsertionPolicy.BLOCKED` for invalid or impossible.
    """
    if outcome in (ValidationOutcome.REJECTED_METHODOLOGICALLY, ValidationOutcome.INVALID):
        return InsertionPolicy.BLOCKED
    if outcome == ValidationOutcome.PENDING:
        return InsertionPolicy.GUARDED
    # VALID
    if rank is None:
        return InsertionPolicy.BLOCKED
    if rank == EpistemicRank.CERTAIN:
        return InsertionPolicy.FOUNDATIONAL
    if rank == EpistemicRank.TRUE_NON_CERTAIN:
        return InsertionPolicy.ADMISSIBLE
    if rank == EpistemicRank.PROBABILISTIC_DOUBT:
        return InsertionPolicy.GUARDED
    # IMPOSSIBLE
    return InsertionPolicy.BLOCKED


# ── _check_method_fit ───────────────────────────────────────────────────────

def _check_method_fit(
    method: MethodRecord,
    judgement: JudgementRecord,
    proof_path: ProofPathRecord,
) -> Tuple[List[DecisionCode], List[GapRecord]]:
    """Check method-fit and proof-path compatibility."""
    codes: List[DecisionCode] = []
    gaps: List[GapRecord] = []

    if judgement.judgement_type not in method.domain_fit:
        codes.append(DecisionCode.EPI008_METHOD_FIT_FAILURE)
        gaps.append(_make_gap(
            DecisionCode.EPI008_METHOD_FIT_FAILURE,
            GapSeverity.CRITICAL,
            f"Method '{method.method_id}' (family={method.family.name}) "
            f"does not fit judgement type {judgement.judgement_type.name}",
        ))

    if proof_path.method_fit != method.family:
        codes.append(DecisionCode.EPI013_PROOF_METHOD_MISMATCH)
        gaps.append(_make_gap(
            DecisionCode.EPI013_PROOF_METHOD_MISMATCH,
            GapSeverity.CRITICAL,
            f"ProofPath '{proof_path.path_id}' expects method family "
            f"{proof_path.method_fit.name} but got {method.family.name}",
        ))

    return codes, gaps


# ── validate_episode ────────────────────────────────────────────────────────

def validate_episode(inp: KnowledgeEpisodeInput) -> ValidationResult:
    """التحقق من الخبرة المعرفية — validate a knowledge episode.

    This is the *central function* of the rational method layer.  It checks
    all twelve conditions in order and returns a :class:`ValidationResult`.

    Validation order
    ----------------
    1.  Reality anchor present
    2.  Sense trace present
    3.  At least one prior info present
    4.  No high-level opinion contamination
    5.  Linking trace present
    6.  Judgement present
    7.  Method present
    8.  Method-fit and proof-path compatibility
    9.  Linguistic carrier valid
    10. Proof path present
    11. Conflict rule present
    12. (If BOTH carrier) check for utterance/concept conflict

    Parameters
    ----------
    inp:
        The :class:`KnowledgeEpisodeInput` to validate.

    Returns
    -------
    :class:`ValidationResult`
        A result record containing the ``outcome``, ``rank``,
        ``insertion_policy``, ``gaps``, and ``messages`` collected
        across all twelve validation checks.
    """
    codes: List[DecisionCode] = []
    gaps: List[GapRecord] = []
    messages: List[str] = []

    def _add(code: DecisionCode, severity: GapSeverity, msg: str) -> None:
        codes.append(code)
        gaps.append(_make_gap(code, severity, msg, episode_id=inp.episode_id))
        messages.append(msg)

    # 1. Reality anchor
    if inp.reality_anchor is None:
        _add(
            DecisionCode.EPI001_MISSING_REALITY,
            GapSeverity.FATAL,
            "Missing RealityAnchor — الخبرة تفتقر إلى مرساة الواقع",
        )

    # 2. Sense trace
    if inp.sense_trace is None:
        _add(
            DecisionCode.EPI002_MISSING_SENSE,
            GapSeverity.FATAL,
            "Missing SenseTrace — الخبرة تفتقر إلى أثر حسي",
        )

    # 3. Prior info (at least one)
    if not inp.prior_infos:
        _add(
            DecisionCode.EPI003_MISSING_PRIOR_INFO,
            GapSeverity.FATAL,
            "Missing PriorInfo — الخبرة تفتقر إلى معلومة سابقة",
        )

    # 4. Opinion contamination
    for op in inp.opinion_traces:
        if op.contamination_level == _OPINION_REJECT_THRESHOLD:
            _add(
                DecisionCode.EPI004_OPINION_CONTAMINATION,
                GapSeverity.FATAL,
                f"Opinion contamination HIGH in '{op.opinion_id}' — "
                "تلوث الرأي المسبق يتجاوز العتبة المقبولة",
            )
            break  # one FATAL per episode is sufficient

    # 5. Linking trace
    if inp.linking_trace is None:
        _add(
            DecisionCode.EPI005_MISSING_LINKING,
            GapSeverity.FATAL,
            "Missing LinkingTrace — الخبرة تفتقر إلى أثر الربط",
        )

    # 6. Judgement
    if inp.judgement is None:
        _add(
            DecisionCode.EPI006_MISSING_JUDGEMENT,
            GapSeverity.FATAL,
            "Missing JudgementRecord — الخبرة تفتقر إلى حكم",
        )

    # 7. Method
    if inp.method is None:
        _add(
            DecisionCode.EPI007_MISSING_METHOD,
            GapSeverity.FATAL,
            "Missing MethodRecord — الخبرة تفتقر إلى طريقة",
        )

    # 8. Method-fit and proof-path compatibility (only when both present)
    if inp.method is not None and inp.judgement is not None and inp.proof_path is not None:
        fit_codes, fit_gaps = _check_method_fit(inp.method, inp.judgement, inp.proof_path)
        # Stamp fit gaps with episode_id
        fit_gaps = [
            GapRecord(
                gap_id=f"{inp.episode_id}::{g.gap_id}",
                code=g.code,
                severity=g.severity,
                description=g.description,
            )
            for g in fit_gaps
        ]
        codes.extend(fit_codes)
        gaps.extend(fit_gaps)
        messages.extend(g.description for g in fit_gaps)

    # 8b. Scientific method requires a MATERIAL reality anchor
    if (
        inp.method is not None
        and inp.method.family in _EMPIRICAL_ONLY_METHODS
        and inp.reality_anchor is not None
        and inp.reality_anchor.kind != RealityKind.MATERIAL
    ):
        _add(
            DecisionCode.EPI008_METHOD_FIT_FAILURE,
            GapSeverity.CRITICAL,
            f"SCIENTIFIC method requires a MATERIAL reality anchor; "
            f"got {inp.reality_anchor.kind.name}",
        )

    # 9. Linguistic carrier
    carrier_valid = True
    if inp.carrier is None:
        _add(
            DecisionCode.EPI009_CARRIER_INVALID,
            GapSeverity.FATAL,
            "Missing LinguisticCarrier — الخبرة تفتقر إلى حامل لغوي",
        )
        carrier_valid = False
    else:
        cv, carrier_codes, carrier_gaps = validate_linguistic_carrier(inp.carrier)
        if not cv:
            carrier_valid = False
            # Re-stamp carrier gaps with episode_id
            carrier_gaps = [
                GapRecord(
                    gap_id=f"{inp.episode_id}::{g.gap_id}",
                    code=g.code,
                    severity=g.severity,
                    description=g.description,
                )
                for g in carrier_gaps
            ]
            codes.extend(carrier_codes)
            gaps.extend(carrier_gaps)
            messages.extend(g.description for g in carrier_gaps)

    # 10. Proof path
    if inp.proof_path is None:
        _add(
            DecisionCode.EPI010_MISSING_PROOF_PATH,
            GapSeverity.FATAL,
            "Missing ProofPath — الخبرة تفتقر إلى مسار إثبات",
        )

    # 11. Conflict rule
    if inp.conflict_rule is None:
        _add(
            DecisionCode.EPI011_MISSING_CONFLICT_RULE,
            GapSeverity.FATAL,
            "Missing ConflictRule — الخبرة تفتقر إلى قاعدة حل التعارض",
        )

    # 12. BOTH carrier conflict check
    has_hard_conflict = False
    if (
        carrier_valid
        and inp.carrier is not None
        and inp.carrier.carrier_type == CarrierType.BOTH
        and inp.carrier.utterance is not None
        and inp.carrier.concept is not None
    ):
        utt_text = inp.carrier.utterance.text
        con_label = inp.carrier.concept.label
        if utt_text != con_label:
            if inp.conflict_rule is not None:
                # Soft conflict — apply rule
                resolution = resolve_utterance_concept_conflict(inp.carrier, inp.conflict_rule)
                messages.append(
                    f"Utterance/concept conflict resolved: winner='{resolution.winner}' "
                    f"via rule '{resolution.rule_applied.rule_id}'"
                )
                has_hard_conflict = False
            else:
                # Hard conflict — no rule to resolve (EPI011 fires above; EPI014 here)
                _add(
                    DecisionCode.EPI014_UTTERANCE_CONCEPT_CONFLICT,
                    GapSeverity.FATAL,
                    "CarrierType.BOTH has utterance/concept mismatch with no ConflictRule — "
                    "لا توجد قاعدة لحل التعارض بين المنطوق والمفهوم",
                )
                has_hard_conflict = True

    # Determine outcome
    fatal_codes = {
        DecisionCode.EPI001_MISSING_REALITY,
        DecisionCode.EPI002_MISSING_SENSE,
        DecisionCode.EPI003_MISSING_PRIOR_INFO,
        DecisionCode.EPI004_OPINION_CONTAMINATION,
        DecisionCode.EPI005_MISSING_LINKING,
        DecisionCode.EPI006_MISSING_JUDGEMENT,
        DecisionCode.EPI007_MISSING_METHOD,
        DecisionCode.EPI009_CARRIER_INVALID,
        DecisionCode.EPI010_MISSING_PROOF_PATH,
        DecisionCode.EPI011_MISSING_CONFLICT_RULE,
        DecisionCode.EPI012_CARRIER_BOTH_MISSING,
        DecisionCode.EPI014_UTTERANCE_CONCEPT_CONFLICT,
    }
    has_fatal = any(c in fatal_codes for c in codes)
    has_method_errors = any(
        c in (DecisionCode.EPI008_METHOD_FIT_FAILURE, DecisionCode.EPI013_PROOF_METHOD_MISMATCH)
        for c in codes
    )

    if has_fatal:
        outcome = ValidationOutcome.REJECTED_METHODOLOGICALLY
        rank = None
    elif has_method_errors:
        outcome = ValidationOutcome.INVALID
        rank = None
    else:
        outcome = ValidationOutcome.VALID
        # All required fields present — assign rank
        assert inp.judgement is not None  # noqa: S101 (guaranteed above)
        assert inp.method is not None     # noqa: S101
        assert inp.proof_path is not None # noqa: S101
        rank = assign_epistemic_rank(
            inp.judgement,
            inp.method,
            inp.proof_path,
            has_hard_conflict=has_hard_conflict,
        )
        # IMPOSSIBLE rank from formal contradiction → outcome stays VALID
        # (the rank itself encodes the impossibility)

    insertion_policy = derive_insertion_policy(outcome, rank)

    return ValidationResult(
        episode_id=inp.episode_id,
        outcome=outcome,
        codes=tuple(codes),
        rank=rank,
        insertion_policy=insertion_policy,
        gaps=tuple(gaps),
        messages=tuple(messages),
    )


# ── validate_batch ──────────────────────────────────────────────────────────

def validate_batch(
    inputs: Sequence[KnowledgeEpisodeInput],
) -> Tuple[ValidationResult, ...]:
    """التحقق الجماعي — validate a sequence of episodes in order.

    Episodes are validated in the order given.  Results are returned in the
    same order.

    Parameters
    ----------
    inputs:
        An ordered sequence of :class:`KnowledgeEpisodeInput` objects.

    Returns
    -------
    Tuple of :class:`ValidationResult` in the same order as ``inputs``.
    """
    return tuple(validate_episode(inp) for inp in inputs)
