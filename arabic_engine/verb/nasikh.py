"""Nāsikh verb system — نظام الأفعال الناسخة.

Formalises the three categories of copular / modal verbs as
*epistemic-possibility gates* rather than grammatical anomalies:

1. **كان وأخواتها** — temporal / predicative binding
2. **كاد وأخواتها** — approximation / inception / hope
3. **ظنّ وأخواتها** — belief / epistemic judgment
"""

from __future__ import annotations

from typing import Dict, Optional

from arabic_engine.core.enums import NasikhCategory
from arabic_engine.core.types import NasikhProfile

# ── كان وأخواتها — temporal/predicative binding ─────────────────────

_KANA: Dict[str, NasikhProfile] = {
    v: NasikhProfile(
        verb_label=v,
        category=NasikhCategory.KANA_WA_AKHAWAT,
        epistemic_function="ربط زمني حكمي",
        argument_structure="اسم + خبر",
    )
    for v in (
        "كان", "أصبح", "أمسى", "أضحى", "ظل", "بات",
        "صار", "ليس", "ما_زال", "ما_فتئ", "ما_برح",
        "ما_انفك", "ما_دام",
    )
}

# ── كاد وأخواتها — approximation / inception ───────────────────────

_KADA: Dict[str, NasikhProfile] = {
    v: NasikhProfile(
        verb_label=v,
        category=NasikhCategory.KADA_WA_AKHAWAT,
        epistemic_function="مقاربة أو شروع أو رجاء",
        argument_structure="اسم + خبر (جملة فعلية)",
    )
    for v in (
        "كاد", "أوشك", "عسى", "شرع", "بدأ", "أخذ",
        "جعل", "طفق", "أنشأ", "هبّ",
    )
}

# ── ظنّ وأخواتها — belief / epistemic judgment ─────────────────────

_ZANNA: Dict[str, NasikhProfile] = {
    v: NasikhProfile(
        verb_label=v,
        category=NasikhCategory.ZANNA_WA_AKHAWAT,
        epistemic_function="اعتقاد أو تقدير أو تحويل",
        argument_structure="مفعول أول + مفعول ثانٍ",
    )
    for v in (
        "ظنّ", "حسب", "خال", "زعم", "رأى", "علم",
        "وجد", "درى", "تعلّم", "اتّخذ", "ردّ", "ترك", "صيّر",
    )
}

# Combined lookup
_ALL_NASIKH: Dict[str, NasikhProfile] = {**_KANA, **_KADA, **_ZANNA}


# ── Public API ──────────────────────────────────────────────────────


def classify(verb_label: str) -> Optional[NasikhProfile]:
    """Return the nāsikh profile for *verb_label*, or ``None``.

    The lookup is exact-match on the lemma.
    """
    return _ALL_NASIKH.get(verb_label)


def is_nasikh(verb_label: str) -> bool:
    """Check whether *verb_label* belongs to any nāsikh category."""
    return verb_label in _ALL_NASIKH


def all_kana() -> list[NasikhProfile]:
    """Return all members of كان وأخواتها."""
    return list(_KANA.values())


def all_kada() -> list[NasikhProfile]:
    """Return all members of كاد وأخواتها."""
    return list(_KADA.values())


def all_zanna() -> list[NasikhProfile]:
    """Return all members of ظنّ وأخواتها."""
    return list(_ZANNA.values())
