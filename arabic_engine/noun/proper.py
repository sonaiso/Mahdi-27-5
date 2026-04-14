"""جهة العلم وأنواعه — Proper-noun classification facet.

Classifies proper nouns into nine sub-types: personal, place, time,
transferred, compound, nickname, patronymic, coined, borrowed.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import ProperNounType
from arabic_engine.core.types import LexicalClosure

# ── Seed databases ──────────────────────────────────────────────────

_PERSONAL_NAMES = frozenset({
    "زَيْد", "زيد", "عمرو", "عمر", "خالد", "فاطمة", "عائشة",
    "محمد", "أحمد", "علي", "حسن", "حسين", "إبراهيم", "موسى",
    "عيسى", "مريم", "هند", "سعاد", "خديجة", "نور",
})

_PLACE_NAMES = frozenset({
    "مكة", "المدينة", "دمشق", "بغداد", "القاهرة", "عمّان", "عمان",
    "الأردن", "مصر", "العراق", "الشام", "اليمن", "الحجاز",
    "نجد", "بيروت", "الرياض", "جدة", "القدس", "بعلبك",
})

_TIME_NAMES = frozenset({
    "رمضان", "شعبان", "رجب", "محرم", "صفر",
    "الجمعة", "السبت", "الأحد",
})

_NICKNAMES = frozenset({
    "الفاروق", "الصدّيق", "المأمون", "الرشيد",
    "ذو النورين", "أبو تراب", "سيف الله",
})

_PATRONYMICS = frozenset({
    "أبو بكر", "أبو هريرة", "أم كلثوم", "أم سلمة",
    "ابن عباس", "ابن مالك", "ابن سينا",
})


def resolve_proper_type(closure: LexicalClosure) -> Optional[ProperNounType]:
    """Classify the proper-noun sub-type, or return ``None`` if not proper.

    Uses seed databases and heuristic rules.
    """
    lemma = closure.lemma

    if lemma in _PERSONAL_NAMES:
        return ProperNounType.PERSONAL

    if lemma in _PLACE_NAMES:
        return ProperNounType.PLACE

    if lemma in _TIME_NAMES:
        return ProperNounType.TIME

    if lemma in _NICKNAMES:
        return ProperNounType.NICKNAME

    if lemma in _PATRONYMICS:
        return ProperNounType.PATRONYMIC

    # Heuristic: if concept has proper_noun flag but not in any database
    # check features for hints
    features = closure.features
    if features.get("proper_noun") or features.get("is_proper"):
        return ProperNounType.PERSONAL  # default for unknown proper nouns

    return None
