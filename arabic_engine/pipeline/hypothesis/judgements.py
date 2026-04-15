"""Judgement hypotheses — فرضيات الحكم.

Produces a judgement hypothesis from case, role, and concept hypotheses.
The judgement is the final output of the hypothesis graph.

Proposition types:
- تقريرية (declarative) — خبر
- استفهام (interrogative) — إنشائي طلبي
- أمر (imperative) — إنشائي طلبي
- نداء (vocative) — إنشائي طلبي
- تعجب (exclamatory) — إنشائي غير طلبي
- قسم (oath) — إنشائي غير طلبي
- تمنّي (wish) — إنشائي طلبي
- ترجّي (hope) — إنشائي طلبي
- نهي (prohibition) — إنشائي طلبي
- معلّق (suspended) — unresolved
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode

# ── Particle / tool lists for proposition type detection ────────────

_INTERROGATIVE_PARTICLES = frozenset({
    "هل", "أ", "ما", "من", "أين", "كيف", "متى", "لماذا",
    "أي", "أنّى", "كم", "أيّ", "ماذا",
})

_VOCATIVE_PARTICLES = frozenset({"يا", "أيّها", "أيّتها", "أيا", "هيا"})

_OATH_PARTICLES = frozenset({"والله", "تالله", "بالله", "وربّ", "لعمر"})

_WISH_PARTICLES = frozenset({"ليت", "ليتني"})

_HOPE_PARTICLES = frozenset({"لعل", "لعلّ", "لعلّي"})

_PROHIBITION_PARTICLES = frozenset({"لا"})

# Exclamatory patterns: "ما أفعلَ" (ما + أفعل)
_EXCLAMATORY_MA = "ما"

# Minimum length for أفعلَ exclamatory pattern (hamza + root + vowel)
_MIN_AFAL_LENGTH = 3

# Common imperative patterns (verb-initial with no visible subject)
_IMPERATIVE_ROLES = frozenset({"فعل_أمر", "أمر"})


def generate(
    case_hypotheses: List[HypothesisNode],
    concept_hypotheses: Optional[List[HypothesisNode]] = None,
    role_hypotheses: Optional[List[HypothesisNode]] = None,
) -> List[HypothesisNode]:
    """Generate a judgement hypothesis from case, concept, and role hypotheses.

    Parameters
    ----------
    case_hypotheses : list[HypothesisNode]
        Case hypotheses (one per token).
    concept_hypotheses : list[HypothesisNode] or None
        Concept hypotheses for detecting particles and tools.
    role_hypotheses : list[HypothesisNode] or None
        Role hypotheses for detecting imperative mood.

    Returns
    -------
    list[HypothesisNode]
        A singleton list containing the judgement hypothesis.
    """
    if not case_hypotheses:
        return [
            HypothesisNode(
                node_id="JUDG_0",
                hypothesis_type="judgement",
                stage=ActivationStage.JUDGEMENT,
                payload=(
                    ("proposition_type", "غير محدد"),
                    ("rank", "غير محدد"),
                ),
                confidence=0.5,
                status=HypothesisStatus.ACTIVE,
            )
        ]

    avg_conf = sum(h.confidence for h in case_hypotheses) / len(case_hypotheses)
    source_refs = tuple(h.node_id for h in case_hypotheses)

    # Detect proposition type from available hypotheses
    prop_type, rank, detection_conf = _detect_proposition_type(
        concept_hypotheses or [], role_hypotheses or []
    )

    # Apply detection confidence to the overall confidence
    final_conf = round(avg_conf * detection_conf, 4)

    return [
        HypothesisNode(
            node_id="JUDG_0",
            hypothesis_type="judgement",
            stage=ActivationStage.JUDGEMENT,
            source_refs=source_refs,
            payload=(
                ("proposition_type", prop_type),
                ("rank", rank),
                ("case_count", len(case_hypotheses)),
            ),
            confidence=final_conf,
            status=HypothesisStatus.ACTIVE,
        )
    ]


def _detect_proposition_type(
    concept_hypotheses: List[HypothesisNode],
    role_hypotheses: List[HypothesisNode],
) -> Tuple[str, str, float]:
    """Detect the proposition type from concept and role hypotheses.

    Returns
    -------
    tuple[str, str, float]
        (proposition_type, rank, detection_confidence)
    """
    # Collect all labels from concepts for particle detection
    labels = [str(c.get("label", "")) for c in concept_hypotheses]
    roles = [str(r.get("role", "")) for r in role_hypotheses]

    # 1. Check for exclamatory pattern: "ما أفعلَ" (before interrogative,
    #    because ما is both interrogative and exclamatory)
    if _is_exclamatory(labels):
        return ("تعجب", "إنشائي_غير_طلبي", 0.9)

    # 2. Check for interrogative particles
    for label in labels:
        if label in _INTERROGATIVE_PARTICLES:
            return ("استفهام", "إنشائي_طلبي", 0.95)

    # 3. Check for vocative particles
    for label in labels:
        if label in _VOCATIVE_PARTICLES:
            return ("نداء", "إنشائي_طلبي", 0.95)

    # 4. Check for oath particles
    for label in labels:
        if label in _OATH_PARTICLES:
            return ("قسم", "إنشائي_غير_طلبي", 0.9)

    # 5. Check for wish particles (ليت)
    for label in labels:
        if label in _WISH_PARTICLES:
            return ("تمنّي", "إنشائي_طلبي", 0.9)

    # 6. Check for hope particles (لعل)
    for label in labels:
        if label in _HOPE_PARTICLES:
            return ("ترجّي", "إنشائي_طلبي", 0.9)

    # 7. Check for imperative roles
    for role in roles:
        if role in _IMPERATIVE_ROLES:
            return ("أمر", "إنشائي_طلبي", 0.9)

    # 8. Check for prohibition (لا + imperative context)
    if _is_prohibition(labels, roles):
        return ("نهي", "إنشائي_طلبي", 0.85)

    # 9. Default: declarative
    if labels or roles:
        return ("تقريرية", "إخبار", 1.0)

    # No evidence at all — suspend
    return ("معلّق", "غير محدد", 0.5)


def _is_exclamatory(labels: List[str]) -> bool:
    """Check for exclamatory pattern 'ما أفعلَ'."""
    if len(labels) < 2:
        return False
    for i, label in enumerate(labels[:-1]):
        if label == _EXCLAMATORY_MA:
            next_label = labels[i + 1]
            # أفعلَ pattern: starts with أ and has ≥ _MIN_AFAL_LENGTH chars
            # (minimum 3 = hamza + root consonant + vowel pattern)
            if next_label.startswith("أ") and len(next_label) >= _MIN_AFAL_LENGTH:
                return True
    return False


def _is_prohibition(labels: List[str], roles: List[str]) -> bool:
    """Check for prohibition pattern: لا + verb context."""
    has_la = any(label == "لا" for label in labels)
    has_verb = any(role == "فعل" for role in roles)
    return has_la and has_verb
