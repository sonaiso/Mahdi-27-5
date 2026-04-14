"""جهة المركب الاسمي — Compound-noun facet.

Detects compound nouns: annexation (عبد الله), blend (بعلبك),
and predicative (تأبط شرًا).
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import CompoundType, POS
from arabic_engine.core.types import LexicalClosure

# ── Known blend compounds (مركب مزجي) ──────────────────────────────

_BLEND_COMPOUNDS = frozenset({
    "بعلبك", "حضرموت", "سيبويه", "نفطويه", "معديكرب",
    "بورسعيد",
})

# ── Known predicative compounds (مركب إسنادي) ──────────────────────

_PREDICATIVE_COMPOUNDS = frozenset({
    "تأبط شرًا", "جاد المولى", "فتح الله", "شاب قرناها",
})

# ── Common first elements of annexation compounds ──────────────────

_ANNEXATION_FIRST = frozenset({
    "عبد", "أبو", "أم", "ابن", "بنت", "ذو", "ذات",
    "أخو", "صاحب", "رب",
})


def resolve_compound(
    tokens: List[LexicalClosure],
    index: int = 0,
) -> Optional[CompoundType]:
    """Detect if the noun at *index* begins a compound noun.

    Parameters
    ----------
    tokens : list[LexicalClosure]
        All tokens in the utterance.
    index : int
        Position of the noun under analysis.

    Returns ``None`` if the noun is not part of a compound.
    """
    if index >= len(tokens):
        return None

    current = tokens[index]
    if current.pos != POS.ISM:
        return None

    surface = current.surface
    lemma = current.lemma

    # Check blend compounds (single token)
    if lemma in _BLEND_COMPOUNDS or surface in _BLEND_COMPOUNDS:
        return CompoundType.BLEND

    # Check predicative compounds (multi-token, need sequence match)
    if index + 1 < len(tokens):
        pair = f"{surface} {tokens[index + 1].surface}"
        if pair in _PREDICATIVE_COMPOUNDS:
            return CompoundType.PREDICATIVE

    # Check annexation compounds (first element + following noun)
    if lemma in _ANNEXATION_FIRST and index + 1 < len(tokens):
        if tokens[index + 1].pos == POS.ISM:
            return CompoundType.ANNEXATION

    return None
