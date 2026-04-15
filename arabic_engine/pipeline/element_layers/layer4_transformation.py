"""Layer 4 — طبقة التحول (Transformation Layer).

Documents what changes have affected the element: substitution,
deletion, ʿillal (weak-letter transformation), idghām (assimilation),
and stability across inflection.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import (
    PhonCategory,
    PhonFeature,
    PhonTransform,
    StrictLayerID,
    TransitionGateStatus,
)
from arabic_engine.core.types import (
    StructuralProfileRecord,
    TransformationProfileRecord,
    TransitionGate,
)
from arabic_engine.morphology.dmin import DMIN_REGISTRY

# ── Weak letters (أحرف العلة) ─────────────────────────────────────────
_WEAK_CODEPOINTS = {0x0627, 0x0648, 0x064A}  # ا و ي

# ── Scoring constants ────────────────────────────────────────────────
_TRANSFORM_COUNT_PENALTY = 0.1


def assess_inflection_stability(
    codepoint: int,
    structural: Optional[StructuralProfileRecord] = None,
) -> float:
    """الثبات عبر التصريف — stability across inflectional paradigms.

    Root consonants that never change across conjugation/declension
    score high.  Weak letters that transform score low.
    """
    if codepoint in _WEAK_CODEPOINTS:
        return 0.3
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    # Consonants with few transforms are more stable
    stability = 1.0 - min(1.0, len(entry.transforms) * _TRANSFORM_COUNT_PENALTY)
    # Root consonants get a boost
    if structural and structural.root_slot in ("fa", "ayn", "lam"):
        stability = min(1.0, stability + 0.2)
    return stability


def assess_recoverability(
    codepoint: int,
    surface_form: Optional[str] = None,
    underlying_form: Optional[str] = None,
) -> float:
    """إمكان الرد إلى الأصل — recoverability to the original form.

    If surface and underlying match, fully recoverable.
    If they differ, partially recoverable via morphological rules.
    """
    if surface_form is not None and underlying_form is not None:
        if surface_form == underlying_form:
            return 1.0
        return 0.6
    # Default: check if element has transforms that suggest recoverability
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    if PhonTransform.IBDAL in entry.transforms:
        return 0.7
    if PhonTransform.ITLAL_TR in entry.transforms:
        return 0.6
    return 0.9


def detect_substitution(
    codepoint: int,
    surface_form: Optional[str] = None,
    underlying_form: Optional[str] = None,
) -> float:
    """ثقة الإبدال — substitution confidence."""
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    if PhonTransform.IBDAL in entry.transforms:
        if surface_form and underlying_form and surface_form != underlying_form:
            return 0.9
        return 0.4
    return 0.0


def detect_deletion(
    surface_present: bool,
    underlying_present: bool,
) -> float:
    """ثقة الحذف — deletion confidence."""
    if not surface_present and underlying_present:
        return 0.9
    return 0.0


def detect_illal(codepoint: int) -> float:
    """ثقة الإعلال — weak-letter transformation confidence."""
    if codepoint not in _WEAK_CODEPOINTS:
        return 0.0
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    if PhonTransform.ITLAL_TR in entry.transforms:
        return 0.8
    if entry.category in (PhonCategory.SEMI_VOWEL, PhonCategory.LONG_VOWEL):
        return 0.5
    return 0.2


def detect_idgham(codepoint: int) -> float:
    """ثقة الإدغام — assimilation confidence."""
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    if PhonTransform.IDGHAM in entry.transforms:
        return 0.7
    if PhonFeature.SHADID in entry.features:
        return 0.3
    return 0.0


def build_transformation_record(
    codepoint: int,
    structural: Optional[StructuralProfileRecord] = None,
    surface_form: Optional[str] = None,
    underlying_form: Optional[str] = None,
    surface_present: bool = True,
    underlying_present: bool = True,
) -> TransformationProfileRecord:
    """بناء سجل طبقة التحول."""
    stability = assess_inflection_stability(codepoint, structural)
    recover = assess_recoverability(codepoint, surface_form, underlying_form)
    sub_conf = detect_substitution(codepoint, surface_form, underlying_form)
    del_conf = detect_deletion(surface_present, underlying_present)
    illal_conf = detect_illal(codepoint)
    idgham_conf = detect_idgham(codepoint)

    return TransformationProfileRecord(
        inflection_stability_score=stability,
        recoverability_score=recover,
        surface_presence=surface_present,
        underlying_presence=underlying_present,
        substitution_confidence=sub_conf,
        deletion_confidence=del_conf,
        illal_confidence=illal_conf,
        idgham_confidence=idgham_conf,
    )


def check_gate_4_to_5(
    record: TransformationProfileRecord,
) -> TransitionGate:
    """بوابة الانتقال من الطبقة 4 إلى الطبقة 5.

    Conditions:
    1. Meaningful recoverability score, OR
    2. At least one transformation confidence is meaningful
    """
    c1 = record.recoverability_score >= 0.2
    c2 = max(
        record.substitution_confidence,
        record.deletion_confidence,
        record.illal_confidence,
        record.idgham_confidence,
    ) >= 0.1

    passed = c1 or c2
    conditions = (c1, c2)
    failures: list[str] = []
    if not passed:
        failures.append("no_recoverability_or_transformation")

    status = (
        TransitionGateStatus.PASSED
        if passed
        else TransitionGateStatus.BLOCKED
    )

    return TransitionGate(
        source_layer=StrictLayerID.TRANSFORMATION,
        target_layer=StrictLayerID.HIGHER_FUNCTION,
        conditions_met=conditions,
        gate_status=status,
        failure_reasons=tuple(failures),
    )
