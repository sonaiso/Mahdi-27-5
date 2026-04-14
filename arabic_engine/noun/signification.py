"""جهة المطابقة والتضمن والالتزام — Signification facet.

Builds the three-layer signification structure for a fully classified
noun:

* **Mutābaqa** (مطابقة) — what the noun exactly denotes.
* **Taḍammun** (تضمن) — what parts / limits it includes.
* **Iltizām** (التزام) — what it necessarily entails.
"""

from __future__ import annotations

from arabic_engine.core.enums import NounKind, UniversalParticular
from arabic_engine.core.types import Concept, NounNode, NounSignification


def build_noun_signification(
    node: NounNode,
    concept: Concept,
) -> NounSignification:
    """Build the signification record for a classified noun.

    Parameters
    ----------
    node : NounNode
        A fully classified noun node.
    concept : Concept
        The concept node the noun maps to.

    Returns
    -------
    NounSignification
        The three-layer signification record.
    """
    mutabaqa = _build_mutabaqa(node, concept)
    tadammun = _build_tadammun(node, concept)
    iltizam = _build_iltizam(node)
    ref_status = _referential_status(node)

    return NounSignification(
        noun=node,
        mutabaqa_target=mutabaqa,
        tadammun_parts=tadammun,
        iltizam_entailments=iltizam,
        referential_status=ref_status,
    )


# ── Internals ───────────────────────────────────────────────────────


def _build_mutabaqa(node: NounNode, concept: Concept) -> str:
    """Exact denotation: what the noun names or refers to."""
    kind = node.noun_kind
    if kind == NounKind.PROPER:
        return f"proper:{node.lemma}"
    if kind == NounKind.GENUS:
        return f"genus:{concept.label}"
    if kind == NounKind.SPECIES:
        return f"species:{concept.label}"
    if kind == NounKind.INDIVIDUAL:
        return f"individual:{concept.label}"
    if kind == NounKind.ATTRIBUTE:
        return f"attribute:{concept.label}"
    if kind == NounKind.NUMERAL:
        return f"numeral:{node.lemma}"
    return f"entity:{concept.label}"


def _build_tadammun(node: NounNode, concept: Concept) -> tuple[str, ...]:
    """Parts / limits included in the noun's meaning."""
    parts: list[str] = []

    # Genus / species boundaries
    if node.noun_kind in (NounKind.GENUS, NounKind.SPECIES):
        parts.append(f"category_boundary:{node.noun_kind.name}")

    # Descriptive elements
    if node.noun_kind == NounKind.ATTRIBUTE:
        parts.append("descriptive_quality")

    # Reference conditions
    if node.universality == UniversalParticular.UNIVERSAL:
        parts.append("universal_scope")
    else:
        parts.append("particular_scope")

    # Number / unity
    parts.append(f"number:{node.number.name}")

    # Gender
    parts.append(f"gender:{node.gender.name}")

    # Definiteness
    parts.append(f"definiteness:{node.definiteness.name}")

    return tuple(parts)


def _build_iltizam(node: NounNode) -> tuple[str, ...]:
    """Necessary entailments of the noun."""
    entailments: list[str] = []

    # Genus entailments
    if node.noun_kind == NounKind.GENUS:
        entailments.append("entails_species_membership")
        entailments.append("entails_individual_instances")

    # Species entailments
    if node.noun_kind == NounKind.SPECIES:
        entailments.append("entails_genus_membership")
        entailments.append("entails_shared_essence")

    # Individual entailments
    if node.noun_kind in (NounKind.INDIVIDUAL, NounKind.PROPER):
        entailments.append("entails_unique_reference")
        entailments.append("entails_species_membership")

    # Attribute entailments
    if node.noun_kind == NounKind.ATTRIBUTE:
        entailments.append("entails_qualified_subject")

    # Number entailments
    entailments.append(f"number_entailment:{node.number.name}")

    # Gender entailments
    entailments.append(f"gender_entailment:{node.gender.name}")

    # Definiteness entailments
    entailments.append(f"definiteness_entailment:{node.definiteness.name}")

    return tuple(entailments)


def _referential_status(node: NounNode) -> str:
    """Whether the noun refers to a specific entity."""
    if node.noun_kind in (NounKind.PROPER, NounKind.INDIVIDUAL):
        return "specific_referent"
    if node.universality == UniversalParticular.UNIVERSAL:
        return "generic_referent"
    return "non_specific_referent"
