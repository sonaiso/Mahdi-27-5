"""Layer 2 — القوام السمعي الأدنى (Auditory Minimum).

Proves that the perceived element is a complete, minimal auditory unit
with sufficient presence, boundary, extension, cohesion, and unity.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import StrictLayerID, TransitionGateStatus
from arabic_engine.core.types import (
    AuditoryMinimumRecord,
    GenerativeProfileRecord,
    Syllable,
    TransitionGate,
)

# ── Thresholds ───────────────────────────────────────────────────────
_AUDIBILITY_MIN = 0.1
_UNITY_MIN = 0.2
_COHESION_MIN = 0.15

# ── Scoring constants ────────────────────────────────────────────────
_VOICING_AUDIBILITY_BOOST = 0.15


def assess_audibility(generative: GenerativeProfileRecord) -> float:
    """الحضور السمعي — audibility from sonority and voicedness.

    Voiced sounds are inherently more audible; higher sonority
    means the sound carries further.
    """
    base = generative.sonority_level
    if generative.voicedness:
        base += _VOICING_AUDIBILITY_BOOST
    return min(1.0, base)


def assess_temporal_span(
    syllable: Optional[Syllable],
) -> float:
    """الامتداد الزمني — temporal span from syllable weight.

    Heavier syllables occupy more time.
    """
    if syllable is None:
        return 0.3  # minimal span for an element without syllable context
    weight_map = {1: 0.4, 2: 0.7, 3: 1.0}
    return weight_map.get(syllable.weight, 0.3)


def assess_cohesion(generative: GenerativeProfileRecord) -> float:
    """التماسك — how well the element holds together as a unit.

    Elements with clear place + manner + sonority are more cohesive.
    """
    score = 0.0
    if generative.place_class != "UNKNOWN":
        score += 0.35
    if generative.manner_class != "unknown":
        score += 0.35
    if generative.sonority_level > 0:
        score += 0.3
    return min(1.0, score)


def assess_unity(
    audibility: float,
    cohesion: float,
    temporal: float,
) -> float:
    """الوحدة — overall unity score combining audibility, cohesion, span."""
    return min(1.0, (audibility + cohesion + temporal) / 3.0)


def build_auditory_minimum(
    generative: GenerativeProfileRecord,
    syllable: Optional[Syllable] = None,
) -> AuditoryMinimumRecord:
    """بناء سجل القوام السمعي الأدنى."""
    audibility = assess_audibility(generative)
    temporal = assess_temporal_span(syllable)
    cohesion = assess_cohesion(generative)
    unity = assess_unity(audibility, cohesion, temporal)
    phase_count = 1
    if generative.continuancy:
        phase_count = 2
    if syllable and syllable.weight >= 3:
        phase_count = 3
    order_score = min(1.0, cohesion * 1.1)

    return AuditoryMinimumRecord(
        audibility_score=audibility,
        temporal_span=temporal,
        phase_count=phase_count,
        order_score=order_score,
        cohesion_score=cohesion,
        unity_score=unity,
    )


def check_gate_2_to_3(record: AuditoryMinimumRecord) -> TransitionGate:
    """بوابة الانتقال من الطبقة 2 إلى الطبقة 3.

    Conditions:
    1. audibility_score above minimum
    2. unity_score sufficient for a unit
    3. cohesion_score prevents being mere noise
    4. has temporal_span or estimated position
    """
    c1 = record.audibility_score >= _AUDIBILITY_MIN
    c2 = record.unity_score >= _UNITY_MIN
    c3 = record.cohesion_score >= _COHESION_MIN
    c4 = record.temporal_span > 0.0

    conditions = (c1, c2, c3, c4)
    failures: list[str] = []
    if not c1:
        failures.append("below_audibility_minimum")
    if not c2:
        failures.append("insufficient_unity")
    if not c3:
        failures.append("low_cohesion_noise")
    if not c4:
        failures.append("no_temporal_span")

    status = (
        TransitionGateStatus.PASSED
        if all(conditions)
        else TransitionGateStatus.BLOCKED
    )

    return TransitionGate(
        source_layer=StrictLayerID.AUDITORY_MINIMUM,
        target_layer=StrictLayerID.STRUCTURAL,
        conditions_met=conditions,
        gate_status=status,
        failure_reasons=tuple(failures),
    )
