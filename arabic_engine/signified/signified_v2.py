"""Signified v2.0 — المدلول الشامل (CompleteSignified).

This module introduces three key additions on top of the basic
:class:`~arabic_engine.core.types.Concept` node:

1. :class:`SignifiedKind` — classifies each semantic axis as a *Type*,
   *Axis*, *Relation*, or *Constraint* so callers can reason about what
   kind of semantic contribution each field makes.

2. :class:`SignifiedNode` — wraps a :class:`~arabic_engine.core.types.Concept`
   with an explicit :class:`SignifiedKind` label and exposes a convenience
   method for querying populated axes.

3. :class:`ConceptNetwork` — an in-memory graph of
   :class:`SignifiedNode` objects connected by
   :class:`~arabic_engine.core.types.ConceptRelation` edges, with helpers
   for adding nodes / relations and traversing neighbours.

Public API
----------
* :class:`SignifiedKind`
* :class:`SignifiedNode`
* :func:`build_signified_node`
* :class:`ConceptNetwork`
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Iterator, List, Optional

from arabic_engine.core.enums import (
    AffectiveDimension,
    CategorizationMode,
    CausalRole,
    ConceptFormationMode,
    ConceptRelationType,
    CulturalScope,
    DiachronicStatus,
    EmbodiedDomain,
    EpistemicStatus,
    FrameType,
    InstitutionalCategory,
    InterpretiveStability,
    MentalIntentionalType,
    MetaConceptualLevel,
    ModalCategory,
    NormativeCategory,
    OperationalCapacity,
    SalienceLevel,
    ScriptPhase,
    SelfModelAspect,
    SemanticType,
)
from arabic_engine.core.types import Concept, ConceptRelation

# ── SignifiedKind ────────────────────────────────────────────────────

class SignifiedKind(Enum):
    """تصنيف نوع المدلول — how each semantic axis contributes to meaning.

    Following the v2 design decision, every semantic dimension carried
    by a concept is classified as one of four meta-categories:

    ============  =================================================
    Kind           Description
    ============  =================================================
    TYPE           Primary ontological type (SemanticType,
                   MentalIntentionalType, InstitutionalCategory,
                   MetaConceptualLevel, SelfModelAspect).
                   Defines *what kind of thing* the concept is.
    AXIS           Descriptive axis that modifies / qualifies the
                   concept (EpistemicStatus, AffectiveDimension,
                   ModalCategory, …).  Multiple axes can apply
                   simultaneously.
    RELATION       Marks the concept's role in a relational or
                   causal network (CausalRole, ConceptRelationType).
    CONSTRAINT     Interpretive / contextual constraint that limits
                   or conditions how the concept is understood
                   (FrameType, InterpretiveStability).
    ============  =================================================
    """

    TYPE = auto()        # نوع        — defines the kind of concept
    AXIS = auto()        # محور       — descriptive dimension / qualifier
    RELATION = auto()    # علاقة      — relational / causal role
    CONSTRAINT = auto()  # قيد        — interpretive / contextual constraint


# ── Axis classification map ──────────────────────────────────────────

#: Maps each v2 axis *field name* on :class:`~arabic_engine.core.types.Concept`
#: to its :class:`SignifiedKind` classification.
AXIS_KIND_MAP: Dict[str, SignifiedKind] = {
    "semantic_type": SignifiedKind.TYPE,
    "epistemic_status": SignifiedKind.AXIS,
    "normative_category": SignifiedKind.AXIS,
    "affective_dimension": SignifiedKind.AXIS,
    "mental_intentional_type": SignifiedKind.TYPE,
    "modal_category": SignifiedKind.AXIS,
    "frame_type": SignifiedKind.CONSTRAINT,
    "script_phase": SignifiedKind.AXIS,
    "causal_role": SignifiedKind.RELATION,
    "institutional_category": SignifiedKind.TYPE,
    "categorization_mode": SignifiedKind.AXIS,
    "cultural_scope": SignifiedKind.AXIS,
    "diachronic_status": SignifiedKind.AXIS,
    "formation_mode": SignifiedKind.AXIS,
    "meta_level": SignifiedKind.TYPE,
    "interpretive_stability": SignifiedKind.CONSTRAINT,
    "salience": SignifiedKind.AXIS,
    "embodied_domain": SignifiedKind.AXIS,
    "self_model_aspect": SignifiedKind.TYPE,
    "operational_capacity": SignifiedKind.AXIS,
}


# ── SignifiedNode ────────────────────────────────────────────────────

@dataclass
class SignifiedNode:
    """عقدة المدلول — a concept node enriched with a SignifiedKind label.

    Wraps a :class:`~arabic_engine.core.types.Concept` and adds an
    explicit :class:`SignifiedKind` so that downstream systems can
    distinguish *types* from *axes*, *relations*, and *constraints*.

    Fields
    ------
    concept     the underlying :class:`~arabic_engine.core.types.Concept`
    kind        primary :class:`SignifiedKind` of this node
    """

    concept: Concept
    kind: SignifiedKind = SignifiedKind.TYPE

    # ── convenience helpers ──────────────────────────────────────────

    @property
    def concept_id(self) -> int:
        """Shortcut to ``concept.concept_id``."""
        return self.concept.concept_id

    @property
    def label(self) -> str:
        """Shortcut to ``concept.label``."""
        return self.concept.label

    @property
    def semantic_type(self) -> SemanticType:
        """Shortcut to ``concept.semantic_type``."""
        return self.concept.semantic_type

    def populated_axes(self) -> Dict[str, object]:
        """Return a dict of all v2 axes that have been set (non-None).

        Returns
        -------
        dict
            ``{field_name: value}`` for every optional axis field on
            :attr:`concept` that is not ``None``.

        Example
        -------
        >>> node.populated_axes()
        {'epistemic_status': <EpistemicStatus.CERTAIN: 1>,
         'modal_category': <ModalCategory.ACTUAL: 6>}
        """
        axis_fields = [
            "epistemic_status",
            "normative_category",
            "affective_dimension",
            "mental_intentional_type",
            "modal_category",
            "frame_type",
            "script_phase",
            "causal_role",
            "institutional_category",
            "categorization_mode",
            "cultural_scope",
            "diachronic_status",
            "formation_mode",
            "meta_level",
            "interpretive_stability",
            "salience",
            "embodied_domain",
            "self_model_aspect",
            "operational_capacity",
        ]
        return {
            f: getattr(self.concept, f)
            for f in axis_fields
            if getattr(self.concept, f) is not None
        }

    def axis_kind(self, field_name: str) -> Optional[SignifiedKind]:
        """Return the :class:`SignifiedKind` classification of a named axis.

        Args:
            field_name: The field name as it appears on
                :class:`~arabic_engine.core.types.Concept` (e.g.
                ``"epistemic_status"``).

        Returns:
            The corresponding :class:`SignifiedKind`, or ``None`` if the
            field name is not a recognised axis.
        """
        return AXIS_KIND_MAP.get(field_name)


# ── build_signified_node ─────────────────────────────────────────────

def build_signified_node(
    concept: Concept,
    *,
    kind: Optional[SignifiedKind] = None,
    epistemic_status: Optional[EpistemicStatus] = None,
    normative_category: Optional[NormativeCategory] = None,
    affective_dimension: Optional[AffectiveDimension] = None,
    mental_intentional_type: Optional[MentalIntentionalType] = None,
    modal_category: Optional[ModalCategory] = None,
    frame_type: Optional[FrameType] = None,
    script_phase: Optional[ScriptPhase] = None,
    causal_role: Optional[CausalRole] = None,
    institutional_category: Optional[InstitutionalCategory] = None,
    categorization_mode: Optional[CategorizationMode] = None,
    cultural_scope: Optional[CulturalScope] = None,
    diachronic_status: Optional[DiachronicStatus] = None,
    formation_mode: Optional[ConceptFormationMode] = None,
    meta_level: Optional[MetaConceptualLevel] = None,
    interpretive_stability: Optional[InterpretiveStability] = None,
    salience: Optional[SalienceLevel] = None,
    embodied_domain: Optional[EmbodiedDomain] = None,
    self_model_aspect: Optional[SelfModelAspect] = None,
    operational_capacity: Optional[OperationalCapacity] = None,
) -> SignifiedNode:
    """Build a :class:`SignifiedNode` from a concept plus optional axes.

    This is the primary factory for constructing fully-enriched signified
    nodes.  Pass keyword arguments only for the axes you want to set;
    unspecified axes remain ``None`` on the concept.

    The ``kind`` parameter defaults to :attr:`SignifiedKind.TYPE` when
    omitted.

    Args:
        concept:   Base :class:`~arabic_engine.core.types.Concept`.  Its
                   optional axis fields are *mutated in-place* by any
                   keyword argument that is not ``None``.
        kind:      :class:`SignifiedKind` label for the resulting node.
                   Defaults to ``SignifiedKind.TYPE``.
        **axes:    Any of the nineteen optional axis keyword arguments
                   listed above.  Each non-``None`` value is written to
                   the matching field on ``concept``.

    Returns:
        A :class:`SignifiedNode` wrapping the (possibly updated) concept.
    """
    # Write axes to concept fields
    if epistemic_status is not None:
        concept.epistemic_status = epistemic_status
    if normative_category is not None:
        concept.normative_category = normative_category
    if affective_dimension is not None:
        concept.affective_dimension = affective_dimension
    if mental_intentional_type is not None:
        concept.mental_intentional_type = mental_intentional_type
    if modal_category is not None:
        concept.modal_category = modal_category
    if frame_type is not None:
        concept.frame_type = frame_type
    if script_phase is not None:
        concept.script_phase = script_phase
    if causal_role is not None:
        concept.causal_role = causal_role
    if institutional_category is not None:
        concept.institutional_category = institutional_category
    if categorization_mode is not None:
        concept.categorization_mode = categorization_mode
    if cultural_scope is not None:
        concept.cultural_scope = cultural_scope
    if diachronic_status is not None:
        concept.diachronic_status = diachronic_status
    if formation_mode is not None:
        concept.formation_mode = formation_mode
    if meta_level is not None:
        concept.meta_level = meta_level
    if interpretive_stability is not None:
        concept.interpretive_stability = interpretive_stability
    if salience is not None:
        concept.salience = salience
    if embodied_domain is not None:
        concept.embodied_domain = embodied_domain
    if self_model_aspect is not None:
        concept.self_model_aspect = self_model_aspect
    if operational_capacity is not None:
        concept.operational_capacity = operational_capacity

    return SignifiedNode(
        concept=concept,
        kind=kind if kind is not None else SignifiedKind.TYPE,
    )


# ── ConceptNetwork ───────────────────────────────────────────────────

@dataclass
class ConceptNetwork:
    """شبكة المفاهيم — an in-memory directed concept graph.

    Nodes are :class:`SignifiedNode` objects keyed by their
    ``concept_id``.  Edges are :class:`~arabic_engine.core.types.ConceptRelation`
    records stored in insertion order.

    Usage
    -----
    >>> net = ConceptNetwork()
    >>> net.add_node(node_a)
    >>> net.add_node(node_b)
    >>> net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
    >>> list(net.get_related(1))
    [SignifiedNode(...)]
    """

    nodes: Dict[int, SignifiedNode] = field(default_factory=dict)
    relations: List[ConceptRelation] = field(default_factory=list)

    # ── mutation ─────────────────────────────────────────────────────

    def add_node(self, node: SignifiedNode) -> None:
        """Register a :class:`SignifiedNode` in the network.

        If a node with the same ``concept_id`` already exists it is
        silently replaced.

        Args:
            node: The node to add.
        """
        self.nodes[node.concept_id] = node

    def add_relation(self, relation: ConceptRelation) -> None:
        """Add a directed :class:`~arabic_engine.core.types.ConceptRelation`.

        Both ``source_id`` and ``target_id`` must already exist in
        :attr:`nodes`; a :exc:`KeyError` is raised otherwise.

        Args:
            relation: The relation to add.

        Raises:
            KeyError: When either endpoint is not in the network.
        """
        if relation.source_id not in self.nodes:
            raise KeyError(
                f"Source concept_id {relation.source_id} not in network."
            )
        if relation.target_id not in self.nodes:
            raise KeyError(
                f"Target concept_id {relation.target_id} not in network."
            )
        self.relations.append(relation)

    # ── query ─────────────────────────────────────────────────────────

    def get_related(
        self,
        concept_id: int,
        *,
        relation_type: Optional[ConceptRelationType] = None,
        direction: str = "outgoing",
    ) -> Iterator[SignifiedNode]:
        """Yield nodes reachable from *concept_id* via stored relations.

        Args:
            concept_id:    The source (or target, if ``direction="incoming"``)
                           node identifier.
            relation_type: Optional filter; when supplied only relations of
                           that type are considered.
            direction:     ``"outgoing"`` (default) — follow edges *from*
                           ``concept_id``; ``"incoming"`` — follow edges
                           *to* ``concept_id``.

        Yields:
            :class:`SignifiedNode` objects for each matching neighbour.
        """
        for rel in self.relations:
            if relation_type is not None and rel.relation_type != relation_type:
                continue
            if direction == "outgoing" and rel.source_id == concept_id:
                target = self.nodes.get(rel.target_id)
                if target is not None:
                    yield target
            elif direction == "incoming" and rel.target_id == concept_id:
                source = self.nodes.get(rel.source_id)
                if source is not None:
                    yield source

    def node_count(self) -> int:
        """Return the number of nodes currently in the network."""
        return len(self.nodes)

    def relation_count(self) -> int:
        """Return the number of relations currently in the network."""
        return len(self.relations)
