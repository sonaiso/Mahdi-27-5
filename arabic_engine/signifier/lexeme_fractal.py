"""lexeme_fractal — دستور المفرد الفراكتالي: Lexeme Fractal Constitution v2

This module implements the Lexeme Fractal Constitution v2 which
establishes the single lexeme (المفرد) as a complete fractal unit
ready for composition.  It answers:

1. What are the six pillars of a lexeme?   (Art. 20–26)
2. How does the fractal law cycle apply?   (Art. 46–52)
3. When is a lexeme ready for composition? (Art. 53–59)
4. What are the acceptance/rejection criteria? (Art. 60–61)

The fractal cycle follows:
    تعيين → حفظ → ربط → حكم → انتقال → ردّ

Public API
----------
* :func:`classify_conceptual_type`
* :func:`compute_readiness`
* :func:`validate_lexeme`
* :func:`build_signification_triad`
* :func:`run_lexeme_fractal`
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from arabic_engine.core.enums import (
    POS,
    ConceptualType,
    LexemeAcceptanceCode,
    LexemeFractalPhase,
    SemanticDirectionGenus,
)
from arabic_engine.core.types import (
    CompositionReadiness,
    Concept,
    DirectionAssignment,
    Lexeme,
    LexemeFractalNode,
    LexemeFractalResult,
    LexicalClosure,
    SignificationTriad,
    WeightFractalResult,
)

# ── Readiness threshold ─────────────────────────────────────────────

_THETA_R: float = 0.75

# ── POS + Genus → ConceptualType mapping (Art. 24) ──────────────────

_POS_GENUS_TO_TYPE: dict[
    Tuple[POS, SemanticDirectionGenus], ConceptualType
] = {
    # Noun-like
    (POS.ISM, SemanticDirectionGenus.WUJUD): ConceptualType.KULLI,
    (POS.ISM, SemanticDirectionGenus.SIFA): ConceptualType.SIFA,
    (POS.ISM, SemanticDirectionGenus.HADATH): ConceptualType.MASDARIYYA,
    (POS.ISM, SemanticDirectionGenus.NISBA): ConceptualType.ALA2IQIYYA,
    # Verb-like
    (POS.FI3L, SemanticDirectionGenus.HADATH): ConceptualType.FA3ILIYYA,
    (POS.FI3L, SemanticDirectionGenus.WUJUD): ConceptualType.FA3ILIYYA,
    (POS.FI3L, SemanticDirectionGenus.SIFA): ConceptualType.FA3ILIYYA,
    (POS.FI3L, SemanticDirectionGenus.NISBA): ConceptualType.FA3ILIYYA,
    # Adjective
    (POS.SIFA, SemanticDirectionGenus.SIFA): ConceptualType.SIFA,
    (POS.SIFA, SemanticDirectionGenus.WUJUD): ConceptualType.SIFA,
    (POS.SIFA, SemanticDirectionGenus.HADATH): ConceptualType.SIFA,
    (POS.SIFA, SemanticDirectionGenus.NISBA): ConceptualType.SIFA,
    # Particle
    (POS.HARF, SemanticDirectionGenus.NISBA): ConceptualType.ALA2IQIYYA,
    (POS.HARF, SemanticDirectionGenus.WUJUD): ConceptualType.ALA2IQIYYA,
    (POS.HARF, SemanticDirectionGenus.HADATH): ConceptualType.ALA2IQIYYA,
    (POS.HARF, SemanticDirectionGenus.SIFA): ConceptualType.ALA2IQIYYA,
    # Adverb → temporal/locative
    (POS.ZARF, SemanticDirectionGenus.WUJUD): ConceptualType.ZAMANIYYA,
    (POS.ZARF, SemanticDirectionGenus.HADATH): ConceptualType.ZAMANIYYA,
    (POS.ZARF, SemanticDirectionGenus.SIFA): ConceptualType.ZAMANIYYA,
    (POS.ZARF, SemanticDirectionGenus.NISBA): ConceptualType.ZAMANIYYA,
    # Pronoun → particular
    (POS.DAMIR, SemanticDirectionGenus.WUJUD): ConceptualType.JUZ2I,
    (POS.DAMIR, SemanticDirectionGenus.HADATH): ConceptualType.JUZ2I,
    (POS.DAMIR, SemanticDirectionGenus.SIFA): ConceptualType.JUZ2I,
    (POS.DAMIR, SemanticDirectionGenus.NISBA): ConceptualType.JUZ2I,
    # Masdar → infinitival
    (POS.MASDAR_SARIH, SemanticDirectionGenus.HADATH): ConceptualType.MASDARIYYA,
    (POS.MASDAR_SARIH, SemanticDirectionGenus.WUJUD): ConceptualType.MASDARIYYA,
    (POS.MASDAR_SARIH, SemanticDirectionGenus.SIFA): ConceptualType.MASDARIYYA,
    (POS.MASDAR_SARIH, SemanticDirectionGenus.NISBA): ConceptualType.MASDARIYYA,
    (POS.MASDAR_MUAWWAL, SemanticDirectionGenus.HADATH): ConceptualType.MASDARIYYA,
    (POS.MASDAR_MUAWWAL, SemanticDirectionGenus.WUJUD): ConceptualType.MASDARIYYA,
    (POS.MASDAR_MUAWWAL, SemanticDirectionGenus.SIFA): ConceptualType.MASDARIYYA,
    (POS.MASDAR_MUAWWAL, SemanticDirectionGenus.NISBA): ConceptualType.MASDARIYYA,
}


# ── Public API ──────────────────────────────────────────────────────


def classify_conceptual_type(
    closure: LexicalClosure,
    genus: Optional[SemanticDirectionGenus] = None,
) -> ConceptualType:
    """Classify the conceptual type of a lexeme (Art. 24).

    Args:
        closure: The lexical closure of the word.
        genus: The semantic direction genus (inferred from POS if absent).

    Returns:
        A :class:`~arabic_engine.core.enums.ConceptualType`.
    """
    if genus is None:
        from arabic_engine.signifier.weight_fractal import _POS_TO_GENUS

        genus = _POS_TO_GENUS.get(closure.pos, SemanticDirectionGenus.WUJUD)

    key = (closure.pos, genus)
    return _POS_GENUS_TO_TYPE.get(key, ConceptualType.KULLI)


def compute_readiness(
    closure: LexicalClosure,
    direction: Optional[DirectionAssignment] = None,
    weight: Optional[WeightFractalResult] = None,
) -> CompositionReadiness:
    """Compute composition readiness score (Art. 53–59).

    Ready(L) = (Mat + Struct + Dir + Type + POS + Recover) / 6

    Each sub-score is 1.0 when the dimension is present and valid,
    0.0 otherwise.

    Args:
        closure: The lexical closure.
        direction: Optional direction assignment.
        weight: Optional weight fractal result.

    Returns:
        A :class:`~arabic_engine.core.types.CompositionReadiness`.
    """
    mat = 1.0 if (closure.root and len(closure.root) > 0) else 0.0
    struct = 1.0 if (weight is not None and weight.is_closed) else 0.0
    dir_score = 1.0 if direction is not None else 0.0
    type_score = 1.0 if closure.pos != POS.UNKNOWN else 0.0
    pos_score = 1.0 if closure.pos != POS.UNKNOWN else 0.0
    recover = 1.0 if (closure.root and closure.pattern) else 0.0

    overall = round(
        (mat + struct + dir_score + type_score + pos_score + recover) / 6, 4
    )

    return CompositionReadiness(
        material_score=mat,
        structural_score=struct,
        direction_score=dir_score,
        type_score=type_score,
        pos_score=pos_score,
        recovery_score=recover,
        overall=overall,
        is_ready=overall >= _THETA_R,
    )


def validate_lexeme(
    lexeme: Lexeme,
) -> Tuple[bool, Tuple[LexemeAcceptanceCode, ...], Tuple[LexemeAcceptanceCode, ...]]:
    """Validate a lexeme against acceptance/rejection criteria (Art. 58, 60–61).

    Args:
        lexeme: The lexeme tuple to validate.

    Returns:
        (is_valid, acceptance_codes, rejection_codes)
    """
    accept: List[LexemeAcceptanceCode] = []
    reject: List[LexemeAcceptanceCode] = []

    # Art. 60 — acceptance criteria
    if lexeme.material and len(lexeme.material) > 0:
        accept.append(LexemeAcceptanceCode.MADDA_THABITA)
    else:
        reject.append(LexemeAcceptanceCode.MADDA_MAFTUHA)

    if lexeme.weight_pattern:
        accept.append(LexemeAcceptanceCode.WAZN_THABIT)

    if lexeme.semantic_direction is not None:
        accept.append(LexemeAcceptanceCode.JIHA_THABITA)
    else:
        reject.append(LexemeAcceptanceCode.JIHA_MUTA3ADHIRA)

    if lexeme.conceptual_type is not None:
        accept.append(LexemeAcceptanceCode.NAW3_THABIT)

    if lexeme.final_pos != POS.UNKNOWN:
        accept.append(LexemeAcceptanceCode.QISM_THABIT)
    else:
        reject.append(LexemeAcceptanceCode.QISM_GHAYR_THABIT)

    # Recovery: root must be present
    if lexeme.material and len(lexeme.material) > 0 and lexeme.weight_pattern:
        accept.append(LexemeAcceptanceCode.RADD_MUMKIN)
    else:
        reject.append(LexemeAcceptanceCode.RADD_MUTA3ADHIR)

    if lexeme.readiness >= _THETA_R:
        accept.append(LexemeAcceptanceCode.JAHIZ_LIL_TARKIB)
    else:
        reject.append(LexemeAcceptanceCode.GHAYR_JAHIZ)

    is_valid = len(reject) == 0
    return is_valid, tuple(accept), tuple(reject)


def build_signification_triad(
    closure: LexicalClosure,
    concept: Optional[Concept] = None,
) -> SignificationTriad:
    """Build the signification triad for a lexeme (Art. 42–45).

    The three modes — mutabaqa, tadammun, iltizam — vary by POS.

    Args:
        closure: The lexical closure.
        concept: Optional ontological concept.

    Returns:
        A :class:`~arabic_engine.core.types.SignificationTriad`.
    """
    lemma = closure.lemma or closure.surface
    pos = closure.pos

    if pos == POS.FI3L:
        mutabaqa = f"event:{lemma}"
        tadammun = f"agent+patient:{lemma}"
        iltizam = f"temporal-frame:{lemma}"
    elif pos == POS.HARF:
        mutabaqa = f"relation:{lemma}"
        tadammun = f"binding:{lemma}"
        iltizam = f"constraint:{lemma}"
    elif pos in (POS.MASDAR_SARIH, POS.MASDAR_MUAWWAL):
        mutabaqa = f"nominalized-event:{lemma}"
        tadammun = f"event-core:{lemma}"
        iltizam = f"agent-capacity:{lemma}"
    elif pos == POS.SIFA:
        mutabaqa = f"attribute:{lemma}"
        tadammun = f"described-entity:{lemma}"
        iltizam = f"degree:{lemma}"
    else:
        # ISM and fallback
        mutabaqa = f"entity:{lemma}"
        tadammun = f"genus:{lemma}"
        iltizam = f"properties:{lemma}"

    if concept is not None:
        mutabaqa = f"{concept.semantic_type.name.lower()}:{lemma}"

    return SignificationTriad(
        mutabaqa=mutabaqa,
        tadammun=tadammun,
        iltizam=iltizam,
        pos_category=pos,
    )


# ── Fractal cycle phases (Art. 46–52) ───────────────────────────────


def _build_phase_node(
    idx: int,
    phase: LexemeFractalPhase,
    label: str,
    detail: Tuple[Tuple[str, str], ...],
    root_tag: str,
    parent_phase: Optional[LexemeFractalPhase],
) -> LexemeFractalNode:
    """Build a single fractal node."""
    return LexemeFractalNode(
        node_id=f"LFN_{root_tag}_{idx}",
        phase=phase,
        label=label,
        detail=detail,
        parent_phase=parent_phase,
    )


def run_lexeme_fractal(
    closure: LexicalClosure,
    direction: Optional[DirectionAssignment] = None,
    weight: Optional[WeightFractalResult] = None,
    concept: Optional[Concept] = None,
) -> LexemeFractalResult:
    """Run the full lexeme fractal cycle (Art. 46–61).

    Orchestrates: classify → readiness → fractal tree → validate.

    Args:
        closure: The lexical closure of the word.
        direction: Optional direction assignment.
        weight: Optional weight fractal result.
        concept: Optional ontological concept.

    Returns:
        A :class:`~arabic_engine.core.types.LexemeFractalResult`.
    """
    genus = (
        direction.genus
        if direction is not None
        else SemanticDirectionGenus.WUJUD
    )

    # Derive pillars
    ctype = classify_conceptual_type(closure, genus)
    readiness = compute_readiness(closure, direction, weight)

    # Build lexeme tuple (Art. 57)
    lexeme = Lexeme(
        material=closure.root,
        weight_pattern=closure.pattern,
        semantic_direction=genus,
        conceptual_type=ctype,
        final_pos=closure.pos,
        readiness=readiness.overall,
    )

    # Build signification triad (Art. 42–45)
    signification = build_signification_triad(closure, concept)

    # Build 6-phase fractal tree (Art. 46–52)
    root_tag = closure.root[0] if closure.root else "x"
    nodes: List[LexemeFractalNode] = []

    # Phase 1: TA3YIN — assignment (Art. 47)
    nodes.append(
        _build_phase_node(
            0,
            LexemeFractalPhase.TA3YIN,
            "تعيين المادة والجهة والنوع والقسم",
            (
                ("material", ",".join(closure.root) if closure.root else ""),
                ("direction", genus.name),
                ("type", ctype.name),
                ("pos", closure.pos.name),
            ),
            root_tag,
            None,
        )
    )

    # Phase 2: HIFZ — preservation (Art. 48)
    nodes.append(
        _build_phase_node(
            1,
            LexemeFractalPhase.HIFZ,
            "حفظ الجذر والوزن والجهة والهوية",
            (
                ("root", ",".join(closure.root) if closure.root else ""),
                ("pattern", closure.pattern),
                ("direction", genus.name),
                ("lemma", closure.lemma),
            ),
            root_tag,
            LexemeFractalPhase.TA3YIN,
        )
    )

    # Phase 3: RABT — linking (Art. 49)
    nodes.append(
        _build_phase_node(
            2,
            LexemeFractalPhase.RABT,
            "ربط المادة بالبنية والبنية بالجهة والجهة بالقسم",
            (
                ("material_to_structure", closure.pattern),
                ("structure_to_direction", genus.name),
                ("direction_to_pos", closure.pos.name),
                ("lexeme_to_composition", str(readiness.is_ready)),
            ),
            root_tag,
            LexemeFractalPhase.HIFZ,
        )
    )

    # Phase 4: HUKM — judgment (Art. 50)
    is_derived = bool(closure.pattern and len(closure.pattern) > 3)
    nodes.append(
        _build_phase_node(
            3,
            LexemeFractalPhase.HUKM,
            "حكم على الصحة والقسم والجهة والجاهزية",
            (
                ("valid", str(closure.pos != POS.UNKNOWN)),
                ("pos", closure.pos.name),
                ("direction", genus.name),
                ("derived", str(is_derived)),
                ("ready", str(readiness.is_ready)),
            ),
            root_tag,
            LexemeFractalPhase.RABT,
        )
    )

    # Phase 5: INTIQAL — transition (Art. 51)
    composition_slot = _infer_composition_slot(closure.pos, genus)
    nodes.append(
        _build_phase_node(
            4,
            LexemeFractalPhase.INTIQAL,
            "انتقال إلى الأدوار التركيبية",
            (
                ("opens_slot", composition_slot),
                ("pos", closure.pos.name),
            ),
            root_tag,
            LexemeFractalPhase.HUKM,
        )
    )

    # Phase 6: RADD — return (Art. 52)
    nodes.append(
        _build_phase_node(
            5,
            LexemeFractalPhase.RADD,
            "رد إلى الجذر والوزن والجهة ومسار التوليد",
            (
                ("root", ",".join(closure.root) if closure.root else ""),
                ("pattern", closure.pattern),
                ("direction", genus.name),
                ("derived", str(is_derived)),
            ),
            root_tag,
            LexemeFractalPhase.INTIQAL,
        )
    )

    # Validate (Art. 58, 60–61)
    is_valid, accept_codes, reject_codes = validate_lexeme(lexeme)

    # Completeness score
    expected_phases = set(LexemeFractalPhase)
    actual_phases = {n.phase for n in nodes}
    phase_coverage = len(actual_phases & expected_phases) / max(
        len(expected_phases), 1
    )
    completeness = round((phase_coverage + readiness.overall) / 2, 4)

    return LexemeFractalResult(
        lexeme=lexeme,
        fractal_tree=tuple(nodes),
        readiness=readiness,
        signification=signification,
        completeness_score=completeness,
        is_valid=is_valid,
        acceptance_codes=accept_codes,
        rejection_codes=reject_codes,
    )


# ── Helpers ─────────────────────────────────────────────────────────


def _infer_composition_slot(
    pos: POS, genus: SemanticDirectionGenus
) -> str:
    """Infer the compositional slot a lexeme opens (Art. 55)."""
    if pos == POS.FI3L:
        return "predicative"
    if pos == POS.HARF:
        return "relational"
    if pos == POS.ZARF:
        return "temporal-locative"
    if pos == POS.SIFA:
        return "attributive"
    if pos in (POS.MASDAR_SARIH, POS.MASDAR_MUAWWAL):
        return "nominalized-event"
    if genus == SemanticDirectionGenus.NISBA:
        return "relational"
    return "nominal"
