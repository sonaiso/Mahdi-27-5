"""Tests for the signified v2.0 layer.

Covers:
  * All 20 new enums: member counts and specific member names
  * Concept v2 fields: default None, assignment, independence from v1
  * ConceptRelation dataclass
  * SignifiedNode and SignifiedKind
  * build_signified_node factory
  * ConceptNetwork: add / query / error paths
  * Backwards-compatibility: existing pipeline concepts still work
"""

from __future__ import annotations

import pytest

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
from arabic_engine.signified.signified_v2 import (
    AXIS_KIND_MAP,
    ConceptNetwork,
    SignifiedKind,
    SignifiedNode,
    build_signified_node,
)

# ── helpers ──────────────────────────────────────────────────────────

def _concept(cid: int = 1, label: str = "test") -> Concept:
    return Concept(concept_id=cid, label=label, semantic_type=SemanticType.ENTITY)


# ═══════════════════════════════════════════════════════════════════════
# 1. Enum member counts and spot-checks
# ═══════════════════════════════════════════════════════════════════════

class TestEpistemicStatus:
    def test_member_count(self):
        assert len(EpistemicStatus) == 10

    def test_members(self):
        names = {m.name for m in EpistemicStatus}
        assert "CERTAIN" in names
        assert "IMPOSSIBLE" in names
        assert "AXIOMATIC" in names
        assert "THEORETICAL" in names


class TestNormativeCategory:
    def test_member_count(self):
        assert len(NormativeCategory) == 10

    def test_members(self):
        names = {m.name for m in NormativeCategory}
        assert "OBLIGATORY" in names
        assert "FORBIDDEN" in names
        assert "JUST" in names
        assert "UNJUST" in names
        assert "NEUTRAL" in names


class TestAffectiveDimension:
    def test_member_count(self):
        assert len(AffectiveDimension) == 12

    def test_members(self):
        names = {m.name for m in AffectiveDimension}
        assert "LOVE" in names
        assert "AWE" in names
        assert "ALIENATION" in names
        assert "NEUTRAL" in names


class TestMentalIntentionalType:
    def test_member_count(self):
        assert len(MentalIntentionalType) == 10

    def test_members(self):
        names = {m.name for m in MentalIntentionalType}
        assert "BELIEF" in names
        assert "INTENTION" in names
        assert "AWARENESS" in names


class TestModalCategory:
    def test_member_count(self):
        assert len(ModalCategory) == 6

    def test_members(self):
        names = {m.name for m in ModalCategory}
        assert "POSSIBLE" in names
        assert "COUNTERFACTUAL" in names
        assert "ACTUAL" in names


class TestFrameType:
    def test_member_count(self):
        assert len(FrameType) == 10

    def test_none_member(self):
        assert FrameType.NONE is not None

    def test_members(self):
        names = {m.name for m in FrameType}
        assert "COMMERCIAL" in names
        assert "GOVERNANCE" in names
        assert "RELIGIOUS" in names


class TestScriptPhase:
    def test_member_count(self):
        assert len(ScriptPhase) == 7

    def test_members(self):
        names = {m.name for m in ScriptPhase}
        assert "PRECONDITION" in names
        assert "CLIMAX" in names
        assert "POSTCONDITION" in names


class TestCausalRole:
    def test_member_count(self):
        assert len(CausalRole) == 10

    def test_members(self):
        names = {m.name for m in CausalRole}
        assert "CAUSE" in names
        assert "MECHANISM" in names
        assert "LAW" in names
        assert "NONE" in names


class TestInstitutionalCategory:
    def test_member_count(self):
        assert len(InstitutionalCategory) == 10

    def test_members(self):
        names = {m.name for m in InstitutionalCategory}
        assert "STATE" in names
        assert "CONTRACT" in names
        assert "CURRENCY" in names
        assert "RITUAL" in names


class TestCategorizationMode:
    def test_member_count(self):
        assert len(CategorizationMode) == 5

    def test_members(self):
        names = {m.name for m in CategorizationMode}
        assert "CLASSICAL" in names
        assert "PROTOTYPE_BASED" in names
        assert "RADIAL" in names


class TestCulturalScope:
    def test_member_count(self):
        assert len(CulturalScope) == 5

    def test_members(self):
        names = {m.name for m in CulturalScope}
        assert "UNIVERSAL" in names
        assert "RELIGIOUS_SPECIFIC" in names


class TestDiachronicStatus:
    def test_member_count(self):
        assert len(DiachronicStatus) == 7

    def test_members(self):
        names = {m.name for m in DiachronicStatus}
        assert "ORIGINAL" in names
        assert "OBSOLETE" in names
        assert "SPECIALIZED" in names


class TestConceptFormationMode:
    def test_member_count(self):
        assert len(ConceptFormationMode) == 6

    def test_members(self):
        names = {m.name for m in ConceptFormationMode}
        assert "PRIMITIVE" in names
        assert "BLENDED" in names
        assert "METAPHORICAL" in names


class TestMetaConceptualLevel:
    def test_member_count(self):
        assert len(MetaConceptualLevel) == 3

    def test_members(self):
        names = {m.name for m in MetaConceptualLevel}
        assert "FIRST_ORDER" in names
        assert "SECOND_ORDER" in names
        assert "THIRD_ORDER" in names


class TestInterpretiveStability:
    def test_member_count(self):
        assert len(InterpretiveStability) == 5

    def test_members(self):
        names = {m.name for m in InterpretiveStability}
        assert "STABLE" in names
        assert "CONTESTED" in names
        assert "POLYSEMOUS" in names


class TestSalienceLevel:
    def test_member_count(self):
        assert len(SalienceLevel) == 6

    def test_members(self):
        names = {m.name for m in SalienceLevel}
        assert "CENTRAL" in names
        assert "UNEXPECTED" in names


class TestEmbodiedDomain:
    def test_member_count(self):
        assert len(EmbodiedDomain) == 10

    def test_members(self):
        names = {m.name for m in EmbodiedDomain}
        assert "VISUAL" in names
        assert "CONTAINMENT" in names
        assert "VERTICAL_AXIS" in names
        assert "NONE" in names


class TestSelfModelAspect:
    def test_member_count(self):
        assert len(SelfModelAspect) == 7

    def test_members(self):
        names = {m.name for m in SelfModelAspect}
        assert "EGO" in names
        assert "PERSONAL_CONTINUITY" in names
        assert "NONE" in names


class TestOperationalCapacity:
    def test_member_count(self):
        assert len(OperationalCapacity) == 7

    def test_members(self):
        names = {m.name for m in OperationalCapacity}
        assert "ENABLES" in names
        assert "PROMISES" in names
        assert "NONE" in names


class TestConceptRelationType:
    def test_member_count(self):
        assert len(ConceptRelationType) == 10

    def test_members(self):
        names = {m.name for m in ConceptRelationType}
        assert "IS_A" in names
        assert "PART_OF" in names
        assert "PRESUPPOSES" in names
        assert "REGULATES" in names


# ═══════════════════════════════════════════════════════════════════════
# 2. Concept v2 field defaults and assignment
# ═══════════════════════════════════════════════════════════════════════

class TestConceptV2Fields:
    def test_v1_fields_unchanged(self):
        c = _concept(42, "مفهوم")
        assert c.concept_id == 42
        assert c.label == "مفهوم"
        assert c.semantic_type == SemanticType.ENTITY
        assert c.properties == {}

    def test_all_v2_axes_default_none(self):
        c = _concept()
        axes = [
            "epistemic_status", "normative_category", "affective_dimension",
            "mental_intentional_type", "modal_category", "frame_type",
            "script_phase", "causal_role", "institutional_category",
            "categorization_mode", "cultural_scope", "diachronic_status",
            "formation_mode", "meta_level", "interpretive_stability",
            "salience", "embodied_domain", "self_model_aspect",
            "operational_capacity",
        ]
        for axis in axes:
            assert getattr(c, axis) is None, f"{axis} should default to None"

    def test_assign_epistemic_status(self):
        c = _concept()
        c.epistemic_status = EpistemicStatus.CERTAIN
        assert c.epistemic_status == EpistemicStatus.CERTAIN

    def test_assign_multiple_axes(self):
        c = _concept()
        c.epistemic_status = EpistemicStatus.PROBABLE
        c.modal_category = ModalCategory.POSSIBLE
        c.cultural_scope = CulturalScope.UNIVERSAL
        assert c.epistemic_status == EpistemicStatus.PROBABLE
        assert c.modal_category == ModalCategory.POSSIBLE
        assert c.cultural_scope == CulturalScope.UNIVERSAL

    def test_two_concepts_independent(self):
        c1 = _concept(1)
        c2 = _concept(2)
        c1.epistemic_status = EpistemicStatus.CERTAIN
        assert c2.epistemic_status is None


# ═══════════════════════════════════════════════════════════════════════
# 3. ConceptRelation
# ═══════════════════════════════════════════════════════════════════════

class TestConceptRelation:
    def test_basic_construction(self):
        rel = ConceptRelation(
            source_id=1,
            target_id=2,
            relation_type=ConceptRelationType.IS_A,
        )
        assert rel.source_id == 1
        assert rel.target_id == 2
        assert rel.relation_type == ConceptRelationType.IS_A
        assert rel.weight == 1.0
        assert rel.notes == ""

    def test_custom_weight_and_notes(self):
        rel = ConceptRelation(
            source_id=10,
            target_id=20,
            relation_type=ConceptRelationType.CAUSES,
            weight=0.75,
            notes="سبب جزئي",
        )
        assert rel.weight == 0.75
        assert rel.notes == "سبب جزئي"

    def test_all_relation_types_constructible(self):
        for rtype in ConceptRelationType:
            rel = ConceptRelation(source_id=1, target_id=2, relation_type=rtype)
            assert rel.relation_type == rtype


# ═══════════════════════════════════════════════════════════════════════
# 4. SignifiedKind
# ═══════════════════════════════════════════════════════════════════════

class TestSignifiedKind:
    def test_member_count(self):
        assert len(SignifiedKind) == 4

    def test_members(self):
        names = {m.name for m in SignifiedKind}
        assert names == {"TYPE", "AXIS", "RELATION", "CONSTRAINT"}


# ═══════════════════════════════════════════════════════════════════════
# 5. AXIS_KIND_MAP
# ═══════════════════════════════════════════════════════════════════════

class TestAxisKindMap:
    def test_total_entries(self):
        # 19 optional axes + semantic_type = 20
        assert len(AXIS_KIND_MAP) == 20

    def test_type_axes(self):
        type_axes = [k for k, v in AXIS_KIND_MAP.items() if v == SignifiedKind.TYPE]
        assert "semantic_type" in type_axes
        assert "mental_intentional_type" in type_axes
        assert "institutional_category" in type_axes
        assert "meta_level" in type_axes
        assert "self_model_aspect" in type_axes

    def test_relation_axes(self):
        rel_axes = [k for k, v in AXIS_KIND_MAP.items() if v == SignifiedKind.RELATION]
        assert "causal_role" in rel_axes

    def test_constraint_axes(self):
        con_axes = [k for k, v in AXIS_KIND_MAP.items() if v == SignifiedKind.CONSTRAINT]
        assert "frame_type" in con_axes
        assert "interpretive_stability" in con_axes

    def test_axis_axes(self):
        ax_axes = [k for k, v in AXIS_KIND_MAP.items() if v == SignifiedKind.AXIS]
        assert "epistemic_status" in ax_axes
        assert "modal_category" in ax_axes
        assert "affective_dimension" in ax_axes


# ═══════════════════════════════════════════════════════════════════════
# 6. SignifiedNode
# ═══════════════════════════════════════════════════════════════════════

class TestSignifiedNode:
    def test_construction_defaults(self):
        node = SignifiedNode(concept=_concept())
        assert node.kind == SignifiedKind.TYPE

    def test_shortcut_properties(self):
        c = _concept(7, "حرية")
        node = SignifiedNode(concept=c, kind=SignifiedKind.AXIS)
        assert node.concept_id == 7
        assert node.label == "حرية"
        assert node.semantic_type == SemanticType.ENTITY

    def test_populated_axes_empty_by_default(self):
        node = SignifiedNode(concept=_concept())
        assert node.populated_axes() == {}

    def test_populated_axes_after_assignment(self):
        c = _concept()
        c.epistemic_status = EpistemicStatus.CERTAIN
        c.modal_category = ModalCategory.ACTUAL
        node = SignifiedNode(concept=c)
        populated = node.populated_axes()
        assert populated["epistemic_status"] == EpistemicStatus.CERTAIN
        assert populated["modal_category"] == ModalCategory.ACTUAL
        assert len(populated) == 2

    def test_axis_kind_known_field(self):
        node = SignifiedNode(concept=_concept())
        assert node.axis_kind("epistemic_status") == SignifiedKind.AXIS
        assert node.axis_kind("causal_role") == SignifiedKind.RELATION
        assert node.axis_kind("frame_type") == SignifiedKind.CONSTRAINT
        assert node.axis_kind("semantic_type") == SignifiedKind.TYPE

    def test_axis_kind_unknown_field(self):
        node = SignifiedNode(concept=_concept())
        assert node.axis_kind("nonexistent_field") is None


# ═══════════════════════════════════════════════════════════════════════
# 7. build_signified_node
# ═══════════════════════════════════════════════════════════════════════

class TestBuildSignifiedNode:
    def test_no_axes(self):
        node = build_signified_node(_concept())
        assert node.kind == SignifiedKind.TYPE
        assert node.populated_axes() == {}

    def test_single_axis(self):
        node = build_signified_node(
            _concept(),
            epistemic_status=EpistemicStatus.PROBABLE,
        )
        assert node.concept.epistemic_status == EpistemicStatus.PROBABLE

    def test_multiple_axes(self):
        node = build_signified_node(
            _concept(),
            epistemic_status=EpistemicStatus.CERTAIN,
            modal_category=ModalCategory.NECESSARY,
            cultural_scope=CulturalScope.UNIVERSAL,
            formation_mode=ConceptFormationMode.PRIMITIVE,
        )
        c = node.concept
        assert c.epistemic_status == EpistemicStatus.CERTAIN
        assert c.modal_category == ModalCategory.NECESSARY
        assert c.cultural_scope == CulturalScope.UNIVERSAL
        assert c.formation_mode == ConceptFormationMode.PRIMITIVE

    def test_custom_kind(self):
        node = build_signified_node(_concept(), kind=SignifiedKind.CONSTRAINT)
        assert node.kind == SignifiedKind.CONSTRAINT

    def test_all_axes(self):
        node = build_signified_node(
            _concept(),
            epistemic_status=EpistemicStatus.DOUBTFUL,
            normative_category=NormativeCategory.FORBIDDEN,
            affective_dimension=AffectiveDimension.FEAR,
            mental_intentional_type=MentalIntentionalType.BELIEF,
            modal_category=ModalCategory.POSSIBLE,
            frame_type=FrameType.RELIGIOUS,
            script_phase=ScriptPhase.INITIATION,
            causal_role=CausalRole.CAUSE,
            institutional_category=InstitutionalCategory.LAW,
            categorization_mode=CategorizationMode.PROTOTYPE_BASED,
            cultural_scope=CulturalScope.RELIGIOUS_SPECIFIC,
            diachronic_status=DiachronicStatus.ORIGINAL,
            formation_mode=ConceptFormationMode.PRIMITIVE,
            meta_level=MetaConceptualLevel.FIRST_ORDER,
            interpretive_stability=InterpretiveStability.STABLE,
            salience=SalienceLevel.CENTRAL,
            embodied_domain=EmbodiedDomain.NONE,
            self_model_aspect=SelfModelAspect.NONE,
            operational_capacity=OperationalCapacity.NONE,
        )
        assert len(node.populated_axes()) == 19

    def test_none_axes_not_written(self):
        c = _concept()
        c.epistemic_status = EpistemicStatus.CERTAIN
        # Passing None for an axis should NOT overwrite a previously set value
        build_signified_node(c, epistemic_status=None)
        # None kwarg is ignored, existing value preserved
        assert c.epistemic_status == EpistemicStatus.CERTAIN

    def test_none_axes_unset_field_stays_none(self):
        c = _concept()
        # axis was None before; passing None for it should leave it None
        assert c.modal_category is None
        build_signified_node(c, modal_category=None)
        assert c.modal_category is None


# ═══════════════════════════════════════════════════════════════════════
# 8. ConceptNetwork
# ═══════════════════════════════════════════════════════════════════════

def _node(cid: int, label: str = "") -> SignifiedNode:
    return SignifiedNode(concept=_concept(cid, label or str(cid)))


class TestConceptNetwork:
    def test_empty_network(self):
        net = ConceptNetwork()
        assert net.node_count() == 0
        assert net.relation_count() == 0

    def test_add_node(self):
        net = ConceptNetwork()
        net.add_node(_node(1, "حيوان"))
        assert net.node_count() == 1
        assert 1 in net.nodes

    def test_add_node_replaces_existing(self):
        net = ConceptNetwork()
        net.add_node(_node(1, "قديم"))
        net.add_node(_node(1, "جديد"))
        assert net.node_count() == 1
        assert net.nodes[1].label == "جديد"

    def test_add_relation(self):
        net = ConceptNetwork()
        net.add_node(_node(1))
        net.add_node(_node(2))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
        assert net.relation_count() == 1

    def test_add_relation_unknown_source_raises(self):
        net = ConceptNetwork()
        net.add_node(_node(2))
        with pytest.raises(KeyError, match="99"):
            net.add_relation(ConceptRelation(99, 2, ConceptRelationType.IS_A))

    def test_add_relation_unknown_target_raises(self):
        net = ConceptNetwork()
        net.add_node(_node(1))
        with pytest.raises(KeyError, match="99"):
            net.add_relation(ConceptRelation(1, 99, ConceptRelationType.IS_A))

    def test_get_related_outgoing(self):
        net = ConceptNetwork()
        net.add_node(_node(1, "إنسان"))
        net.add_node(_node(2, "حيوان"))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
        related = list(net.get_related(1))
        assert len(related) == 1
        assert related[0].label == "حيوان"

    def test_get_related_incoming(self):
        net = ConceptNetwork()
        net.add_node(_node(1, "إنسان"))
        net.add_node(_node(2, "حيوان"))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
        related = list(net.get_related(2, direction="incoming"))
        assert len(related) == 1
        assert related[0].label == "إنسان"

    def test_get_related_filtered_by_type(self):
        net = ConceptNetwork()
        net.add_node(_node(1))
        net.add_node(_node(2))
        net.add_node(_node(3))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
        net.add_relation(ConceptRelation(1, 3, ConceptRelationType.CAUSES))
        # Only IS_A
        isa = list(net.get_related(1, relation_type=ConceptRelationType.IS_A))
        assert len(isa) == 1
        assert isa[0].concept_id == 2
        # Only CAUSES
        causes = list(net.get_related(1, relation_type=ConceptRelationType.CAUSES))
        assert len(causes) == 1
        assert causes[0].concept_id == 3

    def test_get_related_no_matches(self):
        net = ConceptNetwork()
        net.add_node(_node(1))
        net.add_node(_node(2))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
        result = list(net.get_related(2))  # no outgoing from 2
        assert result == []

    def test_multiple_relations_same_pair(self):
        net = ConceptNetwork()
        net.add_node(_node(1))
        net.add_node(_node(2))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.IS_A))
        net.add_relation(ConceptRelation(1, 2, ConceptRelationType.ENABLES))
        assert net.relation_count() == 2
        related = list(net.get_related(1))
        assert len(related) == 2


# ═══════════════════════════════════════════════════════════════════════
# 9. Backwards compatibility with existing pipeline
# ═══════════════════════════════════════════════════════════════════════

class TestBackwardsCompatibility:
    """Ensure the v2 Concept can be used wherever v1 Concept was used."""

    def test_ontology_map_concept_still_works(self):
        from arabic_engine.core.enums import POS
        from arabic_engine.core.types import LexicalClosure
        from arabic_engine.signified.ontology import map_concept

        closure = LexicalClosure(
            surface="كَتَبَ", lemma="كَتَبَ", root=("ك", "ت", "ب"),
            pattern="فَعَلَ", pos=POS.FI3L,
        )
        c = map_concept(closure)
        # v1 fields present
        assert c.semantic_type == SemanticType.EVENT
        # v2 fields absent (None) — no regression
        assert c.epistemic_status is None
        assert c.modal_category is None

    def test_pipeline_run_produces_concept_with_none_axes(self):
        from arabic_engine.pipeline import run
        result = run("زَيْدٌ كَتَبَ رِسَالَةً")
        for concept in result.concepts:
            # All v2 axes should be None (pipeline not yet enriched)
            assert concept.epistemic_status is None

    def test_concept_import_from_core(self):
        from arabic_engine.core import Concept as CoreConcept
        assert CoreConcept is Concept

    def test_concept_relation_import_from_core(self):
        from arabic_engine.core import ConceptRelation as CoreCR
        assert CoreCR is ConceptRelation
