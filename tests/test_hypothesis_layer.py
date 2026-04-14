"""Tests for the hypothesis layer (morphology through judgement).

Invariants tested
-----------------
1. No hypothesis without source_refs.
2. Every hypothesis has a valid stage.
3. Each generator produces ACTIVE hypotheses.
4. Downstream generators consume upstream output.
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


def _build_segments(text: str = "كتب الرسالة") -> list[HypothesisNode]:
    """Helper: produce segmentation hypotheses from text."""
    atoms = decompose(text)
    units, _ = normalize_atoms(atoms)
    return segment(units)


# ═══════════════════════════════════════════════════════════════════════
# Morphology
# ═══════════════════════════════════════════════════════════════════════


class TestMorphologyGeneration:
    def test_produces_hypotheses(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        assert len(hyps) >= len(segs)

    def test_all_active(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        for h in hyps:
            assert h.status == HypothesisStatus.ACTIVE

    def test_correct_stage(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        for h in hyps:
            assert h.stage == ActivationStage.MORPHOLOGY

    def test_has_source_refs(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        for h in hyps:
            assert len(h.source_refs) > 0

    def test_has_lemma_in_payload(self):
        segs = _build_segments()
        hyps = morphology.generate(segs)
        for h in hyps:
            assert h.get("lemma") is not None


# ═══════════════════════════════════════════════════════════════════════
# Concepts
# ═══════════════════════════════════════════════════════════════════════


class TestConceptGeneration:
    def test_produces_hypotheses(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        hyps = concepts.generate(morph)
        assert len(hyps) == len(morph)

    def test_correct_stage(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        hyps = concepts.generate(morph)
        for h in hyps:
            assert h.stage == ActivationStage.CONCEPT

    def test_has_source_refs(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        hyps = concepts.generate(morph)
        for h in hyps:
            assert len(h.source_refs) > 0

    def test_has_label(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        hyps = concepts.generate(morph)
        for h in hyps:
            assert h.get("label") is not None


# ═══════════════════════════════════════════════════════════════════════
# Axes
# ═══════════════════════════════════════════════════════════════════════


class TestAxisGeneration:
    def test_produces_multiple_per_concept(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = axes.generate(conc)
        # Each concept gets 6 axes
        assert len(hyps) == len(conc) * 6

    def test_correct_stage(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = axes.generate(conc)
        for h in hyps:
            assert h.stage == ActivationStage.AXIS


# ═══════════════════════════════════════════════════════════════════════
# Relations
# ═══════════════════════════════════════════════════════════════════════


class TestRelationGeneration:
    def test_produces_n_minus_1_relations(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = relations.generate(conc)
        assert len(hyps) == len(conc) - 1

    def test_correct_stage(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = relations.generate(conc)
        for h in hyps:
            assert h.stage == ActivationStage.RELATION

    def test_has_two_source_refs(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = relations.generate(conc)
        for h in hyps:
            assert len(h.source_refs) == 2


# ═══════════════════════════════════════════════════════════════════════
# Roles
# ═══════════════════════════════════════════════════════════════════════


class TestRoleGeneration:
    def test_produces_one_per_concept(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = roles.generate(conc)
        assert len(hyps) == len(conc)

    def test_correct_stage(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        hyps = roles.generate(conc)
        for h in hyps:
            assert h.stage == ActivationStage.ROLE


# ═══════════════════════════════════════════════════════════════════════
# Factors
# ═══════════════════════════════════════════════════════════════════════


class TestFactorGeneration:
    def test_produces_one_per_role(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        hyps = factors.generate(role_h, conc)
        assert len(hyps) == len(role_h)

    def test_correct_stage(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        hyps = factors.generate(role_h, conc)
        for h in hyps:
            assert h.stage == ActivationStage.FACTOR


# ═══════════════════════════════════════════════════════════════════════
# Cases
# ═══════════════════════════════════════════════════════════════════════


class TestCaseGeneration:
    def test_produces_one_per_pair(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        factor_h = factors.generate(role_h, conc)
        hyps = cases.generate(role_h, factor_h)
        assert len(hyps) == len(role_h)

    def test_has_case_state(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        factor_h = factors.generate(role_h, conc)
        hyps = cases.generate(role_h, factor_h)
        for h in hyps:
            assert h.get("case_state") is not None

    def test_has_justification(self):
        """No stabilization without support."""
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        factor_h = factors.generate(role_h, conc)
        hyps = cases.generate(role_h, factor_h)
        for h in hyps:
            assert h.get("justification") is not None
            assert h.get("justification") != ""


# ═══════════════════════════════════════════════════════════════════════
# Judgements
# ═══════════════════════════════════════════════════════════════════════


class TestJudgementGeneration:
    def test_produces_single_judgement(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        factor_h = factors.generate(role_h, conc)
        case_h = cases.generate(role_h, factor_h)
        hyps = judgements.generate(case_h)
        assert len(hyps) == 1

    def test_correct_stage(self):
        segs = _build_segments()
        morph = morphology.generate(segs)
        conc = concepts.generate(morph)
        role_h = roles.generate(conc)
        factor_h = factors.generate(role_h, conc)
        case_h = cases.generate(role_h, factor_h)
        hyps = judgements.generate(case_h)
        assert hyps[0].stage == ActivationStage.JUDGEMENT

    def test_empty_input_still_produces_judgement(self):
        hyps = judgements.generate([])
        assert len(hyps) == 1
        assert hyps[0].confidence == 0.5
