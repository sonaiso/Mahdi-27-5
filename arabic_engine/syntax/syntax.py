"""Syntactic analysis — i'rāb and dependency relations (v2).

Maps each token to its grammatical case (رفع / نصب / جر / جزم) and
syntactic role (فاعل / مفعول به / مبتدأ / خبر / …), producing a
dependency-style tree anchored to the main verb or predicate.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import POS, IrabCase, IrabRole
from arabic_engine.core.types import LexicalClosure, SyntaxNode


def _assign_case_and_role(
    closure: LexicalClosure,
    position: int,
    verb_seen: bool,
    subject_seen: bool,
) -> SyntaxNode:
    """Heuristic i'rāb assignment for a single token.

    Applies the following priority rules:

    * **FI3L** (verb) → case=SUKUN (مبني), role=FI3L.
    * **ZARF** (adverb) → case=NASB (ظرف منصوب), role=ZARF.
    * **ISM**, first after verb → case=RAF3 (مرفوع), role=FA3IL.
    * **ISM**, second after verb → case=NASB (منصوب), role=MAF3UL_BIH.
    * **ISM**, no verb yet → case=RAF3, role=MUBTADA (nominal sentence).
    * Fallback → case=UNKNOWN, role=UNKNOWN.

    Args:
        closure: Lexical closure for the token.
        position: Zero-based position of the token in the sentence.
        verb_seen: Whether a verb has already been encountered.
        subject_seen: Whether a subject (فاعل) has already been assigned.

    Returns:
        A :class:`~arabic_engine.core.types.SyntaxNode` with case and
        role populated.
    """
    if closure.pos == POS.FI3L:
        return SyntaxNode(
            token=closure.surface,
            lemma=closure.lemma,
            pos=closure.pos,
            case=IrabCase.SUKUN,   # verbs are مبني in the past tense
            role=IrabRole.FI3L,
        )

    if closure.pos == POS.ZARF:
        # Adverbs of time/place → ظرف (منصوب)
        return SyntaxNode(
            token=closure.surface,
            lemma=closure.lemma,
            pos=closure.pos,
            case=IrabCase.NASB,
            role=IrabRole.ZARF,
        )

    if closure.pos == POS.ISM:
        if verb_seen and not subject_seen:
            # First noun after verb → فاعل (مرفوع)
            return SyntaxNode(
                token=closure.surface,
                lemma=closure.lemma,
                pos=closure.pos,
                case=IrabCase.RAF3,
                role=IrabRole.FA3IL,
            )
        if verb_seen and subject_seen:
            # Second noun after verb → مفعول به (منصوب)
            return SyntaxNode(
                token=closure.surface,
                lemma=closure.lemma,
                pos=closure.pos,
                case=IrabCase.NASB,
                role=IrabRole.MAF3UL_BIH,
            )
        # Nominal sentence — مبتدأ
        return SyntaxNode(
            token=closure.surface,
            lemma=closure.lemma,
            pos=closure.pos,
            case=IrabCase.RAF3,
            role=IrabRole.MUBTADA,
        )

    # Fallback
    return SyntaxNode(
        token=closure.surface,
        lemma=closure.lemma,
        pos=closure.pos,
        case=IrabCase.UNKNOWN,
        role=IrabRole.UNKNOWN,
    )


def analyse(closures: List[LexicalClosure]) -> List[SyntaxNode]:
    """Perform syntactic analysis on a list of lexical closures.

    Produces a flat dependency list where all nouns and adverbs depend
    on the governing verb.  Case and role are assigned by
    :func:`_assign_case_and_role`.

    Args:
        closures: Lexical closures for all tokens in the sentence, as
            produced by
            :func:`~arabic_engine.signifier.root_pattern.batch_closure`.

    Returns:
        A list of :class:`~arabic_engine.core.types.SyntaxNode` objects
        in the same order as *closures*, with ``case``, ``role``,
        ``governor``, and ``dependents`` fields populated.
    """
    nodes: List[SyntaxNode] = []
    verb_seen = False
    subject_seen = False
    verb_node: SyntaxNode | None = None

    for i, cl in enumerate(closures):
        node = _assign_case_and_role(cl, i, verb_seen, subject_seen)

        if cl.pos == POS.FI3L:
            verb_seen = True
            verb_node = node
        elif cl.pos == POS.ZARF:
            # Adverbs of time/place depend on the verb
            if verb_node is not None:
                node.governor = verb_node.lemma
                verb_node.dependents.append(node.lemma)
        elif cl.pos == POS.ISM and verb_seen and not subject_seen:
            subject_seen = True
            if verb_node is not None:
                node.governor = verb_node.lemma
                verb_node.dependents.append(node.lemma)
        elif cl.pos == POS.ISM and verb_seen and subject_seen:
            if verb_node is not None:
                node.governor = verb_node.lemma
                verb_node.dependents.append(node.lemma)

        nodes.append(node)

    return nodes
