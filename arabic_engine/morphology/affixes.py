"""Affix stripping — السوابق واللواحق.

Strips and classifies Arabic prefixes, suffixes, and infixes
from surface tokens for morphological analysis.
"""

from __future__ import annotations

from arabic_engine.core.enums import AffixType
from arabic_engine.core.types import AffixSet

# ── Known Arabic affix patterns ─────────────────────────────────────

# Common prefixes (definite article, conjunction, prepositions, mudāri' markers)
KNOWN_PREFIXES: tuple[str, ...] = (
    "ال",   # الـ — definite article
    "و",    # وَ — conjunction
    "ف",    # فَ — conjunction / result
    "ب",    # بِ — preposition (in/with)
    "ل",    # لِ — preposition (for/to)
    "ك",    # كَ — preposition (like)
    "س",    # سَ — future marker
    "ي",    # يَ — 3rd person masc. mudāri'
    "ت",    # تَ — 2nd person / 3rd fem. mudāri'
    "أ",    # أَ — 1st person mudāri'
    "ن",    # نَ — 1st person plural mudāri'
)

# Common suffixes (pronouns, verb endings, noun endings)
KNOWN_SUFFIXES: tuple[str, ...] = (
    "ه",    # ـه — his / him
    "ها",   # ـها — her / hers
    "هم",   # ـهم — their (masc.)
    "هن",   # ـهن — their (fem.)
    "ك",    # ـك — your (masc. sg.)
    "كم",   # ـكم — your (masc. pl.)
    "كن",   # ـكن — your (fem. pl.)
    "نا",   # ـنا — our / us
    "ي",    # ـي — my / me
    "ت",    # ـتْ — past 3rd fem. sg.
    "وا",   # ـوا — past 3rd masc. pl.
    "ون",   # ـون — masc. pl. nominative
    "ين",   # ـين — masc. pl. accusative/genitive
    "ات",   # ـات — fem. pl.
    "ان",   # ـان — dual nominative
    "ة",    # ـة — ta marbuta
    "تم",   # ـتم — 2nd person masc. pl. past
    "تن",   # ـتن — 2nd person fem. pl. past
)


def strip_affixes(token: str) -> AffixSet:
    """Strip known affixes from *token*.

    Parameters
    ----------
    token : str
        A single Arabic token (diacritics stripped preferred).

    Returns
    -------
    AffixSet
        The set of identified prefixes, suffixes, and infixes.
    """
    # Strip diacritics for matching
    stripped = _strip_diacritics(token)

    found_prefixes: list[str] = []
    found_suffixes: list[str] = []

    remaining = stripped

    # Prefix stripping (greedy: longest first)
    for prefix in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if remaining.startswith(prefix) and len(remaining) > len(prefix) + 1:
            found_prefixes.append(prefix)
            remaining = remaining[len(prefix):]
            break  # Only strip one prefix layer

    # Suffix stripping (greedy: longest first)
    for suffix in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if remaining.endswith(suffix) and len(remaining) > len(suffix) + 1:
            found_suffixes.append(suffix)
            remaining = remaining[:-len(suffix)]
            break  # Only strip one suffix layer

    return AffixSet(
        prefixes=tuple(found_prefixes),
        suffixes=tuple(found_suffixes),
        infixes=(),
        affix_type=AffixType.PREFIX if found_prefixes else AffixType.SUFFIX,
    )


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritical marks from text."""
    diacritics = frozenset(
        "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655"
    )
    return "".join(ch for ch in text if ch not in diacritics)
