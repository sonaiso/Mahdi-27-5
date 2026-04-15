"""Layer 1 — القوام التوليدي (Generative Phonetic Profile).

Determines how a sound is physically produced — vocal fold state,
articulation place and mode, closure degree, and resonance — before
it is perceived and classified.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    PhonCategory,
    PhonFeature,
    StrictLayerID,
    TransitionGateStatus,
)
from arabic_engine.core.types import (
    DMin,
    GenerativeProfileRecord,
    TransitionGate,
)
from arabic_engine.morphology.dmin import DMIN_REGISTRY

# ── Feature-group mappings ──────────────────────────────────────────

_VOICED_FEATURES = {PhonFeature.MAJHUR}
_VOICELESS_FEATURES = {PhonFeature.MAHMOUS}
_STOP_FEATURES = {PhonFeature.SHADID}
_FRICATIVE_FEATURES = {PhonFeature.RAKHW}
_NASAL_FEATURES = {PhonFeature.ANFI}
_CONTINUANT_FEATURES = {PhonFeature.RAKHW, PhonFeature.LAYIN}

# Sonority hierarchy: vowels > nasals > fricatives > stops
_SONORITY_BASE = {
    "LONG_VOWEL": 1.0,
    "SHORT_VOWEL": 0.9,
    "SEMI_VOWEL": 0.75,
    "CONSONANT": 0.3,
    "TANWIN": 0.6,
    "SUKUN": 0.0,
    "SHADDA": 0.3,
    "SPECIAL_MARK": 0.2,
}

# ── Scoring constants ────────────────────────────────────────────────
_VOICING_SONORITY_BOOST = 0.15
_NASAL_SONORITY_BOOST = 0.2
_CONTINUANT_SONORITY_BOOST = 0.1


def extract_voicedness(dmin: DMin) -> bool:
    """مجهور أم مهموس — voiced or voiceless."""
    return bool(dmin.features & _VOICED_FEATURES)


def extract_place(dmin: DMin) -> str:
    """صنف الموضع — articulation place class from group name."""
    return dmin.group.name


def extract_manner(dmin: DMin) -> str:
    """صنف نوع الاعتراض — manner of articulation."""
    if dmin.features & _STOP_FEATURES:
        return "stop"
    if dmin.features & _FRICATIVE_FEATURES:
        return "fricative"
    if dmin.category == PhonCategory.SEMI_VOWEL:
        return "approximant"
    if dmin.category in (PhonCategory.LONG_VOWEL, PhonCategory.SHORT_VOWEL):
        return "vowel"
    return "other"


def compute_closure(dmin: DMin) -> float:
    """درجة الانغلاق — closure degree [0, 1].

    Stops have full closure (1.0), fricatives partial (0.6),
    vowels open (0.1).
    """
    if dmin.features & _STOP_FEATURES:
        return 1.0
    if dmin.features & _FRICATIVE_FEATURES:
        return 0.6
    if PhonFeature.ITBAQ in dmin.features:
        return 0.8
    if dmin.category in (PhonCategory.LONG_VOWEL, PhonCategory.SHORT_VOWEL):
        return 0.1
    if dmin.category == PhonCategory.SEMI_VOWEL:
        return 0.3
    return 0.5


def compute_sonority(dmin: DMin) -> float:
    """مستوى الرنة — sonority level [0, 1]."""
    base = _SONORITY_BASE.get(dmin.category.name, 0.2)
    # Voiced consonants are more sonorous
    if dmin.category == PhonCategory.CONSONANT and extract_voicedness(dmin):
        base += _VOICING_SONORITY_BOOST
    # Nasals add sonority
    if dmin.features & _NASAL_FEATURES:
        base += _NASAL_SONORITY_BOOST
    # Continuants add some
    if dmin.features & _CONTINUANT_FEATURES:
        base += _CONTINUANT_SONORITY_BOOST
    return min(1.0, base)


def build_generative_profile(codepoint: int) -> GenerativeProfileRecord:
    """بناء سجل القوام التوليدي لعنصر صوتي."""
    entry = DMIN_REGISTRY.get(codepoint)
    if entry is None:
        return GenerativeProfileRecord(
            voicedness=False,
            air_pressure=0.0,
            place_class="UNKNOWN",
            manner_class="unknown",
            closure_value=0.0,
            release_type="",
            nasality=False,
            continuancy=False,
            sonority_level=0.0,
        )

    voiced = extract_voicedness(entry)
    place = extract_place(entry)
    manner = extract_manner(entry)
    closure = compute_closure(entry)
    sonority = compute_sonority(entry)
    nasal = bool(entry.features & _NASAL_FEATURES)
    continuant = bool(entry.features & _CONTINUANT_FEATURES)

    # Air pressure: stops > fricatives > vowels
    air_pressure = closure * 0.8 + (0.2 if voiced else 0.0)

    # Release type
    release = ""
    if manner == "stop":
        release = "plosive"
    elif manner == "fricative":
        release = "gradual"
    elif manner == "approximant":
        release = "open"
    elif manner == "vowel":
        release = "continuous"

    return GenerativeProfileRecord(
        voicedness=voiced,
        air_pressure=min(1.0, air_pressure),
        place_class=place,
        manner_class=manner,
        closure_value=closure,
        release_type=release,
        nasality=nasal,
        continuancy=continuant,
        sonority_level=sonority,
    )


def check_gate_1_to_2(record: GenerativeProfileRecord) -> TransitionGate:
    """بوابة الانتقال من الطبقة 1 إلى الطبقة 2.

    Conditions:
    1. Has articulation place (موضع تحقق)
    2. Has articulation mode (نوع اعتراض)
    3. Is an independent generative unit (وحدة توليدية مستقلة)
    4. Has minimal sonority or closure value
    """
    c1 = record.place_class != "UNKNOWN"
    c2 = record.manner_class != "unknown"
    c3 = record.place_class != "" and record.manner_class != ""
    c4 = record.sonority_level > 0.0 or record.closure_value > 0.0

    conditions = (c1, c2, c3, c4)
    failures: list[str] = []
    if not c1:
        failures.append("no_place")
    if not c2:
        failures.append("no_manner")
    if not c3:
        failures.append("not_independent_unit")
    if not c4:
        failures.append("no_sonority_or_closure")

    status = (
        TransitionGateStatus.PASSED
        if all(conditions)
        else TransitionGateStatus.BLOCKED
    )

    return TransitionGate(
        source_layer=StrictLayerID.GENERATIVE,
        target_layer=StrictLayerID.AUDITORY_MINIMUM,
        conditions_met=conditions,
        gate_status=status,
        failure_reasons=tuple(failures),
    )
