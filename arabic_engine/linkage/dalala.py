"""Dalāla (signification) validation (التعريف 6).

D : T × C → {0,1} × [0,1]

Validates the link between a signifier (lexical closure) and its
signified (concept), producing an acceptance flag and a confidence
score.  The three core dalāla modes from the manuscript are:

  • مطابقة (mutābaqa) — exact denotation
  • تضمن  (taḍammun) — part of the meaning
  • التزام (iltizām) — necessary concomitant

Additional structural links (إسناد، تقييد، إضافة، إحالة) connect
concepts within a proposition.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import POS, DalalaType
from arabic_engine.core.types import Concept, DalalaLink, LexicalClosure


def validate_link(
    closure: LexicalClosure,
    concept: Concept,
) -> DalalaLink:
    """Compute the dalāla link between *closure* and *concept*.

    Applies the three core signification modes in priority order:

    1. **Mutābaqa** (مطابقة) — exact denotation: lemma equals concept
       label.  Confidence = 1.0.
    2. **Taḍammun** (تضمن) — partial inclusion: a root radical appears
       in the concept label.  Confidence = 0.75.
    3. **Iltizām** (التزام) — necessary concomitant (fallback).
       Confidence = 0.5.

    When a :class:`~arabic_engine.core.types.NounNode` is attached,
    the confidence is boosted by the noun's own confidence score.

    Args:
        closure: Lexical closure representing the signifier.
        concept: Concept node representing the signified.

    Returns:
        A :class:`~arabic_engine.core.types.DalalaLink` with
        ``accepted=True`` and the appropriate type and confidence.
    """
    noun_boost = 1.0
    if closure.noun_node is not None:
        noun_boost = closure.noun_node.confidence

    # Primary denotation — mutābaqa
    if closure.lemma == concept.label:
        return DalalaLink(
            source_lemma=closure.lemma,
            target_concept_id=concept.concept_id,
            dalala_type=DalalaType.MUTABAQA,
            accepted=True,
            confidence=min(1.0, 1.0 * noun_boost),
        )

    # If root overlaps (shared semantic field) → taḍammun
    if closure.root and any(
        r in concept.label for r in closure.root
    ):
        return DalalaLink(
            source_lemma=closure.lemma,
            target_concept_id=concept.concept_id,
            dalala_type=DalalaType.TADAMMUN,
            accepted=True,
            confidence=min(1.0, 0.75 * noun_boost),
        )

    # Fallback — weak iltizām
    return DalalaLink(
        source_lemma=closure.lemma,
        target_concept_id=concept.concept_id,
        dalala_type=DalalaType.ILTIZAM,
        accepted=True,
        confidence=min(1.0, 0.5 * noun_boost),
    )


def build_isnad_links(
    closures: List[LexicalClosure],
    concepts: List[Concept],
) -> List[DalalaLink]:
    """Build predication (إسناد) links for a verb-subject-object structure.

    Assumes the first verb found is the predicate and that noun arguments
    following it are linked to the verb concept via ``ISNAD`` (first noun)
    or ``TAQYID`` (subsequent nouns).

    Args:
        closures: Lexical closures for all tokens in the sentence.
        concepts: Corresponding concept nodes (parallel list to *closures*).

    Returns:
        A list of :class:`~arabic_engine.core.types.DalalaLink` objects
        representing predication links.  May be empty if no verb is found.
    """
    links: List[DalalaLink] = []
    verb_concept: Concept | None = None

    for cl, co in zip(closures, concepts):
        if cl.pos == POS.FI3L:
            verb_concept = co
            continue
        if verb_concept is not None and cl.pos == POS.ISM:
            links.append(DalalaLink(
                source_lemma=cl.lemma,
                target_concept_id=verb_concept.concept_id,
                dalala_type=DalalaType.ISNAD,
                accepted=True,
                confidence=0.95,
            ))

    return links


def full_validation(
    closures: List[LexicalClosure],
    concepts: List[Concept],
) -> List[DalalaLink]:
    """Run mutābaqa validation and isnād linking for a token list.

    Combines per-token :func:`validate_link` results with the structural
    isnād links from :func:`build_isnad_links`.

    Args:
        closures: Lexical closures for all tokens in the sentence.
        concepts: Corresponding concept nodes (parallel list to *closures*).

    Returns:
        A combined list of all
        :class:`~arabic_engine.core.types.DalalaLink` objects — first the
        per-token mutābaqa/taḍammun/iltizām links, then the isnād links.
    """
    links = [validate_link(c, o) for c, o in zip(closures, concepts)]
    links.extend(build_isnad_links(closures, concepts))
    return links
