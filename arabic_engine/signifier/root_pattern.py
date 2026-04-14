"""Root and pattern extraction (التعريف 3 — الجذر والوزن).

Provides a rule-based extractor for tri-literal roots and their
morphological patterns.  A production system would replace the
hard-coded dictionary with a full morphological database.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from arabic_engine.core.enums import POS
from arabic_engine.core.types import LexicalClosure, RootPattern

# ── Mini lexicon (enough for the demo sentence) ─────────────────────

_LEXICON: Dict[str, dict] = {
    "كَتَبَ": {
        "lemma": "كَتَبَ",
        "root": ("ك", "ت", "ب"),
        "pattern": "فَعَلَ",
        "pos": POS.FI3L,
        "root_id": 1,
        "pattern_id": 1,
        "lemma_id": 1,
    },
    "كتب": {
        "lemma": "كَتَبَ",
        "root": ("ك", "ت", "ب"),
        "pattern": "فَعَلَ",
        "pos": POS.FI3L,
        "root_id": 1,
        "pattern_id": 1,
        "lemma_id": 1,
    },
    "زَيْدٌ": {
        "lemma": "زَيْد",
        "root": ("ز", "ي", "د"),
        "pattern": "فَعْل",
        "pos": POS.ISM,
        "root_id": 2,
        "pattern_id": 2,
        "lemma_id": 2,
    },
    "زيد": {
        "lemma": "زَيْد",
        "root": ("ز", "ي", "د"),
        "pattern": "فَعْل",
        "pos": POS.ISM,
        "root_id": 2,
        "pattern_id": 2,
        "lemma_id": 2,
    },
    "الرِّسَالَةَ": {
        "lemma": "رِسَالَة",
        "root": ("ر", "س", "ل"),
        "pattern": "فِعَالَة",
        "pos": POS.ISM,
        "root_id": 3,
        "pattern_id": 3,
        "lemma_id": 3,
    },
    "الرسالة": {
        "lemma": "رِسَالَة",
        "root": ("ر", "س", "ل"),
        "pattern": "فِعَالَة",
        "pos": POS.ISM,
        "root_id": 3,
        "pattern_id": 3,
        "lemma_id": 3,
    },
    # ── Time adverbs (v2) ───────────────────────────────────────
    "أَمْسَ": {
        "lemma": "أَمْس",
        "root": ("أ", "م", "س"),
        "pattern": "فَعْل",
        "pos": POS.ZARF,
        "root_id": 4,
        "pattern_id": 2,
        "lemma_id": 4,
    },
    "أَمْسِ": {
        "lemma": "أَمْس",
        "root": ("أ", "م", "س"),
        "pattern": "فَعْل",
        "pos": POS.ZARF,
        "root_id": 4,
        "pattern_id": 2,
        "lemma_id": 4,
    },
    "أمس": {
        "lemma": "أَمْس",
        "root": ("أ", "م", "س"),
        "pattern": "فَعْل",
        "pos": POS.ZARF,
        "root_id": 4,
        "pattern_id": 2,
        "lemma_id": 4,
    },
    "غَدًا": {
        "lemma": "غَد",
        "root": ("غ", "د", "و"),
        "pattern": "فَعْل",
        "pos": POS.ZARF,
        "root_id": 5,
        "pattern_id": 2,
        "lemma_id": 5,
    },
    "غدا": {
        "lemma": "غَد",
        "root": ("غ", "د", "و"),
        "pattern": "فَعْل",
        "pos": POS.ZARF,
        "root_id": 5,
        "pattern_id": 2,
        "lemma_id": 5,
    },
}

# Auto-generate pos_id from enum value
for _entry in _LEXICON.values():
    _entry.setdefault("pos_id", _entry["pos"].value)


def extract_root_pattern(token: str) -> Optional[RootPattern]:
    """Try to extract root and pattern from *token* via the mini-lexicon.

    Args:
        token: A single Arabic token string (with or without tashkīl).

    Returns:
        A :class:`~arabic_engine.core.types.RootPattern` when the token
        is found in the lexicon, or ``None`` if it is unknown.
    """
    entry = _LEXICON.get(token)
    if entry is None:
        return None
    return RootPattern(
        root=entry["root"],
        pattern=entry["pattern"],
        root_id=entry["root_id"],
        pattern_id=entry["pattern_id"],
    )


def lexical_closure(token: str) -> LexicalClosure:
    """Build a full :class:`~arabic_engine.core.types.LexicalClosure` for *token* (التعريف 4).

    Looks up *token* in the internal lexicon.  Unknown tokens receive a
    fallback closure with ``POS.UNKNOWN`` and empty root/pattern fields.

    Args:
        token: A single Arabic token string.

    Returns:
        A fully populated :class:`~arabic_engine.core.types.LexicalClosure`
        when the token is in the lexicon, or a minimal fallback closure
        otherwise.
    """
    entry = _LEXICON.get(token)
    if entry is not None:
        return LexicalClosure(
            surface=token,
            lemma=entry["lemma"],
            root=entry["root"],
            pattern=entry["pattern"],
            pos=entry["pos"],
            lemma_id=entry["lemma_id"],
            root_id=entry["root_id"],
            pattern_id=entry["pattern_id"],
            pos_id=entry["pos_id"],
        )
    # Fallback for unknown tokens
    return LexicalClosure(
        surface=token,
        lemma=token,
        root=(),
        pattern="",
        pos=POS.UNKNOWN,
    )


def batch_closure(tokens: List[str]) -> List[LexicalClosure]:
    """Return lexical closures for every token in *tokens*.

    Convenience wrapper around :func:`lexical_closure` for a list of
    tokens (as produced by
    :func:`~arabic_engine.signifier.unicode_norm.tokenize`).

    Args:
        tokens: List of Arabic token strings.

    Returns:
        A list of :class:`~arabic_engine.core.types.LexicalClosure`
        objects, one per input token, preserving order.
    """
    return [lexical_closure(t) for t in tokens]
