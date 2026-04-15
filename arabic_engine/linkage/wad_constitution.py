"""Wad' and Mental Meaning Constitution v1 — دستور الوضع والمعنى الذهني عند النبهاني.

This module encodes the sovereignty invariants of the Wad' and Mental
Meaning Constitution v1 as computable Python objects.  It provides:

* :func:`build_wad_record` — build a Wad' record for a lafz–meaning pair.
* :func:`build_mental_meaning` — build a mental meaning record.
* :func:`build_nisba` — build a ratio/relation record.
* :func:`check_wad_jump` — check a single anti-jump condition.
* :func:`check_all_wad_jumps` — check all prohibited jumps.
* :func:`validate_wad_chain` — validate T → W → M → R → E chain.
* :func:`validate_wad_constitution` — full constitution validation.

Governing chain position (Art. 37)::

    واقع/خبر → إدراك → معلومات سابقة → ربط → تمييز → تصور
    → وضع/لغة/نسب → ضبط دلالي → تحرير موضوع → جهة حكم → حكم

The document this module implements is
``docs/wad_mental_meaning_constitution_v1.md``.

Reference
---------
Art. 4 — Sovereign rule::

    لا تُفهم اللغة من اللفظ ابتداءً، بل من الوضع الذي جعل اللفظ
    بإزاء معنى ذهني متصور، ومن الغاية التي لأجلها وُضع، وهي إفادة
    النسب والتعبير عما في النفس.

Art. 43 — Mathematical representation::

    T → W → M → R → E
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    ExpressionMode,
    MentalMeaningSource,
    NisbaType,
    WadElement,
    WadJumpViolation,
)
from arabic_engine.core.types import (
    MentalMeaningRecord,
    NisbaRecord,
    WadConstitutionResult,
    WadJumpCheckResult,
    WadRecord,
)

# ── Art. 37: Governing chain position ────────────────────────────────

GOVERNING_CHAIN = (
    "واقع/خبر",
    "إدراك",
    "معلومات سابقة",
    "ربط",
    "تمييز",
    "تصور",
    "وضع/لغة/نسب",
    "ضبط دلالي",
    "تحرير موضوع",
    "جهة حكم",
    "حكم",
)

CHAIN_POSITION = "وضع/لغة/نسب"

# ── Art. 14: Expression mode preferences ────────────────────────────

EXPRESSION_PREFERENCE_ORDER: tuple[ExpressionMode, ...] = (
    ExpressionMode.LAFZ,
    ExpressionMode.ISHARA,
    ExpressionMode.MITHAL,
)

# ── Wad' record builder (Art. 5–8) ──────────────────────────────────


def build_wad_record(
    wad_id: str,
    lafz: str,
    mental_meaning: str,
    tasawwur_present: bool,
    *,
    confidence: float = 1.0,
) -> WadRecord:
    """Build a Wad' (designation) record.

    Parameters
    ----------
    wad_id : str
        Unique identifier for this designation.
    lafz : str
        The utterance/word being designated (Art. 6 element 1).
    mental_meaning : str
        The mental meaning the lafz is designated for (Art. 6 element 2).
    tasawwur_present : bool
        Whether the conception prerequisite is met (Art. 24–27).
    confidence : float
        Confidence score in [0, 1].

    Returns
    -------
    WadRecord

    Raises
    ------
    ValueError
        If any constitutive element is missing (Art. 6).
    """
    errors: list[str] = []

    if not lafz:
        errors.append("Wad' requires a non-empty lafz (Art. 6 element 1: لفظ)")
    if not mental_meaning:
        errors.append("Wad' requires a non-empty mental meaning (Art. 6 element 2: معنى)")
    if not tasawwur_present:
        errors.append(
            "Wad' requires tasawwur to be present — الوضع فرع عن التصور "
            "(Art. 24–27)"
        )
    if not (0.0 <= confidence <= 1.0):
        errors.append(f"Confidence must be in [0, 1], got {confidence}")

    if errors:
        raise ValueError(
            "Wad' Constitution violation (Art. 5–8): " + "; ".join(errors)
        )

    # All four elements confirmed present
    elements = (
        WadElement.LAFZ,
        WadElement.MEANING,
        WadElement.TAKHSIS,
        WadElement.COMPREHENSIBILITY,
    )

    return WadRecord(
        wad_id=wad_id,
        lafz=lafz,
        mental_meaning=mental_meaning,
        tasawwur_present=tasawwur_present,
        elements=elements,
        confidence=confidence,
    )


# ── Mental meaning builder (Art. 18–23) ─────────────────────────────


def build_mental_meaning(
    meaning_id: str,
    content: str,
    source: MentalMeaningSource,
    *,
    matches_external: bool = True,
    source_tasawwur: str = "",
) -> MentalMeaningRecord:
    """Build a mental meaning record.

    Art. 19 — الألفاظ موضوعة للمعاني الذهنية، لا للماهيات الخارجية مباشرة.

    Parameters
    ----------
    meaning_id : str
        Unique identifier.
    content : str
        Description of the mental meaning.
    source : MentalMeaningSource
        How the meaning arises.
    matches_external : bool
        Whether it matches external reality (Art. 23).
    source_tasawwur : str
        Identifier of the source tasawwur (conception).

    Returns
    -------
    MentalMeaningRecord

    Raises
    ------
    ValueError
        If content is empty.
    """
    if not content:
        raise ValueError(
            "Mental meaning requires non-empty content (Art. 18: "
            "المعنى الذهني هو ما يثبت في الذهن)"
        )

    return MentalMeaningRecord(
        meaning_id=meaning_id,
        content=content,
        source=source,
        matches_external=matches_external,
        source_tasawwur=source_tasawwur,
    )


# ── Nisba builder (Art. 32–35) ──────────────────────────────────────


def build_nisba(
    nisba_id: str,
    nisba_type: NisbaType,
    first_term: str,
    second_term: str,
    *,
    expression_complete: bool = False,
) -> NisbaRecord:
    """Build a ratio/relation (nisba) record.

    Art. 33 — الغرض الأعلى من وضع الألفاظ هو إفادة النسب.

    Parameters
    ----------
    nisba_id : str
        Unique identifier.
    nisba_type : NisbaType
        Kind of ratio (isnadiyya, taqyidiyya, etc.).
    first_term : str
        First term of the relation.
    second_term : str
        Second term of the relation.
    expression_complete : bool
        Whether the relation suffices for complete expression.

    Returns
    -------
    NisbaRecord

    Raises
    ------
    ValueError
        If either term is empty.
    """
    if not first_term or not second_term:
        raise ValueError(
            "Nisba requires two non-empty terms (Art. 34: "
            "التعبير عما في النفس لا يحصل بالمفردات المقطوعة وحدها)"
        )

    return NisbaRecord(
        nisba_id=nisba_id,
        nisba_type=nisba_type,
        first_term=first_term,
        second_term=second_term,
        expression_complete=expression_complete,
    )


# ── Anti-jump checks (Art. 40–42) ───────────────────────────────────

_JUMP_DESCRIPTIONS = {
    WadJumpViolation.LAFZ_TO_MEANING_NO_TASAWWUR: (
        "Lafz → complete meaning without tasawwur",
        "لفظ → معنى مكتمل بلا تصور",
    ),
    WadJumpViolation.LAFZ_TO_EXTERNAL_NO_MENTAL: (
        "Lafz → external reality without mental meaning",
        "لفظ → خارج بلا معنى ذهني",
    ),
    WadJumpViolation.LANGUAGE_TO_JUDGEMENT_NO_METHOD: (
        "Language → judgement without method of reason",
        "لغة → حكم بلا طريقة عقل",
    ),
    WadJumpViolation.WAD_TO_EXTERNAL_DIRECT: (
        "Wad' → external reality directly without mental mediation",
        "وضع → خارج مباشر بلا توسط ذهني",
    ),
    WadJumpViolation.MUFRADAT_TO_EXPRESSION_NO_NISAB: (
        "Individual words → complete expression without ratios/relations",
        "مفردات → تعبير كامل بلا نسب",
    ),
}


def check_wad_jump(
    violation: WadJumpViolation,
    *,
    tasawwur_present: bool = False,
    mental_meaning_present: bool = False,
    method_present: bool = False,
    mental_mediation: bool = False,
    nisab_present: bool = False,
) -> WadJumpCheckResult:
    """Check a single anti-jump condition (Art. 40–42).

    Parameters
    ----------
    violation : WadJumpViolation
        The jump type to check.
    tasawwur_present : bool
        Whether tasawwur is available.
    mental_meaning_present : bool
        Whether a mental meaning is available.
    method_present : bool
        Whether the method of reason is applied.
    mental_mediation : bool
        Whether mental mediation is present.
    nisab_present : bool
        Whether ratios/relations are present.

    Returns
    -------
    WadJumpCheckResult
        ``detected=True`` when the prohibited jump is found.
    """
    desc, desc_ar = _JUMP_DESCRIPTIONS[violation]

    detected = False
    if violation == WadJumpViolation.LAFZ_TO_MEANING_NO_TASAWWUR:
        detected = not tasawwur_present
    elif violation == WadJumpViolation.LAFZ_TO_EXTERNAL_NO_MENTAL:
        detected = not mental_meaning_present
    elif violation == WadJumpViolation.LANGUAGE_TO_JUDGEMENT_NO_METHOD:
        detected = not method_present
    elif violation == WadJumpViolation.WAD_TO_EXTERNAL_DIRECT:
        detected = not mental_mediation
    elif violation == WadJumpViolation.MUFRADAT_TO_EXPRESSION_NO_NISAB:
        detected = not nisab_present

    return WadJumpCheckResult(
        violation=violation,
        detected=detected,
        description=desc,
        description_ar=desc_ar,
    )


def check_all_wad_jumps(
    *,
    tasawwur_present: bool = True,
    mental_meaning_present: bool = True,
    method_present: bool = True,
    mental_mediation: bool = True,
    nisab_present: bool = True,
) -> tuple[WadJumpCheckResult, ...]:
    """Check all five prohibited jumps (Art. 40–42).

    With all flags ``True``, no jumps are detected (clean chain).

    Returns
    -------
    tuple[WadJumpCheckResult, ...]
        Five check results, one per violation type.
    """
    results: list[WadJumpCheckResult] = []
    for v in WadJumpViolation:
        results.append(check_wad_jump(
            v,
            tasawwur_present=tasawwur_present,
            mental_meaning_present=mental_meaning_present,
            method_present=method_present,
            mental_mediation=mental_mediation,
            nisab_present=nisab_present,
        ))
    return tuple(results)


# ── Chain validation (Art. 43–44) ───────────────────────────────────


def validate_wad_chain(
    tasawwur: bool,
    wad: bool,
    mental_meaning: bool,
    nisab: bool,
    expression: bool,
) -> tuple[bool, list[str]]:
    """Validate the T → W → M → R → E chain (Art. 43–44).

    Each stage requires all preceding stages to be present:

    * T (Tasawwur) — no prerequisite
    * W (Wad') — requires T
    * M (Mental Meaning) — requires T and W
    * R (Ratios/Nisab) — requires T, W, and M
    * E (Expression) — requires T, W, M, and R

    Parameters
    ----------
    tasawwur : bool
        Tasawwur (conception) present.
    wad : bool
        Wad' (designation) present.
    mental_meaning : bool
        Mental meaning present.
    nisab : bool
        Ratios/relations present.
    expression : bool
        Expression complete.

    Returns
    -------
    tuple[bool, list[str]]
        (valid, errors) — valid is True when no chain violations.
    """
    errors: list[str] = []

    # T — no prerequisite
    if not tasawwur:
        errors.append(
            "T (Tasawwur) missing: لا وضع بلا تصور (Art. 24)"
        )

    # W requires T
    if wad and not tasawwur:
        errors.append(
            "W (Wad') without T: الوضع فرع عن التصور (Art. 24–27)"
        )

    # M requires T + W
    if mental_meaning and not wad:
        errors.append(
            "M (Mental Meaning) without W: "
            "اللفظ موضوع للمعنى الذهني فلا معنى بلا وضع (Art. 19)"
        )

    # R requires T + W + M
    if nisab and not mental_meaning:
        errors.append(
            "R (Nisab) without M: "
            "إفادة النسب تحتاج إلى المعاني الذهنية أولًا (Art. 32–34)"
        )

    # E requires T + W + M + R
    if expression and not nisab:
        errors.append(
            "E (Expression) without R: "
            "التعبير لا يتم بالمفردات وحدها بل بالنسب (Art. 34)"
        )

    return (len(errors) == 0, errors)


# ── Full constitution validation (Art. 1–51) ────────────────────────


def validate_wad_constitution(
    lafz: str = "كَتَبَ",
    mental_meaning_content: str = "فعل الكتابة",
) -> WadConstitutionResult:
    """Validate the full Wad' and Mental Meaning Constitution.

    Runs a demonstration validation on the given lafz and mental
    meaning, checking all constitutional invariants:

    1. Wad' record completeness (Art. 5–8)
    2. Mental meaning integrity (Art. 18–23)
    3. Nisba construction (Art. 32–35)
    4. Anti-jump conditions (Art. 40–42)
    5. Chain ordering T → W → M → R → E (Art. 43–44)
    6. Chain position (Art. 37)

    Parameters
    ----------
    lafz : str
        Sample lafz for demonstration.
    mental_meaning_content : str
        Sample mental meaning content.

    Returns
    -------
    WadConstitutionResult
    """
    errors: list[str] = []
    wad_records: list[WadRecord] = []
    mental_meanings: list[MentalMeaningRecord] = []
    nisab: list[NisbaRecord] = []

    # 1. Build Wad' record (Art. 5–8)
    try:
        wr = build_wad_record(
            wad_id=f"WAD_{lafz}",
            lafz=lafz,
            mental_meaning=mental_meaning_content,
            tasawwur_present=True,
        )
        wad_records.append(wr)
    except ValueError as exc:
        errors.append(str(exc))

    # 2. Build mental meaning (Art. 18–23)
    try:
        mm = build_mental_meaning(
            meaning_id=f"MM_{lafz}",
            content=mental_meaning_content,
            source=MentalMeaningSource.PERCEPTION,
            source_tasawwur=f"TASAWWUR_{lafz}",
        )
        mental_meanings.append(mm)
    except ValueError as exc:
        errors.append(str(exc))

    # 3. Build nisba (Art. 32–35)
    try:
        nr = build_nisba(
            nisba_id=f"NISBA_{lafz}",
            nisba_type=NisbaType.ISNADIYYA,
            first_term=lafz,
            second_term=mental_meaning_content,
            expression_complete=True,
        )
        nisab.append(nr)
    except ValueError as exc:
        errors.append(str(exc))

    # 4. Anti-jump checks (Art. 40–42)
    jump_checks = check_all_wad_jumps(
        tasawwur_present=True,
        mental_meaning_present=bool(mental_meanings),
        method_present=True,
        mental_mediation=True,
        nisab_present=bool(nisab),
    )
    for jc in jump_checks:
        if jc.detected:
            errors.append(
                f"Jump violation detected: {jc.description} — {jc.description_ar}"
            )

    # 5. Chain validation (Art. 43–44)
    chain_valid, chain_errors = validate_wad_chain(
        tasawwur=True,
        wad=bool(wad_records),
        mental_meaning=bool(mental_meanings),
        nisab=bool(nisab),
        expression=True,
    )
    errors.extend(chain_errors)

    # 6. Verify chain position (Art. 37)
    if CHAIN_POSITION not in GOVERNING_CHAIN:
        errors.append(
            f"Chain position {CHAIN_POSITION!r} not found in "
            "governing chain (Art. 37)"
        )

    return WadConstitutionResult(
        valid=len(errors) == 0,
        errors=tuple(errors),
        wad_records=tuple(wad_records),
        mental_meanings=tuple(mental_meanings),
        nisab=tuple(nisab),
        jump_checks=jump_checks,
        chain_position=CHAIN_POSITION,
    )
