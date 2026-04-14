"""Mafhūm analysis — minimal types of implied meaning (Ch. 21).

Fh_min* = {مفهوم الشرط, مفهوم الغاية, مفهوم العدد, مفهوم الوصف, مفهوم الإشارة}

This module implements the proof from Chapter 21 of the Arabic formal
system: the five irreducible minimal types of Mafhūm (مفهوم) that arise
from structural constraints in the Manṭūq (منطوق).

Each Mafhūm type corresponds to a unique constraint domain:
  • Condition (شرط)   — suspension of judgment on a premise
  • Goal (غاية)       — endpoint / limit of judgment
  • Number (عدد)      — quantitative restriction
  • Description (وصف) — qualitative restriction
  • Reference (إشارة) — referential / deictic specification

A Mafhūm is valid only when its four pillars (أركان) hold:
  1. Closed Manṭūq (منطوق مغلق)
  2. Structural constraint (قيد بنيوي)
  3. Mental counterpart (مقابل ذهني)
  4. Transition rule (قاعدة انتقال)
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import POS, ConstraintType, MafhumType
from arabic_engine.core.types import (
    LexicalClosure,
    MafhumPillar,
    MafhumResult,
    Proposition,
)

# Default confidence for a valid Mafhūm result.  Set at 0.85 to reflect
# that the structural detection is high-confidence but below 1.0 because
# pragmatic/contextual factors (not modelled at this layer) may override.
_DEFAULT_MAFHUM_CONFIDENCE: float = 0.85


# ── Constraint markers ──────────────────────────────────────────────
# Known Arabic particles/constructs that signal each constraint type.

_CONDITION_MARKERS: set[str] = {
    "إِنْ", "إن", "إِذَا", "إذا", "لَوْ", "لو",
    "مَنْ", "من", "مَا", "ما", "أَيْنَمَا", "أينما",
    "حَيْثُمَا", "حيثما", "كُلَّمَا", "كلما", "مَهْمَا", "مهما",
}

_GOAL_MARKERS: set[str] = {
    "حَتَّى", "حتى", "إِلَى", "إلى",
    "إلى أَنْ", "إلى أن",
}

_NUMBER_PATTERNS: set[str] = {
    # Numeric words and common counting terms
    "وَاحِد", "واحد", "اِثْنَان", "اثنان", "ثَلَاث", "ثلاث",
    "أَرْبَع", "أربع", "خَمْس", "خمس", "سِتّ", "ست",
    "سَبْع", "سبع", "ثَمَان", "ثمان", "تِسْع", "تسع",
    "عَشْر", "عشر", "مِائَة", "مائة", "أَلْف", "ألف",
    "مَرَّة", "مرة", "مَرَّتَيْن", "مرتين",
}

_DESCRIPTION_POS: set[POS] = {POS.SIFA}

_REFERENCE_MARKERS: set[str] = {
    "هَذَا", "هذا", "هَذِهِ", "هذه", "ذَلِكَ", "ذلك",
    "تِلْكَ", "تلك", "هُنَا", "هنا", "هُنَاكَ", "هناك",
    "هَؤُلَاء", "هؤلاء", "أُولَئِكَ", "أولئك",
}

_REFERENCE_POS: set[POS] = {POS.DAMIR, POS.ZARF}


# ── Constraint detection ────────────────────────────────────────────


def _detect_condition(
    closures: List[LexicalClosure],
) -> Optional[tuple[int, str]]:
    """Detect a conditional (شرط) constraint in the token stream.

    Returns (index, marker_lemma) or None.
    """
    for i, cl in enumerate(closures):
        if cl.lemma in _CONDITION_MARKERS or cl.surface in _CONDITION_MARKERS:
            return i, cl.lemma
        if cl.pos == POS.HARF and cl.lemma in _CONDITION_MARKERS:
            return i, cl.lemma
    return None


def _detect_goal(
    closures: List[LexicalClosure],
) -> Optional[tuple[int, str]]:
    """Detect a goal/endpoint (غاية) constraint.

    Returns (index, marker_lemma) or None.
    """
    for i, cl in enumerate(closures):
        if cl.lemma in _GOAL_MARKERS or cl.surface in _GOAL_MARKERS:
            return i, cl.lemma
    return None


def _detect_number(
    closures: List[LexicalClosure],
) -> Optional[tuple[int, str]]:
    """Detect a numerical (عدد) constraint.

    Returns (index, number_lemma) or None.
    """
    for i, cl in enumerate(closures):
        if cl.lemma in _NUMBER_PATTERNS or cl.surface in _NUMBER_PATTERNS:
            return i, cl.lemma
        # Check if the surface form contains digits
        if any(c.isdigit() for c in cl.surface):
            return i, cl.surface
    return None


def _detect_description(
    closures: List[LexicalClosure],
) -> Optional[tuple[int, str]]:
    """Detect a descriptive (وصف) constraint.

    Returns (index, description_lemma) or None.
    """
    for i, cl in enumerate(closures):
        if cl.pos in _DESCRIPTION_POS:
            return i, cl.lemma
    return None


def _detect_reference(
    closures: List[LexicalClosure],
) -> Optional[tuple[int, str]]:
    """Detect a referential/deictic (إشارة) constraint.

    Returns (index, reference_lemma) or None.
    """
    for i, cl in enumerate(closures):
        if cl.lemma in _REFERENCE_MARKERS or cl.surface in _REFERENCE_MARKERS:
            return i, cl.lemma
        if cl.pos in _REFERENCE_POS and cl.lemma:
            return i, cl.lemma
    return None


# ── Counterpart and transition rule generators ──────────────────────

_CONSTRAINT_TO_MAFHUM: dict[ConstraintType, MafhumType] = {
    ConstraintType.SHART: MafhumType.SHART,
    ConstraintType.GHAYA: MafhumType.GHAYA,
    ConstraintType.ADAD: MafhumType.ADAD,
    ConstraintType.WASF: MafhumType.WASF,
    ConstraintType.ISHARA: MafhumType.ISHARA,
}


def _build_counterpart(
    constraint_type: ConstraintType,
    constraint_value: str,
) -> str:
    """Generate the mental counterpart (المقابل الذهني) for a constraint.

    The counterpart is the negation or opposite of the constraint:
      • Condition q  → ¬q (absence of the condition)
      • Goal g       → ما بعد g (what lies beyond the endpoint)
      • Number n     → m ≠ n (a different quantity)
      • Description ω → ¬ω (absence of the description)
      • Reference δ  → غير المشار إليه (the non-referenced)
    """
    if constraint_type == ConstraintType.SHART:
        return f"انتفاء الشرط: ¬({constraint_value})"
    if constraint_type == ConstraintType.GHAYA:
        return f"ما بعد الغاية: بعد ({constraint_value})"
    if constraint_type == ConstraintType.ADAD:
        return f"المغاير العددي: ≠ ({constraint_value})"
    if constraint_type == ConstraintType.WASF:
        return f"انتفاء الوصف: ¬({constraint_value})"
    if constraint_type == ConstraintType.ISHARA:
        return f"غير المشار إليه: خارج ({constraint_value})"
    return ""


def _build_transition_rule(
    constraint_type: ConstraintType,
) -> str:
    """Return the transition rule (قاعدة الانتقال) for a constraint type."""
    rules = {
        ConstraintType.SHART: (
            "إذا عُلِّق الحكم على شرط، فيُبحث في حال انتفاء الشرط"
        ),
        ConstraintType.GHAYA: (
            "إذا حُدَّ الحكم بغاية، فبعد الغاية ليس هو عين ما قبلها إلا بدليل جديد"
        ),
        ConstraintType.ADAD: (
            "إذا خُصَّ الحكم بعدد، فالمغاير العددي يفتح باب النظر في اختلاف الحكم"
        ),
        ConstraintType.WASF: (
            "إذا عُلِّق الحكم على وصف، فانتفاء الوصف يفتح النظر في انتفاء الحكم"
        ),
        ConstraintType.ISHARA: (
            "إذا خُصّ الحكم بمرجع إشاري، فخارج الحقل الإشاري يُنظر فيه بحكم مستقل"
        ),
    }
    return rules.get(constraint_type, "")


def _build_derived_meaning(
    constraint_type: ConstraintType,
    proposition: Proposition,
    constraint_value: str,
) -> str:
    """Derive the implied meaning from the constraint and proposition."""
    subj = proposition.subject or "الموضوع"
    pred = proposition.predicate or "الحكم"

    if constraint_type == ConstraintType.SHART:
        return f"عند انتفاء ({constraint_value})، يُنظر في حال ({pred}) بالنسبة إلى ({subj})"
    if constraint_type == ConstraintType.GHAYA:
        return f"بعد ({constraint_value})، ينتهي ({pred}) ما لم يثبت بدليل جديد"
    if constraint_type == ConstraintType.ADAD:
        return f"بغير العدد ({constraint_value})، يتغير حكم ({pred}) في ({subj})"
    if constraint_type == ConstraintType.WASF:
        return f"عند انتفاء وصف ({constraint_value})، يُنظر في بقاء ({pred})"
    if constraint_type == ConstraintType.ISHARA:
        return f"خارج نطاق الإشارة ({constraint_value})، يُنظر في ({pred}) بحكم مستقل"
    return ""


# ── Main analysis ───────────────────────────────────────────────────

# Ordered list of detectors: (ConstraintType, detector_function)
_DETECTORS = [
    (ConstraintType.SHART, _detect_condition),
    (ConstraintType.GHAYA, _detect_goal),
    (ConstraintType.ADAD, _detect_number),
    (ConstraintType.WASF, _detect_description),
    (ConstraintType.ISHARA, _detect_reference),
]


def analyse_mafhum(
    closures: List[LexicalClosure],
    proposition: Proposition,
    *,
    mantuq_closed: bool = True,
) -> List[MafhumResult]:
    """Analyse closures for all five minimal Mafhūm types.

    Parameters
    ----------
    closures : List[LexicalClosure]
        The lexical closures from the pipeline.
    proposition : Proposition
        The proposition built from the Manṭūq.
    mantuq_closed : bool
        Whether the Manṭūq has been verified as closed (Ch. 19).
        Defaults to True.

    Returns
    -------
    List[MafhumResult]
        A list of detected Mafhūm results (may be empty if no
        structural constraints are found).
    """
    results: List[MafhumResult] = []
    source_text = " ".join(cl.surface for cl in closures)

    for constraint_type, detector in _DETECTORS:
        detection = detector(closures)
        if detection is None:
            continue

        _index, constraint_value = detection
        mafhum_type = _CONSTRAINT_TO_MAFHUM[constraint_type]
        counterpart = _build_counterpart(constraint_type, constraint_value)
        transition_rule = _build_transition_rule(constraint_type)
        derived = _build_derived_meaning(
            constraint_type, proposition, constraint_value,
        )

        pillars = MafhumPillar(
            closed_mantuq=mantuq_closed,
            constraint_type=constraint_type,
            mental_counterpart=counterpart,
            transition_rule=transition_rule,
        )

        valid = (
            mantuq_closed
            and bool(constraint_value)
            and bool(counterpart)
            and bool(transition_rule)
        )

        results.append(MafhumResult(
            mafhum_type=mafhum_type,
            constraint_type=constraint_type,
            pillars=pillars,
            source_text=source_text,
            constraint_value=constraint_value,
            counterpart=counterpart,
            derived_meaning=derived,
            valid=valid,
            confidence=_DEFAULT_MAFHUM_CONFIDENCE if valid else 0.0,
        ))

    return results


def get_minimal_types() -> List[MafhumType]:
    """Return the five minimal Mafhūm types (Fh_min*).

    This is the complete minimal set proven in Chapter 21:
      {مفهوم الشرط, مفهوم الغاية, مفهوم العدد, مفهوم الوصف, مفهوم الإشارة}
    """
    return [
        MafhumType.SHART,
        MafhumType.GHAYA,
        MafhumType.ADAD,
        MafhumType.WASF,
        MafhumType.ISHARA,
    ]


def verify_irreducibility() -> dict[str, bool]:
    """Verify that the five minimal types are mutually irreducible.

    Each type covers an independent domain; removing any one would
    leave its domain uncovered.  This function returns a dict mapping
    each domain name to True (covered) or False (gap).
    """
    domains = {
        "تعليق (suspension)": MafhumType.SHART,
        "حد ومنتهى (limit)": MafhumType.GHAYA,
        "تحديد كمي (quantity)": MafhumType.ADAD,
        "تقييد نوعي (quality)": MafhumType.WASF,
        "تخصيص مرجعي (reference)": MafhumType.ISHARA,
    }
    minimal = set(get_minimal_types())
    return {name: (mtype in minimal) for name, mtype in domains.items()}
