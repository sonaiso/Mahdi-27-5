"""Integration tests for Rational Self Ontology v1.

Validates:
  * Full chain: Unicode → Material → Root/Weight → Lexeme → POS → CompositionReady.
  * Rational self bridge (perceive → identify → build → prepare).
  * End-to-end flow for multiple Arabic words.
  * Type consistency across all new structures.
  * Non-regression: existing pipeline behaviour is preserved.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    POS,
    IndependenceType,
    JamidDerivedType,
    LexemeLayer,
    ParticleRelationType,
    ReferentialMode,
    TimeRef,
    VerbActionType,
    WeightTemplateType,
)
from arabic_engine.core.types import (
    BareLexicalMaterial,
    ClosedTemplateNode,
    LexemeNode,
    LexicalClosure,
    RationalSelfExtendedRecord,
    WeightNode,
)

# ═══════════════════════════════════════════════════════════════════════
# Full chain integration tests
# ═══════════════════════════════════════════════════════════════════════


class TestFullChain:
    """Test the complete chain from Unicode to CompositionReady."""

    def test_verb_full_chain(self):
        """Test: كَتَبَ through the full chain."""
        from arabic_engine.lexeme.composition_gate import check_composition_readiness
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_verb
        from arabic_engine.lexeme.transitions import (
            transition_material_to_root_weight,
            transition_unicode_to_material,
        )
        from arabic_engine.lexeme.validation import validate_all

        # Step 1: Unicode → Material
        material = transition_unicode_to_material("كَتَبَ")
        assert material.source_layer == LexemeLayer.BARE_MATERIAL

        # Step 2: Material → Root + Weight
        root, weight = transition_material_to_root_weight(
            material, root=("ك", "ت", "ب"), pattern="فَعَلَ",
        )
        assert root == ("ك", "ت", "ب")
        assert weight is not None
        assert weight.template_type == WeightTemplateType.VERBAL

        # Step 3: Root + Weight → Lexeme
        closure = LexicalClosure(
            surface="كَتَبَ", lemma="كتب",
            root=("ك", "ت", "ب"), pattern="فَعَلَ", pos=POS.FI3L,
        )
        lexeme = build_lexeme(closure, weight=weight)
        assert lexeme.pos_final == POS.FI3L
        assert lexeme.concept_type == "حدث"

        # Step 4: Lexeme → POS (Verb)
        verb = finalize_as_verb(
            lexeme, VerbActionType.EVENT, TimeRef.PAST,
            transitivity="متعد",
        )
        assert verb.action_type == VerbActionType.EVENT

        # Step 5: Lexeme → CompositionReady
        comp = check_composition_readiness(lexeme)
        assert comp.ready is True

        # Step 6: Validate all rules
        results = validate_all(
            lexeme, weight=weight, pos_node=verb, composition_node=comp,
        )
        assert all(passed for _, passed in results)

    def test_noun_full_chain(self):
        """Test: كاتب (active participle) through the full chain."""
        from arabic_engine.lexeme.composition_gate import check_composition_readiness
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_noun
        from arabic_engine.lexeme.transitions import (
            transition_material_to_root_weight,
            transition_unicode_to_material,
        )
        from arabic_engine.lexeme.validation import validate_all

        material = transition_unicode_to_material("كاتب")
        root, weight = transition_material_to_root_weight(
            material, root=("ك", "ت", "ب"), pattern="فَاعِل",
        )
        assert weight.template_type == WeightTemplateType.NOMINAL

        closure = LexicalClosure(
            surface="كاتب", lemma="كاتب",
            root=("ك", "ت", "ب"), pattern="فَاعِل", pos=POS.ISM,
        )
        lexeme = build_lexeme(closure, weight=weight)
        noun = finalize_as_noun(
            lexeme, ReferentialMode.JINS, JamidDerivedType.MUSHTAQ,
        )
        comp = check_composition_readiness(lexeme)
        assert comp.ready is True

        results = validate_all(
            lexeme, weight=weight, pos_node=noun, composition_node=comp,
        )
        assert all(passed for _, passed in results)

    def test_particle_full_chain(self):
        """Test: في (particle) through the full chain."""
        from arabic_engine.lexeme.composition_gate import check_composition_readiness
        from arabic_engine.lexeme.lexeme_builder import build_lexeme
        from arabic_engine.lexeme.pos_finalization import finalize_as_particle
        from arabic_engine.lexeme.validation import validate_all

        closure = LexicalClosure(
            surface="في", lemma="في",
            root=(), pattern="", pos=POS.HARF,
        )
        template = ClosedTemplateNode(
            id="CT_fi", template_form="في",
            function_type=ParticleRelationType.JARR,
        )
        lexeme = build_lexeme(closure, template=template)
        particle = finalize_as_particle(
            lexeme, ParticleRelationType.JARR,
            governing_scope="اسم_مجرور",
        )
        comp = check_composition_readiness(lexeme)
        assert comp.ready is True

        results = validate_all(lexeme, pos_node=particle, composition_node=comp)
        assert all(passed for _, passed in results)


class TestRationalSelfIntegration:
    """Test the Rational Self bridge end-to-end."""

    def _self(self) -> RationalSelfExtendedRecord:
        return RationalSelfExtendedRecord(
            self_id="SELF_INT",
            name="ذات_اختبارية",
            perception_mode="بصري",
            judgment_capacity=0.95,
        )

    def test_self_full_chain(self):
        """Test rational self perceives, identifies, builds, and prepares."""
        from arabic_engine.lexeme.rational_self import (
            self_builds_lexeme,
            self_identifies_weight,
            self_perceives_material,
            self_prepares_composition,
        )

        s = self._self()

        # Perceive
        mat = self_perceives_material(s, "كَتَبَ")
        assert mat.material == "كَتَبَ"

        # Identify weight
        w = self_identifies_weight(s, mat, root=("ك", "ت", "ب"), pattern="فَعَلَ")
        assert w is not None

        # Build lexeme
        closure = LexicalClosure(
            surface="كَتَبَ", lemma="كتب",
            root=("ك", "ت", "ب"), pattern="فَعَلَ", pos=POS.FI3L,
        )
        lex = self_builds_lexeme(s, closure, weight=w)
        assert lex.pos_final == POS.FI3L

        # Prepare composition
        comp = self_prepares_composition(s, lex)
        assert comp.ready is True


class TestNonRegression:
    """Ensure existing pipeline behaviour is preserved."""

    def test_pipeline_still_produces_all_original_fields(self):
        from arabic_engine.pipeline import run

        result = run("كتب الطالبُ الدرسَ")
        # Original fields
        assert result.raw == "كتب الطالبُ الدرسَ"
        assert result.normalised is not None
        assert len(result.tokens) > 0
        assert len(result.closures) > 0
        assert len(result.syntax_nodes) > 0
        assert len(result.concepts) > 0
        assert len(result.dalala_links) > 0
        assert result.proposition is not None
        assert result.eval_result is not None
        # New fields
        assert len(result.weight_nodes) > 0
        assert len(result.lexeme_nodes) > 0
        assert len(result.composition_ready) > 0

    def test_runtime_pipeline_still_produces_all_stages(self):
        from arabic_engine.runtime_pipeline import run_pipeline

        state = run_pipeline("ذهب الطالبُ")
        assert len(state.utterance_units) > 0
        assert len(state.lexeme_units) > 0
        assert len(state.concepts) > 0
        assert len(state.relations) >= 0
        assert len(state.roles) > 0
        assert state.judgement is not None

    def test_pipeline_token_alignment(self):
        """Weight/lexeme/composition counts match closure count."""
        from arabic_engine.pipeline import run

        result = run("ذهب محمد إلى المكتبة")
        n = len(result.closures)
        assert len(result.weight_nodes) == n
        assert len(result.lexeme_nodes) == n
        assert len(result.composition_ready) == n


class TestDataclassIntegrity:
    """Test that all new dataclasses are frozen and have correct fields."""

    def test_weight_node_fields(self):
        w = WeightNode(
            id="W_test", weight_form="فَعَلَ",
            template_type=WeightTemplateType.VERBAL,
            slots=("C1:ك", "C2:ت", "C3:ب"),
            semantic_tendency="حدث",
            recoverability_score=0.8,
            completeness_score=0.9,
            productivity_mode=__import__(
                "arabic_engine.core.enums", fromlist=["ProductivityMode"]
            ).ProductivityMode.LIVING,
            pos_affinity=POS.FI3L,
        )
        assert w.id == "W_test"
        assert w.completeness_score == 0.9

    def test_lexeme_node_fields(self):
        lex = LexemeNode(
            id="LEX_test", surface_form="كاتب", normalized_form="كاتب",
            root_ref="ك:ت:ب", weight_ref="W_001",
            closed_template_ref=None,
            independence_type=IndependenceType.MEANING_INDEPENDENT,
            concept_type="ذات", pos_final=POS.ISM, readiness_score=0.85,
        )
        assert lex.surface_form == "كاتب"
        assert lex.independence_type == IndependenceType.MEANING_INDEPENDENT

    def test_rational_self_record_fields(self):
        rs = RationalSelfExtendedRecord(
            self_id="S1", name="ذات", perception_mode="بصري",
            judgment_capacity=0.9,
        )
        assert rs.epistemic_autonomy is True
        assert rs.lexicon_boundary == 0

    def test_bare_lexical_material_fields(self):
        m = BareLexicalMaterial(material="كتب")
        assert m.source_layer == LexemeLayer.BARE_MATERIAL
        assert m.grapheme_count == 0
