"""جهة المقترض — Borrowed-noun facet.

Detects loanword nouns and, where possible, identifies the source
language.  A borrowed noun enters the Arabic nominal system when its
usage stabilises and it can be designated, referred to, and classified.
"""

from __future__ import annotations

from typing import Optional, Tuple

from arabic_engine.core.types import LexicalClosure

# ── Known borrowed nouns: lemma → source language ───────────────────

_BORROWED_NOUNS: dict[str, str] = {
    # Modern technology
    "تلفون": "Greek/English",
    "تلفزيون": "English",
    "كمبيوتر": "English",
    "إنترنت": "English",
    "راديو": "Italian/English",
    "فيديو": "English",
    "موبايل": "English",
    "تكنولوجيا": "Greek",
    "ديمقراطية": "Greek",
    "فلسفة": "Greek",
    "برلمان": "English/French",
    # Historical
    "إستبرق": "Persian",
    "فردوس": "Persian",
    "دينار": "Latin/Greek",
    "درهم": "Greek",
    "فرسخ": "Persian",
    "بستان": "Persian",
    "ياقوت": "Persian",
    "زبرجد": "Persian",
    "سندس": "Persian",
    # Qur'anic
    "مشكاة": "Ethiopic",
    "سجّيل": "Persian",
    "قسطاس": "Greek",
    "صراط": "Latin",
}


def resolve_borrowed(
    closure: LexicalClosure,
) -> Tuple[bool, Optional[str]]:
    """Detect whether the noun is a borrowed word.

    Returns ``(is_borrowed, source_language)`` where
    *source_language* is ``None`` if not borrowed or unknown.
    """
    lemma = closure.lemma
    bare = lemma.removeprefix("ال")

    # Direct lookup
    if bare in _BORROWED_NOUNS:
        return True, _BORROWED_NOUNS[bare]
    if lemma in _BORROWED_NOUNS:
        return True, _BORROWED_NOUNS[lemma]

    # Heuristic: no Arabic root (empty root tuple) may indicate borrowing,
    # but only if the noun is not already identified as a compound or blend.
    # Compound nouns and other native Arabic constructions may also lack roots.
    if not closure.root and closure.lemma and not closure.features.get("is_compound"):
        return True, None

    return False, None
