"""Layer 5 — طبقة الوظيفة العليا والحكم (Higher Function & Judgment).

Issues the final non-arbitrary judgment about the element's
functional classification: original, augmented, substituted,
deleted, weakened, assimilated, attached marker, deictic builder,
or relational connector.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import (
    JudgmentCategory,
    StrictLayerID,
    TransitionGateStatus,
)
from arabic_engine.core.types import (
    JudgmentRecordL5,
    MentalFoundationRecord,
    StructuralProfileRecord,
    TransformationProfileRecord,
    TransitionGate,
)

# ── Judgment thresholds ──────────────────────────────────────────────
_CONFIDENCE_MIN = 0.3

# ── Scoring weights ─────────────────────────────────────────────────
_CONSTITUTIVE_WEIGHT = 0.6
_STABILITY_WEIGHT = 0.3
_ROOT_TRANSFORM_PENALTY = 0.1
_NONROOT_TRANSFORM_PENALTY = 0.3


def judge_original(
    structural: StructuralProfileRecord,
    transformation: TransformationProfileRecord,
) -> float:
    """هل هو أصل؟

    Original = high constitutiveness + high stability + low transformation.
    A confirmed root consonant (high constitutiveness) strongly favours
    the ORIGINAL judgment — transformation potentials are only
    *potential* and do not override actual root membership.
    """
    score = structural.constitutiveness_score * _CONSTITUTIVE_WEIGHT
    score += transformation.inflection_stability_score * _STABILITY_WEIGHT
    # Only penalize if transformation is actually realized, not potential
    # Confirmed root consonants should not lose to potential transforms
    if structural.constitutiveness_score >= 0.5:
        # Root consonant — minimal penalty from transforms
        max_transform = max(
            transformation.substitution_confidence,
            transformation.deletion_confidence,
            transformation.illal_confidence,
            transformation.idgham_confidence,
        )
        score -= max_transform * _ROOT_TRANSFORM_PENALTY
    else:
        max_transform = max(
            transformation.substitution_confidence,
            transformation.deletion_confidence,
            transformation.illal_confidence,
            transformation.idgham_confidence,
        )
        score -= max_transform * _NONROOT_TRANSFORM_PENALTY
    return max(0.0, min(1.0, score))


def judge_augmented(structural: StructuralProfileRecord) -> float:
    """هل هو زائد؟

    Augmented = high dependency + high augmentation capacity.
    A confirmed root consonant cannot be augmented.
    """
    if structural.constitutiveness_score >= 0.5:
        return 0.0
    return min(
        1.0,
        structural.dependency_score * 0.5
        + structural.augmentation_score * 0.5,
    )


def judge_substituted(
    transformation: TransformationProfileRecord,
) -> float:
    """هل هو مبدل؟"""
    return transformation.substitution_confidence


def judge_deleted(
    transformation: TransformationProfileRecord,
) -> float:
    """هل هو محذوف؟"""
    return transformation.deletion_confidence


def judge_weakened(
    transformation: TransformationProfileRecord,
) -> float:
    """هل هو معلول؟"""
    return transformation.illal_confidence


def judge_assimilated(
    transformation: TransformationProfileRecord,
    structural: Optional[StructuralProfileRecord] = None,
) -> float:
    """هل هو مدغم؟

    A confirmed root consonant is not assimilated even if idgham
    is a potential transform.
    """
    if structural and structural.constitutiveness_score >= 0.5:
        return transformation.idgham_confidence * 0.2
    return transformation.idgham_confidence


def judge_attached(structural: StructuralProfileRecord) -> float:
    """هل هو عنصر إلصاق؟

    Attached markers have high attachment + low constitutiveness.
    """
    if structural.constitutiveness_score > 0.5:
        return 0.0
    return min(1.0, structural.attachment_score * 0.8)


def judge_deictic(
    structural: StructuralProfileRecord,
) -> float:
    """هل هو باني مبنيات؟

    Elements that are dependent and have fixed form (high stability)
    and serve as structural builders.
    """
    if structural.constitutiveness_score > 0.5:
        return 0.0
    return min(
        1.0,
        structural.dependency_score * 0.4
        + structural.attachment_score * 0.3
        + 0.1,
    )


def judge_relational(
    structural: StructuralProfileRecord,
) -> float:
    """هل هو أداة ربط / معنى؟"""
    if structural.constitutiveness_score > 0.5:
        return 0.0
    return min(
        1.0,
        structural.dependency_score * 0.3
        + structural.attachment_score * 0.4
        + 0.1,
    )


def select_final_judgment(
    original: float,
    augmented: float,
    substituted: float,
    deleted: float,
    weakened: float,
    assimilated: float,
    attached: float,
    deictic: float,
    relational: float,
) -> JudgmentCategory:
    """اختيار الحكم النهائي — select the highest-confidence judgment."""
    candidates = [
        (original, JudgmentCategory.ORIGINAL),
        (augmented, JudgmentCategory.AUGMENTED),
        (substituted, JudgmentCategory.SUBSTITUTED),
        (deleted, JudgmentCategory.DELETED),
        (weakened, JudgmentCategory.WEAKENED_TRANSFORMED),
        (assimilated, JudgmentCategory.ASSIMILATED),
        (attached, JudgmentCategory.ATTACHED_MARKER),
        (deictic, JudgmentCategory.DEICTIC_BUILDER),
        (relational, JudgmentCategory.RELATIONAL_CONNECTOR),
    ]
    # Sort by score descending; ties broken by enum order (earlier = preferred)
    best_score, best_cat = max(candidates, key=lambda x: x[0])
    return best_cat


def build_judgment(
    structural: StructuralProfileRecord,
    transformation: TransformationProfileRecord,
) -> JudgmentRecordL5:
    """بناء سجل الوظيفة العليا والحكم."""
    orig = judge_original(structural, transformation)
    augm = judge_augmented(structural)
    subs = judge_substituted(transformation)
    delt = judge_deleted(transformation)
    weak = judge_weakened(transformation)
    assi = judge_assimilated(transformation, structural)
    atch = judge_attached(structural)
    deic = judge_deictic(structural)
    rela = judge_relational(structural)

    final = select_final_judgment(
        orig, augm, subs, delt, weak, assi, atch, deic, rela,
    )

    scores = [orig, augm, subs, delt, weak, assi, atch, deic, rela]
    confidence = max(scores)

    # Determine functional class
    _class_map = {
        JudgmentCategory.ORIGINAL: "root_consonant",
        JudgmentCategory.AUGMENTED: "augmented_letter",
        JudgmentCategory.SUBSTITUTED: "substituted",
        JudgmentCategory.DELETED: "deleted",
        JudgmentCategory.WEAKENED_TRANSFORMED: "weakened",
        JudgmentCategory.ASSIMILATED: "assimilated",
        JudgmentCategory.ATTACHED_MARKER: "attached_marker",
        JudgmentCategory.DEICTIC_BUILDER: "deictic_builder",
        JudgmentCategory.RELATIONAL_CONNECTOR: "relational_connector",
    }
    func_class = _class_map.get(final, "unknown")

    # Identity preservation: how much of the original identity remains
    identity_pres = transformation.inflection_stability_score

    return JudgmentRecordL5(
        final_judgment=final,
        judgment_confidence=confidence,
        functional_class=func_class,
        deictic_score=deic,
        relational_score=rela,
        identity_preservation_score=identity_pres,
    )


def check_gate_5_to_6(
    record: JudgmentRecordL5,
    mental: Optional[MentalFoundationRecord] = None,
) -> TransitionGate:
    """بوابة الانتقال من الطبقة 5 إلى الطبقة 6.

    Conditions:
    1. A final_judgment has been issued
    2. judgment_confidence is recorded
    3. reality_match_score from Layer 0 is adequate
    """
    c1 = record.final_judgment is not None
    c2 = record.judgment_confidence >= _CONFIDENCE_MIN
    c3 = True
    if mental is not None:
        c3 = mental.reality_match_score >= 0.1

    conditions = (c1, c2, c3)
    failures: list[str] = []
    if not c1:
        failures.append("no_judgment")
    if not c2:
        failures.append("low_confidence")
    if not c3:
        failures.append("reality_mismatch")

    status = (
        TransitionGateStatus.PASSED
        if all(conditions)
        else TransitionGateStatus.BLOCKED
    )

    return TransitionGate(
        source_layer=StrictLayerID.HIGHER_FUNCTION,
        target_layer=StrictLayerID.PROGRAMMATIC,
        conditions_met=conditions,
        gate_status=status,
        failure_reasons=tuple(failures),
    )
