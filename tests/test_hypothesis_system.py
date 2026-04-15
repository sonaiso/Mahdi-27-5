"""Comprehensive tests for the arabic_engine/hypothesis/ modules.

Covers every generator stage from morphology through judgements,
end-to-end pipeline integrity, and edge-case inputs.
"""

from __future__ import annotations

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode
from arabic_engine.hypothesis import (
    axes,
    cases,
    concepts,
    factors,
    judgements,
    morphology,
    relations,
    roles,
)
from arabic_engine.signal.normalization import normalize_atoms
from arabic_engine.signal.segmentation import segment
from arabic_engine.signal.unicode_atoms import decompose

# ── helpers ──────────────────────────────────────────────────────────


def _build_segments(text: str = "كتب الرسالة") -> list[HypothesisNode]:
    """Produce segmentation hypotheses from raw Arabic text."""
    atoms = decompose(text)
    units, _ = normalize_atoms(atoms)
    return segment(units)


def _build_morph(text: str = "كتب الرسالة") -> list[HypothesisNode]:
    return morphology.generate(_build_segments(text))


def _build_concepts(text: str = "كتب الرسالة") -> list[HypothesisNode]:
    return concepts.generate(_build_morph(text))


def _build_roles(text: str = "كتب الرسالة") -> list[HypothesisNode]:
    return roles.generate(_build_concepts(text))


def _build_axes(text: str = "كتب الرسالة") -> list[HypothesisNode]:
    return axes.generate(_build_concepts(text))


def _full_pipeline(
    text: str = "كتب الرسالة",
) -> dict[str, list[HypothesisNode]]:
    """Run the entire hypothesis pipeline and return every stage."""
    segs = _build_segments(text)
    morph = morphology.generate(segs)
    conc = concepts.generate(morph)
    rol = roles.generate(conc)
    ax = axes.generate(conc)
    rel = relations.generate(conc)
    fac = factors.generate(rol, conc)
    cas = cases.generate(rol, fac)
    jud = judgements.generate(cas, conc, rol)
    return {
        "segments": segs,
        "morphology": morph,
        "concepts": conc,
        "roles": rol,
        "axes": ax,
        "relations": rel,
        "factors": fac,
        "cases": cas,
        "judgements": jud,
    }


# ═══════════════════════════════════════════════════════════════════════
# 1. Morphology
# ═══════════════════════════════════════════════════════════════════════


class TestMorphology:
    def test_generate_produces_list(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        assert isinstance(hyps, list)
        assert all(isinstance(h, HypothesisNode) for h in hyps)

    def test_hypothesis_type(self):
        hyps = _build_morph()
        allowed = {"morphology", "morphology_masdar"}
        for h in hyps:
            assert h.hypothesis_type in allowed

    def test_stage_is_morphology(self):
        for h in _build_morph():
            assert h.stage == ActivationStage.MORPHOLOGY

    def test_source_refs_reference_segments(self):
        segs = _build_segments()
        seg_ids = {s.node_id for s in segs}
        hyps = morphology.generate(segs)
        for h in hyps:
            assert len(h.source_refs) > 0
            for ref in h.source_refs:
                assert ref in seg_ids

    def test_confidence_valid(self):
        for h in _build_morph():
            assert 0.0 < h.confidence <= 1.0

    def test_status_active(self):
        for h in _build_morph():
            assert h.status == HypothesisStatus.ACTIVE

    def test_empty_input(self):
        assert morphology.generate([]) == []

    def test_count_matches_segments(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        assert len(hyps) == len(segs)


# ═══════════════════════════════════════════════════════════════════════
# 2. Concepts
# ═══════════════════════════════════════════════════════════════════════


class TestConcepts:
    def test_generate_from_morph(self):
        conc = _build_concepts()
        assert isinstance(conc, list)
        assert len(conc) > 0

    def test_stage_is_concept(self):
        for h in _build_concepts():
            assert h.stage == ActivationStage.CONCEPT

    def test_payload_has_label_and_semantic_type(self):
        for h in _build_concepts():
            assert h.get("label") is not None
            assert h.get("semantic_type") is not None

    def test_source_refs_link_to_morph(self):
        morph = _build_morph()
        morph_ids = {m.node_id for m in morph}
        conc = concepts.generate(morph)
        for h in conc:
            assert len(h.source_refs) > 0
            for ref in h.source_refs:
                assert ref in morph_ids

    def test_concept_count(self):
        assert len(_build_concepts()) == 2

    def test_hypothesis_type(self):
        for h in _build_concepts():
            assert h.hypothesis_type == "concept"

    def test_status_active(self):
        for h in _build_concepts():
            assert h.status == HypothesisStatus.ACTIVE


# ═══════════════════════════════════════════════════════════════════════
# 3. Roles
# ═══════════════════════════════════════════════════════════════════════


class TestRoles:
    def test_generate_from_concepts(self):
        rol = _build_roles()
        assert isinstance(rol, list)
        assert len(rol) > 0

    def test_stage_is_role(self):
        for h in _build_roles():
            assert h.stage == ActivationStage.ROLE

    def test_payload_has_role_key(self):
        for h in _build_roles():
            assert h.get("role") is not None

    def test_verb_sentence_roles(self):
        rol = _build_roles()
        role_values = {h.get("role") for h in rol}
        assert role_values & {"فعل", "فاعل", "مفعول"}

    def test_source_refs_link_to_concepts(self):
        conc = _build_concepts()
        conc_ids = {c.node_id for c in conc}
        rol = roles.generate(conc)
        for h in rol:
            assert len(h.source_refs) > 0
            for ref in h.source_refs:
                assert ref in conc_ids

    def test_hypothesis_type(self):
        for h in _build_roles():
            assert h.hypothesis_type == "role"

    def test_preposition_roles(self):
        rol = _build_roles("في البيت")
        role_values = {h.get("role") for h in rol}
        assert "حرف_جر" in role_values
        assert "مجرور" in role_values


# ═══════════════════════════════════════════════════════════════════════
# 4. Axes
# ═══════════════════════════════════════════════════════════════════════


class TestAxes:
    def test_generate_from_concepts(self):
        ax = _build_axes()
        assert isinstance(ax, list)
        assert len(ax) > 0

    def test_stage_is_axis(self):
        for h in _build_axes():
            assert h.stage == ActivationStage.AXIS

    def test_six_axes_per_concept(self):
        conc = _build_concepts()
        ax = axes.generate(conc)
        assert len(ax) == 6 * len(conc)

    def test_total_twelve_for_two_concepts(self):
        assert len(_build_axes()) == 12

    def test_payload_has_axis_keys(self):
        for h in _build_axes():
            assert h.get("axis_name") is not None
            assert h.get("axis_value") is not None

    def test_axis_names_cover_six_types(self):
        ax = _build_axes()
        names = {h.get("axis_name") for h in ax}
        expected = {
            "معرفة/نكرة",
            "جامد/مشتق",
            "مبني/معرب",
            "كلي/جزئي",
            "ثابت/متحول",
            "زمني/مكاني",
        }
        assert names == expected

    def test_source_refs_link_to_concepts(self):
        conc = _build_concepts()
        conc_ids = {c.node_id for c in conc}
        ax = axes.generate(conc)
        for h in ax:
            for ref in h.source_refs:
                assert ref in conc_ids

    def test_hypothesis_type(self):
        for h in _build_axes():
            assert h.hypothesis_type == "axis"


# ═══════════════════════════════════════════════════════════════════════
# 5. Relations
# ═══════════════════════════════════════════════════════════════════════


class TestRelations:
    def test_generate_from_concepts(self):
        conc = _build_concepts()
        rel = relations.generate(conc)
        assert isinstance(rel, list)
        assert len(rel) > 0

    def test_stage_is_relation(self):
        conc = _build_concepts()
        for h in relations.generate(conc):
            assert h.stage == ActivationStage.RELATION

    def test_payload_has_relation_type(self):
        conc = _build_concepts()
        for h in relations.generate(conc):
            assert h.get("relation_type") is not None

    def test_isnad_for_verb_sentence(self):
        conc = _build_concepts()
        rel = relations.generate(conc)
        rel_types = {h.get("relation_type") for h in rel}
        assert "إسناد" in rel_types

    def test_source_refs_pair_concepts(self):
        conc = _build_concepts()
        conc_ids = {c.node_id for c in conc}
        rel = relations.generate(conc)
        for h in rel:
            assert len(h.source_refs) >= 2
            for ref in h.source_refs:
                assert ref in conc_ids

    def test_hypothesis_type(self):
        conc = _build_concepts()
        for h in relations.generate(conc):
            assert h.hypothesis_type == "relation"

    def test_single_relation_for_two_concepts(self):
        conc = _build_concepts()
        rel = relations.generate(conc)
        assert len(rel) == 1


# ═══════════════════════════════════════════════════════════════════════
# 6. Factors
# ═══════════════════════════════════════════════════════════════════════


class TestFactors:
    def test_generate_from_roles_and_concepts(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        assert isinstance(fac, list)
        assert len(fac) > 0

    def test_stage_is_factor(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        for h in factors.generate(rol, conc):
            assert h.stage == ActivationStage.FACTOR

    def test_payload_has_factor_keys(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        for h in factors.generate(rol, conc):
            assert h.get("factor_type") is not None
            assert h.get("factor_value") is not None or h.get("factor_type") is not None

    def test_count_matches_roles(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        assert len(fac) == len(rol)

    def test_source_refs_link_to_roles(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        role_ids = {r.node_id for r in rol}
        for h in factors.generate(rol, conc):
            assert len(h.source_refs) > 0
            assert any(ref in role_ids for ref in h.source_refs)

    def test_hypothesis_type(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        for h in factors.generate(rol, conc):
            assert h.hypothesis_type == "factor"


# ═══════════════════════════════════════════════════════════════════════
# 7. Cases
# ═══════════════════════════════════════════════════════════════════════


class TestCases:
    def test_generate_from_roles_and_factors(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        assert isinstance(cas, list)
        assert len(cas) > 0

    def test_stage_is_case(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        for h in cases.generate(rol, fac):
            assert h.stage == ActivationStage.CASE

    def test_payload_has_role_and_case_state(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        for h in cases.generate(rol, fac):
            assert h.get("role") is not None
            assert h.get("case_state") is not None

    def test_count_matches_roles(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        assert len(cas) == len(rol)

    def test_source_refs_link_to_roles_and_factors(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        role_ids = {r.node_id for r in rol}
        fac_ids = {f.node_id for f in fac}
        combined = role_ids | fac_ids
        for h in cases.generate(rol, fac):
            for ref in h.source_refs:
                assert ref in combined

    def test_hypothesis_type(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        for h in cases.generate(rol, fac):
            assert h.hypothesis_type == "case"

    def test_verb_is_mabni(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        verb_cases = [h for h in cas if h.get("role") == "فعل"]
        assert any(h.get("case_state") == "مبني" for h in verb_cases)


# ═══════════════════════════════════════════════════════════════════════
# 8. Judgements
# ═══════════════════════════════════════════════════════════════════════


class TestJudgements:
    def test_generate_produces_judgement(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        jud = judgements.generate(cas, conc, rol)
        assert isinstance(jud, list)
        assert len(jud) > 0

    def test_stage_is_judgement(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        for h in judgements.generate(cas, conc, rol):
            assert h.stage == ActivationStage.JUDGEMENT

    def test_payload_has_proposition_type(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        for h in judgements.generate(cas, conc, rol):
            assert h.get("proposition_type") is not None

    def test_declarative_proposition(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        jud = judgements.generate(cas, conc, rol)
        assert jud[0].get("proposition_type") == "تقريرية"

    def test_single_judgement(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        jud = judgements.generate(cas, conc, rol)
        assert len(jud) == 1

    def test_confidence_value(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        jud = judgements.generate(cas, conc, rol)
        assert abs(jud[0].confidence - 0.7909) < 0.01

    def test_hypothesis_type(self):
        conc = _build_concepts()
        rol = roles.generate(conc)
        fac = factors.generate(rol, conc)
        cas = cases.generate(rol, fac)
        for h in judgements.generate(cas, conc, rol):
            assert h.hypothesis_type == "judgement"


# ═══════════════════════════════════════════════════════════════════════
# 9. End-to-end pipeline
# ═══════════════════════════════════════════════════════════════════════


class TestEndToEnd:
    def test_stage_counts(self):
        p = _full_pipeline()
        assert len(p["segments"]) == 2
        assert len(p["morphology"]) == 2
        assert len(p["concepts"]) == 2
        assert len(p["roles"]) == 2
        assert len(p["axes"]) == 12
        assert len(p["relations"]) == 1
        assert len(p["factors"]) == 2
        assert len(p["cases"]) == 2
        assert len(p["judgements"]) == 1

    def test_node_ids_unique_across_stages(self):
        p = _full_pipeline()
        all_ids: list[str] = []
        for stage_nodes in p.values():
            all_ids.extend(n.node_id for n in stage_nodes)
        assert len(all_ids) == len(set(all_ids))

    def test_source_refs_chain(self):
        """Verify each stage's source_refs reference the preceding stage."""
        p = _full_pipeline()
        seg_ids = {n.node_id for n in p["segments"]}
        morph_ids = {n.node_id for n in p["morphology"]}
        conc_ids = {n.node_id for n in p["concepts"]}
        role_ids = {n.node_id for n in p["roles"]}
        fac_ids = {n.node_id for n in p["factors"]}

        for m in p["morphology"]:
            assert all(r in seg_ids for r in m.source_refs)
        for c in p["concepts"]:
            assert all(r in morph_ids for r in c.source_refs)
        for r in p["roles"]:
            assert all(ref in conc_ids for ref in r.source_refs)
        for a in p["axes"]:
            assert all(ref in conc_ids for ref in a.source_refs)
        for rel in p["relations"]:
            assert all(ref in conc_ids for ref in rel.source_refs)
        for f in p["factors"]:
            assert all(ref in role_ids for ref in f.source_refs)
        for c in p["cases"]:
            assert all(
                ref in role_ids | fac_ids for ref in c.source_refs
            )

    def test_all_nodes_active(self):
        p = _full_pipeline()
        for stage_nodes in p.values():
            for n in stage_nodes:
                assert n.status == HypothesisStatus.ACTIVE

    def test_all_confidences_valid(self):
        p = _full_pipeline()
        for stage_nodes in p.values():
            for n in stage_nodes:
                assert 0.0 < n.confidence <= 1.0

    def test_stages_correct(self):
        p = _full_pipeline()
        stage_map = {
            "segments": ActivationStage.SIGNAL,
            "morphology": ActivationStage.MORPHOLOGY,
            "concepts": ActivationStage.CONCEPT,
            "roles": ActivationStage.ROLE,
            "axes": ActivationStage.AXIS,
            "relations": ActivationStage.RELATION,
            "factors": ActivationStage.FACTOR,
            "cases": ActivationStage.CASE,
            "judgements": ActivationStage.JUDGEMENT,
        }
        for key, expected_stage in stage_map.items():
            for n in p[key]:
                assert n.stage == expected_stage, (
                    f"{key}: expected {expected_stage}, got {n.stage}"
                )


# ═══════════════════════════════════════════════════════════════════════
# 10. Edge cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    def test_single_word(self):
        segs = _build_segments("كتب")
        assert len(segs) == 1
        morph = morphology.generate(segs)
        assert len(morph) == 1
        assert morph[0].stage == ActivationStage.MORPHOLOGY

    def test_preposition_phrase(self):
        p = _full_pipeline("في البيت")
        assert len(p["segments"]) == 2
        role_vals = {h.get("role") for h in p["roles"]}
        assert "حرف_جر" in role_vals
        assert "مجرور" in role_vals

    def test_empty_segment_list(self):
        assert morphology.generate([]) == []
        assert concepts.generate([]) == []
        assert roles.generate([]) == []
        assert axes.generate([]) == []
        assert relations.generate([]) == []
        assert factors.generate([], []) == []
        assert cases.generate([], []) == []
        jud = judgements.generate([])
        assert len(jud) == 1
        assert jud[0].get("proposition_type") == "غير محدد"

    def test_single_word_full_pipeline(self):
        p = _full_pipeline("كتب")
        assert len(p["segments"]) == 1
        assert len(p["morphology"]) == 1
        assert len(p["concepts"]) == 1
        for stage_nodes in p.values():
            for n in stage_nodes:
                assert isinstance(n, HypothesisNode)
