"""Comprehensive tests for arabic_engine.cognition.mafhum (Ch. 21)."""

from __future__ import annotations

import pytest

from arabic_engine.cognition.mafhum import (
    _DEFAULT_MAFHUM_CONFIDENCE,
    analyse_mafhum,
    get_minimal_types,
    verify_irreducibility,
)
from arabic_engine.core.enums import POS, ConstraintType, MafhumType
from arabic_engine.core.types import LexicalClosure, MafhumPillar, Proposition

# ── helpers ─────────────────────────────────────────────────────────

def _cl(surface: str, lemma: str, pos: POS = POS.ISM) -> LexicalClosure:
    """Shortcut to build a minimal LexicalClosure."""
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=(),
        pattern="",
        pos=pos,
    )


def _prop(subject: str = "زيد", predicate: str = "يجب", obj: str = "الزكاة") -> Proposition:
    """Shortcut to build a minimal Proposition."""
    return Proposition(subject=subject, predicate=predicate, obj=obj)


# ── TestGetMinimalTypes ─────────────────────────────────────────────

class TestGetMinimalTypes:
    def test_returns_five_types(self):
        types = get_minimal_types()
        assert len(types) == 5

    def test_correct_order(self):
        types = get_minimal_types()
        assert types == [
            MafhumType.SHART,
            MafhumType.GHAYA,
            MafhumType.ADAD,
            MafhumType.WASF,
            MafhumType.ISHARA,
        ]

    def test_all_are_mafhum_type(self):
        for t in get_minimal_types():
            assert isinstance(t, MafhumType)

    def test_returns_list(self):
        assert isinstance(get_minimal_types(), list)


# ── TestVerifyIrreducibility ────────────────────────────────────────

class TestVerifyIrreducibility:
    def test_all_true(self):
        result = verify_irreducibility()
        assert all(result.values())

    def test_five_domains(self):
        result = verify_irreducibility()
        assert len(result) == 5

    def test_domain_names_present(self):
        result = verify_irreducibility()
        for name in result:
            assert isinstance(name, str)
            assert len(name) > 0

    def test_returns_dict(self):
        assert isinstance(verify_irreducibility(), dict)


# ── TestAnalyseMafhum ───────────────────────────────────────────────

class TestAnalyseMafhum:
    # ── SHART detection ─────────────────────────────────────────

    def test_condition_marker_in_detected_as_shart(self):
        closures = [_cl("إن", "إن", POS.HARF), _cl("جاء", "جاء")]
        results = analyse_mafhum(closures, _prop())
        shart = [r for r in results if r.mafhum_type == MafhumType.SHART]
        assert len(shart) == 1
        assert shart[0].constraint_type == ConstraintType.SHART

    def test_shart_valid_and_confidence(self):
        closures = [_cl("إن", "إن", POS.HARF), _cl("جاء", "جاء")]
        results = analyse_mafhum(closures, _prop())
        shart = [r for r in results if r.mafhum_type == MafhumType.SHART][0]
        assert shart.valid is True
        assert shart.confidence == pytest.approx(_DEFAULT_MAFHUM_CONFIDENCE)

    # ── GHAYA detection ─────────────────────────────────────────

    def test_goal_marker_hatta_detected_as_ghaya(self):
        closures = [_cl("صم", "صم"), _cl("حتى", "حتى")]
        results = analyse_mafhum(closures, _prop())
        ghaya = [r for r in results if r.mafhum_type == MafhumType.GHAYA]
        assert len(ghaya) == 1
        assert ghaya[0].constraint_type == ConstraintType.GHAYA

    # ── ADAD detection ──────────────────────────────────────────

    def test_number_word_detected_as_adad(self):
        closures = [_cl("واحد", "واحد"), _cl("كتاب", "كتاب")]
        results = analyse_mafhum(closures, _prop())
        adad = [r for r in results if r.mafhum_type == MafhumType.ADAD]
        assert len(adad) == 1
        assert adad[0].constraint_type == ConstraintType.ADAD

    def test_digit_in_surface_detected_as_adad(self):
        closures = [_cl("3", "عدد"), _cl("كتب", "كتب")]
        results = analyse_mafhum(closures, _prop())
        adad = [r for r in results if r.mafhum_type == MafhumType.ADAD]
        assert len(adad) == 1
        assert adad[0].constraint_value == "3"

    # ── WASF detection ──────────────────────────────────────────

    def test_sifa_pos_detected_as_wasf(self):
        closures = [_cl("الطويل", "طويل", POS.SIFA)]
        results = analyse_mafhum(closures, _prop())
        wasf = [r for r in results if r.mafhum_type == MafhumType.WASF]
        assert len(wasf) == 1
        assert wasf[0].constraint_type == ConstraintType.WASF

    # ── ISHARA detection ────────────────────────────────────────

    def test_reference_marker_hatha_detected_as_ishara(self):
        closures = [_cl("هذا", "هذا"), _cl("الكتاب", "كتاب")]
        results = analyse_mafhum(closures, _prop())
        ishara = [r for r in results if r.mafhum_type == MafhumType.ISHARA]
        assert len(ishara) == 1
        assert ishara[0].constraint_type == ConstraintType.ISHARA

    def test_damir_pos_detected_as_ishara(self):
        closures = [_cl("هو", "هو", POS.DAMIR)]
        results = analyse_mafhum(closures, _prop())
        ishara = [r for r in results if r.mafhum_type == MafhumType.ISHARA]
        assert len(ishara) == 1

    # ── No constraints ──────────────────────────────────────────

    def test_no_constraints_returns_empty(self):
        closures = [_cl("كتاب", "كتاب"), _cl("جديد", "جديد")]
        results = analyse_mafhum(closures, _prop())
        assert results == []

    # ── Empty closures ──────────────────────────────────────────

    def test_empty_closures_returns_empty(self):
        results = analyse_mafhum([], _prop())
        assert results == []

    # ── mantuq_closed=False ─────────────────────────────────────

    def test_mantuq_closed_false_makes_invalid(self):
        closures = [_cl("إن", "إن", POS.HARF), _cl("جاء", "جاء")]
        results = analyse_mafhum(closures, _prop(), mantuq_closed=False)
        assert len(results) > 0
        for r in results:
            assert r.valid is False
            assert r.confidence == 0.0

    # ── Multiple constraints ────────────────────────────────────

    def test_multiple_constraints_in_one_sentence(self):
        closures = [
            _cl("إن", "إن", POS.HARF),
            _cl("واحد", "واحد"),
            _cl("هذا", "هذا"),
        ]
        results = analyse_mafhum(closures, _prop())
        detected_types = {r.mafhum_type for r in results}
        assert MafhumType.SHART in detected_types
        assert MafhumType.ADAD in detected_types
        assert MafhumType.ISHARA in detected_types
        assert len(results) >= 3

    # ── Pillars fields ──────────────────────────────────────────

    def test_pillars_fields_populated(self):
        closures = [_cl("إن", "إن", POS.HARF), _cl("جاء", "جاء")]
        results = analyse_mafhum(closures, _prop())
        shart = [r for r in results if r.mafhum_type == MafhumType.SHART][0]
        pillars = shart.pillars
        assert isinstance(pillars, MafhumPillar)
        assert pillars.closed_mantuq is True
        assert pillars.constraint_type == ConstraintType.SHART
        assert len(pillars.mental_counterpart) > 0
        assert len(pillars.transition_rule) > 0

    def test_pillars_closed_mantuq_false_when_not_closed(self):
        closures = [_cl("حتى", "حتى")]
        results = analyse_mafhum(closures, _prop(), mantuq_closed=False)
        ghaya = [r for r in results if r.mafhum_type == MafhumType.GHAYA][0]
        assert ghaya.pillars.closed_mantuq is False

    # ── Counterpart and derived meaning ─────────────────────────

    def test_counterpart_nonempty(self):
        closures = [_cl("حتى", "حتى")]
        results = analyse_mafhum(closures, _prop())
        for r in results:
            assert isinstance(r.counterpart, str)
            assert len(r.counterpart) > 0

    def test_derived_meaning_nonempty(self):
        closures = [_cl("واحد", "واحد")]
        results = analyse_mafhum(closures, _prop())
        for r in results:
            assert isinstance(r.derived_meaning, str)
            assert len(r.derived_meaning) > 0

    # ── source_text ─────────────────────────────────────────────

    def test_source_text_joined_surfaces(self):
        closures = [_cl("إن", "إن", POS.HARF), _cl("جاء", "جاء")]
        results = analyse_mafhum(closures, _prop())
        for r in results:
            assert r.source_text == "إن جاء"

    # ── Constraint value ────────────────────────────────────────

    def test_constraint_value_is_lemma_for_marker(self):
        closures = [_cl("إذا", "إذا", POS.HARF)]
        results = analyse_mafhum(closures, _prop())
        shart = [r for r in results if r.mafhum_type == MafhumType.SHART][0]
        assert shart.constraint_value == "إذا"

    # ── Default confidence constant ─────────────────────────────

    def test_default_confidence_value(self):
        assert _DEFAULT_MAFHUM_CONFIDENCE == pytest.approx(0.85)
