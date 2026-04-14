"""Unicode normalisation for Arabic text (التعريف 2).

N : ℕ* → ℕ*

Removes tatweel, normalises whitespace, and optionally strips or
preserves tashkīl (diacritics) according to a policy flag.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List

from arabic_engine.core.types import Grapheme

# Arabic Unicode ranges
_TATWEEL = "\u0640"
_COMBINING_RANGE = range(0x064B, 0x0670)  # Fathatan … Superscript Alef
_HAMZA_MAP = {
    "\u0622": "\u0627",  # آ → ا
    "\u0623": "\u0627",  # أ → ا
    "\u0625": "\u0627",  # إ → ا
}

_MULTI_SPACE = re.compile(r"\s+")


def normalize(text: str, *, strip_tashkil: bool = False) -> str:
    """Return a normalised copy of *text*.

    Performs the following transformations in order:

    1. NFC Unicode normalisation.
    2. Tatweel (kashida, U+0640) removal.
    3. Optionally strips all combining diacritics (tashkīl) in the
       range U+064B–U+0670.
    4. Collapses multiple whitespace characters to a single space and
       strips leading/trailing whitespace.

    Args:
        text: Raw Arabic input string (may contain tashkīl).
        strip_tashkil: When ``True``, remove all combining diacritics
            from the output.  Defaults to ``False``.

    Returns:
        The normalised string.

    Example::

        >>> normalize("كَتَبَـ  زَيْدٌ")
        'كَتَبَ زَيْدٌ'
        >>> normalize("كَتَبَ", strip_tashkil=True)
        'كتب'
    """
    text = unicodedata.normalize("NFC", text)
    text = text.replace(_TATWEEL, "")
    if strip_tashkil:
        text = "".join(
            ch for ch in text if ord(ch) not in _COMBINING_RANGE
        )
    text = _MULTI_SPACE.sub(" ", text).strip()
    return text


def normalize_hamza(text: str) -> str:
    """Unify hamza-bearing alefs to bare alef (ا).

    Replaces the following characters:

    * آ (U+0622) → ا
    * أ (U+0623) → ا
    * إ (U+0625) → ا

    Args:
        text: Input Arabic string.

    Returns:
        The string with all hamza-bearing alef variants replaced by
        a bare alef (U+0627).
    """
    for src, dst in _HAMZA_MAP.items():
        text = text.replace(src, dst)
    return text


def tokenize(text: str) -> List[str]:
    """Split normalised Arabic text into whitespace-delimited tokens.

    The input is first passed through :func:`normalize` (with default
    settings), then split on whitespace.

    Args:
        text: Raw or partially normalised Arabic input.

    Returns:
        A list of token strings.  Never returns ``None``; returns an
        empty list for blank input.

    Example::

        >>> tokenize("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        ['كَتَبَ', 'زَيْدٌ', 'الرِّسَالَةَ']
    """
    return normalize(text).split()


def to_graphemes(token: str) -> List[Grapheme]:
    """Decompose a token into a sequence of :class:`~arabic_engine.core.types.Grapheme` clusters.

    A grapheme cluster consists of a base character code-point plus
    zero or more combining mark code-points (tashkīl) that follow it.
    Unicode combining characters (general category ``M*``) are attached
    to the preceding base character.

    Args:
        token: A single Arabic token string (no whitespace).

    Returns:
        An ordered list of :class:`~arabic_engine.core.types.Grapheme`
        objects, one per base character in *token*.  Returns an empty
        list for an empty string.

    Example::

        >>> [g.char for g in to_graphemes("كَ")]
        ['كَ']
    """
    clusters: List[Grapheme] = []
    base: int | None = None
    marks: list[int] = []
    for ch in token:
        cp = ord(ch)
        if unicodedata.category(ch).startswith("M"):
            # combining mark — attach to current base
            marks.append(cp)
        else:
            if base is not None:
                clusters.append(Grapheme(base=base, marks=tuple(marks)))
            base = cp
            marks = []
    if base is not None:
        clusters.append(Grapheme(base=base, marks=tuple(marks)))
    return clusters
