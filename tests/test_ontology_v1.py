"""Tests for the Ontology v1.0 model.

Validates:
  * All seven new enums are complete (correct member counts).
  * classify_signifier — POS-to-SignifierNode mapping.
  * classify_signified — SemanticType-to-SignifiedNode mapping.
  * select_coupling — DalalaType-to-CouplingRelationType mapping.
  * evaluate_constraints — all seven utterance→concept guards.
  * build_ontology_record — end-to-end for the three canonical examples:
      "الأسد" (direct), "الأسد" (figurative), "هذا" (referential),
      "ما زيد إلا قائم" (propositional / restrictive).
  * batch_build — parallel list factory.
  * Re-exports from arabic_engine.core.
"""

from __future__ import annotations

import pytest

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
    OntologyV1Record,
    SignifiedNode,
    SignifierNode,
)
from arabic_engine.signified.ontology_v1 import (
    batch_build,
    build_ontology_record,
    classify_signified,
    classify_signifier,
    evaluate_constraints,
    select_coupling,
)

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def _closure(surface: str, lemma: str, pos: POS, root=("ك", "ت", "ب")) -> LexicalClosure:
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=root,
        pattern="فَعَلَ",
        pos=pos,
    )


def _concept(label: str, stype: SemanticType, **props) -> Concept:
    return Concept(concept_id=999, label=label, semantic_type=stype, properties=props)


# ═══════════════════════════════════════════════════════════════════════
# Enum completeness
# ═══════════════════════════════════════════════════════════════════════

class TestEnumCompleteness:
    def test_signifier_class_count(self):
        assert len(SignifierClass) == 8

    def test_uttered_form_class_count(self):
        assert len(UtteredFormClass) == 5

    def test_signified_class_count(self):
        assert len(SignifiedClass) == 22

    def test_conceptual_signified_class_count(self):
        assert len(ConceptualSignifiedClass) == 8

    def test_coupling_relation_type_count(self):
        assert len(CouplingRelationType) == 10

    def test_ontological_constraint_type_count(self):
        assert len(OntologicalConstraintType) == 13

    def test_utterance_to_concept_constraint_count(self):
        assert len(UtteranceToConceptConstraint) == 7

    def test_signifier_class_members(self):
        members = {m.name for m in SignifierClass}
        assert "PHONOLOGICAL" in members
        assert "UTTERED_FORM" in members
        assert "RHETORICAL" in members

    def test_uttered_form_class_members(self):
        members = {m.name for m in UtteredFormClass}
        assert "WORD_UTTERANCE" in members
        assert "SENTENCE_UTTERANCE" in members
        assert "MARKED_UTTERANCE" in members

    def test_signified_class_members(self):
        members = {m.name for m in SignifiedClass}
        assert "ONTOLOGICAL" in members
        assert "REFERENTIAL" in members
        assert "CONCEPTUAL" in members
        assert "META_CONCEPTUAL" in members

    def test_conceptual_class_members(self):
        members = {m.name for m in ConceptualSignifiedClass}
        assert "ENTITY_CONCEPT" in members
        assert "META_CONCEPT" in members

    def test_coupling_relation_type_members(self):
        members = {m.name for m in CouplingRelationType}
        assert "DIRECT" in members
        assert "FIGURATIVE" in members
        assert "REFERENTIAL_COUPLING" in members

    def test_constraint_type_members(self):
        members = {m.name for m in OntologicalConstraintType}
        assert "STRUCTURAL" in members
        assert "RHETORICAL_CONSTRAINT" in members
        assert "INTERPRETIVE_CONSTRAINT" in members

    def test_utterance_constraint_members(self):
        members = {m.name for m in UtteranceToConceptConstraint}
        assert "SURFACE_VALIDITY" in members
        assert "LOGICAL_COHERENCE" in members
        assert "FIGURATIVE_DISAMBIGUATION" in members


# ═══════════════════════════════════════════════════════════════════════
# classify_signifier
# ═══════════════════════════════════════════════════════════════════════

class TestClassifySignifier:
    def test_lexical_noun(self):
        cl = _closure("الأَسَد", "أسد", POS.ISM, root=("أ", "س", "د"))
        node = classify_signifier(cl)
        assert isinstance(node, SignifierNode)
        assert node.signifier_class is SignifierClass.UTTERED_FORM
        assert node.uttered_form_class is UtteredFormClass.WORD_UTTERANCE
        assert node.surface == "الأَسَد"
        assert node.layer is OntologicalLayer.ROOT

    def test_lexical_verb(self):
        cl = _closure("كَتَبَ", "كتب", POS.FI3L)
        node = classify_signifier(cl)
        assert node.signifier_class is SignifierClass.UTTERED_FORM
        assert node.uttered_form_class is UtteredFormClass.WORD_UTTERANCE
        assert node.layer is OntologicalLayer.PATTERN

    def test_syntactic_particle(self):
        cl = _closure("مَا", "ما", POS.HARF, root=("م", "ا"))
        node = classify_signifier(cl)
        assert node.signifier_class is SignifierClass.UTTERED_FORM
        assert node.uttered_form_class is UtteredFormClass.MARKED_UTTERANCE
        assert node.layer is OntologicalLayer.CELL

    def test_pronoun(self):
        cl = _closure("هَذَا", "هذا", POS.DAMIR, root=("ه", "ذ", "ا"))
        node = classify_signifier(cl)
        assert node.signifier_class is SignifierClass.UTTERED_FORM
        assert node.uttered_form_class is UtteredFormClass.WORD_UTTERANCE

    def test_figurative_flag_sets_layer(self):
        cl = _closure("الأَسَد", "أسد", POS.ISM, root=("أ", "س", "د"))
        node = classify_signifier(cl, figurative=True)
        assert node.layer is OntologicalLayer.PATTERN
        assert "figurative=True" in node.notes

    def test_is_uttered_property(self):
        cl = _closure("زَيْد", "زيد", POS.ISM, root=("ز", "ي", "د"))
        node = classify_signifier(cl)
        assert node.is_uttered is True
        assert node.uttered_form_is_set is True

    def test_node_id_auto_generated(self):
        cl = _closure("رِسَالَة", "رسالة", POS.ISM)
        n1 = classify_signifier(cl)
        n2 = classify_signifier(cl)
        assert n1.node_id != n2.node_id
        assert n1.node_id.startswith("SIG_")

    def test_explicit_node_id(self):
        cl = _closure("رِسَالَة", "رسالة", POS.ISM)
        node = classify_signifier(cl, node_id="SIG_CUSTOM")
        assert node.node_id == "SIG_CUSTOM"

    def test_frozen(self):
        cl = _closure("زَيْد", "زيد", POS.ISM, root=("ز", "ي", "د"))
        node = classify_signifier(cl)
        with pytest.raises((AttributeError, TypeError)):
            node.surface = "other"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# classify_signified
# ═══════════════════════════════════════════════════════════════════════

class TestClassifySignified:
    def test_entity_concept(self):
        c = _concept("أسد", SemanticType.ENTITY, animacy=True)
        node = classify_signified(c)
        assert isinstance(node, SignifiedNode)
        assert node.signified_class is SignifiedClass.CONCEPTUAL
        assert node.conceptual_class is ConceptualSignifiedClass.ENTITY_CONCEPT
        assert node.label == "أسد"
        assert node.is_conceptual is True

    def test_event_concept(self):
        c = _concept("كتابة", SemanticType.EVENT)
        node = classify_signified(c)
        assert node.signified_class is SignifiedClass.CONCEPTUAL
        assert node.conceptual_class is ConceptualSignifiedClass.EVENT_CONCEPT

    def test_attribute_concept(self):
        c = _concept("طويل", SemanticType.ATTRIBUTE)
        node = classify_signified(c)
        assert node.signified_class is SignifiedClass.CONCEPTUAL
        assert node.conceptual_class is ConceptualSignifiedClass.PROPERTY_CONCEPT

    def test_relational_signified(self):
        c = _concept("فوق", SemanticType.RELATION)
        node = classify_signified(c)
        assert node.signified_class is SignifiedClass.RELATIONAL
        assert node.conceptual_class is None
        assert node.is_conceptual is False

    def test_normative_signified(self):
        c = _concept("وجوب", SemanticType.NORM)
        node = classify_signified(c)
        assert node.signified_class is SignifiedClass.NORMATIVE
        assert node.conceptual_class is None

    def test_referential_flag(self):
        c = _concept("هذا", SemanticType.ENTITY)
        node = classify_signified(c, referential=True)
        assert node.signified_class is SignifiedClass.REFERENTIAL
        assert node.conceptual_class is None
        assert node.is_conceptual is False
        assert "referential=True" in node.notes

    def test_properties_copied(self):
        c = _concept("أسد", SemanticType.ENTITY, animacy=True, wild=True)
        node = classify_signified(c)
        assert node.properties["animacy"] is True
        assert node.properties["wild"] is True

    def test_conceptual_class_is_set(self):
        c = _concept("زيد", SemanticType.ENTITY)
        node = classify_signified(c)
        assert node.conceptual_class_is_set is True

    def test_relational_conceptual_class_not_set(self):
        c = _concept("مع", SemanticType.RELATION)
        node = classify_signified(c)
        assert node.conceptual_class_is_set is False

    def test_frozen(self):
        c = _concept("أسد", SemanticType.ENTITY)
        node = classify_signified(c)
        with pytest.raises((AttributeError, TypeError)):
            node.label = "other"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# select_coupling
# ═══════════════════════════════════════════════════════════════════════

class TestSelectCoupling:
    def _pair(self, pos=POS.ISM, stype=SemanticType.ENTITY):
        cl = _closure("test", "test", pos)
        c = _concept("test", stype)
        sig = classify_signifier(cl)
        sfd = classify_signified(c)
        return sig, sfd

    def test_mutabaqa_maps_to_direct(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        assert rec.coupling_type is CouplingRelationType.DIRECT
        assert rec.is_direct is True

    def test_tadammun_maps_to_inferential(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.TADAMMUN, confidence=0.75)
        assert rec.coupling_type is CouplingRelationType.INFERENTIAL

    def test_iltizam_maps_to_inferential(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.ILTIZAM, confidence=0.5)
        assert rec.coupling_type is CouplingRelationType.INFERENTIAL

    def test_ihala_maps_to_referential_coupling(self):
        cl = _closure("هذا", "هذا", POS.DAMIR)
        c = _concept("هذا", SemanticType.ENTITY)
        sig = classify_signifier(cl)
        sfd = classify_signified(c, referential=True)
        rec = select_coupling(sig, sfd, DalalaType.IHALA, confidence=0.8)
        assert rec.coupling_type is CouplingRelationType.REFERENTIAL_COUPLING

    def test_referential_signified_forces_referential_coupling(self):
        cl = _closure("هو", "هو", POS.DAMIR)
        c = _concept("هو", SemanticType.ENTITY)
        sig = classify_signifier(cl)
        sfd = classify_signified(c, referential=True)
        # Even with MUTABAQA, referential node forces REFERENTIAL_COUPLING
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        assert rec.coupling_type is CouplingRelationType.REFERENTIAL_COUPLING

    def test_isnad_maps_to_compositional(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.ISNAD, confidence=0.95)
        assert rec.coupling_type is CouplingRelationType.COMPOSITIONAL

    def test_taqyid_maps_to_hierarchical(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.TAQYID, confidence=0.85)
        assert rec.coupling_type is CouplingRelationType.HIERARCHICAL

    def test_confidence_stored(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA, confidence=0.9)
        assert rec.confidence == pytest.approx(0.9)

    def test_evidence_defaults_to_dalala_name(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        assert rec.evidence == "MUTABAQA"

    def test_explicit_coupling_id(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA,
                              coupling_id="CRP_CUSTOM")
        assert rec.coupling_id == "CRP_CUSTOM"

    def test_signifier_signified_ids_stored(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        assert rec.signifier_id == sig.node_id
        assert rec.signified_id == sfd.node_id

    def test_is_figurative_false_for_direct(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        assert rec.is_figurative is False

    def test_frozen(self):
        sig, sfd = self._pair()
        rec = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        with pytest.raises((AttributeError, TypeError)):
            rec.confidence = 0.0  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# evaluate_constraints
# ═══════════════════════════════════════════════════════════════════════

class TestEvaluateConstraints:
    def _build(self, surface="أسد", stype=SemanticType.ENTITY,
               dalala=DalalaType.MUTABAQA, figurative=False, referential=False,
               confidence=None):
        cl = _closure(surface, surface, POS.ISM)
        c = _concept(surface, stype)
        sig = classify_signifier(cl, figurative=figurative)
        sfd = classify_signified(c, referential=referential)
        conf = confidence if confidence is not None else (
            1.0 if dalala is DalalaType.MUTABAQA else 0.8
        )
        coup = select_coupling(sig, sfd, dalala, confidence=conf)
        return sig, sfd, coup

    def test_returns_seven_constraints(self):
        sig, sfd, coup = self._build()
        constraints = evaluate_constraints(sig, sfd, coup)
        assert len(constraints) == 7

    def test_all_pass_for_valid_direct(self):
        sig, sfd, coup = self._build()
        for c in evaluate_constraints(sig, sfd, coup):
            assert c.passes is True, f"{c.utterance_constraint} failed"

    def test_surface_validity_fails_for_empty_surface(self):
        cl = LexicalClosure(surface="  ", lemma="test", root=(), pattern="", pos=POS.ISM)
        c = _concept("test", SemanticType.ENTITY)
        sig = classify_signifier(cl)
        sfd = classify_signified(c)
        coup = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        constraints = evaluate_constraints(sig, sfd, coup)
        sv = next(c for c in constraints
                  if c.utterance_constraint is UtteranceToConceptConstraint.SURFACE_VALIDITY)
        assert sv.passes is False
        assert sv.is_violated is True

    def test_lexical_access_fails_for_empty_label(self):
        cl = _closure("test", "test", POS.ISM)
        c = Concept(concept_id=1, label="   ", semantic_type=SemanticType.ENTITY)
        sig = classify_signifier(cl)
        sfd = classify_signified(c)
        coup = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        constraints = evaluate_constraints(sig, sfd, coup)
        la = next(c for c in constraints
                  if c.utterance_constraint is UtteranceToConceptConstraint.LEXICAL_ACCESS)
        assert la.passes is False

    def test_context_resolution_fails_for_low_confidence_referential(self):
        sig, sfd, coup = self._build(referential=True, confidence=0.3)
        constraints = evaluate_constraints(sig, sfd, coup)
        cr = next(c for c in constraints
                  if c.utterance_constraint is UtteranceToConceptConstraint.CONTEXT_RESOLUTION)
        assert cr.passes is False

    def test_context_resolution_passes_for_non_referential(self):
        sig, sfd, coup = self._build()
        constraints = evaluate_constraints(sig, sfd, coup)
        cr = next(c for c in constraints
                  if c.utterance_constraint is UtteranceToConceptConstraint.CONTEXT_RESOLUTION)
        assert cr.passes is True

    def test_concept_selection_fails_when_conceptual_class_missing(self):
        cl = _closure("test", "test", POS.ISM)
        sig = classify_signifier(cl)
        # Manually create a CONCEPTUAL node without a conceptual_class
        sfd = SignifiedNode(
            node_id="SFD_MANUAL",
            signified_class=SignifiedClass.CONCEPTUAL,
            label="test",
            semantic_type=SemanticType.ENTITY,
            conceptual_class=None,
        )
        coup = select_coupling(sig, sfd, DalalaType.MUTABAQA)
        constraints = evaluate_constraints(sig, sfd, coup)
        cs = next(c for c in constraints
                  if c.utterance_constraint is UtteranceToConceptConstraint.CONCEPT_SELECTION)
        assert cs.passes is False

    def test_figurative_disambiguation_passes_with_high_confidence(self):
        cl = _closure("الأسد", "أسد", POS.ISM, root=("أ", "س", "د"))
        c = _concept("رجل شجاع", SemanticType.ENTITY)
        sig = classify_signifier(cl, figurative=True)
        sfd = classify_signified(c)
        coup = CouplingRecord(
            coupling_id="CRP_FIG",
            coupling_type=CouplingRelationType.FIGURATIVE,
            signifier_id=sig.node_id,
            signified_id=sfd.node_id,
            confidence=0.9,
            evidence="metaphor",
        )
        constraints = evaluate_constraints(sig, sfd, coup)
        fd = next(
            c for c in constraints
            if c.utterance_constraint
            is UtteranceToConceptConstraint.FIGURATIVE_DISAMBIGUATION
        )
        assert fd.passes is True

    def test_figurative_disambiguation_fails_with_low_confidence(self):
        cl = _closure("الأسد", "أسد", POS.ISM, root=("أ", "س", "د"))
        c = _concept("رجل شجاع", SemanticType.ENTITY)
        sig = classify_signifier(cl, figurative=True)
        sfd = classify_signified(c)
        coup = CouplingRecord(
            coupling_id="CRP_FIG2",
            coupling_type=CouplingRelationType.FIGURATIVE,
            signifier_id=sig.node_id,
            signified_id=sfd.node_id,
            confidence=0.4,
            evidence="weak metaphor",
        )
        constraints = evaluate_constraints(sig, sfd, coup)
        fd = next(
            c for c in constraints
            if c.utterance_constraint
            is UtteranceToConceptConstraint.FIGURATIVE_DISAMBIGUATION
        )
        assert fd.passes is False
        assert "0.4" in fd.violated_by

    def test_referential_resolution_passes_with_positive_confidence(self):
        sig, sfd, coup = self._build(referential=True, confidence=0.8)
        constraints = evaluate_constraints(sig, sfd, coup)
        rr = next(c for c in constraints
                  if c.utterance_constraint is UtteranceToConceptConstraint.REFERENTIAL_RESOLUTION)
        assert rr.passes is True

    def test_all_constraint_types_represented(self):
        sig, sfd, coup = self._build()
        constraints = evaluate_constraints(sig, sfd, coup)
        utc_types = {c.utterance_constraint for c in constraints}
        for member in UtteranceToConceptConstraint:
            assert member in utc_types, f"Missing constraint: {member}"

    def test_constraint_records_are_frozen(self):
        sig, sfd, coup = self._build()
        constraints = evaluate_constraints(sig, sfd, coup)
        with pytest.raises((AttributeError, TypeError)):
            constraints[0].passes = False  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# build_ontology_record — canonical examples
# ═══════════════════════════════════════════════════════════════════════

class TestBuildOntologyRecord:

    # ── Example 1a: "الأسد" — direct (حقيقي) ─────────────────────────

    def test_asad_direct(self):
        cl = _closure("الأَسَد", "أسد", POS.ISM, root=("أ", "س", "د"))
        c = _concept("أسد", SemanticType.ENTITY, animacy=True)
        rec = build_ontology_record(cl, c, DalalaType.MUTABAQA,
                                    record_id="ONT_ASAD_DIRECT")
        assert isinstance(rec, OntologyV1Record)
        assert rec.record_id == "ONT_ASAD_DIRECT"
        assert rec.signifier.signifier_class is SignifierClass.UTTERED_FORM
        assert rec.signified.signified_class is SignifiedClass.CONCEPTUAL
        assert rec.signified.conceptual_class is ConceptualSignifiedClass.ENTITY_CONCEPT
        assert rec.coupling.coupling_type is CouplingRelationType.DIRECT
        assert rec.valid is True
        assert len(rec.constraints) == 7
        assert len(rec.failed_constraints) == 0

    # ── Example 1b: "الأسد" — figurative (مجازي) ─────────────────────

    def test_asad_figurative(self):
        cl = _closure("الأَسَد", "أسد", POS.ISM, root=("أ", "س", "د"))
        c = _concept("رجل شجاع", SemanticType.ENTITY)
        rec = build_ontology_record(
            cl, c, DalalaType.ILTIZAM,
            figurative=True,
            confidence=0.85,
            record_id="ONT_ASAD_FIG",
        )
        assert rec.record_id == "ONT_ASAD_FIG"
        assert rec.signifier.layer is OntologicalLayer.PATTERN  # figurative=True
        assert rec.coupling.coupling_type is CouplingRelationType.INFERENTIAL
        assert rec.valid is True

    # ── Example 2: "هذا" — referential (إحالي) ───────────────────────

    def test_hadha_referential(self):
        cl = _closure("هَذَا", "هذا", POS.DAMIR, root=("ه", "ذ", "ا"))
        c = _concept("مرجع حاضر", SemanticType.ENTITY)
        rec = build_ontology_record(
            cl, c, DalalaType.IHALA,
            referential=True,
            confidence=0.9,
            record_id="ONT_HADHA",
        )
        assert rec.signified.signified_class is SignifiedClass.REFERENTIAL
        assert rec.coupling.coupling_type is CouplingRelationType.REFERENTIAL_COUPLING
        assert rec.valid is True

    # ── Example 3: "ما زيد إلا قائم" — propositional/restrictive ─────

    def test_ma_zayd_propositional(self):
        cl = _closure("مَا زَيْد إِلَّا قَائِم", "قصر", POS.HARF,
                      root=("م", "ا"))
        c = _concept("حكم القصر", SemanticType.NORM)
        rec = build_ontology_record(
            cl, c, DalalaType.TAQYID,
            record_id="ONT_QASR",
        )
        assert rec.signifier.uttered_form_class is UtteredFormClass.MARKED_UTTERANCE
        assert rec.signified.signified_class is SignifiedClass.NORMATIVE
        assert rec.coupling.coupling_type is CouplingRelationType.HIERARCHICAL
        assert rec.valid is True

    # ── Validity flag reflects constraint failures ────────────────────

    def test_invalid_record_when_surface_empty(self):
        cl = LexicalClosure(surface="", lemma="test", root=(), pattern="", pos=POS.ISM)
        c = _concept("test", SemanticType.ENTITY)
        rec = build_ontology_record(cl, c, DalalaType.MUTABAQA)
        assert rec.valid is False
        assert len(rec.failed_constraints) > 0

    def test_notes_stored(self):
        cl = _closure("زَيْد", "زيد", POS.ISM, root=("ز", "ي", "د"))
        c = _concept("زيد", SemanticType.ENTITY)
        rec = build_ontology_record(cl, c, DalalaType.MUTABAQA, notes="test note")
        assert rec.notes == "test note"

    def test_auto_generated_record_id(self):
        cl = _closure("زَيْد", "زيد", POS.ISM, root=("ز", "ي", "د"))
        c = _concept("زيد", SemanticType.ENTITY)
        r1 = build_ontology_record(cl, c, DalalaType.MUTABAQA)
        r2 = build_ontology_record(cl, c, DalalaType.MUTABAQA)
        assert r1.record_id != r2.record_id
        assert r1.record_id.startswith("ONT_")

    def test_record_is_frozen(self):
        cl = _closure("زَيْد", "زيد", POS.ISM, root=("ز", "ي", "د"))
        c = _concept("زيد", SemanticType.ENTITY)
        rec = build_ontology_record(cl, c, DalalaType.MUTABAQA)
        with pytest.raises((AttributeError, TypeError)):
            rec.valid = False  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# batch_build
# ═══════════════════════════════════════════════════════════════════════

class TestBatchBuild:
    def _inputs(self):
        closures = [
            _closure("الأَسَد", "أسد", POS.ISM, root=("أ", "س", "د")),
            _closure("هَذَا", "هذا", POS.DAMIR, root=("ه", "ذ", "ا")),
            _closure("كَتَبَ", "كتب", POS.FI3L),
        ]
        concepts = [
            _concept("أسد", SemanticType.ENTITY),
            _concept("مرجع", SemanticType.ENTITY),
            _concept("كتابة", SemanticType.EVENT),
        ]
        dalala = [DalalaType.MUTABAQA, DalalaType.IHALA, DalalaType.MUTABAQA]
        return closures, concepts, dalala

    def test_returns_correct_count(self):
        closures, concepts, dalala = self._inputs()
        results = batch_build(closures, concepts, dalala)
        assert len(results) == 3

    def test_all_are_ontology_records(self):
        closures, concepts, dalala = self._inputs()
        for rec in batch_build(closures, concepts, dalala):
            assert isinstance(rec, OntologyV1Record)

    def test_referential_flags_applied(self):
        closures, concepts, dalala = self._inputs()
        results = batch_build(closures, concepts, dalala,
                              referential_flags=[False, True, False])
        assert results[1].signified.signified_class is SignifiedClass.REFERENTIAL
        assert results[0].signified.signified_class is not SignifiedClass.REFERENTIAL

    def test_figurative_flags_applied(self):
        closures, concepts, dalala = self._inputs()
        results = batch_build(closures, concepts, dalala,
                              figurative_flags=[True, False, False])
        assert results[0].signifier.layer is OntologicalLayer.PATTERN

    def test_empty_input(self):
        assert batch_build([], [], []) == []


# ═══════════════════════════════════════════════════════════════════════
# Re-exports from arabic_engine.core
# ═══════════════════════════════════════════════════════════════════════

class TestCoreReexports:
    def test_enum_reexports(self):
        from arabic_engine.core import (  # noqa: F401
            ConceptualSignifiedClass,
            CouplingRelationType,
            OntologicalConstraintType,
            SignifiedClass,
            SignifierClass,
            UtteranceToConceptConstraint,
            UtteredFormClass,
        )

    def test_type_reexports(self):
        from arabic_engine.core import (  # noqa: F401
            CouplingRecord,
            OntologicalConstraintRecord,
            OntologyV1Record,
            SignifiedNode,
            SignifierNode,
        )

    def test_reexported_enums_are_same_objects(self):
        from arabic_engine.core import SignifierClass as SC1
        from arabic_engine.core.enums import SignifierClass as SC2
        assert SC1 is SC2

    def test_reexported_types_are_same_objects(self):
        from arabic_engine.core import SignifierNode as SN1
        from arabic_engine.core.types import SignifierNode as SN2
        assert SN1 is SN2
