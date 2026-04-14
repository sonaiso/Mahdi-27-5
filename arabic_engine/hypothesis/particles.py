"""Particle hypotheses — فرضيات حرفية.

Generates particle hypothesis nodes from concept hypotheses.
For each concept whose label is a known particle, produces a
hypothesis with the particle's type, relation, direction, scope,
effect, and fractal score.

This stage sits between CONCEPT and AXIS in the fractal kernel
pipeline, establishing particle identity **before** syntactic
composition.
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode
from arabic_engine.particle.registry import lookup
from arabic_engine.particle.validation import compute_fractal_score


def generate(concept_hypotheses: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate particle hypotheses from concept hypotheses.

    For each concept whose label is a known Arabic particle, creates
    a particle hypothesis carrying full fractal identity.  Non-particle
    concepts are silently skipped.

    Parameters
    ----------
    concept_hypotheses : list[HypothesisNode]
        Concept hypotheses (``hypothesis_type == "concept"``).

    Returns
    -------
    list[HypothesisNode]
        Particle hypotheses, zero or one per concept.
    """
    hypotheses: List[HypothesisNode] = []

    for concept in concept_hypotheses:
        label = str(concept.get("label", ""))
        stype = str(concept.get("semantic_type", ""))

        record = lookup(label)
        if record is None:
            continue

        fs = compute_fractal_score(record)

        hypotheses.append(
            HypothesisNode(
                node_id=f"PART_{concept.node_id}",
                hypothesis_type="particle",
                stage=ActivationStage.PARTICLE,
                source_refs=(concept.node_id,),
                payload=(
                    ("particle_form", record.form),
                    ("particle_type", record.particle_type.name),
                    ("relation_type", record.relation_type.name),
                    ("direction", record.direction),
                    ("scope", record.scope),
                    ("effect", record.effect),
                    ("fractal_score", fs.fractal_score),
                ),
                confidence=concept.confidence * 0.95,
                status=HypothesisStatus.ACTIVE,
            )
        )

    return hypotheses
