"""reception_constitution — دستور التلقي المعرفي v1 (Epistemic Reception Constitution).

Establishes the constitutional separation between:

* **Subject Axis** (محور الموضوع الوارد) — what arrives at the rational self:
  existence (وجود), attribute (صفة), event (حدث), relation (نسبة).

* **Reception Axis** (محور التلقي والمعالجة) — how the rational self receives
  and processes the subject: sense (حس), feeling (شعور), thought (فكر),
  intention (نية), choice (خيار), will (إرادة).

A governing matrix classifies every (genre × rank) pair as:
  أصيل (original), تبعي (subsidiary), or ممتنع (impossible).

This constitution is a prerequisite to all downstream constitutions
(Semantic Direction Space, Lexeme Fractal, Weight Fractal).

Public API
----------
* :func:`build_constitutional_matrix`
* :func:`classify_carrying`
* :func:`get_layer`
* :func:`get_primary_entry`
* :func:`get_closure_rank`
* :func:`validate_carrying_claim`
* :func:`assess_subject`
* :func:`get_reception_ranks_for_layer`
* :func:`map_semantic_type_to_genre`
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from arabic_engine.core.enums import (
    CarryingStatus,
    ReceptionLayer,
    ReceptionRank,
    SemanticType,
    SubjectGenre,
)
from arabic_engine.core.types import (
    CarryingCell,
    ReceptionConstitutionMatrix,
    ReceptionConstitutionRecord,
    ReceptionRankDefinition,
    SubjectGenreDefinition,
)

# ── Subject Genre Definitions ───────────────────────────────────────

SUBJECT_GENRE_DEFINITIONS: Tuple[SubjectGenreDefinition, ...] = (
    SubjectGenreDefinition(
        genre=SubjectGenre.WUJUD,
        name_ar="الوجود",
        definition_ar="ما يثبت الشيء أو الذات أو المرجع",
        definition_en="What establishes a thing, entity, or referent",
    ),
    SubjectGenreDefinition(
        genre=SubjectGenre.SIFA,
        name_ar="الصفة",
        definition_ar="ما يثبت كيف الشيء أو حاله أو هيئته",
        definition_en="What establishes how a thing is, its state, or its form",
    ),
    SubjectGenreDefinition(
        genre=SubjectGenre.HADATH,
        name_ar="الحدث",
        definition_ar="ما يثبت الوقوع أو التغير أو الصيرورة",
        definition_en="What establishes occurrence, change, or becoming",
    ),
    SubjectGenreDefinition(
        genre=SubjectGenre.NISBA,
        name_ar="النسبة",
        definition_ar="ما يثبت الربط أو التعلق أو الجهة بين اثنين فأكثر",
        definition_en=(
            "What establishes connection, attachment, or direction "
            "between two or more"
        ),
    ),
)

# ── Reception Rank Definitions ──────────────────────────────────────

RECEPTION_RANK_DEFINITIONS: Tuple[ReceptionRankDefinition, ...] = (
    ReceptionRankDefinition(
        rank=ReceptionRank.HISS,
        layer=ReceptionLayer.ISTIQBAL,
        name_ar="الحس",
        definition_ar="إدخال أولي للموضوع من طريق الأثر المباشر",
        definition_en=(
            "First entry of the subject into the rational self "
            "via direct or quasi-direct effect"
        ),
    ),
    ReceptionRankDefinition(
        rank=ReceptionRank.SHUUR,
        layer=ReceptionLayer.ISTIQBAL,
        name_ar="الشعور",
        definition_ar="الأثر الداخلي الحيّ للموضوع في الذات",
        definition_en=(
            "Inner living effect of the subject on the rational self"
        ),
    ),
    ReceptionRankDefinition(
        rank=ReceptionRank.FIKR,
        layer=ReceptionLayer.MUALAJA_MARIFIYYA,
        name_ar="الفكر",
        definition_ar="ربط المدرك بالمعلومات السابقة لإنتاج تعيين",
        definition_en=(
            "Linking the perceived to prior information "
            "to produce determination and meaning"
        ),
    ),
    ReceptionRankDefinition(
        rank=ReceptionRank.NIYYA,
        layer=ReceptionLayer.TAWJIH,
        name_ar="النية",
        definition_ar="تعيين جهة القصد بعد الفهم",
        definition_en=(
            "Determining the aimed direction after understanding"
        ),
    ),
    ReceptionRankDefinition(
        rank=ReceptionRank.KHIYAR,
        layer=ReceptionLayer.TAWJIH,
        name_ar="الخيار",
        definition_ar="فتح البدائل الممكنة",
        definition_en="Opening possible alternatives",
    ),
    ReceptionRankDefinition(
        rank=ReceptionRank.IRADA,
        layer=ReceptionLayer.TAWJIH,
        name_ar="الإرادة",
        definition_ar="إمضاء البديل المختار",
        definition_en="Ratifying the chosen alternative",
    ),
)

# ── Layer → Rank mapping ────────────────────────────────────────────

_LAYER_TO_RANKS: Dict[ReceptionLayer, Tuple[ReceptionRank, ...]] = {
    ReceptionLayer.ISTIQBAL: (ReceptionRank.HISS, ReceptionRank.SHUUR),
    ReceptionLayer.MUALAJA_MARIFIYYA: (ReceptionRank.FIKR,),
    ReceptionLayer.TAWJIH: (
        ReceptionRank.NIYYA,
        ReceptionRank.KHIYAR,
        ReceptionRank.IRADA,
    ),
}

_RANK_TO_LAYER: Dict[ReceptionRank, ReceptionLayer] = {
    rank: layer
    for layer, ranks in _LAYER_TO_RANKS.items()
    for rank in ranks
}

# ── Constitutional Matrix (4 genres × 6 ranks) ─────────────────────

_A = CarryingStatus.ASIL
_T = CarryingStatus.TABA3I
_M = CarryingStatus.MUMTANI3

CONSTITUTIONAL_MATRIX: Tuple[CarryingCell, ...] = (
    # ── الوجود (Existence) ──────────────────────────────────────────
    CarryingCell(
        genre=SubjectGenre.WUJUD,
        rank=ReceptionRank.HISS,
        status=_A,
        qualification="أصيل",
        justification=(
            "أول ما يلتقطه الحس هو: أن هناك شيئًا"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.WUJUD,
        rank=ReceptionRank.SHUUR,
        status=_T,
        qualification="تبعي",
        justification=(
            "الشعور لا يثبت الوجود أولًا، بل يتأثر به"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.WUJUD,
        rank=ReceptionRank.FIKR,
        status=_A,
        qualification="أصيل",
        justification=(
            "الفكر يحول الحضور إلى تعيين وإثبات وتمييز"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.WUJUD,
        rank=ReceptionRank.NIYYA,
        status=_T,
        qualification="تبعي",
        justification=(
            "النية لا تثبت الوجود، بل تبني موقفًا منه"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.WUJUD,
        rank=ReceptionRank.KHIYAR,
        status=_T,
        qualification="تبعي",
        justification=(
            "الخيار لا يثبت الوجود، بل تبني موقفًا منه"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.WUJUD,
        rank=ReceptionRank.IRADA,
        status=_T,
        qualification="تبعي",
        justification=(
            "الإرادة لا تثبت الوجود، بل تبني موقفًا منه"
        ),
    ),
    # ── الصفة (Attribute) ───────────────────────────────────────────
    CarryingCell(
        genre=SubjectGenre.SIFA,
        rank=ReceptionRank.HISS,
        status=_A,
        qualification="أصيل في المحسوس، تبعي في غيره",
        justification=(
            "الصفات المحسوسة كالأبيض والحار والثقيل تُدرك حسًا مباشرة"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.SIFA,
        rank=ReceptionRank.SHUUR,
        status=_A,
        qualification="أصيل من جهة الأثر",
        justification=(
            "الصفات تدخل الشعور مباشرة: جميل، قبيح، مزعج، مريح"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.SIFA,
        rank=ReceptionRank.FIKR,
        status=_A,
        qualification="أصيل",
        justification=(
            "الفكر يغلق الوصف تعريفًا وتمييزًا"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.SIFA,
        rank=ReceptionRank.NIYYA,
        status=_T,
        qualification="تبعي",
        justification=(
            "النية لا تحمل الصفة أصالةً بل تبني موقفًا منها"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.SIFA,
        rank=ReceptionRank.KHIYAR,
        status=_T,
        qualification="تبعي",
        justification=(
            "الخيار لا يحمل الصفة أصالةً بل تبني موقفًا منها"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.SIFA,
        rank=ReceptionRank.IRADA,
        status=_T,
        qualification="تبعي",
        justification=(
            "الإرادة لا تحمل الصفة أصالةً بل تبني موقفًا منها"
        ),
    ),
    # ── الحدث (Event) ───────────────────────────────────────────────
    CarryingCell(
        genre=SubjectGenre.HADATH,
        rank=ReceptionRank.HISS,
        status=_T,
        qualification="تبعي أو جزئي",
        justification=(
            "الحس قد يرى الحركة أو يسمع الصوت، لكنه لا يغلق "
            "مفهوم الحدث ولا نوعه ولا جهته"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.HADATH,
        rank=ReceptionRank.SHUUR,
        status=_A,
        qualification="أصيل من جهة التأثر بالحركة والوقوع",
        justification=(
            "الحدث يقع في النفس: خوفًا، فرحًا، اضطرابًا، توترًا"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.HADATH,
        rank=ReceptionRank.FIKR,
        status=_A,
        qualification="أصيل",
        justification=(
            "الفكر يثبت أن هذا وقوع أو تغير أو صيرورة أو فعل"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.HADATH,
        rank=ReceptionRank.NIYYA,
        status=_T,
        qualification="تبعي",
        justification=(
            "النية لا تحمل الحدث أصالةً بل تبني موقفًا منه"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.HADATH,
        rank=ReceptionRank.KHIYAR,
        status=_T,
        qualification="تبعي",
        justification=(
            "الخيار لا يحمل الحدث أصالةً بل تبني موقفًا منه"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.HADATH,
        rank=ReceptionRank.IRADA,
        status=_T,
        qualification="تبعي",
        justification=(
            "الإرادة لا تحمل الحدث أصالةً بل تبني موقفًا منه"
        ),
    ),
    # ── النسبة (Relation) ───────────────────────────────────────────
    CarryingCell(
        genre=SubjectGenre.NISBA,
        rank=ReceptionRank.HISS,
        status=_T,
        qualification="تبعي في القريب المحسوس، ممتنع في المجرد الخالص",
        justification=(
            "الحس قد يدرك قربًا وبعدًا حسًا، لكنه لا يغلق "
            "السببية أو الشرطية أو العلية أو الربط المجرد"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.NISBA,
        rank=ReceptionRank.SHUUR,
        status=_T,
        qualification="تبعي",
        justification=(
            "النسبة لا تدخل الشعور غالبًا إلا بواسطة أثرها"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.NISBA,
        rank=ReceptionRank.FIKR,
        status=_A,
        qualification="أصيل",
        justification=(
            "الفكر هو الذي يثبت أن هذا متعلق بذاك أو سببه "
            "أو شرطه أو ظرفه أو نسبته"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.NISBA,
        rank=ReceptionRank.NIYYA,
        status=_T,
        qualification="تبعي",
        justification=(
            "النية لا تحمل النسبة أصالةً بل تبني موقفًا منها"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.NISBA,
        rank=ReceptionRank.KHIYAR,
        status=_T,
        qualification="تبعي",
        justification=(
            "الخيار لا يحمل النسبة أصالةً بل تبني موقفًا منها"
        ),
    ),
    CarryingCell(
        genre=SubjectGenre.NISBA,
        rank=ReceptionRank.IRADA,
        status=_T,
        qualification="تبعي",
        justification=(
            "الإرادة لا تحمل النسبة أصالةً بل تبني موقفًا منها"
        ),
    ),
)

# ── Internal index for fast lookup ──────────────────────────────────

_MATRIX_INDEX: Dict[Tuple[SubjectGenre, ReceptionRank], CarryingCell] = {
    (cell.genre, cell.rank): cell for cell in CONSTITUTIONAL_MATRIX
}

# ── Primary entry per genre ─────────────────────────────────────────

_PRIMARY_ENTRY: Dict[SubjectGenre, ReceptionRank] = {
    SubjectGenre.WUJUD: ReceptionRank.HISS,
    SubjectGenre.SIFA: ReceptionRank.HISS,
    SubjectGenre.HADATH: ReceptionRank.SHUUR,
    SubjectGenre.NISBA: ReceptionRank.FIKR,
}

# ── SemanticType → SubjectGenre mapping ─────────────────────────────

_SEMANTIC_TO_GENRE: Dict[SemanticType, SubjectGenre] = {
    SemanticType.ENTITY: SubjectGenre.WUJUD,
    SemanticType.ATTRIBUTE: SubjectGenre.SIFA,
    SemanticType.EVENT: SubjectGenre.HADATH,
    SemanticType.NOMINALIZED_EVENT: SubjectGenre.HADATH,
    SemanticType.EVENT_CONCEPT: SubjectGenre.HADATH,
    SemanticType.RELATION: SubjectGenre.NISBA,
}

# ── Public API ──────────────────────────────────────────────────────


def build_constitutional_matrix() -> ReceptionConstitutionMatrix:
    """Build and return the full canonical 4×6 governing matrix."""
    return ReceptionConstitutionMatrix(
        matrix_id="ERC-v1-matrix",
        cells=list(CONSTITUTIONAL_MATRIX),
        version="v1",
    )


def classify_carrying(
    genre: SubjectGenre,
    rank: ReceptionRank,
) -> CarryingCell:
    """Look up the carrying status for *genre* in *rank*.

    Parameters
    ----------
    genre:
        The subject genre to query.
    rank:
        The reception rank to query.

    Returns
    -------
    :class:`CarryingCell`
        The constitutional cell for this (genre, rank) pair.

    Raises
    ------
    KeyError
        If the (genre, rank) pair is not in the matrix — should never
        happen with valid enum values.
    """
    return _MATRIX_INDEX[(genre, rank)]


def get_layer(rank: ReceptionRank) -> ReceptionLayer:
    """Return the constitutional layer for the given reception *rank*."""
    return _RANK_TO_LAYER[rank]


def get_primary_entry(genre: SubjectGenre) -> ReceptionRank:
    """Return the first reception rank where *genre* is أصيل (original).

    * WUJUD → HISS  (existence enters first via sense)
    * SIFA  → HISS  (sensible attributes enter first via sense)
    * HADATH → SHUUR (events enter first via inner feeling)
    * NISBA → FIKR  (relations enter first via thought)
    """
    return _PRIMARY_ENTRY[genre]


def get_closure_rank(genre: SubjectGenre) -> ReceptionRank:  # noqa: ARG001
    """Return the rank that achieves epistemic closure for *genre*.

    Per the constitution, the epistemic closure rank is always FIKR
    (thought) for all four subject genres, because thought is the
    first rank capable of distinguishing between existence, attribute,
    event, and relation, classifying what arrives, and producing a
    determination that can be judged.
    """
    return ReceptionRank.FIKR


def validate_carrying_claim(
    genre: SubjectGenre,
    rank: ReceptionRank,
    claimed_status: CarryingStatus,
) -> Tuple[bool, str]:
    """Validate whether *claimed_status* matches the constitutional matrix.

    Parameters
    ----------
    genre:
        The subject genre being assessed.
    rank:
        The reception rank being assessed.
    claimed_status:
        The carrying status being claimed.

    Returns
    -------
    tuple[bool, str]
        ``(True, rationale)`` if the claim matches the constitution,
        ``(False, rationale)`` otherwise.
    """
    cell = _MATRIX_INDEX[(genre, rank)]
    if cell.status == claimed_status:
        return (True, cell.justification)
    return (
        False,
        (
            f"Constitutional status is {cell.status.name} "
            f"({cell.qualification}), not {claimed_status.name}. "
            f"Reason: {cell.justification}"
        ),
    )


def assess_subject(genre: SubjectGenre) -> ReceptionConstitutionRecord:
    """Build a full constitutional assessment for *genre* across all ranks.

    Returns
    -------
    :class:`ReceptionConstitutionRecord`
        Contains one :class:`CarryingCell` for each of the six
        reception ranks, plus the primary entry rank and epistemic
        closure rank.
    """
    cells = [
        _MATRIX_INDEX[(genre, rank)]
        for rank in ReceptionRank
    ]
    return ReceptionConstitutionRecord(
        record_id=f"ERC-{genre.name}",
        subject_genre=genre,
        carrying_cells=cells,
        epistemic_closure_rank=get_closure_rank(genre),
        primary_entry_rank=get_primary_entry(genre),
    )


def get_reception_ranks_for_layer(
    layer: ReceptionLayer,
) -> Tuple[ReceptionRank, ...]:
    """Return the reception ranks belonging to *layer*."""
    return _LAYER_TO_RANKS[layer]


def map_semantic_type_to_genre(
    st: SemanticType,
) -> Optional[SubjectGenre]:
    """Map an existing :class:`SemanticType` to a :class:`SubjectGenre`.

    Returns ``None`` for semantic types that do not map to a subject
    genre (e.g. ``NORM``, which is a normative judgment rather than
    a subject arriving at the rational self).
    """
    return _SEMANTIC_TO_GENRE.get(st)
