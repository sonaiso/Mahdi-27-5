"""Concept hypotheses — فرضيات مفهومية.

Generates conceptual hypothesis nodes from morphological hypotheses.
Wraps the existing :mod:`arabic_engine.semantics.ontology` to map
lemmas to concept candidates.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus, SemanticType
from arabic_engine.core.types import HypothesisNode
from arabic_engine.semantics.ontology import map_concept
from arabic_engine.morphology.root_pattern import lexical_closure


def generate(morph_hypotheses: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate concept hypotheses from morphological hypotheses.

    For each morphological hypothesis, builds a lexical closure and
    maps it to a concept via the ontology module.

    For masdar-typed hypotheses, produces a ``NOMINALIZED_EVENT``
    semantic type to distinguish them from plain events or entities.

    Parameters
    ----------
    morph_hypotheses : list[HypothesisNode]
        Morphological hypotheses (``hypothesis_type == "morphology"``
        or ``"morphology_masdar"``).

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

        # Use NOMINALIZED_EVENT for masdar hypotheses
        if morph.hypothesis_type == "morphology_masdar":
            sem_type = SemanticType.NOMINALIZED_EVENT.name
        else:
            sem_type = concept.semantic_type.name

        hypotheses.append(
            HypothesisNode(
                node_id=f"CONC_{morph.node_id}",
                hypothesis_type="concept",
                stage=ActivationStage.CONCEPT,
                source_refs=(morph.node_id,),
                payload=(
                    ("concept_id", concept.concept_id),
                    ("label", concept.label),
                    ("semantic_type", sem_type),
                    ("referentiality", "referential"),
                    ("determination", "definite" if lemma.startswith("ال") else "indefinite"),
                ),
                confidence=morph.confidence * 0.9,
                status=HypothesisStatus.ACTIVE,
            )
        )
    return hypotheses
