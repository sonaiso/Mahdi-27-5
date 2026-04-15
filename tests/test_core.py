"""Tests for core enums and types."""

from __future__ import annotations

from arabic_engine.core.enums import (
    POS,
    ActivationStage,
    DalalaType,
    GuidanceState,
    IrabCase,
    IrabRole,
    MethodFamily,
    SemanticType,
    SpaceRef,
    TimeRef,
    TruthState,
    ValidationState,
)
from arabic_engine.core.types import (
    Concept,
    DalalaLink,
    LexicalClosure,
    Proposition,
    SyntaxNode,
    WorldFact,
)


class TestEnums:
    """Basic enum sanity checks."""

    def test_truth_state_has_certain(self):
        assert TruthState.CERTAIN is not None

    def test_guidance_state_exists(self):
        assert hasattr(GuidanceState, "NOT_APPLICABLE")

    def test_pos_has_ism(self):
        assert POS.ISM is not None

    def test_pos_has_fi3l(self):
        assert POS.FI3L is not None


class TestEnumsComprehensive:
    """Comprehensive enum member checks."""

    def test_pos_has_harf(self):
        assert POS.HARF is not None

    def test_pos_has_sifa(self):
        assert POS.SIFA is not None

    def test_dalala_type_mutabaqa(self):
        assert DalalaType.MUTABAQA is not None

    def test_dalala_type_tadammun(self):
        assert DalalaType.TADAMMUN is not None

    def test_dalala_type_iltizam(self):
        assert DalalaType.ILTIZAM is not None

    def test_dalala_type_isnad(self):
        assert DalalaType.ISNAD is not None

    def test_irab_case_values(self):
        assert IrabCase.UNKNOWN is not None
        assert IrabCase.RAF3 is not None
        assert IrabCase.NASB is not None
        assert IrabCase.JARR is not None

    def test_irab_role_values(self):
        assert IrabRole.FI3L is not None
        assert IrabRole.FA3IL is not None
        assert IrabRole.MAF3UL_BIH is not None
        assert IrabRole.UNKNOWN is not None

    def test_semantic_type_values(self):
        assert SemanticType.ENTITY is not None
        assert SemanticType.EVENT is not None
        assert SemanticType.ATTRIBUTE is not None
        assert SemanticType.RELATION is not None

    def test_time_ref_has_unspecified(self):
        assert TimeRef.UNSPECIFIED is not None

    def test_space_ref_has_unspecified(self):
        assert SpaceRef.UNSPECIFIED is not None

    def test_validation_state_values(self):
        assert ValidationState.PENDING is not None
        assert ValidationState.VALID is not None

    def test_method_family_values(self):
        assert MethodFamily.RATIONAL is not None
        assert MethodFamily.SCIENTIFIC is not None
        assert MethodFamily.LINGUISTIC is not None
        assert MethodFamily.MATHEMATICAL is not None
        assert MethodFamily.PHYSICAL is not None

    def test_activation_stage_values(self):
        assert ActivationStage.SIGNAL is not None
        assert ActivationStage.CONCEPT is not None
        assert ActivationStage.AXIS is not None


class TestCoreTypes:
    """Core dataclass sanity checks."""

    def test_lexical_closure_defaults(self):
        lc = LexicalClosure(
            surface="كتب", lemma="كتب", root=("ك", "ت", "ب"),
            pattern="فَعَلَ", pos=POS.FI3L,
        )
        assert lc.confidence == 1.0

    def test_lexical_closure_fields(self):
        lc = LexicalClosure(
            surface="كتب", lemma="كتب", root=("ك", "ت", "ب"),
            pattern="فَعَلَ", pos=POS.FI3L,
        )
        assert lc.surface == "كتب"
        assert lc.lemma == "كتب"
        assert lc.root == ("ك", "ت", "ب")
        assert lc.pattern == "فَعَلَ"
        assert lc.pos == POS.FI3L

    def test_concept_defaults(self):
        c = Concept(concept_id=1, label="كتاب", semantic_type=SemanticType.ENTITY)
        assert c.properties == {}

    def test_concept_fields(self):
        c = Concept(concept_id=1, label="كتاب", semantic_type=SemanticType.ENTITY)
        assert c.concept_id == 1
        assert c.label == "كتاب"
        assert c.semantic_type == SemanticType.ENTITY

    def test_dalala_link_fields(self):
        dl = DalalaLink(
            source_lemma="كتب", target_concept_id=1,
            dalala_type=DalalaType.MUTABAQA, accepted=True, confidence=0.9,
        )
        assert dl.source_lemma == "كتب"
        assert dl.target_concept_id == 1
        assert dl.dalala_type == DalalaType.MUTABAQA
        assert dl.accepted is True
        assert dl.confidence == 0.9

    def test_proposition_defaults(self):
        p = Proposition(subject="s", predicate="p", obj="o")
        assert p.polarity is True
        assert p.time == TimeRef.UNSPECIFIED

    def test_proposition_fields(self):
        p = Proposition(subject="s", predicate="p", obj="o")
        assert p.subject == "s"
        assert p.predicate == "p"
        assert p.obj == "o"

    def test_syntax_node_fields(self):
        sn = SyntaxNode(
            token="كتب", lemma="كتب", pos=POS.FI3L,
            case=IrabCase.UNKNOWN, role=IrabRole.FI3L,
        )
        assert sn.token == "كتب"
        assert sn.lemma == "كتب"
        assert sn.role == IrabRole.FI3L
        assert sn.case == IrabCase.UNKNOWN

    def test_world_fact_defaults(self):
        wf = WorldFact(fact_id=1, subject="s", predicate="p", obj="o")
        assert wf.truth_state == TruthState.CERTAIN
        assert wf.source == "axiom"
