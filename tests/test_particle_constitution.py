"""Tests for the Particle Fractal Constitution — باب الحرف الفراكتالي.

Invariants tested
-----------------
1. Particle catalog loads and contains expected entries.
2. Registry lookup, classify, and is_particle work correctly.
3. Minimal completeness holds for all catalog particles.
4. Fractal score ≥ θ₂ for all catalog particles.
5. validate_particle accepts known particles and rejects non-particles.
6. Particle dalala (mutabaqa, tadammun, iltizam) returns correct values.
7. Pipeline integration: sentences with particles produce particle hypotheses.
8. New enums and types are properly re-exported.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    ActivationStage,
    ParticleRelationType,
    ParticleType,
)
from arabic_engine.core.types import (
    ParticleFractalScore,
    ParticleMinimalCompleteness,
    ParticleRecord,
)
from arabic_engine.particle.dalala import iltizam, mutabaqa, tadammun
from arabic_engine.particle.registry import (
    all_forms,
    classify,
    forms_by_type,
    is_particle,
    load_catalog,
    lookup,
)
from arabic_engine.particle.validation import (
    check_minimal_completeness,
    compute_fractal_score,
    validate_particle,
    validate_record,
)
from arabic_engine.runtime.orchestrator import run

# ═══════════════════════════════════════════════════════════════════════
# Phase 1: Core types
# ═══════════════════════════════════════════════════════════════════════


class TestCoreTypes:
    """ParticleType, ParticleRelationType, ParticleRecord, etc."""

    def test_particle_type_has_12_members(self):
        assert len(ParticleType) == 12

    def test_particle_relation_type_has_7_members(self):
        assert len(ParticleRelationType) == 7

    def test_particle_record_frozen(self):
        r = ParticleRecord(
            form="في",
            particle_type=ParticleType.JARR,
            relation_type=ParticleRelationType.RESTRICTION,
            scope="noun",
            direction="ظرفية",
            effect="jarr",
        )
        with pytest.raises(AttributeError):
            r.form = "من"  # type: ignore[misc]

    def test_particle_fractal_score_computation(self):
        fs = ParticleFractalScore(
            identification=1.0,
            preservation=1.0,
            binding=1.0,
            judgment=1.0,
            transition=1.0,
            return_trace=1.0,
        )
        assert fs.fractal_score == 1.0

    def test_particle_fractal_score_partial(self):
        fs = ParticleFractalScore(
            identification=1.0,
            preservation=0.0,
            binding=1.0,
            judgment=0.0,
            transition=1.0,
            return_trace=0.0,
        )
        assert abs(fs.fractal_score - 0.5) < 1e-9

    def test_particle_minimal_completeness_all_true(self):
        mc = ParticleMinimalCompleteness(
            existence=True,
            boundary=True,
            extension=True,
            constituent=True,
            structural_relation=True,
            regularity=True,
            unity=True,
            assignability=True,
        )
        assert mc.is_complete is True

    def test_particle_minimal_completeness_one_false(self):
        mc = ParticleMinimalCompleteness(
            existence=True,
            boundary=True,
            extension=True,
            constituent=True,
            structural_relation=True,
            regularity=True,
            unity=True,
            assignability=False,
        )
        assert mc.is_complete is False

    def test_activation_stage_includes_particle(self):
        assert hasattr(ActivationStage, "PARTICLE")
        assert ActivationStage.PARTICLE.name == "PARTICLE"


# ═══════════════════════════════════════════════════════════════════════
# Phase 2: Catalog
# ═══════════════════════════════════════════════════════════════════════


class TestCatalog:
    """Particle catalog loading and content."""

    def test_catalog_loads(self):
        cat = load_catalog()
        assert isinstance(cat, dict)
        assert len(cat) >= 30  # at least 30 particles

    def test_catalog_has_key_particles(self):
        cat = load_catalog()
        for form in ["في", "من", "إلى", "على", "هل", "لا", "و", "إنّ"]:
            assert form in cat, f"'{form}' missing from catalog"

    def test_catalog_values_are_particle_records(self):
        cat = load_catalog()
        for form, record in cat.items():
            assert isinstance(record, ParticleRecord)
            assert record.form == form


# ═══════════════════════════════════════════════════════════════════════
# Phase 3: Registry
# ═══════════════════════════════════════════════════════════════════════


class TestRegistry:
    """Registry lookup, classify, is_particle."""

    def test_lookup_existing(self):
        r = lookup("في")
        assert r is not None
        assert r.form == "في"
        assert r.particle_type == ParticleType.JARR

    def test_lookup_missing(self):
        assert lookup("كتب") is None

    def test_classify_jarr(self):
        assert classify("في") == ParticleType.JARR
        assert classify("من") == ParticleType.JARR
        assert classify("إلى") == ParticleType.JARR

    def test_classify_atf(self):
        assert classify("و") == ParticleType.ATF
        assert classify("ثم") == ParticleType.ATF

    def test_classify_nafy(self):
        assert classify("لا") == ParticleType.NAFY
        assert classify("لم") == ParticleType.NAFY

    def test_classify_istifham(self):
        assert classify("هل") == ParticleType.ISTIFHAM

    def test_classify_mashabbah(self):
        assert classify("إنّ") == ParticleType.MASHABBAH
        assert classify("ليت") == ParticleType.MASHABBAH

    def test_classify_shart(self):
        assert classify("إن") == ParticleType.SHART
        assert classify("لو") == ParticleType.SHART

    def test_classify_nida(self):
        assert classify("يا") == ParticleType.NIDA

    def test_classify_unknown(self):
        assert classify("كتب") is None

    def test_is_particle(self):
        assert is_particle("في") is True
        assert is_particle("من") is True
        assert is_particle("كتب") is False

    def test_all_forms(self):
        forms = all_forms()
        assert isinstance(forms, frozenset)
        assert len(forms) >= 30

    def test_forms_by_type(self):
        jarr = forms_by_type(ParticleType.JARR)
        assert "في" in jarr
        assert "من" in jarr
        assert "إلى" in jarr
        assert "كتب" not in jarr


# ═══════════════════════════════════════════════════════════════════════
# Phase 3b: Validation
# ═══════════════════════════════════════════════════════════════════════


class TestValidation:
    """Minimal completeness and fractal score."""

    @pytest.mark.parametrize("form", ["في", "من", "لا", "هل", "و", "إنّ"])
    def test_minimal_completeness_representative(self, form: str):
        r = lookup(form)
        assert r is not None
        mc = check_minimal_completeness(r)
        assert mc.is_complete is True

    def test_all_catalog_particles_minimally_complete(self):
        for form, record in load_catalog().items():
            mc = check_minimal_completeness(record)
            assert mc.is_complete, f"'{form}' fails minimal completeness"

    @pytest.mark.parametrize("form", ["في", "من", "لا", "هل", "و", "إنّ"])
    def test_fractal_score_above_threshold(self, form: str):
        r = lookup(form)
        assert r is not None
        fs = compute_fractal_score(r)
        assert fs.fractal_score >= 0.5

    def test_all_catalog_particles_fractal_valid(self):
        for form, record in load_catalog().items():
            fs = compute_fractal_score(record)
            assert fs.fractal_score >= 0.5, (
                f"'{form}' fractal score {fs.fractal_score:.3f} < 0.5"
            )

    def test_validate_particle_accepts_known(self):
        assert validate_particle("في") is True
        assert validate_particle("من") is True
        assert validate_particle("هل") is True

    def test_validate_particle_rejects_unknown(self):
        assert validate_particle("كتب") is False
        assert validate_particle("زيد") is False
        assert validate_particle("") is False

    def test_validate_record(self):
        r = lookup("في")
        assert r is not None
        assert validate_record(r) is True


# ═══════════════════════════════════════════════════════════════════════
# Phase 3c: Dalala
# ═══════════════════════════════════════════════════════════════════════


class TestDalala:
    """Particle signification — mutabaqa, tadammun, iltizam."""

    def test_mutabaqa_fi(self):
        r = lookup("في")
        assert r is not None
        assert mutabaqa(r) == "ظرفية"

    def test_mutabaqa_min(self):
        r = lookup("من")
        assert r is not None
        assert mutabaqa(r) == "ابتداء"

    def test_mutabaqa_la(self):
        r = lookup("لا")
        assert r is not None
        assert mutabaqa(r) == "نفي"

    def test_tadammun(self):
        r = lookup("في")
        assert r is not None
        result = tadammun(r)
        assert result["scope"] == "noun"
        assert result["particle_type"] == "JARR"
        assert result["relation_type"] == "RESTRICTION"

    def test_iltizam_fi(self):
        r = lookup("في")
        assert r is not None
        commitments = iltizam(r)
        assert any("jarr" in c for c in commitments)
        assert any("اسم" in c for c in commitments)

    def test_iltizam_lam(self):
        r = lookup("لم")
        assert r is not None
        commitments = iltizam(r)
        assert any("jazm" in c for c in commitments)

    def test_iltizam_hal(self):
        r = lookup("هل")
        assert r is not None
        commitments = iltizam(r)
        assert any("جملة" in c for c in commitments)


# ═══════════════════════════════════════════════════════════════════════
# Phase 4: Pipeline integration
# ═══════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    """Particle hypothesis generation in the fractal kernel pipeline."""

    def test_sentence_with_preposition_produces_particle_hyps(self):
        state = run("ذهب إلى المدرسة")
        particle_hyps = state.hypotheses.hypotheses.get(
            ActivationStage.PARTICLE, []
        )
        assert len(particle_hyps) >= 1

    def test_particle_hypothesis_has_expected_payload(self):
        state = run("ذهب إلى المدرسة")
        particle_hyps = state.hypotheses.hypotheses.get(
            ActivationStage.PARTICLE, []
        )
        if particle_hyps:
            h = particle_hyps[0]
            assert h.hypothesis_type == "particle"
            assert h.get("particle_type") is not None
            assert h.get("relation_type") is not None
            assert h.get("direction") is not None
            assert h.get("fractal_score") is not None

    def test_sentence_without_particles_produces_no_particle_hyps(self):
        state = run("كتب الرسالة")
        particle_hyps = state.hypotheses.hypotheses.get(
            ActivationStage.PARTICLE, []
        )
        # "كتب الرسالة" has no particles in the catalog
        assert len(particle_hyps) == 0

    def test_multiple_particles(self):
        state = run("لم يذهب إلى المدرسة")
        particle_hyps = state.hypotheses.hypotheses.get(
            ActivationStage.PARTICLE, []
        )
        # "لم" and "إلى" are both particles
        assert len(particle_hyps) >= 2

    def test_all_activated_still_stabilized(self):
        """Ensure the pipeline still stabilizes correctly."""
        state = run("ذهب إلى المدرسة")
        from arabic_engine.core.enums import HypothesisStatus
        for h in state.decisions.activated:
            assert h.status == HypothesisStatus.STABILIZED


# ═══════════════════════════════════════════════════════════════════════
# Phase 8b: Re-exports
# ═══════════════════════════════════════════════════════════════════════


class TestReExports:
    """New particle symbols are accessible from arabic_engine.core."""

    def test_enums_re_exported(self):
        import arabic_engine.core as core
        assert hasattr(core, "ParticleType")
        assert hasattr(core, "ParticleRelationType")

    def test_types_re_exported(self):
        import arabic_engine.core as core
        assert hasattr(core, "ParticleRecord")
        assert hasattr(core, "ParticleFractalScore")
        assert hasattr(core, "ParticleMinimalCompleteness")


# ═══════════════════════════════════════════════════════════════════════
# Phase 6: Closure
# ═══════════════════════════════════════════════════════════════════════


class TestClosure:
    """Particle constitution closure check."""

    def test_closure_includes_particle_layer(self):
        from arabic_engine.closure import verify_general_closure
        result = verify_general_closure()
        particle_verdicts = [
            v for v in result.verdicts if v.layer_name == "particle_constitution"
        ]
        assert len(particle_verdicts) >= 1
        from arabic_engine.closure import ClosureStatus
        assert all(v.status == ClosureStatus.CLOSED for v in particle_verdicts)
