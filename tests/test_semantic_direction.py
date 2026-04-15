"""tests/test_semantic_direction.py — comprehensive tests for semantic_direction.

Covers:
* Direction space construction (Art. 1–5)
* Genus classification for known words
* Direction assignment
* Weight carrying validation (Art. 20–26)
* Root carrying validation (Art. 27–33)
* Relation retrieval (Art. 34–40)
* Completeness validation (Art. 41–45)
* All 7 relation types
* Boundary types (Art. 13–19)
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    POS,
    DerivationalDirection,
    DirectionBoundary,
    DirectionRelation,
    SemanticDirectionGenus,
)
from arabic_engine.core.types import (
    DirectionAssignment,
    DirectionRelationRecord,
    LexicalClosure,
    SemanticDirection,
    SemanticDirectionSpace,
)
from arabic_engine.signified.semantic_direction import (
    assign_direction,
    build_direction_space,
    classify_genus,
    get_relations,
    validate_direction_completeness,
    validate_root_carrying,
    validate_weight_carrying,
)

# ── Helpers ─────────────────────────────────────────────────────────


def _closure(
    surface: str = "كَتَبَ",
    lemma: str = "كَتَبَ",
    root: tuple[str, ...] = ("ك", "ت", "ب"),
    pattern: str = "فَعَلَ",
    pos: POS = POS.FI3L,
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=root,
        pattern=pattern,
        pos=pos,
    )


# ── Direction space construction ────────────────────────────────────


class TestBuildDirectionSpace:
    """Tests for build_direction_space()."""

    def test_returns_space(self):
        space = build_direction_space()
        assert isinstance(space, SemanticDirectionSpace)

    def test_has_directions(self):
        space = build_direction_space()
        assert len(space.directions) > 0

    def test_has_relations(self):
        space = build_direction_space()
        assert len(space.relations) > 0

    def test_has_all_four_genera(self):
        space = build_direction_space()
        assert len(space.genera) == 4
        expected = {
            SemanticDirectionGenus.WUJUD,
            SemanticDirectionGenus.SIFA,
            SemanticDirectionGenus.HADATH,
            SemanticDirectionGenus.NISBA,
        }
        assert set(space.genera) == expected

    def test_is_complete(self):
        space = build_direction_space()
        assert space.complete is True

    def test_all_directions_have_id(self):
        space = build_direction_space()
        for d in space.directions:
            assert d.direction_id, f"Direction missing ID: {d}"

    def test_all_directions_have_genus(self):
        space = build_direction_space()
        for d in space.directions:
            assert isinstance(d.genus, SemanticDirectionGenus)

    def test_all_directions_have_derivational_direction(self):
        space = build_direction_space()
        for d in space.directions:
            assert isinstance(d.derivational_direction, DerivationalDirection)

    def test_directions_are_frozen(self):
        space = build_direction_space()
        d = space.directions[0]
        with pytest.raises(AttributeError):
            d.direction_id = "CHANGED"  # type: ignore[misc]


# ── Genus classification ────────────────────────────────────────────


class TestClassifyGenus:
    """Tests for classify_genus()."""

    def test_verb_is_hadath(self):
        assert classify_genus(_closure(pos=POS.FI3L)) == SemanticDirectionGenus.HADATH

    def test_noun_is_wujud(self):
        assert classify_genus(_closure(pos=POS.ISM)) == SemanticDirectionGenus.WUJUD

    def test_adjective_is_sifa(self):
        assert classify_genus(_closure(pos=POS.SIFA)) == SemanticDirectionGenus.SIFA

    def test_particle_is_nisba(self):
        assert classify_genus(_closure(pos=POS.HARF)) == SemanticDirectionGenus.NISBA

    def test_masdar_sarih_is_hadath(self):
        assert classify_genus(_closure(pos=POS.MASDAR_SARIH)) == SemanticDirectionGenus.HADATH

    def test_masdar_muawwal_is_hadath(self):
        assert classify_genus(_closure(pos=POS.MASDAR_MUAWWAL)) == SemanticDirectionGenus.HADATH

    def test_zarf_is_nisba(self):
        assert classify_genus(_closure(pos=POS.ZARF)) == SemanticDirectionGenus.NISBA

    def test_damir_is_nisba(self):
        assert classify_genus(_closure(pos=POS.DAMIR)) == SemanticDirectionGenus.NISBA


# ── Direction assignment ────────────────────────────────────────────


class TestAssignDirection:
    """Tests for assign_direction()."""

    def test_returns_assignment(self):
        space = build_direction_space()
        result = assign_direction(_closure(), space)
        assert isinstance(result, DirectionAssignment)

    def test_verb_gets_hadath_genus(self):
        space = build_direction_space()
        result = assign_direction(_closure(pos=POS.FI3L), space)
        assert result.genus == SemanticDirectionGenus.HADATH

    def test_noun_gets_wujud_genus(self):
        space = build_direction_space()
        result = assign_direction(_closure(pos=POS.ISM), space)
        assert result.genus == SemanticDirectionGenus.WUJUD

    def test_masdar_gets_masdar_direction(self):
        space = build_direction_space()
        result = assign_direction(
            _closure(pos=POS.MASDAR_SARIH, pattern="فِعالة"),
            space,
        )
        assert result.assigned_direction.derivational_direction == DerivationalDirection.MASDAR

    def test_confidence_propagated(self):
        space = build_direction_space()
        cl = _closure()
        result = assign_direction(cl, space)
        assert result.confidence > 0

    def test_root_preserved(self):
        space = build_direction_space()
        cl = _closure(root=("ك", "ت", "ب"))
        result = assign_direction(cl, space)
        assert result.root == ("ك", "ت", "ب")

    def test_pattern_preserved(self):
        space = build_direction_space()
        cl = _closure(pattern="فَعَلَ")
        result = assign_direction(cl, space)
        assert result.pattern == "فَعَلَ"


# ── Weight carrying validation ──────────────────────────────────────


class TestValidateWeightCarrying:
    """Tests for validate_weight_carrying()."""

    def test_matching_pattern_accepted(self):
        d = SemanticDirection(
            direction_id="DIR_MASDAR",
            genus=SemanticDirectionGenus.HADATH,
            derivational_direction=DerivationalDirection.MASDAR,
            weight_conditions=("فَعْل", "فِعالة"),
        )
        assert validate_weight_carrying("فَعْل", d) is True

    def test_non_matching_pattern_rejected(self):
        d = SemanticDirection(
            direction_id="DIR_MASDAR",
            genus=SemanticDirectionGenus.HADATH,
            derivational_direction=DerivationalDirection.MASDAR,
            weight_conditions=("فَعْل", "فِعالة"),
        )
        assert validate_weight_carrying("مَفعول", d) is False

    def test_empty_conditions_always_valid(self):
        d = SemanticDirection(
            direction_id="DIR_ANY",
            genus=SemanticDirectionGenus.WUJUD,
            derivational_direction=DerivationalDirection.ISM_JAMID,
        )
        assert validate_weight_carrying("anything", d) is True


# ── Root carrying validation ────────────────────────────────────────


class TestValidateRootCarrying:
    """Tests for validate_root_carrying()."""

    def test_triliteral_accepted(self):
        d = SemanticDirection(
            direction_id="DIR_MASDAR",
            genus=SemanticDirectionGenus.HADATH,
            derivational_direction=DerivationalDirection.MASDAR,
            root_conditions=("triliteral",),
        )
        assert validate_root_carrying(("ك", "ت", "ب"), d) is True

    def test_quadriliteral_accepted(self):
        d = SemanticDirection(
            direction_id="DIR_MASDAR",
            genus=SemanticDirectionGenus.HADATH,
            derivational_direction=DerivationalDirection.MASDAR,
            root_conditions=("quadriliteral",),
        )
        assert validate_root_carrying(("ز", "ل", "ز", "ل"), d) is True

    def test_wrong_length_rejected(self):
        d = SemanticDirection(
            direction_id="DIR_MASDAR",
            genus=SemanticDirectionGenus.HADATH,
            derivational_direction=DerivationalDirection.MASDAR,
            root_conditions=("triliteral",),
        )
        assert validate_root_carrying(("ز", "ل", "ز", "ل"), d) is False

    def test_empty_conditions_always_valid(self):
        d = SemanticDirection(
            direction_id="DIR_ANY",
            genus=SemanticDirectionGenus.WUJUD,
            derivational_direction=DerivationalDirection.ISM_JAMID,
        )
        assert validate_root_carrying(("a", "b", "c", "d", "e"), d) is True


# ── Relation retrieval ──────────────────────────────────────────────


class TestGetRelations:
    """Tests for get_relations()."""

    def test_returns_relations(self):
        space = build_direction_space()
        masdar = None
        for d in space.directions:
            if d.direction_id == "DIR_MASDAR":
                masdar = d
                break
        assert masdar is not None
        rels = get_relations(masdar, space)
        assert len(rels) > 0

    def test_all_results_are_relation_records(self):
        space = build_direction_space()
        for d in space.directions:
            rels = get_relations(d, space)
            for r in rels:
                assert isinstance(r, DirectionRelationRecord)


# ── Completeness validation ─────────────────────────────────────────


class TestValidateDirectionCompleteness:
    """Tests for validate_direction_completeness()."""

    def test_full_space_is_complete(self):
        space = build_direction_space()
        assert validate_direction_completeness(space) is True

    def test_empty_space_is_incomplete(self):
        space = SemanticDirectionSpace(directions=(), genera=())
        assert validate_direction_completeness(space) is False

    def test_missing_genus_is_incomplete(self):
        d = SemanticDirection(
            direction_id="DIR_X",
            genus=SemanticDirectionGenus.WUJUD,
            derivational_direction=DerivationalDirection.ISM_JAMID,
        )
        space = SemanticDirectionSpace(
            directions=(d,),
            genera=(
                SemanticDirectionGenus.WUJUD,
                SemanticDirectionGenus.HADATH,
            ),
        )
        assert validate_direction_completeness(space) is False


# ── All 7 relation types present ────────────────────────────────────


class TestAllRelationTypes:
    """Verify all 7 relation types are represented in the seed data."""

    def test_wiratha_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.WIRATHA for r in space.relations)

    def test_tawafuq_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.TAWAFUQ for r in space.relations)

    def test_man3_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.MAN3 for r in space.relations)

    def test_tahawwul_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.TAHAWWUL for r in space.relations)

    def test_ishtirat_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.ISHTIRAT for r in space.relations)

    def test_isqat_tarkibi_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.ISQAT_TARKIBI for r in space.relations)

    def test_radd_present(self):
        space = build_direction_space()
        assert any(r.relation == DirectionRelation.RADD for r in space.relations)


# ── Boundary types ──────────────────────────────────────────────────


class TestBoundaryTypes:
    """Verify all three boundary types are represented."""

    def test_hadd_fasil_present(self):
        space = build_direction_space()
        assert any(d.boundary == DirectionBoundary.HADD_FASIL for d in space.directions)

    def test_hadd_intiqali_present(self):
        space = build_direction_space()
        assert any(d.boundary == DirectionBoundary.HADD_INTIQALI for d in space.directions)

    def test_hadd_mushtarak_present(self):
        space = build_direction_space()
        assert any(d.boundary == DirectionBoundary.HADD_MUSHTARAK for d in space.directions)
