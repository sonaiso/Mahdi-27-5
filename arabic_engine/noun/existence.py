"""جهة الموجود — Existence facet.

The noun is the primary vessel for establishing an existent:
designation + reference + counting + differentiation.
"""

from __future__ import annotations

from arabic_engine.core.enums import POS
from arabic_engine.core.types import LexicalClosure


def resolve_existence(closure: LexicalClosure) -> str:
    """Determine the existential status of the noun.

    Returns one of: ``"existent"``, ``"abstract"``, ``"unresolved"``.

    A noun establishes an existent when it can be designated, referred to,
    counted, and differentiated from other existents.
    """
    if closure.pos != POS.ISM:
        return "unresolved"

    # A noun with a non-empty lemma and root is a fully established existent
    if closure.lemma and closure.root:
        return "existent"

    # A noun with a lemma but no root is an abstract concept or borrowed noun
    if closure.lemma:
        return "abstract"

    return "unresolved"
