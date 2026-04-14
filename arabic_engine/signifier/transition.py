"""قانون الانتقال بين الخانات — The Law of Cell Transition.

Implements the formal transition engine for the Arabic phonological table.
Every element ``E`` can be mapped to a new cell ``E_new`` when its
position, neighbourhood, function, pattern, economy, or macro-architecture
changes.

Formal transition function::

    T_r(E) = f(P, N, F, W, Ec, M)

where:
    P   = position (SyllablePosition)
    N   = neighbourhood (left_neighbor, right_neighbor DMin units)
    F   = function role (FunctionRole)
    W   = prosodic/morphological pattern string
    Ec  = economy pressure (float ∈ [0, 1])
    M   = macro-architecture label string

Optimality criterion::

    E_new = ArgMin(loss_root, loss_pattern, phonetic_burden)
    subject to: E_new ∈ Nearest_Valid_Functional_Cell

Priority ordering (from the theoretical framework):
    1. Root preservation     (حفظ الجذر)
    2. Pattern preservation  (حفظ الوزن)
    3. Syllabic structure    (حفظ البنية المقطعية)
    4. Economy               (تحقيق الاقتصاد)
    5. Lightness             (تحقيق الخفة)
    6. Surface transformation (السماح بالتحول السطحي)
    7. Deletion — last resort (الحذف عند الضرورة)

Public API
----------
* :data:`TRANSITION_MATRIX`     — the full formal transition matrix
* :func:`stability_check`       — True if element stays in its cell
* :func:`find_applicable_rules` — ordered list of matching rules
* :func:`apply_best_transition` — optimality-driven transition result
* :func:`format_matrix_table`   — human-readable tabular representation
"""

from __future__ import annotations

from typing import FrozenSet, List

from arabic_engine.core.enums import (
    FunctionRole,
    PhonCategory,
    PhonFeature,
    PhonTransform,
    SyllablePosition,
    TransitionCondition,
    TransitionLaw,
    TransitionType,
)
from arabic_engine.core.types import (
    DMin,
    TransitionContext,
    TransitionResult,
    TransitionRule,
)

# ── Shorthand aliases ────────────────────────────────────────────────
_TT = TransitionType
_TL = TransitionLaw
_TC = TransitionCondition
_PC = PhonCategory
_PF = PhonFeature
_PT = PhonTransform
_SP = SyllablePosition
_FR = FunctionRole

# ── Unicode Constants ────────────────────────────────────────────────
_UNICODE_SUKUN: int = 0x0652   # sukūn mark  ْ
_UNICODE_SHADDA: int = 0x0651  # shadda mark ّ

# ── Economy pressure thresholds ──────────────────────────────────────
_ECONOMY_REDUCTION_THRESHOLD: float = 0.5   # minimum pressure for HADHF/WAQF
_ECONOMY_CODA_ITLAL_THRESHOLD: float = 0.2  # ITLAL instability in coda


def _ff(*feats: PhonFeature) -> FrozenSet[PhonFeature]:
    """Return an immutable set of :class:`~arabic_engine.core.enums.PhonFeature` values."""
    return frozenset(feats)


def _cc(*conds: TransitionCondition) -> FrozenSet[TransitionCondition]:
    """Return an immutable set of :class:`~arabic_engine.core.enums.TransitionCondition` values."""
    return frozenset(conds)


# ── Formal Transition Matrix ─────────────────────────────────────────
# Each row represents a directed cell-transition rule:
#
#   from_category [required_features] → to_category
#   | law | transition_type | conditions | priority | example
#
# Priority:  lower integer = higher precedence.

TRANSITION_MATRIX: List[TransitionRule] = [

    # ══════════════════════════════════════════════════════════════════
    # القانون الأول: الاعتلال — Weak-letter (ا و ي) transitions
    # ══════════════════════════════════════════════════════════════════

    # 1a. Semi-vowel acting as consonant → Long vowel nucleus
    #     e.g. وَعَدَ (و = consonant onset) → يَقُولُ (و → long-vowel nucleus)
    TransitionRule(
        law=_TL.ITLAL,
        transition_type=_TT.FUNCTIONAL,
        from_category=_PC.SEMI_VOWEL,
        required_features=_ff(_PF.ITLAL, _PF.TAWIL),
        to_category=_PC.LONG_VOWEL,
        resulting_transform=_PT.MADD,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
            _TC.ROOT_PRESERVATION,
            _TC.FUNCTION_PRESERVATION,
        ),
        priority=1,
        description_ar="الواو أو الياء تنتقل من الصامتية إلى الصائتية الطويلة",
        example="يَقُولُ / يَبِيعُ",
    ),

    # 1b. Long vowel (alef/waw/ya) deleted to deep structure
    #     e.g. قَالَ deep form: ق-و-ل → surface drops the ا/و interior
    TransitionRule(
        law=_TL.ITLAL,
        transition_type=_TT.FUNCTIONAL,
        from_category=_PC.LONG_VOWEL,
        required_features=_ff(_PF.TAWIL),
        to_category=_PC.SPECIAL_MARK,       # حضور بنيوي مقدر (virtual presence)
        resulting_transform=_PT.HADHF,
        conditions=_cc(
            _TC.ROOT_PRESERVATION,
            _TC.STRUCTURAL_VALIDITY,
            _TC.NON_CONTRADICTION,
        ),
        priority=7,                          # last resort in weak-letter branch
        description_ar="حذف حرف العلة بنيويًا مع بقائه في البنية العميقة",
        example="قَالَ ← أصل: قَوَلَ",
    ),

    # 1c. Semi-vowel → glide in onset when followed by consonant
    #     e.g. مَوْعِد: و stays semi-consonantal between two consonants
    TransitionRule(
        law=_TL.INZILAQ,
        transition_type=_TT.RANK,
        from_category=_PC.SEMI_VOWEL,
        required_features=_ff(_PF.LAYIN),
        to_category=_PC.SEMI_VOWEL,         # stays semi-vowel, but rank shifts
        resulting_transform=_PT.ITLAL_TR,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
            _TC.FUNCTION_PRESERVATION,
        ),
        priority=3,
        description_ar="الانزلاق بين الصامتية والصائتية بحسب الموضع والحركة المجاورة",
        example="مَوْعِد — بنت",
    ),

    # ══════════════════════════════════════════════════════════════════
    # القانون الثاني: الإدغام — Gemination
    # ══════════════════════════════════════════════════════════════════

    # 2a. Two identical consonants collapse to Shadda
    #     C + C (identical) → Shadda (ّ)
    TransitionRule(
        law=_TL.IDGHAM,
        transition_type=_TT.CONTEXTUAL,
        from_category=_PC.CONSONANT,
        required_features=_ff(_PF.SHADID),
        to_category=_PC.SHADDA,
        resulting_transform=_PT.IDGHAM,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
            _TC.ROOT_PRESERVATION,
            _TC.NON_CONTRADICTION,
        ),
        priority=2,
        description_ar="صامتان متماثلان يُدغمان في شدة واحدة",
        example="مَدَّ / شَدَّ / رَدَّ",
    ),

    # 2b. Assimilation of ن/ل to following solar letter (إدغام شمسي)
    TransitionRule(
        law=_TL.IDGHAM,
        transition_type=_TT.CONTEXTUAL,
        from_category=_PC.CONSONANT,
        required_features=_ff(_PF.ANFI),
        to_category=_PC.SHADDA,
        resulting_transform=_PT.IDGHAM_SHAMSI,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
        ),
        priority=4,
        description_ar="النون أو اللام تُدغم في الحرف الشمسي التالي",
        example="الشَّمْس / الرَّحْمَن",
    ),

    # ══════════════════════════════════════════════════════════════════
    # القانون الثالث: الإبدال — Substitution within phonetic family
    # ══════════════════════════════════════════════════════════════════

    # 3a. Hamza weakening / tashīl — ء → adjacent sound
    TransitionRule(
        law=_TL.IBDAL,
        transition_type=_TT.CONTEXTUAL,
        from_category=_PC.CONSONANT,
        required_features=_ff(_PF.HMZ),
        to_category=_PC.SEMI_VOWEL,
        resulting_transform=_PT.TASHIL,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
            _TC.FUNCTION_PRESERVATION,
        ),
        priority=5,
        description_ar="الهمزة تُبدل بعنصر مجاور في العائلة الصوتية عند التخفيف",
        example="تسهيل الهمزة في القراءات",
    ),

    # 3b. Generic consonant substitution within same articulatory family
    TransitionRule(
        law=_TL.IBDAL,
        transition_type=_TT.CONTEXTUAL,
        from_category=_PC.CONSONANT,
        required_features=_ff(_PF.SHADID),
        to_category=_PC.CONSONANT,
        resulting_transform=_PT.IBDAL,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.ROOT_PRESERVATION,
            _TC.FUNCTION_PRESERVATION,
            _TC.NON_CONTRADICTION,
        ),
        priority=6,
        description_ar="إبدال صامت بصامت قريب منه في المخرج أو الصفة",
        example="اصطبر ← اصتبر",
    ),

    # ══════════════════════════════════════════════════════════════════
    # القانون الرابع: الحذف — Deletion to deep structure
    # ══════════════════════════════════════════════════════════════════

    # 4a. Weak letter deleted from surface; recoverable from deep form
    TransitionRule(
        law=_TL.HADHF,
        transition_type=_TT.MORPHO_STRUCTURAL,
        from_category=_PC.SEMI_VOWEL,
        required_features=_ff(_PF.ITLAL),
        to_category=_PC.SPECIAL_MARK,       # deep / virtual presence
        resulting_transform=_PT.HADHF,
        conditions=_cc(
            _TC.ROOT_PRESERVATION,
            _TC.FUNCTION_PRESERVATION,
            _TC.STRUCTURAL_VALIDITY,
        ),
        priority=7,
        description_ar="حذف حرف العلة من السطح مع بقائه بنيويًا مقدرًا",
        example="يَقُل (مجزوم) ← يَقُولُ",
    ),

    # 4b. Case/mood vowel deleted at clause boundary (جزم/وقف)
    TransitionRule(
        law=_TL.HADHF,
        transition_type=_TT.MORPHO_STRUCTURAL,
        from_category=_PC.SHORT_VOWEL,
        required_features=_ff(_PF.NUWAWI),
        to_category=_PC.SUKUN,
        resulting_transform=_PT.JAZM,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.FUNCTION_PRESERVATION,
        ),
        priority=6,
        description_ar="الحركة الإعرابية تُحذف في الجزم وتُعوَّض بسكون",
        example="لَمْ يَكْتُبْ",
    ),

    # ══════════════════════════════════════════════════════════════════
    # القانون الخامس: الوقف — Pause-final reduction
    # ══════════════════════════════════════════════════════════════════

    # 5a. Tanwīn deleted at pause (آخر الكلمة)
    TransitionRule(
        law=_TL.WAQF,
        transition_type=_TT.CONTEXTUAL,
        from_category=_PC.TANWIN,
        required_features=_ff(_PF.NUWAWI),
        to_category=_PC.SUKUN,
        resulting_transform=_PT.MAQTAA,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
            _TC.ROOT_PRESERVATION,
        ),
        priority=4,
        description_ar="التنوين يُسقط عند الوقف ويُعوَّض بسكون أو ألف",
        example="كِتَابٌ → كِتَابْ (وقف)",
    ),

    # 5b. Short final vowel suppressed at pause
    TransitionRule(
        law=_TL.WAQF,
        transition_type=_TT.CONTEXTUAL,
        from_category=_PC.SHORT_VOWEL,
        required_features=_ff(_PF.QASIR),
        to_category=_PC.SUKUN,
        resulting_transform=_PT.MAQTAA,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.PHONETIC_BALANCE,
        ),
        priority=5,
        description_ar="الحركة القصيرة النهائية تُحذف عند الوقف وتُعوَّض بسكون",
        example="كَتَبَ → كَتَبْ (وقف)",
    ),

    # ══════════════════════════════════════════════════════════════════
    # القانون السادس: الزيادة — Augmentation re-slotting
    # ══════════════════════════════════════════════════════════════════

    # 6a. Consonant re-slotted as morphological augment
    #     e.g. س in اسْتَفْعَلَ, م in مَفْعُول, ت in تَفَاعَلَ
    #     Applies only when function_role is AUGMENT or architecture is augmented.
    TransitionRule(
        law=_TL.ZIYADA,
        transition_type=_TT.MORPHO_STRUCTURAL,
        from_category=_PC.CONSONANT,
        required_features=_ff(),             # any consonant may become augment
        to_category=_PC.CONSONANT,           # remains consonant, role changes
        resulting_transform=_PT.ZIYADA,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.FUNCTION_PRESERVATION,
            _TC.NON_CONTRADICTION,
        ),
        priority=3,
        description_ar="عنصر صامت يُعاد تموضعه كزيادة صرفية في البنية المزيدة",
        example="اسْتَخْرَجَ: س-ت زيادة / مَكْتُوب: م زيادة",
    ),

    # 6b. Semi-vowel entering augment role (و in تَفَاوُت, ي in تَيَاسَر)
    #     Applies only when function_role is AUGMENT or architecture is augmented.
    TransitionRule(
        law=_TL.ZIYADA,
        transition_type=_TT.MORPHO_STRUCTURAL,
        from_category=_PC.SEMI_VOWEL,
        required_features=_ff(_PF.TAWIL),
        to_category=_PC.SEMI_VOWEL,
        resulting_transform=_PT.BINA_SARFI,
        conditions=_cc(
            _TC.STRUCTURAL_VALIDITY,
            _TC.FUNCTION_PRESERVATION,
        ),
        priority=4,
        description_ar="الواو أو الياء تدخل وظيفة الزيادة البنيوية",
        example="تَفَاوُت / تَيَاسَر",
    ),
]


# ── Priority ordering (canonical, from the theoretical framework) ────

TRANSITION_PRIORITY: List[str] = [
    "حفظ الجذر            — Root preservation",
    "حفظ الوزن            — Pattern preservation",
    "حفظ البنية المقطعية  — Syllabic structure preservation",
    "تحقيق الاقتصاد       — Economy",
    "تحقيق الخفة          — Lightness",
    "السماح بالتحول السطحي — Surface transformation",
    "الحذف عند الضرورة    — Deletion (last resort)",
]


# ── Cost constants ───────────────────────────────────────────────────

_COST_ROOT_LOSS_BY_LAW = {
    _TL.ITLAL:   0.1,
    _TL.INZILAQ: 0.05,
    _TL.IDGHAM:  0.15,
    _TL.IBDAL:   0.25,
    _TL.HADHF:   0.40,
    _TL.WAQF:    0.05,
    _TL.ZIYADA:  0.0,
}

_COST_PATTERN_LOSS_BY_LAW = {
    _TL.ITLAL:   0.05,
    _TL.INZILAQ: 0.02,
    _TL.IDGHAM:  0.10,
    _TL.IBDAL:   0.20,
    _TL.HADHF:   0.30,
    _TL.WAQF:    0.02,
    _TL.ZIYADA:  0.0,
}

_COST_PHONETIC_BURDEN_BY_TYPE = {
    _TT.FUNCTIONAL:        0.10,
    _TT.RANK:              0.05,
    _TT.CONTEXTUAL:        0.15,
    _TT.MORPHO_STRUCTURAL: 0.0,
}


# ── Stability check ──────────────────────────────────────────────────

def stability_check(element: DMin, context: TransitionContext) -> bool:
    """Return ``True`` if *element* is stable in *context* (no transition needed).

    An element is stable when **all three** stability conditions hold:

    1. Its function role is consistent with its category and features.
    2. No economy pressure from the context reaches the threshold for
       triggering a reduction law (HADHF / WAQF / IDGHAM).
    3. The element does not carry an ``ITLAL`` feature while occupying
       a coda or onset position under high economy pressure.

    Parameters
    ----------
    element:
        The :class:`~arabic_engine.core.types.DMin` record to test.
    context:
        The :class:`~arabic_engine.core.types.TransitionContext` providing
        positional and neighbourhood information.

    Returns
    -------
    bool
        ``True`` if the element should remain in its current cell.
    """
    # Condition 1: vowel-like element not forced into nucleus by economy
    if _PF.ITLAL in element.features:
        if context.economy_pressure >= _ECONOMY_REDUCTION_THRESHOLD:
            return False
        if (
            context.position == _SP.CODA
            and context.economy_pressure > _ECONOMY_CODA_ITLAL_THRESHOLD
        ):
            return False

    # Condition 2: identical neighbour triggers gemination
    if context.left_neighbor is not None:
        if (
            context.left_neighbor.unicode == element.unicode
            and _PF.SHADID in element.features
        ):
            return False

    # Condition 3: Tanwīn/short-vowel at word boundary triggers waqf
    if element.category in (_PC.TANWIN, _PC.SHORT_VOWEL):
        if context.position == _SP.CODA and context.economy_pressure >= 0.8:
            return False

    return True


# ── Rule matching ────────────────────────────────────────────────────

def find_applicable_rules(
    element: DMin,
    context: TransitionContext,
) -> List[TransitionRule]:
    """Return all :data:`TRANSITION_MATRIX` rules applicable to *element* in *context*.

    Rules are filtered by:

    * ``from_category`` matches ``element.category`` (``None`` = any)
    * ``required_features ⊆ element.features``
    * Economy pressure compatibility: HADHF/WAQF rules require
      ``context.economy_pressure >= 0.5``

    Results are sorted by ``rule.priority`` (ascending = higher precedence).

    Parameters
    ----------
    element:
        The DMin entry being evaluated.
    context:
        Contextual parameters driving the transition.

    Returns
    -------
    List[TransitionRule]
        Applicable rules, sorted by priority.
    """
    applicable: List[TransitionRule] = []
    # Guard: nothing to match if element has no category or features
    if element.category is None or element.features is None:
        return applicable
    for rule in TRANSITION_MATRIX:
        # Category filter
        if rule.from_category is not None and rule.from_category is not element.category:
            continue
        # Feature filter: all required features must be present
        if not rule.required_features.issubset(element.features):
            continue
        # Economy gate for deletion / pause laws
        if (
            rule.law in (_TL.HADHF, _TL.WAQF)
            and context.economy_pressure < _ECONOMY_REDUCTION_THRESHOLD
        ):
            continue
        # Idgham gate: require identical or phonetically similar (same group) neighbour
        if rule.law is _TL.IDGHAM:
            left = context.left_neighbor
            if left is None:
                continue
            # Accept identical codepoint (full gemination) or same articulatory
            # group (partial assimilation, e.g. solar-letter assimilation)
            phonetically_similar = (
                left.unicode == element.unicode
                or left.group == element.group
            )
            if not phonetically_similar:
                continue
        # Ziyada gate: only applies in augmented architecture or AUGMENT role
        if rule.law is _TL.ZIYADA:
            in_augment_role = context.function_role is _FR.AUGMENT
            in_augment_arch = (
                "مزيد" in context.architecture
                or "augment" in context.architecture.lower()
            )
            if not (in_augment_role or in_augment_arch):
                continue
        applicable.append(rule)

    applicable.sort(key=lambda r: r.priority)
    return applicable


# ── Cost computation ─────────────────────────────────────────────────

def _transition_cost(rule: TransitionRule, context: TransitionContext) -> tuple:
    """Return ``(loss_root, loss_pattern, phonetic_burden)`` for *rule*.

    Parameters
    ----------
    rule:
        The :class:`~arabic_engine.core.types.TransitionRule` being evaluated.
    context:
        The :class:`~arabic_engine.core.types.TransitionContext` supplying
        economy pressure and transition type information.

    Raises
    ------
    ValueError
        If ``context.economy_pressure`` is outside the valid range ``[0, 1]``.
    """
    if not (0.0 <= context.economy_pressure <= 1.0):
        raise ValueError(
            f"economy_pressure must be in [0, 1]; got {context.economy_pressure!r}"
        )
    lr = _COST_ROOT_LOSS_BY_LAW.get(rule.law, 0.3)
    lp = _COST_PATTERN_LOSS_BY_LAW.get(rule.law, 0.2)
    # Economy pressure reduces phonetic burden cost
    pb = _COST_PHONETIC_BURDEN_BY_TYPE.get(rule.transition_type, 0.1)
    pb = max(0.0, pb - context.economy_pressure * 0.1)
    return lr, lp, pb


# ── Main engine entry point ──────────────────────────────────────────

def apply_best_transition(
    element: DMin,
    context: TransitionContext,
) -> TransitionResult:
    """Apply the optimality-driven transition to *element* in *context*.

    Implements::

        E_new = ArgMin(loss_root + loss_pattern + phonetic_burden)
        subject to: E_new ∈ Nearest_Valid_Functional_Cell

    When the element is stable (no applicable rules), a stability result
    is returned with ``stable=True`` and zero costs.

    Parameters
    ----------
    element:
        The :class:`~arabic_engine.core.types.DMin` entry to transition.
    context:
        The :class:`~arabic_engine.core.types.TransitionContext` providing
        all parameters of ``T_r(E) = f(P, N, F, W, Ec, M)``.

    Returns
    -------
    TransitionResult
        The result after applying (or refusing) the transition.
    """
    if stability_check(element, context):
        return TransitionResult(
            source_unicode=element.unicode,
            applied_rule=None,
            stable=True,
            target_category=element.category,
            surface_form=element.char,
            loss_root=0.0,
            loss_pattern=0.0,
            phonetic_burden=0.0,
            total_cost=0.0,
            conditions_met=frozenset(_TC),
            notes="مستقر — no transition required",
        )

    rules = find_applicable_rules(element, context)
    if not rules:
        return TransitionResult(
            source_unicode=element.unicode,
            applied_rule=None,
            stable=True,
            target_category=element.category,
            surface_form=element.char,
            loss_root=0.0,
            loss_pattern=0.0,
            phonetic_burden=0.0,
            total_cost=0.0,
            conditions_met=frozenset(),
            notes="لا قاعدة مطابقة — element stays in cell",
        )

    # Select rule with minimum total cost
    best_rule = min(
        rules,
        key=lambda r: sum(_transition_cost(r, context)),
    )
    lr, lp, pb = _transition_cost(best_rule, context)
    total = lr + lp + pb

    # Surface form heuristic
    if best_rule.to_category is _PC.SUKUN:
        surface = element.char + chr(_UNICODE_SUKUN)   # append sukūn mark
    elif best_rule.to_category is _PC.SHADDA:
        surface = element.char + chr(_UNICODE_SHADDA)  # append shadda mark
    elif best_rule.to_category is _PC.SPECIAL_MARK:
        surface = ""                               # deleted from surface
    else:
        surface = element.char

    return TransitionResult(
        source_unicode=element.unicode,
        applied_rule=best_rule,
        stable=False,
        target_category=best_rule.to_category,
        surface_form=surface,
        loss_root=lr,
        loss_pattern=lp,
        phonetic_burden=pb,
        total_cost=total,
        conditions_met=best_rule.conditions,
        notes=best_rule.description_ar,
    )


# ── Display helper ───────────────────────────────────────────────────

def format_matrix_table() -> str:
    """Return a UTF-8 table string of the full :data:`TRANSITION_MATRIX`.

    Columns::

        من خانة → إلى خانة | القانون | نوع التحول | الشرط (مختصر) | مثال

    Returns
    -------
    str
        Human-readable matrix table.
    """
    header = (
        f"{'#':<3} {'من':<14} {'إلى':<14} {'القانون':<12} "
        f"{'النوع':<22} {'أولوية':<7} {'مثال'}"
    )
    sep = "─" * len(header)
    rows = [sep, header, sep]
    for i, rule in enumerate(TRANSITION_MATRIX, 1):
        from_cat = rule.from_category.name if rule.from_category else "*"
        rows.append(
            f"{i:<3} {from_cat:<14} {rule.to_category.name:<14} "
            f"{rule.law.name:<12} {rule.transition_type.name:<22} "
            f"{rule.priority:<7} {rule.example}"
        )
    rows.append(sep)
    return "\n".join(rows)
