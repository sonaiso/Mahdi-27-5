"""Time and space tagging for propositions (v2).

Enriches a :class:`Proposition` with temporal and spatial anchoring
derived from verb morphology, adverbs, and explicit place names.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from arabic_engine.core.enums import POS, SpaceRef, TimeRef
from arabic_engine.core.types import (
    LexicalClosure,
    Proposition,
    TimeSpaceTag,
)

# ── Temporal patterns ───────────────────────────────────────────────

_PAST_PATTERNS = {"فَعَلَ", "فَعِلَ", "فَعُلَ", "اِفْتَعَلَ", "تَفَعَّلَ"}
_PRESENT_PATTERNS = {"يَفْعَلُ", "يَفْعِلُ", "يَفْعُلُ"}
_FUTURE_MARKERS = {"سَ", "سَوْفَ"}

# ── Masdar patterns (carry temporal/spatial potential, not assignment)
_MASDAR_POS = {POS.MASDAR_SARIH, POS.MASDAR_MUAWWAL}

# ── Temporal adverbs (v2) ───────────────────────────────────────────

_TEMPORAL_ADVERBS = {
    "أَمْس": TimeRef.PAST,
    "أَمْسِ": TimeRef.PAST,
    "أمس": TimeRef.PAST,
    "الْيَوْمَ": TimeRef.PRESENT,
    "اليوم": TimeRef.PRESENT,
    "غَدًا": TimeRef.FUTURE,
    "غدا": TimeRef.FUTURE,
    "غَد": TimeRef.FUTURE,
}

# ── Spatial markers (demo set) ──────────────────────────────────────

_SPATIAL_NOUNS = {
    "هُنَا": SpaceRef.HERE,
    "هُنَاكَ": SpaceRef.THERE,
    "هنا": SpaceRef.HERE,
    "هناك": SpaceRef.THERE,
}


def detect_time(closures: List[LexicalClosure]) -> Tuple[TimeRef, str]:
    """Infer temporal reference from verb patterns, particles, and adverbs.

    Priority order:

    1. **Temporal adverbs** (``POS.ZARF``) — most explicit signal.
    2. **Verb morphological pattern** — past/present/future from the
       pattern string.
    3. **Future particles** (``سَ`` / ``سَوْفَ``) on the surface form.

    Args:
        closures: Lexical closures for all sentence tokens.

    Returns:
        A ``(TimeRef, detail)`` tuple where *detail* is the lemma or
        surface form that triggered the detection (empty string if
        ``UNSPECIFIED``).
    """
    time_detail = ""

    # Check adverbs first — they give the most explicit signal
    for cl in closures:
        if cl.pos == POS.ZARF:
            ref = _TEMPORAL_ADVERBS.get(cl.surface) or _TEMPORAL_ADVERBS.get(cl.lemma)
            if ref is not None:
                return ref, cl.lemma

    # Fall back to verb morphology
    for cl in closures:
        if cl.pos == POS.FI3L:
            if cl.pattern in _PAST_PATTERNS:
                return TimeRef.PAST, cl.surface
            if cl.pattern in _PRESENT_PATTERNS:
                return TimeRef.PRESENT, cl.surface
        if cl.surface in _FUTURE_MARKERS:
            return TimeRef.FUTURE, cl.surface

    # Check for masdar — carries temporal potential, not assignment
    for cl in closures:
        if cl.pos in _MASDAR_POS:
            return TimeRef.MASDAR_POTENTIAL, cl.lemma

    return TimeRef.UNSPECIFIED, time_detail


def detect_space(closures: List[LexicalClosure]) -> Tuple[SpaceRef, str]:
    """Infer spatial reference from adverbs and place nouns.

    Currently recognises a small set of spatial adverbs (هنا / هناك).

    Args:
        closures: Lexical closures for all sentence tokens.

    Returns:
        A ``(SpaceRef, detail)`` tuple.  *detail* is the lemma of the
        spatial word; empty string when no spatial anchor is found.
    """
    for cl in closures:
        ref = _SPATIAL_NOUNS.get(cl.surface) or _SPATIAL_NOUNS.get(cl.lemma)
        if ref is not None:
            return ref, cl.lemma

    # Check for masdar — carries spatial potential
    for cl in closures:
        if cl.pos in _MASDAR_POS:
            return SpaceRef.MASDAR_POTENTIAL, cl.lemma

    return SpaceRef.UNSPECIFIED, ""


def tag(
    closures: List[LexicalClosure],
    proposition: Optional[Proposition] = None,
) -> TimeSpaceTag:
    """Return a :class:`~arabic_engine.core.types.TimeSpaceTag` for the given closures.

    Calls :func:`detect_time` and :func:`detect_space` internally and
    packages the results into a :class:`~arabic_engine.core.types.TimeSpaceTag`.

    If a *proposition* is supplied its ``time`` and ``space`` fields are
    **updated in-place** as a side effect — this keeps the
    :class:`~arabic_engine.core.types.Proposition` and the tag in sync.

    Args:
        closures: Lexical closures for the sentence tokens.
        proposition: Optional mutable proposition to update with the
            detected temporal/spatial anchors.

    Returns:
        A :class:`~arabic_engine.core.types.TimeSpaceTag` with
        ``time_ref``, ``space_ref``, ``time_detail``, and
        ``space_detail`` populated.
    """
    t, t_detail = detect_time(closures)
    s, s_detail = detect_space(closures)

    ts_tag = TimeSpaceTag(
        time_ref=t,
        space_ref=s,
        time_detail=t_detail,
        space_detail=s_detail,
    )

    if proposition is not None:
        # Propositions are mutable dataclasses
        proposition.time = t
        proposition.space = s

    return ts_tag
