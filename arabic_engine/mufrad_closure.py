"""mufrad_closure — إقفال اللفظ المفرد إقفالاً جامعاً مانعاً

Total closure of a single Arabic word.  This module orchestrates ALL
dimensions of word-level analysis into a single deterministic record:

    Ω(w) = R ∘ E ∘ D ∘ W ∘ S ∘ M ∘ P ∘ C ∘ N(w)

Where:

* N : normalisation  (str → str)
* C : lexical closure (str → LexicalClosure)
* P : phonological closure (LexicalClosure → DMin)
* M : masdar analysis (LexicalClosure → Optional[MasdarRecord])
* S : semantic direction (LexicalClosure → DirectionAssignment)
* W : weight fractal (LexicalClosure → WeightFractalResult)
* D : dalāla link (LexicalClosure × Concept → DalalaLink)
* E : epistemic reception (SubjectClassification → EpistemicReceptionResult)
* R : record assembly → MufradClosureResult

Ω(w).is_closed = True iff **all** non-optional components are valid.

Public API
----------
* :func:`close_mufrad`
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.cognition.epistemic_reception import (
    classify_subject,
    validate_reception,
)
from arabic_engine.core.enums import (
    ReceptionRank,
    SubjectGenre,
)
from arabic_engine.core.types import (
    CarryingAssignment,
    Concept,
    DalalaLink,
    DMin,
    EpistemicReceptionInput,
    EpistemicReceptionResult,
    LexicalClosure,
    MasdarRecord,
    MufradClosureResult,
)
from arabic_engine.linkage.dalala import validate_link
from arabic_engine.signified.ontology import map_concept
from arabic_engine.signified.semantic_direction import (
    assign_direction,
    build_direction_space,
)
from arabic_engine.signifier.root_pattern import lexical_closure as _lexical_closure
from arabic_engine.signifier.unicode_norm import normalize
from arabic_engine.signifier.weight_fractal import run_weight_fractal

# ── Optional phonology import ───────────────────────────────────────

try:
    from arabic_engine.signifier.dmin import lookup_dmin
except ImportError:  # pragma: no cover
    lookup_dmin = None  # type: ignore[assignment]

# ── Optional masdar import ──────────────────────────────────────────

try:
    from arabic_engine.signifier.masdar import extract_masdar_from_surface
except ImportError:  # pragma: no cover
    extract_masdar_from_surface = None  # type: ignore[assignment]

# ── Genre mapping for epistemic reception ───────────────────────────

_GENUS_TO_SUBJECT_GENRE = {
    "WUJUD": SubjectGenre.WUJUD,
    "SIFA": SubjectGenre.SIFA,
    "HADATH": SubjectGenre.HADATH,
    "NISBA": SubjectGenre.NISBA,
}

# ── Singleton direction space ──────────────────────────────────────

_SPACE = None


def _get_space():
    global _SPACE
    if _SPACE is None:
        _SPACE = build_direction_space()
    return _SPACE


# ── Public API ──────────────────────────────────────────────────────


def close_mufrad(word: str) -> MufradClosureResult:
    """Compute the complete, closed record for a single Arabic word.

    Orchestrates signal, morphological, phonological, semantic-direction,
    weight-fractal, masdar, ontological, dalālatic, and epistemic
    reception closures into one immutable result.

    Args:
        word: A single Arabic word (may include diacritics).

    Returns:
        A :class:`~arabic_engine.core.types.MufradClosureResult`.
        ``is_closed`` is ``True`` when every required dimension
        has been successfully computed.
    """
    # N — normalisation
    normalised = normalize(word)

    # C — lexical closure
    closure: Optional[LexicalClosure] = None
    try:
        closure = _lexical_closure(normalised)
    except Exception:
        pass

    if closure is None:
        return MufradClosureResult(
            surface=word,
            normalized=normalised,
            is_closed=False,
            closure_confidence=0.0,
        )

    # P — phonological closure (DMin)
    dmin: Optional[DMin] = None
    if lookup_dmin is not None and closure.root:
        try:
            first_char = closure.root[0]
            if first_char and len(first_char) > 0:
                dmin = lookup_dmin(ord(first_char[0]))
        except (IndexError, TypeError, Exception):
            pass

    # M — masdar analysis
    masdar: Optional[MasdarRecord] = None
    if extract_masdar_from_surface is not None:
        try:
            masdar = extract_masdar_from_surface(normalised)
        except Exception:
            pass

    # S — semantic direction
    space = _get_space()
    direction_assignment = assign_direction(closure, space)

    # W — weight fractal
    weight_fractal = run_weight_fractal(closure)

    # O — ontological mapping
    concept: Optional[Concept] = None
    try:
        concept = map_concept(closure)
    except Exception:
        pass

    # D — dalāla link
    dalala_link: Optional[DalalaLink] = None
    if concept is not None:
        try:
            dalala_link = validate_link(closure, concept)
        except Exception:
            pass

    # E — epistemic reception
    epistemic_reception: Optional[EpistemicReceptionResult] = None
    try:
        genus = direction_assignment.genus
        subject_genre = _GENUS_TO_SUBJECT_GENRE.get(genus.name, SubjectGenre.WUJUD)
        subject = classify_subject(subject_genre)
        reception_input = EpistemicReceptionInput(
            reception_id=f"REC_{normalised[:10]}",
            subject=subject,
            sense_present=True,
            feeling_present=True,
            thought_present=True,
            intention_present=True,
            choice_present=True,
            will_present=True,
            claimed_assignments=(
                CarryingAssignment(
                    genre=subject_genre,
                    rank=ReceptionRank.HISS,
                    claimed_mode=subject.genre,
                ),
            ),
        )
        epistemic_reception = validate_reception(reception_input)
    except Exception:
        pass

    # R — record assembly
    required_closed = (
        closure is not None
        and direction_assignment is not None
        and weight_fractal is not None
        and weight_fractal.is_closed
    )

    confidences = [
        closure.confidence if closure else 0.0,
        direction_assignment.confidence if direction_assignment else 0.0,
        weight_fractal.completeness_score if weight_fractal else 0.0,
    ]
    if dalala_link is not None:
        confidences.append(dalala_link.confidence)
    closure_confidence = round(sum(confidences) / max(len(confidences), 1), 4)

    return MufradClosureResult(
        surface=word,
        normalized=normalised,
        lexical_closure=closure,
        dmin=dmin,
        direction_assignment=direction_assignment,
        weight_fractal=weight_fractal,
        masdar_record=masdar,
        concept=concept,
        dalala_link=dalala_link,
        epistemic_reception=epistemic_reception,
        is_closed=bool(required_closed),
        closure_confidence=closure_confidence,
    )
