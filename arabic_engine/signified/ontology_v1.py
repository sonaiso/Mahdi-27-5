"""Ontology v1 — الجدول الأنطولوجي v1.0.

Implements the four-chapter ontological analysis model:

    1. الدال   — SignifierNode
    2. المدلول — SignifiedNode
    3. علاقة الاقتران — CouplingRecord
    4. القيود — OntologicalConstraintRecord

Public API
----------
classify_signifier(closure) → SignifierNode
classify_signified(concept) → SignifiedNode
select_coupling(signifier, signified, dalala_type) → CouplingRecord
evaluate_constraints(signifier, signified, coupling) → Tuple[OntologicalConstraintRecord, ...]
build_ontology_record(closure, concept, dalala_type, record_id) → OntologyV1Record
batch_build(closures, concepts, dalala_types) → List[OntologyV1Record]
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from arabic_engine.core.enums import (
    POS,
    ConceptualSignifiedClass,
    CouplingRelationType,
    DalalaType,
    OntologicalConstraintType,
    OntologicalLayer,
    SemanticType,
    SignifiedClass,
    SignifierClass,
    UtteranceToConceptConstraint,
    UtteredFormClass,
)
from arabic_engine.core.types import (
    Concept,
    CouplingRecord,
    LexicalClosure,
    OntologicalConstraintRecord,
    OntologyV1Record,
    SignifiedNode,
    SignifierNode,
)

# ── Internal counters for auto-generated IDs ─────────────────────────

_sig_counter = 0
_sfd_counter = 0
_crp_counter = 0
_con_counter = 0
_ont_counter = 0


def _next_id(prefix: str, counter_name: str) -> str:  # noqa: ARG001
    """Return the next sequential ID for *prefix*.

    Supported prefixes and the global counter each one increments:
      SIG → _sig_counter, SFD → _sfd_counter, CRP → _crp_counter,
      CON → _con_counter, ONT → _ont_counter.
    """
    global _sig_counter, _sfd_counter, _crp_counter, _con_counter, _ont_counter
    if prefix == "SIG":
        _sig_counter += 1
        return f"SIG_{_sig_counter:03d}"
    if prefix == "SFD":
        _sfd_counter += 1
        return f"SFD_{_sfd_counter:03d}"
    if prefix == "CRP":
        _crp_counter += 1
        return f"CRP_{_crp_counter:03d}"
    if prefix == "CON":
        _con_counter += 1
        return f"CON_{_con_counter:03d}"
    _ont_counter += 1
    return f"ONT_{_ont_counter:03d}"


# ── POS → SignifierClass mapping ─────────────────────────────────────

_POS_TO_SIGNIFIER: Dict[POS, SignifierClass] = {
    POS.ISM: SignifierClass.LEXICAL,
    POS.FI3L: SignifierClass.LEXICAL,
    POS.SIFA: SignifierClass.LEXICAL,
    POS.HARF: SignifierClass.SYNTACTIC,
    POS.ZARF: SignifierClass.LEXICAL,
    POS.DAMIR: SignifierClass.SYNTACTIC,
    POS.UNKNOWN: SignifierClass.LEXICAL,
}

_POS_TO_LAYER: Dict[POS, OntologicalLayer] = {
    POS.ISM: OntologicalLayer.ROOT,
    POS.FI3L: OntologicalLayer.PATTERN,
    POS.SIFA: OntologicalLayer.ROOT,
    POS.HARF: OntologicalLayer.CELL,
    POS.ZARF: OntologicalLayer.ROOT,
    POS.DAMIR: OntologicalLayer.ROOT,
    POS.UNKNOWN: OntologicalLayer.ROOT,
}

_POS_TO_UTTERED: Dict[POS, UtteredFormClass] = {
    POS.ISM: UtteredFormClass.WORD_UTTERANCE,
    POS.FI3L: UtteredFormClass.WORD_UTTERANCE,
    POS.SIFA: UtteredFormClass.WORD_UTTERANCE,
    POS.HARF: UtteredFormClass.MARKED_UTTERANCE,
    POS.ZARF: UtteredFormClass.WORD_UTTERANCE,
    POS.DAMIR: UtteredFormClass.WORD_UTTERANCE,
    POS.UNKNOWN: UtteredFormClass.WORD_UTTERANCE,
}

# ── SemanticType → SignifiedClass / ConceptualSignifiedClass mapping ──

_STYPE_TO_SIGNIFIED: Dict[SemanticType, SignifiedClass] = {
    SemanticType.ENTITY: SignifiedClass.CONCEPTUAL,
    SemanticType.EVENT: SignifiedClass.CONCEPTUAL,
    SemanticType.ATTRIBUTE: SignifiedClass.CONCEPTUAL,
    SemanticType.RELATION: SignifiedClass.RELATIONAL,
    SemanticType.NORM: SignifiedClass.NORMATIVE,
}

_STYPE_TO_CONCEPTUAL: Dict[SemanticType, Optional[ConceptualSignifiedClass]] = {
    SemanticType.ENTITY: ConceptualSignifiedClass.ENTITY_CONCEPT,
    SemanticType.EVENT: ConceptualSignifiedClass.EVENT_CONCEPT,
    SemanticType.ATTRIBUTE: ConceptualSignifiedClass.PROPERTY_CONCEPT,
    SemanticType.RELATION: None,  # relational signifieds are not CONCEPTUAL
    SemanticType.NORM: None,      # normative signifieds are not CONCEPTUAL
}

# ── DalalaType → CouplingRelationType mapping ────────────────────────

_DALALA_TO_COUPLING: Dict[DalalaType, CouplingRelationType] = {
    DalalaType.MUTABAQA: CouplingRelationType.DIRECT,
    DalalaType.TADAMMUN: CouplingRelationType.INFERENTIAL,
    DalalaType.ILTIZAM: CouplingRelationType.INFERENTIAL,
    DalalaType.ISNAD: CouplingRelationType.COMPOSITIONAL,
    DalalaType.TAQYID: CouplingRelationType.HIERARCHICAL,
    DalalaType.IDAFA: CouplingRelationType.COMPOSITIONAL,
    DalalaType.IHALA: CouplingRelationType.REFERENTIAL_COUPLING,
}


# ── Public functions ──────────────────────────────────────────────────


def classify_signifier(
    closure: LexicalClosure,
    *,
    node_id: Optional[str] = None,
    figurative: bool = False,
) -> SignifierNode:
    """Map a :class:`~arabic_engine.core.types.LexicalClosure` to a :class:`SignifierNode`.

    Infers the :class:`~arabic_engine.core.enums.SignifierClass` from the
    POS tag and marks the node as ``UTTERED_FORM`` (منطوق) because a
    ``LexicalClosure`` always represents a realised surface form.

    When *figurative* is ``True``, the layer is set to ``PATTERN`` (as
    rhetorical uses operate above the literal lexical level).

    Args:
        closure:    The lexical closure to classify.
        node_id:    Optional explicit ID; auto-generated if omitted.
        figurative: Whether the signifier is used figuratively.

    Returns:
        A frozen :class:`SignifierNode`.
    """
    nid = node_id or _next_id("SIG", "_sig_counter")
    base_class = _POS_TO_SIGNIFIER.get(closure.pos, SignifierClass.LEXICAL)
    layer = _POS_TO_LAYER.get(closure.pos, OntologicalLayer.ROOT)
    uttered_class = _POS_TO_UTTERED.get(closure.pos, UtteredFormClass.WORD_UTTERANCE)

    # A surface utterance always counts as UTTERED_FORM (منطوق)
    sig_class = SignifierClass.UTTERED_FORM

    if figurative:
        layer = OntologicalLayer.PATTERN

    notes = f"base_class={base_class.name}"
    if figurative:
        notes += "; figurative=True"

    return SignifierNode(
        node_id=nid,
        signifier_class=sig_class,
        surface=closure.surface,
        layer=layer,
        uttered_form_class=uttered_class,
        notes=notes,
    )


def classify_signified(
    concept: Concept,
    *,
    node_id: Optional[str] = None,
    referential: bool = False,
) -> SignifiedNode:
    """Map a :class:`~arabic_engine.core.types.Concept` to a :class:`SignifiedNode`.

    Derives the :class:`~arabic_engine.core.enums.SignifiedClass` and
    optional :class:`~arabic_engine.core.enums.ConceptualSignifiedClass`
    from the concept's :class:`~arabic_engine.core.enums.SemanticType`.

    When *referential* is ``True``, the signified is classified as
    ``REFERENTIAL`` (مدلول إحالي) regardless of the semantic type, because
    deictic/anaphoric elements primarily function as reference holders.

    Args:
        concept:    The concept node to classify.
        node_id:    Optional explicit ID; auto-generated if omitted.
        referential: Whether the concept functions as a deictic reference.

    Returns:
        A frozen :class:`SignifiedNode`.
    """
    nid = node_id or _next_id("SFD", "_sfd_counter")

    if referential:
        return SignifiedNode(
            node_id=nid,
            signified_class=SignifiedClass.REFERENTIAL,
            label=concept.label,
            semantic_type=concept.semantic_type,
            conceptual_class=None,
            properties=dict(concept.properties),
            notes="referential=True",
        )

    signified_class = _STYPE_TO_SIGNIFIED.get(
        concept.semantic_type, SignifiedClass.CONCEPTUAL
    )
    conceptual_class = _STYPE_TO_CONCEPTUAL.get(concept.semantic_type)

    return SignifiedNode(
        node_id=nid,
        signified_class=signified_class,
        label=concept.label,
        semantic_type=concept.semantic_type,
        conceptual_class=conceptual_class,
        properties=dict(concept.properties),
    )


def select_coupling(
    signifier: SignifierNode,
    signified: SignifiedNode,
    dalala_type: DalalaType,
    *,
    coupling_id: Optional[str] = None,
    confidence: float = 1.0,
    evidence: str = "",
) -> CouplingRecord:
    """Build a :class:`CouplingRecord` from a dalāla classification.

    Maps the classical :class:`~arabic_engine.core.enums.DalalaType` into
    the broader :class:`~arabic_engine.core.enums.CouplingRelationType`
    that sits one level above it in the ontology.

    When the signified is ``REFERENTIAL`` the coupling is always
    ``REFERENTIAL_COUPLING``, regardless of *dalala_type*.

    Args:
        signifier:   The source signifier node.
        signified:   The target signified node.
        dalala_type: The classical signification kind.
        coupling_id: Optional explicit ID; auto-generated if omitted.
        confidence:  Confidence score ∈ [0, 1].
        evidence:    Human-readable evidence description.

    Returns:
        A frozen :class:`CouplingRecord`.
    """
    cid = coupling_id or _next_id("CRP", "_crp_counter")

    if signified.signified_class is SignifiedClass.REFERENTIAL:
        coupling_type = CouplingRelationType.REFERENTIAL_COUPLING
    else:
        coupling_type = _DALALA_TO_COUPLING.get(
            dalala_type, CouplingRelationType.DIRECT
        )

    return CouplingRecord(
        coupling_id=cid,
        coupling_type=coupling_type,
        signifier_id=signifier.node_id,
        signified_id=signified.node_id,
        confidence=confidence,
        evidence=evidence or dalala_type.name,
    )


def evaluate_constraints(
    signifier: SignifierNode,
    signified: SignifiedNode,
    coupling: CouplingRecord,
) -> Tuple[OntologicalConstraintRecord, ...]:
    """Evaluate the seven utterance→concept constraints for this triple.

    Each of the seven :class:`~arabic_engine.core.enums.UtteranceToConceptConstraint`
    items is checked against the given signifier/signified/coupling and
    returns a :class:`OntologicalConstraintRecord` with ``passes`` set
    accordingly.

    Rules applied
    -------------
    SURFACE_VALIDITY
        Passes when the signifier's surface is non-empty.
    LEXICAL_ACCESS
        Passes when the signified has a non-empty label.
    CONTEXT_RESOLUTION
        Passes always for non-referential signifieds; for referential ones,
        passes only when ``confidence > 0.5``.
    CONCEPT_SELECTION
        Passes when signified class is CONCEPTUAL and a conceptual_class is set,
        or when signified class is anything other than CONCEPTUAL (no
        ambiguity between concept subtypes).
    FIGURATIVE_DISAMBIGUATION
        Passes when coupling type is FIGURATIVE and confidence ≥ 0.7 (i.e.
        a strong-enough qarinah exists), or when coupling is not figurative.
    REFERENTIAL_RESOLUTION
        Passes when coupling is REFERENTIAL_COUPLING and confidence > 0.0,
        or when coupling is not referential.
    LOGICAL_COHERENCE
        Passes when confidence > 0.0 (the interpretation is non-degenerate).
    """
    records: List[OntologicalConstraintRecord] = []
    con_id_counter = [0]

    def _cid() -> str:
        con_id_counter[0] += 1
        return f"CON_{_con_counter + con_id_counter[0]:03d}"

    # 1. SURFACE_VALIDITY
    passes = bool(signifier.surface.strip())
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.STRUCTURAL,
        utterance_constraint=UtteranceToConceptConstraint.SURFACE_VALIDITY,
        description_ar="هل المنطوق سليم في بنيته؟",
        passes=passes,
        violated_by="" if passes else f"empty surface: {signifier.surface!r}",
    ))

    # 2. LEXICAL_ACCESS
    passes = bool(signified.label.strip())
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.LEXICAL_CONSTRAINT,
        utterance_constraint=UtteranceToConceptConstraint.LEXICAL_ACCESS,
        description_ar="هل يملك المنطوق مدخلًا معجميًا معتبرًا؟",
        passes=passes,
        violated_by="" if passes else "signified label is empty",
    ))

    # 3. CONTEXT_RESOLUTION
    if signified.signified_class is SignifiedClass.REFERENTIAL:
        passes = coupling.confidence > 0.5
        violated = "" if passes else f"referential confidence too low: {coupling.confidence}"
    else:
        passes = True
        violated = ""
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.CONTEXTUAL_CONSTRAINT,
        utterance_constraint=UtteranceToConceptConstraint.CONTEXT_RESOLUTION,
        description_ar="هل السياق كافٍ لتعيين المقصود؟",
        passes=passes,
        violated_by=violated,
    ))

    # 4. CONCEPT_SELECTION
    if signified.signified_class is SignifiedClass.CONCEPTUAL:
        passes = signified.conceptual_class is not None
        violated = "" if passes else "CONCEPTUAL signified missing conceptual_class"
    else:
        passes = True
        violated = ""
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.INTERPRETIVE_CONSTRAINT,
        utterance_constraint=UtteranceToConceptConstraint.CONCEPT_SELECTION,
        description_ar="هل اختير المفهوم الصحيح من بين الاحتمالات؟",
        passes=passes,
        violated_by=violated,
    ))

    # 5. FIGURATIVE_DISAMBIGUATION
    if coupling.coupling_type is CouplingRelationType.FIGURATIVE:
        passes = coupling.confidence >= 0.7
        violated = (
            "" if passes
            else f"figurative coupling confidence too low: {coupling.confidence}"
        )
    else:
        passes = True
        violated = ""
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.RHETORICAL_CONSTRAINT,
        utterance_constraint=UtteranceToConceptConstraint.FIGURATIVE_DISAMBIGUATION,
        description_ar="هل توجد قرينة تصرف عن الحقيقة إلى المجاز؟",
        passes=passes,
        violated_by=violated,
    ))

    # 6. REFERENTIAL_RESOLUTION
    if coupling.coupling_type is CouplingRelationType.REFERENTIAL_COUPLING:
        passes = coupling.confidence > 0.0
        violated = "" if passes else "referential coupling with zero confidence"
    else:
        passes = True
        violated = ""
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.REFERENTIAL_CONSTRAINT,
        utterance_constraint=UtteranceToConceptConstraint.REFERENTIAL_RESOLUTION,
        description_ar="هل المرجع متاح إذا كان المنطوق إحاليًا؟",
        passes=passes,
        violated_by=violated,
    ))

    # 7. LOGICAL_COHERENCE
    passes = coupling.confidence > 0.0
    records.append(OntologicalConstraintRecord(
        constraint_id=_cid(),
        constraint_type=OntologicalConstraintType.LOGICAL_CONSTRAINT,
        utterance_constraint=UtteranceToConceptConstraint.LOGICAL_COHERENCE,
        description_ar="هل التفسير متسق مع بقية البنية؟",
        passes=passes,
        violated_by="" if passes else "zero-confidence coupling is logically incoherent",
    ))

    return tuple(records)


def build_ontology_record(
    closure: LexicalClosure,
    concept: Concept,
    dalala_type: DalalaType,
    *,
    record_id: Optional[str] = None,
    figurative: bool = False,
    referential: bool = False,
    confidence: Optional[float] = None,
    notes: str = "",
) -> OntologyV1Record:
    """Build a complete :class:`OntologyV1Record` from a closure/concept pair.

    This is the top-level factory that enforces the correct analysis order
    mandated by Axiom 7::

        الدال → المدلول → علاقة الاقتران → القيود

    Args:
        closure:     The lexical closure (signifier surface form).
        concept:     The ontological concept node (signified).
        dalala_type: The classical signification type for this pair.
        record_id:   Optional explicit record ID; auto-generated if omitted.
        figurative:  Whether the signifier is used figuratively.
        referential: Whether the concept functions as a deictic reference.
        confidence:  Override coupling confidence; defaults inferred from
                     ``dalala_type`` if ``None``.
        notes:       Free-text annotation for the record.

    Returns:
        A frozen :class:`OntologyV1Record` with ``valid`` set to
        ``True`` iff all seven constraint records pass.
    """
    # Default confidence per dalala type
    _default_confidence: Dict[DalalaType, float] = {
        DalalaType.MUTABAQA: 1.0,
        DalalaType.TADAMMUN: 0.75,
        DalalaType.ILTIZAM: 0.5,
        DalalaType.ISNAD: 0.95,
        DalalaType.TAQYID: 0.85,
        DalalaType.IDAFA: 0.9,
        DalalaType.IHALA: 0.8,
    }
    conf = confidence if confidence is not None else _default_confidence.get(dalala_type, 1.0)

    # Step 1: دال
    signifier = classify_signifier(closure, figurative=figurative)

    # Step 2: مدلول
    signified = classify_signified(concept, referential=referential)

    # Step 3: علاقة الاقتران
    coupling = select_coupling(
        signifier,
        signified,
        dalala_type,
        confidence=conf,
        evidence=dalala_type.name,
    )

    # Step 4: القيود
    constraints = evaluate_constraints(signifier, signified, coupling)

    valid = all(c.passes for c in constraints)
    rid = record_id or _next_id("ONT", "_ont_counter")

    return OntologyV1Record(
        record_id=rid,
        signifier=signifier,
        signified=signified,
        coupling=coupling,
        constraints=constraints,
        valid=valid,
        notes=notes,
    )


def batch_build(
    closures: List[LexicalClosure],
    concepts: List[Concept],
    dalala_types: List[DalalaType],
    *,
    figurative_flags: Optional[List[bool]] = None,
    referential_flags: Optional[List[bool]] = None,
) -> List[OntologyV1Record]:
    """Build a list of :class:`OntologyV1Record` from parallel input lists.

    Args:
        closures:          Lexical closures (signifiers).
        concepts:          Concept nodes (signifieds), parallel to *closures*.
        dalala_types:      Dalāla types, parallel to *closures*.
        figurative_flags:  Per-item figurative flag; defaults to all ``False``.
        referential_flags: Per-item referential flag; defaults to all ``False``.

    Returns:
        A list of :class:`OntologyV1Record` objects, one per input triple.
    """
    n = len(closures)
    figs = figurative_flags or [False] * n
    refs = referential_flags or [False] * n
    return [
        build_ontology_record(
            closures[i],
            concepts[i],
            dalala_types[i],
            figurative=figs[i],
            referential=refs[i],
        )
        for i in range(n)
    ]
