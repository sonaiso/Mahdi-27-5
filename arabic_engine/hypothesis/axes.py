"""Axis hypotheses — فرضيات محورية.

Generates axis hypothesis nodes from concept hypotheses.  Each concept
may activate zero or more semantic axes (e.g. definite/indefinite,
derived/frozen, temporal/spatial).

All 6 axes are now resolved:
1. معرفة/نكرة — definite/indefinite
2. جامد/مشتق — frozen/derived
3. مبني/معرب — invariant/declined
4. كلي/جزئي — universal/particular
5. ثابت/متحول — constant/variable
6. زمني/مكاني — temporal/spatial
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode
from arabic_engine.particle.registry import all_forms as all_particle_forms

_AXIS_NAMES = (
    "جامد/مشتق",
    "مبني/معرب",
    "معرفة/نكرة",
    "كلي/جزئي",
    "ثابت/متحول",
    "زمني/مكاني",
)

# ── Derived (مشتق) patterns — morphological weights of Arabic derivatives
_DERIVED_PATTERNS = frozenset({
    "فاعل", "مفعول", "فعيل", "أفعل", "فَعّال", "مُفَعِّل",
    "مُتَفَعِّل", "مُنْفَعِل", "مُفْتَعِل", "مُسْتَفْعِل",
    "فَعِل", "فَعُول", "فَعَلان", "مِفْعَل", "مِفْعال",
})

# ── Invariant (مبني) word lists
_INVARIANT_PARTICLES = all_particle_forms()

_INVARIANT_PRONOUNS = frozenset({
    "هو", "هي", "هم", "هن", "أنت", "أنتم", "أنتن",
    "أنا", "نحن", "هما", "أنتما",
})

_DEMONSTRATIVES = frozenset({
    "هذا", "هذه", "ذلك", "تلك", "هؤلاء", "أولئك",
    "ذاك", "ذانك", "هاتان", "هاتين",
})

_RELATIVE_PRONOUNS = frozenset({
    "الذي", "التي", "الذين", "اللاتي", "اللواتي", "اللتان", "اللتين",
})

# ── Universal (كلي) quantifiers
_UNIVERSAL_QUANTIFIERS = frozenset({
    "كل", "جميع", "كافة", "عامة", "سائر",
})

# ── Temporal (زمني) adverbs
_TEMPORAL_ADVERBS = frozenset({
    "اليوم", "غدًا", "غداً", "أمس", "حين", "إذ", "إذا",
    "متى", "لما", "بعد", "قبل", "عند", "حيث",
    "دائمًا", "أبدًا", "أحيانًا", "صباحًا", "مساءً",
    "ليلًا", "نهارًا",
})

# ── Spatial (مكاني) adverbs
# Shadda diacritic — used to strip doubled consonant marks
_SHADDA = "\u0651"

_SPATIAL_ADVERBS = frozenset({
    "هنا", "هناك", "فوق", "تحت", "أمام", "خلف",
    "يمين", "يسار", "بين", "وسط", "حول",
    "شمال", "جنوب", "شرق", "غرب",
})


def generate(concept_hypotheses: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate axis hypotheses from concept hypotheses.

    For each concept, creates one axis hypothesis per axis name.

    Parameters
    ----------
    concept_hypotheses : list[HypothesisNode]
        Concept hypotheses (``hypothesis_type == "concept"``).

    Returns
    -------
    list[HypothesisNode]
        Axis hypotheses, ``len(concept_hypotheses) * len(_AXIS_NAMES)``
        in total.
    """
    hypotheses: List[HypothesisNode] = []
    for concept in concept_hypotheses:
        determination = concept.get("determination", "indefinite")
        stype = str(concept.get("semantic_type", ""))
        label = str(concept.get("label", ""))
        for axis_name in _AXIS_NAMES:
            value = _resolve_axis(axis_name, str(determination), stype, label)
            hypotheses.append(
                HypothesisNode(
                    node_id=f"AXIS_{concept.node_id}_{axis_name}",
                    hypothesis_type="axis",
                    stage=ActivationStage.AXIS,
                    source_refs=(concept.node_id,),
                    payload=(
                        ("axis_name", axis_name),
                        ("axis_value", value),
                    ),
                    confidence=concept.confidence,
                    status=HypothesisStatus.ACTIVE,
                )
            )
    return hypotheses


def _resolve_axis(
    axis_name: str, determination: str, stype: str, label: str
) -> str:
    """Resolve a single axis value using semantic type and label."""
    if axis_name == "معرفة/نكرة":
        return _resolve_definiteness(determination)
    if axis_name == "جامد/مشتق":
        return _resolve_derivation(stype, label)
    if axis_name == "مبني/معرب":
        return _resolve_declension(stype, label)
    if axis_name == "كلي/جزئي":
        return _resolve_universality(determination, label)
    if axis_name == "ثابت/متحول":
        return _resolve_constancy(stype, label)
    if axis_name == "زمني/مكاني":
        return _resolve_temporospatial(label)
    return "غير محدد"


def _resolve_definiteness(determination: str) -> str:
    """Resolve معرفة/نكرة axis."""
    return "معرفة" if determination == "definite" else "نكرة"


def _resolve_derivation(stype: str, label: str) -> str:
    """Resolve جامد/مشتق axis — frozen vs derived.

    Events (verbs) are derived. Entities are checked against
    known derivative patterns.
    """
    if stype == "EVENT":
        return "مشتق"
    # Check if the label matches a derivative pattern
    # Simple heuristic: active participle starts with م or matches patterns
    if _matches_derivative_pattern(label):
        return "مشتق"
    return "جامد"


def _matches_derivative_pattern(label: str) -> bool:
    """Check if label matches common Arabic derivative patterns."""
    if not label:
        return False
    # Active participle مُفْعِل / مُفَعِّل pattern: starts with م
    # and has 4+ chars
    if label.startswith("م") and len(label) >= 4:
        return True
    # Passive participle: starts with م and ends with ون/ين/ة
    # Agent noun فاعل: second char is ا
    if len(label) >= 4 and len(label) <= 6:
        stripped = label.replace(_SHADDA, "")  # remove shadda
        if len(stripped) >= 3 and stripped[1:2] == "ا":
            return True
    # أفعل pattern (superlative)
    if label.startswith("أ") and len(label) >= 4:
        return True
    return False


def _resolve_declension(stype: str, label: str) -> str:
    """Resolve مبني/معرب axis — invariant vs declined.

    Particles, pronouns, demonstratives, and relative pronouns are invariant.
    Verbs (EVENT) in past tense are invariant; present tense is declined.
    Regular nouns are declined.
    """
    if label in _INVARIANT_PARTICLES:
        return "مبني"
    if label in _INVARIANT_PRONOUNS:
        return "مبني"
    if label in _DEMONSTRATIVES:
        return "مبني"
    if label in _RELATIVE_PRONOUNS:
        return "مبني"
    if stype == "EVENT":
        # Past tense verbs are invariant; present tense is declined
        # Simple heuristic: if starts with ي/ت/ن/أ it's present (declined)
        if label and label[0] in "يتنأ":
            return "معرب"
        return "مبني"
    return "معرب"


def _resolve_universality(determination: str, label: str) -> str:
    """Resolve كلي/جزئي axis — universal vs particular.

    Universal: definite with generic 'ال' or universal quantifiers.
    Particular: indefinite or proper nouns.
    """
    if label in _UNIVERSAL_QUANTIFIERS:
        return "كلي"
    if determination == "definite":
        # Generic definite article → universal
        return "كلي"
    return "جزئي"


def _resolve_constancy(stype: str, label: str) -> str:
    """Resolve ثابت/متحول axis — constant vs variable.

    Events and derivatives are variable (they change state).
    Fixed entities (proper nouns, genus names) are constant.
    """
    if stype == "EVENT":
        return "متحول"
    if _matches_derivative_pattern(label):
        return "متحول"
    return "ثابت"


def _resolve_temporospatial(label: str) -> str:
    """Resolve زمني/مكاني axis — temporal, spatial, or neither.

    Checks against known temporal and spatial adverb lists.
    """
    if label in _TEMPORAL_ADVERBS:
        return "زمني"
    if label in _SPATIAL_ADVERBS:
        return "مكاني"
    return "غير زمني/مكاني"
