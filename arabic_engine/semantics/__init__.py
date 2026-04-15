"""Semantics layer — المدلول والرابطة: ontology, dalāla, semantic roles.

Consolidates the former ``signified/`` and ``linkage/`` packages into a
single semantic analysis sub-package.

Public sub-modules
------------------
* :mod:`~arabic_engine.semantics.ontology` — Ontological concept mapping.
* :mod:`~arabic_engine.semantics.ontology_v1` — v1 ontology with detailed axes.
* :mod:`~arabic_engine.semantics.signified_v2` — v2 signified layer with
  20 semantic axes, SignifiedNode, ConceptNetwork.
* :mod:`~arabic_engine.semantics.dalala` — Dalāla (signification) validation.
* :mod:`~arabic_engine.semantics.semantic_roles` — Semantic role derivation.
* :mod:`~arabic_engine.semantics.masdar_bridge` — Masdar bridge linking.
"""

__all__ = [
    "dalala",
    "masdar_bridge",
    "ontology",
    "ontology_v1",
    "semantic_roles",
    "signified_v2",
]
