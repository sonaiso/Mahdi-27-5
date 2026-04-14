"""Segmentation — primary and clitic-split segmentations.

Produces segmentation candidates from signal units.  Each token
gets a primary segmentation (whitespace-based) plus optional
clitic-split alternatives with lower confidence.

Supported clitic types:
- Proclitics: و (conjunction), ف (conjunction), ب (preposition),
  ل (preposition), ك (preposition)
- Article: ال (definite article)
- Enclitics: ه, ها, هم, هن, ك, كم, كن, نا, ي (attached pronouns)

Architectural rule: **no segmentation without boundary basis**.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode, SignalUnit

# ── Proclitic patterns (conjunctions + prepositions) ────────────────
# Single-char proclitics that attach to the front of a word
_SINGLE_PROCLITICS = frozenset({"و", "ف", "ب", "ل", "ك"})

# ── Enclitic patterns (attached pronouns at end of word) ────────────
_ENCLITICS = (
    "هم", "هن", "كم", "كن", "نا", "ها", "ه", "ك", "ي",
)

# ── Words that must NOT be split (false-split prevention) ───────────
# These start with a proclitic char but the char is part of the root.
_NO_SPLIT_WORDS = frozenset({
    "ولد", "ولي", "وزن", "وقف", "وصل", "وجد", "وجه", "وعد",
    "وقع", "وقت", "وحد", "وطن", "ورد", "ورق", "وسط",
    "فعل", "فتح", "فقط", "فهم", "فرح", "فجر", "فقر",
    "بين", "بيت", "بحر", "بعد", "بلد", "بقي",
    "لون", "ليل", "لغة", "لحم", "لعب",
    "كتب", "كبر", "كثر", "كلم", "كنز",
})

# Minimum remaining length after article removal
_MIN_ARTICLE_REMAINDER = 3

# Minimum remaining length after proclitic removal
_MIN_STEM_LENGTH = 2


def segment(signal_units: List[SignalUnit]) -> List[HypothesisNode]:
    """Generate segmentation hypotheses from signal units.

    Each signal unit becomes a primary segmentation hypothesis with
    confidence 1.0.  If clitic splitting is detected, secondary
    hypotheses are added with lower confidence.

    Parameters
    ----------
    signal_units : list[SignalUnit]
        Output of :func:`~arabic_engine.signal.normalization.normalize_atoms`.

    Returns
    -------
    list[HypothesisNode]
        Primary + clitic-split segmentation hypotheses.
    """
    hypotheses: List[HypothesisNode] = []
    for unit in signal_units:
        # Primary segmentation (always produced)
        hypotheses.append(
            HypothesisNode(
                node_id=f"SEG_{unit.unit_id}",
                hypothesis_type="segmentation",
                stage=ActivationStage.SIGNAL,
                source_refs=(unit.unit_id,),
                payload=(
                    ("token_text", unit.normalized_text),
                    ("boundary_basis", "whitespace"),
                    ("surface_text", unit.surface_text),
                ),
                confidence=1.0,
                status=HypothesisStatus.ACTIVE,
            )
        )

        # Clitic-split alternatives
        splits = _try_clitic_split(unit.normalized_text)
        for split_idx, (parts, basis, conf) in enumerate(splits):
            for part_idx, part in enumerate(parts):
                hypotheses.append(
                    HypothesisNode(
                        node_id=f"SEG_{unit.unit_id}_SPLIT{split_idx}_P{part_idx}",
                        hypothesis_type="segmentation",
                        stage=ActivationStage.SIGNAL,
                        source_refs=(unit.unit_id,),
                        payload=(
                            ("token_text", part),
                            ("boundary_basis", basis),
                            ("surface_text", unit.surface_text),
                            ("split_index", part_idx),
                            ("split_total", len(parts)),
                        ),
                        confidence=conf,
                        status=HypothesisStatus.ACTIVE,
                    )
                )

    return hypotheses


def _try_clitic_split(
    token: str,
) -> List[Tuple[List[str], str, float]]:
    """Attempt to split a token into clitic parts.

    Returns a list of (parts, boundary_basis, confidence) tuples.
    Each entry represents one possible splitting.

    Parameters
    ----------
    token : str
        Normalized token text.

    Returns
    -------
    list[tuple[list[str], str, float]]
        Each tuple: (parts, boundary_basis, confidence).
        Empty list if no splitting is possible.
    """
    results: List[Tuple[List[str], str, float]] = []

    if not token or len(token) < 2:
        return results

    # Check for false-split words
    if token in _NO_SPLIT_WORDS:
        return results

    # 1. Try proclitic splitting (front of word)
    proclitic_split = _try_proclitic(token)
    if proclitic_split is not None:
        results.append(proclitic_split)

    # 2. Try enclitic splitting (end of word)
    enclitic_split = _try_enclitic(token)
    if enclitic_split is not None:
        results.append(enclitic_split)

    return results


def _try_proclitic(
    token: str,
) -> Optional[Tuple[List[str], str, float]]:
    """Try to split a proclitic from the front of the token.

    Handles: و+X, ف+X, ب+X, ل+X, ك+X
    Also handles: وال+X, بال+X, فال+X, لل+X, كال+X

    Parameters
    ----------
    token : str
        The token to attempt splitting.

    Returns
    -------
    tuple[list[str], str, float] or None
        (parts, "proclitic_split", confidence) or None.
    """
    if len(token) < 2:
        return None

    first_char = token[0]
    if first_char not in _SINGLE_PROCLITICS:
        return None

    remainder = token[1:]

    # Don't split if remainder is too short
    if len(remainder) < _MIN_STEM_LENGTH:
        return None

    # Check for ال after proclitic: بالكتاب → ب + الكتاب
    if remainder.startswith("ال") and len(remainder) > _MIN_ARTICLE_REMAINDER:
        return ([first_char, remainder], "proclitic_split", 0.85)

    # Check for لل pattern: لله → ل + الله (lam + al)
    # Lower confidence (0.8) because لل can also be a doubled lam root
    if first_char == "ل" and remainder.startswith("ل"):
        return ([first_char, remainder], "proclitic_split", 0.8)

    # Simple proclitic: والكتاب → و + الكتاب
    if remainder.startswith("ال"):
        return ([first_char, remainder], "proclitic_split", 0.85)

    # General proclitic: وكتب → و + كتب (if remainder ≥ 2 chars)
    if len(remainder) >= _MIN_STEM_LENGTH:
        # Lower confidence for general splits (more ambiguous)
        return ([first_char, remainder], "proclitic_split", 0.7)

    return None


def _try_enclitic(
    token: str,
) -> Optional[Tuple[List[str], str, float]]:
    """Try to split an enclitic pronoun from the end of the token.

    Handles: X+ه, X+ها, X+هم, X+هن, X+ك, X+كم, X+كن, X+نا, X+ي

    Parameters
    ----------
    token : str
        The token to attempt splitting.

    Returns
    -------
    tuple[list[str], str, float] or None
        (parts, "enclitic_split", confidence) or None.
    """
    if len(token) < 3:
        return None

    for suffix in _ENCLITICS:
        if token.endswith(suffix):
            stem = token[: -len(suffix)]
            if len(stem) >= _MIN_STEM_LENGTH:
                return ([stem, suffix], "enclitic_split", 0.75)

    return None
