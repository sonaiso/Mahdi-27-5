"""Syllable patterns — أنماط المقاطع العربية.

Defines the canonical syllable patterns in Arabic phonology and
their phonological properties (weight, mora count, distribution).
"""

from __future__ import annotations

from arabic_engine.core.enums import SyllableType, SyllableWeight

# ── Pattern definitions ─────────────────────────────────────────────

PATTERN_REGISTRY: dict[SyllableType, dict[str, object]] = {
    SyllableType.CV: {
        "label": "مقطع مفتوح قصير",
        "structure": "C + short V",
        "weight": SyllableWeight.LIGHT,
        "morae": 1,
        "example": "كَـ (ka)",
        "position": "any",
    },
    SyllableType.CVV: {
        "label": "مقطع مفتوح طويل",
        "structure": "C + long V",
        "weight": SyllableWeight.HEAVY,
        "morae": 2,
        "example": "كا (kaa)",
        "position": "any",
    },
    SyllableType.CVC: {
        "label": "مقطع مغلق قصير",
        "structure": "C + short V + C",
        "weight": SyllableWeight.HEAVY,
        "morae": 2,
        "example": "كَتْ (kat)",
        "position": "any",
    },
    SyllableType.CVVC: {
        "label": "مقطع مغلق طويل",
        "structure": "C + long V + C",
        "weight": SyllableWeight.SUPER,
        "morae": 3,
        "example": "كاتْ (kaat)",
        "position": "final",
    },
    SyllableType.CVCC: {
        "label": "مقطع مغلق مشدد",
        "structure": "C + short V + CC",
        "weight": SyllableWeight.SUPER,
        "morae": 3,
        "example": "كَتْبْ (katb)",
        "position": "final",
    },
}


def get_pattern_info(stype: SyllableType) -> dict[str, object]:
    """Return the pattern metadata for a syllable type."""
    return PATTERN_REGISTRY.get(stype, {})


def get_weight(stype: SyllableType) -> SyllableWeight:
    """Return the phonological weight for a syllable type."""
    info = PATTERN_REGISTRY.get(stype)
    if info:
        return info["weight"]  # type: ignore[return-value]
    return SyllableWeight.LIGHT
