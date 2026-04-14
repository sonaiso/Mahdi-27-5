"""Layer 0 — الطبقة العقلية المؤسسة (Mental Foundation).

Establishes the conditions without which no classification is valid:
identity, difference, rank, constitutiveness, dependency, stability,
transformation, causality, and reality-match.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    PhonFeature,
    StrictLayerID,
    TransitionGateStatus,
)
from arabic_engine.core.types import (
    DMin,
    MentalFoundationRecord,
    TransitionGate,
)
from arabic_engine.signifier.dmin import DMIN_REGISTRY

# ── Thresholds ───────────────────────────────────────────────────────
_IDENTITY_THRESHOLD = 0.3
_DIFFERENCE_THRESHOLD = 0.2
_RANK_THRESHOLD = 0.1
_REALITY_THRESHOLD = 0.1

# ── Pre-computed average feature count (DMIN_REGISTRY is static) ────
_AVG_FEATURE_COUNT = (
    sum(len(d.features) for d in DMIN_REGISTRY.values()) / len(DMIN_REGISTRY)
    if DMIN_REGISTRY
    else 1.0
)


def assess_identity(codepoint: int) -> float:
    """هل له هوية قابلة للإشارة؟

    Returns 1.0 if the codepoint exists in DMIN_REGISTRY, 0.0 otherwise.
    """
    return 1.0 if codepoint in DMIN_REGISTRY else 0.0


def assess_difference(codepoint: int) -> float:
    """هل يتميز عن غيره؟

    Computes distinctiveness as the ratio of unique features this
    element has compared to the average feature count in the registry.
    """
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    my_features = len(entry.features)
    if _AVG_FEATURE_COUNT == 0:
        return 1.0
    return min(1.0, my_features / _AVG_FEATURE_COUNT)


def assess_rank(codepoint: int) -> float:
    """هل له رتبة أو قابلية رتبة؟

    Returns a rank score based on category ordering:
    CONSONANT > SEMI_VOWEL > LONG_VOWEL > SHORT_VOWEL > marks.
    """
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    _rank_map = {
        "CONSONANT": 1.0,
        "SEMI_VOWEL": 0.9,
        "LONG_VOWEL": 0.8,
        "SHORT_VOWEL": 0.7,
        "SUKUN": 0.5,
        "SHADDA": 0.5,
        "TANWIN": 0.4,
        "SPECIAL_MARK": 0.3,
    }
    return _rank_map.get(entry.category.name, 0.2)


def assess_reality_match(codepoint: int) -> float:
    """هل يمكن اختباره بمطابقة الواقع؟

    An element matches reality if it is a known Arabic phonological
    unit with defined features and transforms.
    """
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return 0.0
    score = 0.0
    if entry.features:
        score += 0.5
    if entry.transforms:
        score += 0.3
    if entry.code:
        score += 0.2
    return min(1.0, score)


def _is_constitutive(entry: DMin) -> bool:
    """هل هو مقوّم؟ — constitutive elements are consonants and semi-vowels."""
    return entry.category.name in {"CONSONANT", "SEMI_VOWEL"}


def _is_dependent(entry: DMin) -> bool:
    """هل هو تابع؟ — dependent elements are vowels, marks, sukun."""
    return entry.category.name in {
        "SHORT_VOWEL",
        "LONG_VOWEL",
        "SUKUN",
        "SHADDA",
        "TANWIN",
        "SPECIAL_MARK",
    }


def build_mental_foundation(codepoint: int) -> MentalFoundationRecord:
    """بناء سجل الطبقة العقلية المؤسسة لعنصر معين."""
    entry = DMIN_REGISTRY.get(codepoint)
    identity = assess_identity(codepoint)
    difference = assess_difference(codepoint)
    rank = assess_rank(codepoint)
    reality = assess_reality_match(codepoint)

    is_const = _is_constitutive(entry) if entry else False
    is_dep = _is_dependent(entry) if entry else False

    stability = 1.0 if entry and PhonFeature.SHADID in entry.features else 0.6
    if entry and PhonFeature.RAKHW in entry.features:
        stability = 0.7

    transform_type = ""
    if entry and entry.transforms:
        transform_type = ",".join(sorted(t.name for t in entry.transforms))

    causal_source = ""
    if entry:
        causal_source = entry.group.name

    return MentalFoundationRecord(
        identity_strength=identity,
        distinctiveness=difference,
        rank_position=rank,
        is_constitutive=is_const,
        is_dependent=is_dep,
        stability_score=stability,
        transformation_type=transform_type,
        causal_source=causal_source,
        reality_match_score=reality,
    )


def check_gate_0_to_1(record: MentalFoundationRecord) -> TransitionGate:
    """بوابة الانتقال من الطبقة 0 إلى الطبقة 1.

    Conditions:
    1. Identity (هوية قابلة للإشارة)
    2. Difference (فرق عن غيره)
    3. Rank (رتبة أو قابلية رتبة)
    4. Reality-match (قابلية اختبار بالمطابقة)
    """
    c1 = record.identity_strength >= _IDENTITY_THRESHOLD
    c2 = record.distinctiveness >= _DIFFERENCE_THRESHOLD
    c3 = record.rank_position >= _RANK_THRESHOLD
    c4 = record.reality_match_score >= _REALITY_THRESHOLD

    conditions = (c1, c2, c3, c4)
    failures: list[str] = []
    if not c1:
        failures.append("no_identity")
    if not c2:
        failures.append("no_difference")
    if not c3:
        failures.append("no_rank")
    if not c4:
        failures.append("no_reality_match")

    status = TransitionGateStatus.PASSED if all(conditions) else TransitionGateStatus.BLOCKED

    return TransitionGate(
        source_layer=StrictLayerID.MENTAL_FOUNDATION,
        target_layer=StrictLayerID.GENERATIVE,
        conditions_met=conditions,
        gate_status=status,
        failure_reasons=tuple(failures),
    )
