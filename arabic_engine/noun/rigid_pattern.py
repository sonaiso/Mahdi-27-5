"""جهة الوزن الجامد — Rigid-pattern facet.

For non-derived (جامد) nouns, determines the fixed template (قالب ثابت)
that gives the noun its phonological and morphological stability.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.types import LexicalClosure

# ── Common rigid (جامد) patterns for non-derived nouns ──────────────

_RIGID_PATTERNS: dict[str, str] = {
    "فَعْل": "فَعْل",       # e.g. بَيْت، كَلْب
    "فُعْل": "فُعْل",       # e.g. قُفْل، حُلْم
    "فِعْل": "فِعْل",       # e.g. عِلْم، حِلْم
    "فَعَل": "فَعَل",       # e.g. جَبَل، بَقَر
    "فُعَل": "فُعَل",       # e.g. صُرَد، جُعَل
    "فِعَل": "فِعَل",       # e.g. عِنَب
    "فَعِل": "فَعِل",       # e.g. كَتِف، كَبِد
    "فَعُل": "فَعُل",       # e.g. عَضُد
    "فُعُل": "فُعُل",       # e.g. عُنُق، أُذُن
    "فَعْلَة": "فَعْلَة",   # e.g. شَجَرَة، زَهْرَة
    "فِعَالَة": "فِعَالَة", # e.g. رِسَالَة
    "فُعُول": "فُعُول",     # e.g. دُرُوس
    "فِعَال": "فِعَال",     # e.g. جِبَال، رِجَال
    "أَفْعَال": "أَفْعَال", # e.g. أَقْلَام
    "فُعْلَان": "فُعْلَان", # e.g. سُلْطَان
}

# ── Derived (مشتق) patterns — these are NOT rigid ──────────────────

_DERIVED_PATTERNS = frozenset({
    "فاعل", "مفعول", "فعيل", "أفعل", "فَعّال", "مُفَعِّل",
    "مُتَفَعِّل", "مُنْفَعِل", "مُفْتَعِل", "مُسْتَفْعِل",
    "فَعول", "مِفْعَل", "مِفْعال",
})


def resolve_rigid_pattern(closure: LexicalClosure) -> Optional[str]:
    """Determine the rigid template for a non-derived noun.

    Returns the canonical rigid pattern string, or ``None`` if the
    noun is derived (مشتق) or the pattern is unrecognised.
    """
    pattern = closure.pattern

    # Derived patterns are not rigid
    if pattern in _DERIVED_PATTERNS:
        return None

    # Direct match in rigid-pattern catalogue
    if pattern in _RIGID_PATTERNS:
        return _RIGID_PATTERNS[pattern]

    # If the pattern is unknown, check if the noun has a root
    # (rigid nouns still have roots, but their pattern is fixed)
    if closure.root and pattern:
        # Return the pattern itself as the rigid template
        return pattern

    return None
