"""Tests for the Lexeme Epistemic Core — نواة اللفظ المفرد المعرفية.

Validates:
  * Weight extraction for known forms (فاعل, مفعول, افتعل, استفعل).
  * Weight template classification (nominal / verbal / closed).
  * Completeness and recoverability scoring.
  * Productivity assessment.
  * Lexeme building from LexicalClosure.
  * Independence determination.
  * Readiness scoring.
  * POS finalisation (noun / verb / particle).
  * Auto-finalisation.
  * Composition readiness gate.
  * Recovery rules (RR-01 … RR-06).
  * Validation rules (RS-01 … RS-12).
  * Transition rules (material → weight → lexeme → POS → composition).
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    POS,
    CompositionReadiness,
    IndependenceType,
    JamidDerivedType,
    LexemeEdgeType,
    LexemeLayer,
    MatchingMode,
    ParticleRelationType,
    ProductivityMode,
    ReferentialMode,
    TimeRef,
    VerbActionType,
    WeightTemplateType,
)
from arabic_engine.core.types import (
    BareLexicalMaterial,
    ClosedTemplateNode,
    CompositionReadyNode,
    LexemeNode,
    LexicalClosure,
    NounNode,
    ParticleNode,
    RationalSelfExtendedRecord,
    VerbNode,
    WeightNode,
)

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def _closure(
    surface: str,
    lemma: str,
    pos: POS,
    root: tuple[str, ...] = ("ك", "ت", "ب"),
    pattern: str = "فَعَلَ",
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=root,
        pattern=pattern,
        pos=pos,
    )


def _verb_closure() -> LexicalClosure:
    return _closure("كَتَبَ", "كتب", POS.FI3L, ("ك", "ت", "ب"), "فَعَلَ")


def _noun_closure() -> LexicalClosure:
    return _closure("كاتب", "كاتب", POS.ISM, ("ك", "ت", "ب"), "فَاعِل")


def _particle_closure() -> LexicalClosure:
    return _closure("في", "في", POS.HARF, (), "")


# ═══════════════════════════════════════════════════════════════════════
# Enum completeness
# ═══════════════════════════════════════════════════════════════════════

class TestNewEnums:
    """Ensure all new enums have the correct member count."""

    def test_lexeme_layer_count(self):
        assert len(LexemeLayer) == 11

    def test_weight_template_type_count(self):
        assert len(WeightTemplateType) == 3

    def test_productivity_mode_count(self):
        assert len(ProductivityMode) == 3

    def test_independence_type_count(self):
        assert len(IndependenceType) == 3

    def test_jamid_derived_type_count(self):
        assert len(JamidDerivedType) == 2

    def test_verb_action_type_count(self):
        assert len(VerbActionType) == 3

    def test_particle_relation_type_count(self):
        assert len(ParticleRelationType) == 9

    def test_referential_mode_count(self):
        assert len(ReferentialMode) == 6

    def test_matching_mode_count(self):
        assert len(MatchingMode) == 3

    def test_composition_readiness_count(self):
        assert len(CompositionReadiness) == 6

    def test_lexeme_edge_type_count(self):
        assert len(LexemeEdgeType) == 16


# ═══════════════════════════════════════════════════════════════════════
# Weight engine
# ═══════════════════════════════════════════════════════════════════════

class TestWeightEngine:
    """Tests for arabic_engine.lexeme.weight."""

    def test_extract_weight_verbal(self):
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        assert isinstance(w, WeightNode)
        assert w.weight_form == "فَعَلَ"
        assert w.template_type == WeightTemplateType.VERBAL
        assert w.pos_affinity == POS.FI3L

    def test_extract_weight_nominal(self):
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كاتب", "فَاعِل")
        assert w.template_type == WeightTemplateType.NOMINAL
        assert w.pos_affinity == POS.ISM

    def test_extract_weight_completeness(self):
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        assert w.completeness_score >= 0.65
        assert w.completeness_score <= 1.0

    def test_extract_weight_recoverability(self):
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        assert w.recoverability_score > 0.0
        assert w.recoverability_score <= 1.0

    def test_classify_template_verbal(self):
        from arabic_engine.lexeme.weight import classify_template_type

        assert classify_template_type("فَعَلَ") == WeightTemplateType.VERBAL
        assert classify_template_type("اِسْتَفْعَلَ") == WeightTemplateType.VERBAL

    def test_classify_template_nominal(self):
        from arabic_engine.lexeme.weight import classify_template_type

        assert classify_template_type("فَاعِل") == WeightTemplateType.NOMINAL
        assert classify_template_type("مَفْعُول") == WeightTemplateType.NOMINAL

    def test_classify_template_closed(self):
        from arabic_engine.lexeme.weight import classify_template_type

        assert classify_template_type("في") == WeightTemplateType.CLOSED
        assert classify_template_type("من") == WeightTemplateType.CLOSED

    def test_assess_productivity_living(self):
        from arabic_engine.lexeme.weight import assess_productivity

        assert assess_productivity("فَعَلَ") == ProductivityMode.LIVING

    def test_assess_productivity_historical(self):
        from arabic_engine.lexeme.weight import assess_productivity

        assert assess_productivity("اِفْعَلَّ") == ProductivityMode.HISTORICAL

    def test_assess_productivity_closed(self):
        from arabic_engine.lexeme.weight import assess_productivity

        assert assess_productivity("في") == ProductivityMode.CLOSED

    def test_weight_has_slots(self):
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        assert len(w.slots) >= 3
        assert any(s.startswith("C1:") for s in w.slots)

    def test_completeness_max(self):
        from arabic_engine.lexeme.weight import compute_completeness, extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        score = compute_completeness(w)
        assert score == 1.0  # All 8 criteria met

    def test_weight_node_frozen(self):
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        with pytest.raises(AttributeError):
            w.weight_form = "test"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# Lexeme builder
# ═══════════════════════════════════════════════════════════════════════

class TestLexemeBuilder:
    """Tests for arabic_engine.lexeme.lexeme_builder."""

    def test_build_lexeme_noun(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        assert isinstance(lex, LexemeNode)
        assert lex.surface_form == "كاتب"
        assert lex.pos_final == POS.ISM
        assert lex.weight_ref == w.id
        assert lex.concept_type == "ذات"

    def test_build_lexeme_verb(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.weight import extract_weight

        cl = _verb_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        assert lex.pos_final == POS.FI3L
        assert lex.concept_type == "حدث"

    def test_build_lexeme_particle(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme

        cl = _particle_closure()
        template = ClosedTemplateNode(
            id="CT_001", template_form="في",
            function_type=ParticleRelationType.JARR,
        )
        lex = build_lexeme(cl, template=template)
        assert lex.pos_final == POS.HARF
        assert lex.concept_type == "نسبة"
        assert lex.closed_template_ref == "CT_001"

    def test_determine_independence_noun(self):
        from arabic_engine.lexeme.lexeme_builder import determine_independence

        assert determine_independence(POS.ISM, "ذات") == IndependenceType.MEANING_INDEPENDENT

    def test_determine_independence_particle(self):
        from arabic_engine.lexeme.lexeme_builder import determine_independence

        assert determine_independence(POS.HARF, "نسبة") == IndependenceType.FUNCTION_INDEPENDENT

    def test_determine_independence_unknown(self):
        from arabic_engine.lexeme.lexeme_builder import determine_independence

        assert determine_independence(POS.UNKNOWN, "غير_محدد") == IndependenceType.DEPENDENT

    def test_readiness_score_range(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        assert 0.0 <= lex.readiness_score <= 1.0

    def test_lexeme_node_frozen(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme

        cl = _noun_closure()
        lex = build_lexeme(cl)
        with pytest.raises(AttributeError):
            lex.surface_form = "test"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════
# POS finalisation
# ═══════════════════════════════════════════════════════════════════════

class TestPOSFinalization:
    """Tests for arabic_engine.lexeme.pos_finalization."""

    def test_finalize_as_noun(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun

        cl = _noun_closure()
        lex = build_lexeme(cl)
        noun = finalize_as_noun(lex, ReferentialMode.JINS, JamidDerivedType.MUSHTAQ)
        assert isinstance(noun, NounNode)
        assert noun.lexeme_ref == lex.id
        assert noun.referential_mode == ReferentialMode.JINS
        assert noun.jamid_or_derived == JamidDerivedType.MUSHTAQ

    def test_finalize_as_verb(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_verb

        cl = _verb_closure()
        lex = build_lexeme(cl)
        verb = finalize_as_verb(lex, VerbActionType.EVENT, TimeRef.PAST)
        assert isinstance(verb, VerbNode)
        assert verb.action_type == VerbActionType.EVENT
        assert verb.tense_direction == TimeRef.PAST

    def test_finalize_as_particle(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_particle

        cl = _particle_closure()
        lex = build_lexeme(cl)
        particle = finalize_as_particle(lex, ParticleRelationType.JARR)
        assert isinstance(particle, ParticleNode)
        assert particle.relation_type == ParticleRelationType.JARR

    def test_auto_finalize_noun(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import auto_finalize

        cl = _noun_closure()
        lex = build_lexeme(cl)
        result = auto_finalize(lex)
        assert isinstance(result, NounNode)

    def test_auto_finalize_verb(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import auto_finalize

        cl = _verb_closure()
        lex = build_lexeme(cl)
        result = auto_finalize(lex)
        assert isinstance(result, VerbNode)

    def test_auto_finalize_particle(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import auto_finalize

        cl = _particle_closure()
        lex = build_lexeme(cl)
        result = auto_finalize(lex)
        assert isinstance(result, ParticleNode)


# ═══════════════════════════════════════════════════════════════════════
# Composition gate
# ═══════════════════════════════════════════════════════════════════════

class TestCompositionGate:
    """Tests for arabic_engine.lexeme.composition_gate."""

    def test_ready_with_weight(self):
        from arabic_engine.lexeme.composition_gate import (
            check_composition_readiness,
            validate_readiness,
        )
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        node = check_composition_readiness(lex)
        assert isinstance(node, CompositionReadyNode)
        assert node.ready is True
        assert validate_readiness(node) is True

    def test_not_ready_without_weight(self):
        from arabic_engine.lexeme.composition_gate import (
            check_composition_readiness,
            validate_readiness,
        )
        from arabic_engine.lexeme.lexeme_builder import build_lexeme

        cl = _noun_closure()
        lex = build_lexeme(cl)  # No weight
        node = check_composition_readiness(lex)
        assert node.ready is False
        assert validate_readiness(node) is False

    def test_ready_with_template(self):
        from arabic_engine.lexeme.composition_gate import (
            check_composition_readiness,
            validate_readiness,
        )
        from arabic_engine.lexeme.lexeme_builder import build_lexeme

        cl = _particle_closure()
        template = ClosedTemplateNode(
            id="CT_test", template_form="في",
            function_type=ParticleRelationType.JARR,
        )
        lex = build_lexeme(cl, template=template)
        node = check_composition_readiness(lex)
        assert node.ready is True
        assert validate_readiness(node) is True


# ═══════════════════════════════════════════════════════════════════════
# Recovery rules (RR-01 … RR-06)
# ═══════════════════════════════════════════════════════════════════════

class TestRecoveryRules:
    """Tests for arabic_engine.lexeme.recovery."""

    def test_rr01_recover_weight_from_lexeme(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.recovery import recover_weight_from_lexeme
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        ref = recover_weight_from_lexeme(lex)
        assert ref == w.id

    def test_rr02_recover_root_from_weight(self):
        from arabic_engine.lexeme.recovery import recover_root_from_weight
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        root = recover_root_from_weight(w)
        assert root == ("ك", "ت", "ب")

    def test_rr03_recover_concept_from_noun(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun
        from arabic_engine.lexeme.recovery import recover_concept_from_noun

        cl = _noun_closure()
        lex = build_lexeme(cl)
        noun = finalize_as_noun(lex, ReferentialMode.JINS, JamidDerivedType.MUSHTAQ)
        concept = recover_concept_from_noun(noun)
        assert "JINS" in concept
        assert "MUSHTAQ" in concept

    def test_rr04_recover_action_from_verb(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_verb
        from arabic_engine.lexeme.recovery import recover_action_from_verb

        cl = _verb_closure()
        lex = build_lexeme(cl)
        verb = finalize_as_verb(lex, VerbActionType.EVENT, TimeRef.PAST)
        action = recover_action_from_verb(verb)
        assert "EVENT" in action
        assert "PAST" in action

    def test_rr05_recover_relation_from_particle(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_particle
        from arabic_engine.lexeme.recovery import recover_relation_from_particle

        cl = _particle_closure()
        lex = build_lexeme(cl)
        particle = finalize_as_particle(
            lex, ParticleRelationType.JARR, governing_scope="اسم_مجرور",
        )
        relation = recover_relation_from_particle(particle)
        assert "JARR" in relation
        assert "اسم_مجرور" in relation

    def test_rr06_recover_composition_source(self):
        from arabic_engine.lexeme.composition_gate import check_composition_readiness
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.recovery import recover_composition_source
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        comp = check_composition_readiness(lex)
        source = recover_composition_source(comp)
        assert "lexeme_ref" in source
        assert "pos_final" in source
        assert source["ready"] is True


# ═══════════════════════════════════════════════════════════════════════
# Validation rules (RS-01 … RS-12)
# ═══════════════════════════════════════════════════════════════════════

class TestValidationRules:
    """Tests for arabic_engine.lexeme.validation."""

    def test_rs01_valid(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.validation import validate_rs01

        cl = _noun_closure()
        lex = build_lexeme(cl)
        assert validate_rs01(lex) is True

    def test_rs02_independent(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.validation import validate_rs02

        cl = _noun_closure()
        lex = build_lexeme(cl)
        assert validate_rs02(lex) is True

    def test_rs02_dependent_fails(self):
        from arabic_engine.lexeme.validation import validate_rs02

        lex = LexemeNode(
            id="test", surface_form="x", normalized_form="x",
            root_ref=None, weight_ref=None, closed_template_ref=None,
            independence_type=IndependenceType.DEPENDENT,
            concept_type="غير_محدد", pos_final=POS.UNKNOWN,
            readiness_score=0.0,
        )
        assert validate_rs02(lex) is False

    def test_rs03_complete_weight(self):
        from arabic_engine.lexeme.validation import validate_rs03
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        assert validate_rs03(w) is True

    def test_rs04_recoverable_weight(self):
        from arabic_engine.lexeme.validation import validate_rs04
        from arabic_engine.lexeme.weight import extract_weight

        w = extract_weight(("ك", "ت", "ب"), "كَتَبَ", "فَعَلَ")
        assert validate_rs04(w) is True

    def test_rs05_derived_with_ref(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun
        from arabic_engine.lexeme.validation import validate_rs05

        cl = _noun_closure()
        lex = build_lexeme(cl)
        noun = finalize_as_noun(lex, ReferentialMode.JINS, JamidDerivedType.MUSHTAQ)
        assert validate_rs05(noun) is True

    def test_rs06_jamid_with_referential(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun
        from arabic_engine.lexeme.validation import validate_rs06

        cl = _noun_closure()
        lex = build_lexeme(cl)
        noun = finalize_as_noun(lex, ReferentialMode.ALAM, JamidDerivedType.JAMID)
        assert validate_rs06(noun) is True

    def test_rs07_verb_with_action(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_verb
        from arabic_engine.lexeme.validation import validate_rs07

        cl = _verb_closure()
        lex = build_lexeme(cl)
        verb = finalize_as_verb(lex, VerbActionType.EVENT, TimeRef.PAST)
        assert validate_rs07(verb) is True

    def test_rs08_particle_with_relation(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_particle
        from arabic_engine.lexeme.validation import validate_rs08

        cl = _particle_closure()
        lex = build_lexeme(cl)
        particle = finalize_as_particle(lex, ParticleRelationType.JARR)
        assert validate_rs08(particle) is True

    def test_rs09_layer_order(self):
        from arabic_engine.lexeme.validation import validate_rs09

        assert validate_rs09(LexemeLayer.UNICODE, LexemeLayer.GRAPHEME) is True
        assert validate_rs09(LexemeLayer.WEIGHT, LexemeLayer.LEXEME) is True
        assert validate_rs09(LexemeLayer.LEXEME, LexemeLayer.UNICODE) is False

    def test_rs10_composition_ready(self):
        from arabic_engine.lexeme.composition_gate import check_composition_readiness
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.validation import validate_rs10
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        comp = check_composition_readiness(lex)
        assert validate_rs10(comp) is True

    def test_rs11_matching_mode_set(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun
        from arabic_engine.lexeme.validation import validate_rs11

        cl = _noun_closure()
        lex = build_lexeme(cl)
        noun = finalize_as_noun(lex, match_mode=MatchingMode.MUTABAQA)
        assert validate_rs11(noun) is True

    def test_rs12_full_chain(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.validation import validate_rs12
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        assert validate_rs12(lex) is True

    def test_validate_all_noun(self):
        from arabic_engine.lexeme.composition_gate import check_composition_readiness
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun
        from arabic_engine.lexeme.validation import validate_all
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        noun = finalize_as_noun(lex, ReferentialMode.JINS, JamidDerivedType.MUSHTAQ)
        comp = check_composition_readiness(lex)

        results = validate_all(lex, weight=w, pos_node=noun, composition_node=comp)
        assert all(passed for _, passed in results)
        # Check all applicable rules were run
        rule_ids = [r for r, _ in results]
        assert "RS-01" in rule_ids
        assert "RS-03" in rule_ids
        assert "RS-05" in rule_ids
        assert "RS-10" in rule_ids


# ═══════════════════════════════════════════════════════════════════════
# Transitions
# ═══════════════════════════════════════════════════════════════════════

class TestTransitions:
    """Tests for arabic_engine.lexeme.transitions."""

    def test_unicode_to_material(self):
        from arabic_engine.lexeme.transitions import transition_unicode_to_material

        mat = transition_unicode_to_material("كاتب")
        assert isinstance(mat, BareLexicalMaterial)
        assert mat.material == "كاتب"
        assert mat.source_layer == LexemeLayer.BARE_MATERIAL

    def test_material_to_root_weight(self):
        from arabic_engine.lexeme.transitions import transition_material_to_root_weight

        mat = BareLexicalMaterial(material="كَتَبَ")
        root, weight = transition_material_to_root_weight(
            mat, root=("ك", "ت", "ب"), pattern="فَعَلَ",
        )
        assert root == ("ك", "ت", "ب")
        assert isinstance(weight, WeightNode)

    def test_material_to_root_weight_no_root(self):
        from arabic_engine.lexeme.transitions import transition_material_to_root_weight

        mat = BareLexicalMaterial(material="في")
        root, weight = transition_material_to_root_weight(mat)
        assert root is None
        assert weight is None

    def test_root_weight_to_lexeme(self):
        from arabic_engine.lexeme.transitions import transition_root_weight_to_lexeme
        from arabic_engine.lexeme.weight import extract_weight

        cl = _verb_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = transition_root_weight_to_lexeme(cl, weight=w)
        assert isinstance(lex, LexemeNode)

    def test_lexeme_to_pos(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.transitions import transition_lexeme_to_pos

        cl = _verb_closure()
        lex = build_lexeme(cl)
        pos_node = transition_lexeme_to_pos(lex)
        assert isinstance(pos_node, VerbNode)

    def test_pos_to_composition(self):
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.transitions import transition_pos_to_composition
        from arabic_engine.lexeme.weight import extract_weight

        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = build_lexeme(cl, weight=w)
        comp = transition_pos_to_composition(lex)
        assert isinstance(comp, CompositionReadyNode)
        assert comp.ready is True


# ═══════════════════════════════════════════════════════════════════════
# Rational Self bridge
# ═══════════════════════════════════════════════════════════════════════

class TestRationalSelfBridge:
    """Tests for arabic_engine.lexeme.rational_self."""

    def _self_record(self) -> RationalSelfExtendedRecord:
        return RationalSelfExtendedRecord(
            self_id="SELF_001",
            name="ذات_اختبارية",
            perception_mode="بصري",
            judgment_capacity=0.9,
        )

    def test_self_perceives_material(self):
        from arabic_engine.lexeme.rational_self import self_perceives_material

        s = self._self_record()
        mat = self_perceives_material(s, "كاتب")
        assert isinstance(mat, BareLexicalMaterial)
        assert mat.material == "كاتب"

    def test_self_identifies_weight(self):
        from arabic_engine.lexeme.rational_self import (
            self_identifies_weight,
            self_perceives_material,
        )

        s = self._self_record()
        mat = self_perceives_material(s, "كَتَبَ")
        w = self_identifies_weight(s, mat, root=("ك", "ت", "ب"), pattern="فَعَلَ")
        assert isinstance(w, WeightNode)

    def test_self_identifies_weight_no_root(self):
        from arabic_engine.lexeme.rational_self import (
            self_identifies_weight,
            self_perceives_material,
        )

        s = self._self_record()
        mat = self_perceives_material(s, "في")
        w = self_identifies_weight(s, mat)
        assert w is None

    def test_self_builds_lexeme(self):
        from arabic_engine.lexeme.rational_self import self_builds_lexeme

        s = self._self_record()
        cl = _noun_closure()
        lex = self_builds_lexeme(s, cl)
        assert isinstance(lex, LexemeNode)

    def test_self_prepares_composition(self):
        from arabic_engine.lexeme.rational_self import (
            self_builds_lexeme,
            self_prepares_composition,
        )
        from arabic_engine.lexeme.weight import extract_weight

        s = self._self_record()
        cl = _noun_closure()
        w = extract_weight(cl.root, cl.surface, cl.pattern)
        lex = self_builds_lexeme(s, cl, weight=w)
        comp = self_prepares_composition(s, lex)
        assert isinstance(comp, CompositionReadyNode)
        assert comp.ready is True


# ═══════════════════════════════════════════════════════════════════════
# Pipeline integration
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineIntegration:
    """Test that the lexeme core integrates with the existing pipeline."""

    def test_pipeline_produces_lexeme_outputs(self):
        from arabic_engine.pipeline import run

        result = run("كتب الطالبُ الدرسَ")
        assert len(result.weight_nodes) > 0
        assert len(result.lexeme_nodes) > 0
        assert len(result.composition_ready) > 0

    def test_pipeline_lexeme_count_matches_closures(self):
        from arabic_engine.pipeline import run

        result = run("ذهب الطالبُ إلى المدرسة")
        assert len(result.weight_nodes) == len(result.closures)
        assert len(result.lexeme_nodes) == len(result.closures)
        assert len(result.composition_ready) == len(result.closures)

    def test_runtime_pipeline_has_lexeme_stage(self):
        from arabic_engine.runtime_pipeline import run_pipeline

        state = run_pipeline("ذهب الطالبُ إلى المدرسة")
        assert len(state.lexeme_units) > 0

    def test_runtime_pipeline_lexeme_trace(self):
        from arabic_engine.runtime_pipeline import PipelineStage, run_pipeline

        state = run_pipeline("ذهب الطالبُ")
        lexeme_traces = [t for t in state.trace if t.stage == PipelineStage.LEXEME]
        assert len(lexeme_traces) == 1


# ═══════════════════════════════════════════════════════════════════════
# Kernel integration
# ═══════════════════════════════════════════════════════════════════════

class TestKernelIntegration:
    """Test kernel extensions for Rational Self Ontology v1."""

    def test_kernel_has_designates(self):
        from arabic_engine.core.kernel import KernelRelation

        assert hasattr(KernelRelation, "DESIGNATES")
        assert KernelRelation.DESIGNATES.value == "DESIGNATES"

    def test_kernel_has_intends_composition(self):
        from arabic_engine.core.kernel import KernelRelation

        assert hasattr(KernelRelation, "INTENDS_COMPOSITION")
        assert KernelRelation.INTENDS_COMPOSITION.value == "INTENDS_COMPOSITION"

    def test_kernel_designates_pair(self):
        from arabic_engine.core.kernel import (
            KERNEL_RELATION_PAIRS,
            KernelLabel,
            KernelRelation,
        )

        pairs = KERNEL_RELATION_PAIRS[KernelRelation.DESIGNATES]
        assert (KernelLabel.SELF, KernelLabel.CONCEPT) in pairs

    def test_kernel_intends_composition_pair(self):
        from arabic_engine.core.kernel import (
            KERNEL_RELATION_PAIRS,
            KernelLabel,
            KernelRelation,
        )

        pairs = KERNEL_RELATION_PAIRS[KernelRelation.INTENDS_COMPOSITION]
        assert (KernelLabel.SELF, KernelLabel.CONCEPT) in pairs
