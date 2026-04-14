"""epistemic_reception — دستور الاستقبال المعرفي: Epistemic Reception Constitution v1

This module is logically prior to :mod:`~arabic_engine.cognition.epistemic_v1`
because it governs **how** the rational self receives the world — before any
judgement, commitment, derivation, or composition takes place.

Two orthogonal axes are modelled:

1. **Subject Axis** (محور الموضوع) — *what* arrives: Existence, Attribute,
   Event, or Relation  (Art. 5).
2. **Reception Axis** (محور التلقي) — *how* it is received and processed:
   Sense → Feeling → Thought → Intention → Choice → Will  (Art. 13).

The constitutional matrix (Art. 40) assigns each (genre, rank) pair a
:class:`CarryingMode` — original / subsidiary / prohibited.

Public API
----------
* :func:`classify_subject`
* :func:`get_reception_layer`
* :func:`lookup_carrying_mode`
* :func:`validate_carrying_claim`
* :func:`validate_reception`
* :func:`validate_reception_batch`
* :func:`build_reception_path`
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from arabic_engine.core.enums import (
    CarryingMode,
    ReceptionDecisionCode,
    ReceptionLayer,
    ReceptionRank,
    ReceptionValidationOutcome,
    SubjectGenre,
)
from arabic_engine.core.types import (
    CarryingAssignment,
    EpistemicReceptionInput,
    EpistemicReceptionResult,
    ReceptionPathRecord,
    SubjectClassification,
)

# ── Rank → Layer mapping (Art. 14) ──────────────────────────────────────────

_RANK_TO_LAYER: Dict[ReceptionRank, ReceptionLayer] = {
    ReceptionRank.HISS: ReceptionLayer.ISTIQBAL,
    ReceptionRank.SHUUUR: ReceptionLayer.ISTIQBAL,
    ReceptionRank.FIKR: ReceptionLayer.MUALAJA_MARIFIYYA,
    ReceptionRank.NIYYA: ReceptionLayer.TAWJIH,
    ReceptionRank.KHIYAR: ReceptionLayer.TAWJIH,
    ReceptionRank.IRADA: ReceptionLayer.TAWJIH,
}

# ── Constitutional Matrix (Art. 40) ─────────────────────────────────────────
#
# Key: (SubjectGenre, ReceptionRank) → CarryingMode
#
# Row 1 — Existence (Art. 41):
#   Sense=ASIL, Feeling=TABI, Thought=ASIL, Intent/Choice/Will=TABI
# Row 2 — Attribute (Art. 42):
#   Sense=ASIL (sensible) / TABI (other), Feeling=ASIL, Thought=ASIL, rest=TABI
# Row 3 — Event (Art. 43):
#   Sense=TABI, Feeling=ASIL, Thought=ASIL, rest=TABI
# Row 4 — Relation (Art. 44):
#   Sense=TABI (near) / MUMTANI (pure abstract), Feeling=TABI, Thought=ASIL, rest=TABI

CONSTITUTIONAL_MATRIX: Dict[Tuple[SubjectGenre, ReceptionRank], CarryingMode] = {
    # ── Existence (الوجود) ──
    (SubjectGenre.WUJUD, ReceptionRank.HISS): CarryingMode.ASIL,
    (SubjectGenre.WUJUD, ReceptionRank.SHUUUR): CarryingMode.TABI,
    (SubjectGenre.WUJUD, ReceptionRank.FIKR): CarryingMode.ASIL,
    (SubjectGenre.WUJUD, ReceptionRank.NIYYA): CarryingMode.TABI,
    (SubjectGenre.WUJUD, ReceptionRank.KHIYAR): CarryingMode.TABI,
    (SubjectGenre.WUJUD, ReceptionRank.IRADA): CarryingMode.TABI,
    # ── Attribute (الصفة) ──
    (SubjectGenre.SIFA, ReceptionRank.HISS): CarryingMode.ASIL,
    (SubjectGenre.SIFA, ReceptionRank.SHUUUR): CarryingMode.ASIL,
    (SubjectGenre.SIFA, ReceptionRank.FIKR): CarryingMode.ASIL,
    (SubjectGenre.SIFA, ReceptionRank.NIYYA): CarryingMode.TABI,
    (SubjectGenre.SIFA, ReceptionRank.KHIYAR): CarryingMode.TABI,
    (SubjectGenre.SIFA, ReceptionRank.IRADA): CarryingMode.TABI,
    # ── Event (الحدث) ──
    (SubjectGenre.HADATH, ReceptionRank.HISS): CarryingMode.TABI,
    (SubjectGenre.HADATH, ReceptionRank.SHUUUR): CarryingMode.ASIL,
    (SubjectGenre.HADATH, ReceptionRank.FIKR): CarryingMode.ASIL,
    (SubjectGenre.HADATH, ReceptionRank.NIYYA): CarryingMode.TABI,
    (SubjectGenre.HADATH, ReceptionRank.KHIYAR): CarryingMode.TABI,
    (SubjectGenre.HADATH, ReceptionRank.IRADA): CarryingMode.TABI,
    # ── Relation (النسبة) ──
    (SubjectGenre.NISBA, ReceptionRank.HISS): CarryingMode.TABI,
    (SubjectGenre.NISBA, ReceptionRank.SHUUUR): CarryingMode.TABI,
    (SubjectGenre.NISBA, ReceptionRank.FIKR): CarryingMode.ASIL,
    (SubjectGenre.NISBA, ReceptionRank.NIYYA): CarryingMode.TABI,
    (SubjectGenre.NISBA, ReceptionRank.KHIYAR): CarryingMode.TABI,
    (SubjectGenre.NISBA, ReceptionRank.IRADA): CarryingMode.TABI,
}

# Qualification strings for cells that have nuanced carrying descriptions.
_QUALIFICATIONS: Dict[Tuple[SubjectGenre, ReceptionRank], str] = {
    (SubjectGenre.WUJUD, ReceptionRank.HISS):
        "أصيل من جهة الحضور الأول",
    (SubjectGenre.WUJUD, ReceptionRank.SHUUUR):
        "تبعي من جهة أثره",
    (SubjectGenre.WUJUD, ReceptionRank.FIKR):
        "أصيل من جهة التعيين والإثبات",
    (SubjectGenre.SIFA, ReceptionRank.HISS):
        "أصيل في المحسوس / تبعي في غيره",
    (SubjectGenre.SIFA, ReceptionRank.SHUUUR):
        "أصيل من جهة أثر الصفات",
    (SubjectGenre.SIFA, ReceptionRank.FIKR):
        "أصيل من جهة الإغلاق المعرفي",
    (SubjectGenre.HADATH, ReceptionRank.HISS):
        "تبعي أو جزئي",
    (SubjectGenre.HADATH, ReceptionRank.SHUUUR):
        "أصيل من جهة الأثر",
    (SubjectGenre.HADATH, ReceptionRank.FIKR):
        "أصيل من جهة تعيين الحدث كحدث",
    (SubjectGenre.NISBA, ReceptionRank.HISS):
        "تبعي في القريب المحسوس / ممتنع في المجرد الخالص",
    (SubjectGenre.NISBA, ReceptionRank.SHUUUR):
        "تبعي من جهة أثر النسبة",
    (SubjectGenre.NISBA, ReceptionRank.FIKR):
        "أصيل من جهة الربط والتعلق والجهة",
}

# Ordered list of ranks for rank-ordering checks.
_RANK_ORDER: Tuple[ReceptionRank, ...] = (
    ReceptionRank.HISS,
    ReceptionRank.SHUUUR,
    ReceptionRank.FIKR,
    ReceptionRank.NIYYA,
    ReceptionRank.KHIYAR,
    ReceptionRank.IRADA,
)

_RANK_INDEX = {r: i for i, r in enumerate(_RANK_ORDER)}

# Subject genre hint keywords for simple classification.
_GENRE_HINTS: Dict[str, SubjectGenre] = {
    "existence": SubjectGenre.WUJUD,
    "entity": SubjectGenre.WUJUD,
    "thing": SubjectGenre.WUJUD,
    "self": SubjectGenre.WUJUD,
    "object": SubjectGenre.WUJUD,
    "وجود": SubjectGenre.WUJUD,
    "ذات": SubjectGenre.WUJUD,
    "شيء": SubjectGenre.WUJUD,
    "كيان": SubjectGenre.WUJUD,
    "attribute": SubjectGenre.SIFA,
    "quality": SubjectGenre.SIFA,
    "state": SubjectGenre.SIFA,
    "description": SubjectGenre.SIFA,
    "صفة": SubjectGenre.SIFA,
    "حال": SubjectGenre.SIFA,
    "هيئة": SubjectGenre.SIFA,
    "نعت": SubjectGenre.SIFA,
    "event": SubjectGenre.HADATH,
    "occurrence": SubjectGenre.HADATH,
    "change": SubjectGenre.HADATH,
    "action": SubjectGenre.HADATH,
    "حدث": SubjectGenre.HADATH,
    "وقوع": SubjectGenre.HADATH,
    "تغير": SubjectGenre.HADATH,
    "فعل": SubjectGenre.HADATH,
    "relation": SubjectGenre.NISBA,
    "link": SubjectGenre.NISBA,
    "connection": SubjectGenre.NISBA,
    "dependency": SubjectGenre.NISBA,
    "نسبة": SubjectGenre.NISBA,
    "علاقة": SubjectGenre.NISBA,
    "ربط": SubjectGenre.NISBA,
    "إضافة": SubjectGenre.NISBA,
}


# ── Public API ──────────────────────────────────────────────────────────────


def classify_subject(
    description: str,
    hints: Optional[Sequence[str]] = None,
    *,
    classification_id: str = "",
) -> SubjectClassification:
    """Classify an incoming subject into one of the four genres (Arts. 5–9).

    If no genre can be determined from *description* or *hints*, returns a
    classification with ``is_closed=False`` (Art. 10 — unclosed material).

    Parameters
    ----------
    description:
        Free-text description of the incoming subject.
    hints:
        Optional keyword hints (matched against known genre keywords).
    classification_id:
        Optional explicit ID; auto-generated if empty.
    """
    cid = classification_id or f"SC_{id(description)}"
    genre: Optional[SubjectGenre] = None

    # Try hints first.
    for h in (hints or []):
        h_lower = h.strip().lower()
        if h_lower in _GENRE_HINTS:
            genre = _GENRE_HINTS[h_lower]
            break

    # Fall back to scanning the description.
    if genre is None:
        desc_lower = description.lower()
        for keyword, g in _GENRE_HINTS.items():
            if keyword in desc_lower:
                genre = g
                break

    if genre is not None:
        return SubjectClassification(
            classification_id=cid,
            genre=genre,
            description=description,
            is_closed=True,
        )
    return SubjectClassification(
        classification_id=cid,
        genre=SubjectGenre.WUJUD,  # default placeholder
        description=description,
        is_closed=False,
    )


def get_reception_layer(rank: ReceptionRank) -> ReceptionLayer:
    """Map a reception rank to its enclosing layer (Art. 14)."""
    return _RANK_TO_LAYER[rank]


def lookup_carrying_mode(
    genre: SubjectGenre,
    rank: ReceptionRank,
) -> CarryingAssignment:
    """Look up the constitutional matrix for a (genre, rank) pair (Art. 40)."""
    mode = CONSTITUTIONAL_MATRIX[(genre, rank)]
    qualification = _QUALIFICATIONS.get((genre, rank), "")
    return CarryingAssignment(
        genre=genre,
        rank=rank,
        mode=mode,
        qualification=qualification,
    )


def validate_carrying_claim(
    claimed: CarryingAssignment,
) -> Tuple[bool, List[ReceptionDecisionCode]]:
    """Validate a single carrying claim against the constitutional matrix.

    Returns ``(True, [])`` when the claim matches the matrix, or
    ``(False, [REC007_CARRYING_VIOLATION])`` when it does not.
    """
    expected = CONSTITUTIONAL_MATRIX.get((claimed.genre, claimed.rank))
    if expected is None:
        return (False, [ReceptionDecisionCode.REC007_CARRYING_VIOLATION])
    if claimed.mode != expected:
        return (False, [ReceptionDecisionCode.REC007_CARRYING_VIOLATION])
    return (True, [])


def validate_reception(
    inp: EpistemicReceptionInput,
) -> EpistemicReceptionResult:
    """Validate an epistemic reception input against all constitutional articles.

    Steps:
    1. Check subject is classified (Art. 10)
    2. Verify axes are not confused (Art. 11)
    3. Validate sense is only first input (Arts. 16–20)
    4. Validate feeling is internal effect, not judgment (Arts. 21–25)
    5. Validate thought is the closure rank (Arts. 26–30)
    6. Validate intention/choice/will are post-thought (Arts. 31–35)
    7. Validate all carrying claims against the matrix (Arts. 36–44)
    8. Apply acceptance criteria (Art. 45)
    9. Apply rejection criteria (Art. 46)
    """
    codes: List[ReceptionDecisionCode] = []
    messages: List[str] = []

    # 1. Subject classification (Art. 10).
    if inp.subject is None or not inp.subject.is_closed:
        codes.append(ReceptionDecisionCode.REC001_SUBJECT_GENRE_UNRESOLVED)
        messages.append("Subject genre is unresolved (Art. 10)")

    # 2. Axis confusion detection (Art. 11).
    #    If a carrying claim assigns reception-rank names as if they were genres,
    #    or maps genre names onto reception semantics, flag confusion.
    for claim in inp.claimed_assignments:
        # A claim where an ASIL mode is asserted for a combination that is
        # actually MUMTANI reveals axis confusion.
        expected = CONSTITUTIONAL_MATRIX.get((claim.genre, claim.rank))
        if expected == CarryingMode.MUMTANI and claim.mode == CarryingMode.ASIL:
            codes.append(ReceptionDecisionCode.REC002_AXIS_CONFUSION)
            messages.append(
                f"Axis confusion: {claim.genre.name} claimed ASIL at "
                f"{claim.rank.name} which is prohibited (Art. 11)"
            )

    # 3. Sense overreach (Arts. 16–20).
    #    If sense is treated as sufficient for cognitive closure, flag overreach.
    _check_sense_overreach(inp, codes, messages)

    # 4. Feeling treated as judgment (Arts. 21–25).
    _check_feeling_as_judgment(inp, codes, messages)

    # 5. Intention treated as first reception (Arts. 31–35).
    _check_intention_as_reception(inp, codes, messages)

    # 6. Will treated as original determination (Art. 33).
    _check_will_as_determination(inp, codes, messages)

    # 7. Rank order violation.
    _check_rank_order(inp, codes, messages)

    # 8. Validate all carrying claims (Arts. 36–44).
    corrected: List[CarryingAssignment] = []
    for claim in inp.claimed_assignments:
        valid, claim_codes = validate_carrying_claim(claim)
        if not valid:
            codes.extend(claim_codes)
            messages.append(
                f"Carrying violation: {claim.genre.name} × {claim.rank.name} "
                f"claimed as {claim.mode.name} (Art. 38)"
            )
            # Replace with matrix-correct value.
            corrected.append(lookup_carrying_mode(claim.genre, claim.rank))
        else:
            corrected.append(claim)

    # Build reception path if subject is available.
    path: Optional[ReceptionPathRecord] = None
    if inp.subject is not None and inp.subject.is_closed:
        path = build_reception_path(
            subject=inp.subject,
            sense=inp.sense_present,
            feeling=inp.feeling_present,
            thought=inp.thought_present,
            intention=inp.intention_present,
            choice=inp.choice_present,
            will=inp.will_present,
        )

    # Determine outcome (Arts. 45–46).
    if codes:
        outcome = ReceptionValidationOutcome.REJECTED_CONSTITUTIONALLY
    elif inp.subject is None or not inp.subject.is_closed:
        outcome = ReceptionValidationOutcome.INCOMPLETE
    else:
        outcome = ReceptionValidationOutcome.ACCEPTED

    return EpistemicReceptionResult(
        reception_id=inp.reception_id,
        outcome=outcome,
        codes=tuple(codes),
        corrected_assignments=tuple(corrected),
        path=path,
        messages=tuple(messages),
    )


def validate_reception_batch(
    inputs: Sequence[EpistemicReceptionInput],
) -> Tuple[EpistemicReceptionResult, ...]:
    """Validate a sequence of reception inputs (in order)."""
    return tuple(validate_reception(inp) for inp in inputs)


def build_reception_path(
    subject: SubjectClassification,
    sense: bool = False,
    feeling: bool = False,
    thought: bool = False,
    intention: bool = False,
    choice: bool = False,
    will: bool = False,
) -> ReceptionPathRecord:
    """Construct the reception path for *subject* through all applicable ranks.

    For each rank that is *present*, the matrix-correct carrying assignment is
    included.  ``current_rank`` is set to the highest (latest) rank present.
    """
    assignments: List[CarryingAssignment] = []
    current = ReceptionRank.HISS  # default to lowest

    for rank, present in (
        (ReceptionRank.HISS, sense),
        (ReceptionRank.SHUUUR, feeling),
        (ReceptionRank.FIKR, thought),
        (ReceptionRank.NIYYA, intention),
        (ReceptionRank.KHIYAR, choice),
        (ReceptionRank.IRADA, will),
    ):
        if present:
            assignments.append(lookup_carrying_mode(subject.genre, rank))
            current = rank

    return ReceptionPathRecord(
        path_id=f"RP_{subject.classification_id}",
        subject=subject,
        assignments=tuple(assignments),
        current_rank=current,
    )


# ── Internal helpers ────────────────────────────────────────────────────────


def _check_sense_overreach(
    inp: EpistemicReceptionInput,
    codes: List[ReceptionDecisionCode],
    messages: List[str],
) -> None:
    """Arts. 16–20: Sense is the first input but cannot carry cognitive closure.

    Overreach is detected when sense is present but thought is absent, yet the
    input implicitly claims full processing (intention/choice/will present).
    """
    if inp.sense_present and not inp.thought_present:
        if inp.intention_present or inp.choice_present or inp.will_present:
            codes.append(ReceptionDecisionCode.REC003_SENSE_OVERREACH)
            messages.append(
                "Sense overreach: direction ranks present without thought (Art. 19)"
            )


def _check_feeling_as_judgment(
    inp: EpistemicReceptionInput,
    codes: List[ReceptionDecisionCode],
    messages: List[str],
) -> None:
    """Arts. 21–25: Feeling is an internal effect, not a judgment.

    If feeling is present, thought is absent, and direction ranks are active,
    feeling is being treated as sufficient for judgment — a violation.
    """
    if inp.feeling_present and not inp.thought_present:
        if inp.intention_present or inp.choice_present or inp.will_present:
            codes.append(ReceptionDecisionCode.REC004_FEELING_AS_JUDGMENT)
            messages.append(
                "Feeling treated as judgment: direction ranks active "
                "without thought (Art. 24)"
            )


def _check_intention_as_reception(
    inp: EpistemicReceptionInput,
    codes: List[ReceptionDecisionCode],
    messages: List[str],
) -> None:
    """Arts. 31–35: Intention is not a reception rank.

    If intention is present but sense and feeling are both absent, intention is
    being treated as first reception — a violation.
    """
    if inp.intention_present and not inp.sense_present and not inp.feeling_present:
        codes.append(ReceptionDecisionCode.REC005_INTENTION_AS_RECEPTION)
        messages.append(
            "Intention treated as first reception: sense and feeling absent (Art. 31)"
        )


def _check_will_as_determination(
    inp: EpistemicReceptionInput,
    codes: List[ReceptionDecisionCode],
    messages: List[str],
) -> None:
    """Art. 33: Will is not original determination.

    If will is present but thought is absent, will is being treated as the
    primary determination rank — a violation.
    """
    if inp.will_present and not inp.thought_present:
        codes.append(ReceptionDecisionCode.REC006_WILL_AS_DETERMINATION)
        messages.append(
            "Will treated as original determination: thought absent (Art. 33)"
        )


def _check_rank_order(
    inp: EpistemicReceptionInput,
    codes: List[ReceptionDecisionCode],
    messages: List[str],
) -> None:
    """Check that active ranks form a contiguous prefix of the rank ordering.

    A gap (e.g. sense + thought but no feeling) is a rank order violation.
    """
    flags = (
        inp.sense_present,
        inp.feeling_present,
        inp.thought_present,
        inp.intention_present,
        inp.choice_present,
        inp.will_present,
    )
    # Find the highest active rank index.
    highest = -1
    for i, f in enumerate(flags):
        if f:
            highest = i

    if highest < 0:
        return  # nothing active

    # Every rank below the highest must be active (contiguous prefix).
    for i in range(highest):
        if not flags[i]:
            codes.append(ReceptionDecisionCode.REC008_RANK_ORDER_VIOLATION)
            messages.append(
                f"Rank order violation: {_RANK_ORDER[i].name} missing "
                f"below active {_RANK_ORDER[highest].name} (Art. 15)"
            )
            break  # one code is sufficient
