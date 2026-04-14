"""Concept hypotheses — فرضيات مفهومية.

Generates conceptual hypothesis nodes from morphological hypotheses.
Wraps the existing :mod:`arabic_engine.signified.ontology` to map
lemmas to concept candidates.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode
from arabic_engine.signified.ontology import map_concept
from arabic_engine.signifier.root_pattern import lexical_closure


def generate(morph_hypotheses: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate concept hypotheses from morphological hypotheses.

    For each morphological hypothesis, builds a lexical closure and
    maps it to a concept via the ontology module.

    Parameters
    ----------
    morph_hypotheses : list[HypothesisNode]
        Morphological hypotheses (``hypothesis_type == "morphology"``).

    Returns
    -------
    list[HypothesisNode]
        Concept hypotheses, one per morphological hypothesis.
    """
    hypotheses: List[HypothesisNode] = []
    for morph in morph_hypotheses:
        lemma = str(morph.get("lemma", ""))
        closure = lexical_closure(lemma)
        concept = map_concept(closure)

        hypotheses.append(
            HypothesisNode(
                node_id=f"CONC_{morph.node_id}",
                hypothesis_type="concept",
                stage=ActivationStage.CONCEPT,
                source_refs=(morph.node_id,),
                payload=(
                    ("concept_id", concept.concept_id),
                    ("label", concept.label),
                    ("semantic_type", concept.semantic_type.name),
                    ("referentiality", "referential"),
                    ("determination", "definite" if lemma.startswith("ال") else "indefinite"),
                ),
                confidence=morph.confidence * 0.9,
                status=HypothesisStatus.ACTIVE,
            )
        )
    return hypotheses
