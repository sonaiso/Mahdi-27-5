"""Unicode atom decomposition — تفكيك اليونيكود إلى ذرات.

Breaks raw text into :class:`~arabic_engine.core.types.UnicodeAtom`
instances, classifying each code-point by its Unicode general category
and assigning the appropriate :class:`~arabic_engine.core.enums.SignalType`.
"""

from __future__ import annotations

import unicodedata
from typing import List

from arabic_engine.core.enums import SignalType
from arabic_engine.core.types import UnicodeAtom

# ── Category → SignalType mapping ───────────────────────────────────

_CATEGORY_MAP: dict[str, SignalType] = {
    "Lo": SignalType.BASE_LETTER,  # Arabic letters
    "Ll": SignalType.BASE_LETTER,
    "Lu": SignalType.BASE_LETTER,
    "Mn": SignalType.DIACRITIC,    # Non-spacing combining marks (tashkīl)
    "Mc": SignalType.DIACRITIC,    # Spacing combining marks
    "Nd": SignalType.NUMERAL,      # Decimal digits
    "Zs": SignalType.WHITESPACE,   # Space separator
    "Cc": SignalType.WHITESPACE,   # Control chars (tab, newline)
    "Po": SignalType.PUNCTUATION,  # Other punctuation
    "Ps": SignalType.PUNCTUATION,  # Open punctuation
    "Pe": SignalType.PUNCTUATION,  # Close punctuation
    "Pi": SignalType.PUNCTUATION,  # Initial quote
    "Pf": SignalType.PUNCTUATION,  # Final quote
    "Pd": SignalType.PUNCTUATION,  # Dash punctuation
}


def _classify(ch: str) -> SignalType:
    """Classify a single character into a SignalType."""
    cat = unicodedata.category(ch)
    return _CATEGORY_MAP.get(cat, SignalType.UNKNOWN)


def decompose(text: str) -> List[UnicodeAtom]:
    """Decompose *text* into a list of :class:`UnicodeAtom` instances.

    Each character in the input becomes a single atom with its Unicode
    general category, combining class, and position index.

    Parameters
    ----------
    text : str
        Raw input text (may contain Arabic, tashkīl, whitespace, etc.).

    Returns
    -------
    list[UnicodeAtom]
        One atom per character, in order.
    """
    atoms: List[UnicodeAtom] = []
    for idx, ch in enumerate(text):
        cp = ord(ch)
        atoms.append(
            UnicodeAtom(
                atom_id=f"A_{idx}",
                char=ch,
                codepoint=cp,
                unicode_category=unicodedata.category(ch),
                combining_class=unicodedata.combining(ch),
                position_index=idx,
                signal_type=_classify(ch),
            )
        )
    return atoms
