"""tests/test_weight_fractal.py — comprehensive tests for weight_fractal.

Covers:
* Weight classification (Art. 1–5)
* Weight direction mapping (Art. 11–15)
* Weight carrying check
* Fractal tree construction (Art. 16–20)
* Weight non-arbitrariness proof (Art. 6–10)
* Full weight fractal run
* Weight classes
* Fractal phases
* Formal tuple (Art. 59)
* Weight possibility (Art. 9–17)
* Minimum weight completeness (Art. 18–26)
* Fractal score (Art. 27–34)
* Direction suitability (Art. 35–42)
* Verb doors (Art. 43–46)
* Augmented weight validation (Art. 47–50)
* Weight acceptance/rejection (Art. 63–64)
* Expanded run_weight_fractal integration
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    POS,
    DerivationalDirection,
    SemanticDirectionGenus,
    ThulathiBab,
    WeightCarryingMode,
    WeightClass,
    WeightFractalPhase,
    WeightKind,
    WeightValidationStatus,
)
from arabic_engine.core.types import (
    LexicalClosure,
    SemanticDirection,
    VerbDoor,
    WeightDirectionMapping,
    WeightDirectionSuitability,
    WeightFormalTuple,
    WeightFractalResult,
    WeightFractalScore,
    WeightMWCScore,
    WeightPossibilityResult,
    WeightProfile,
    WeightValidationResult,
)
from arabic_engine.signifier.weight_fractal import (
    THETA_1,
    THETA_2,
    build_formal_tuple,
    build_fractal_tree,
    build_weight_direction_map,
    check_weight_carrying,
    classify_verb_door,
    classify_weight,
    compute_fractal_score,
    compute_mwc,
    evaluate_direction_suitability,
    run_weight_fractal,
    validate_augmented_weight,
    validate_weight_acceptance,
    validate_weight_non_arbitrariness,
    validate_weight_possibility,
)

# ── Helpers ─────────────────────────────────────────────────────────


def _closure(
    surface: str = "كِتابة",
    lemma: str = "كِتابة",
    root: tuple[str, ...] = ("ك", "ت", "ب"),
    pattern: str = "فِعالة",
    pos: POS = POS.MASDAR_SARIH,
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=root,
        pattern=pattern,
        pos=pos,
    )


def _direction(
    *,
    deriv: DerivationalDirection = DerivationalDirection.MASDAR,
    genus: SemanticDirectionGenus = SemanticDirectionGenus.HADATH,
) -> SemanticDirection:
    return SemanticDirection(
        direction_id=f"DIR_{deriv.name}",
        genus=genus,
        derivational_direction=deriv,
    )


# ── Weight classification ───────────────────────────────────────────


class TestClassifyWeight:
    """Tests for classify_weight()."""

    def test_returns_profile(self):
        p = classify_weight("فَعْل")
        assert isinstance(p, WeightProfile)

    def test_pattern_preserved(self):
        p = classify_weight("فِعالة")
        assert p.pattern == "فِعالة"

    def test_thulathi_mujarrad(self):
        p = classify_weight("فَعْل", radical_count=3)
        assert p.weight_class == WeightClass.THULATHI_MUJARRAD

    def test_thulathi_mazeed(self):
        p = classify_weight("إفعال", radical_count=3)
        assert p.weight_class == WeightClass.THULATHI_MAZEED

    def test_ruba3i_mujarrad(self):
        p = classify_weight("فَعلَل", radical_count=4)
        assert p.weight_class == WeightClass.RUBA3I_MUJARRAD

    def test_khumasi(self):
        p = classify_weight("فَعلَلَل", radical_count=5)
        assert p.weight_class == WeightClass.KHUMASI

    def test_radical_count_stored(self):
        p = classify_weight("فَعْل", radical_count=3)
        assert p.radical_count == 3

    def test_genus_from_pos(self):
        p = classify_weight("فَعَلَ", pos=POS.FI3L)
        assert p.semantic_direction == SemanticDirectionGenus.HADATH

    def test_noun_genus(self):
        p = classify_weight("فَعْل", pos=POS.ISM)
        assert p.semantic_direction == SemanticDirectionGenus.WUJUD

    def test_weight_kind_productive(self):
        p = classify_weight("فَعْل", radical_count=3)
        assert p.weight_kind == WeightKind.PRODUCTIVE

    def test_formal_tuple_present(self):
        p = classify_weight("فَعْل", radical_count=3)
        assert p.formal_tuple is not None
        assert isinstance(p.formal_tuple, WeightFormalTuple)


# ── Weight direction mapping ────────────────────────────────────────


class TestBuildWeightDirectionMap:
    """Tests for build_weight_direction_map()."""

    def test_returns_mapping(self):
        p = classify_weight("فَعْل")
        m = build_weight_direction_map(p)
        assert isinstance(m, WeightDirectionMapping)

    def test_fa3l_permits_masdar(self):
        p = classify_weight("فَعْل")
        m = build_weight_direction_map(p)
        assert DerivationalDirection.MASDAR in m.permitted_directions

    def test_fa3l_prohibits_ism_fa3il(self):
        p = classify_weight("فَعْل")
        m = build_weight_direction_map(p)
        assert DerivationalDirection.ISM_FA3IL in m.prohibited_directions

    def test_fa3il_permits_ism_fa3il(self):
        p = classify_weight("فاعِل")
        m = build_weight_direction_map(p)
        assert DerivationalDirection.ISM_FA3IL in m.permitted_directions

    def test_maf3ul_permits_ism_maf3ul(self):
        p = classify_weight("مَفعول")
        m = build_weight_direction_map(p)
        assert DerivationalDirection.ISM_MAF3UL in m.permitted_directions

    def test_unknown_pattern_falls_back(self):
        p = classify_weight("مجهول_تماماً")
        m = build_weight_direction_map(p)
        # Fallback grants all directions
        assert len(m.permitted_directions) > 0


# ── Weight carrying check ───────────────────────────────────────────


class TestCheckWeightCarrying:
    """Tests for check_weight_carrying()."""

    def test_masdar_from_fa3l_is_asli(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.MASDAR)
        mode = check_weight_carrying(p, d)
        assert mode == WeightCarryingMode.ASLI

    def test_ism_fa3il_from_fa3l_is_mumtani3(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.ISM_FA3IL)
        mode = check_weight_carrying(p, d)
        assert mode == WeightCarryingMode.MUMTANI3

    def test_ism_fa3il_from_fa3il_is_asli(self):
        p = classify_weight("فاعِل")
        d = _direction(deriv=DerivationalDirection.ISM_FA3IL, genus=SemanticDirectionGenus.SIFA)
        mode = check_weight_carrying(p, d)
        assert mode == WeightCarryingMode.ASLI


# ── Fractal tree construction ───────────────────────────────────────


class TestBuildFractalTree:
    """Tests for build_fractal_tree()."""

    def test_returns_nodes(self):
        tree = build_fractal_tree(("ك", "ت", "ب"), "فَعْل")
        assert isinstance(tree, tuple)
        assert len(tree) > 0

    def test_six_phases(self):
        tree = build_fractal_tree(("ك", "ت", "ب"), "فَعْل")
        assert len(tree) == 6

    def test_all_phases_present(self):
        tree = build_fractal_tree(("ك", "ت", "ب"), "فَعْل")
        phases = {n.phase for n in tree}
        assert phases == set(WeightFractalPhase)

    def test_chain_structure(self):
        tree = build_fractal_tree(("ك", "ت", "ب"), "فَعْل")
        # First node has no parent
        assert tree[0].parent is None
        # Last node has no children
        assert tree[-1].children == ()
        # Middle nodes link correctly
        for i in range(1, len(tree)):
            assert tree[i].parent == tree[i - 1].node_id

    def test_nodes_are_frozen(self):
        tree = build_fractal_tree(("ك", "ت", "ب"), "فَعْل")
        with pytest.raises(AttributeError):
            tree[0].node_id = "CHANGED"  # type: ignore[misc]


# ── Non-arbitrariness ───────────────────────────────────────────────


class TestValidateWeightNonArbitrariness:
    """Tests for validate_weight_non_arbitrariness()."""

    def test_permitted_is_non_arbitrary(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.MASDAR)
        assert validate_weight_non_arbitrariness(p, d) is True

    def test_prohibited_is_arbitrary(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.ISM_FA3IL)
        assert validate_weight_non_arbitrariness(p, d) is False


# ── Full weight fractal run ─────────────────────────────────────────


class TestRunWeightFractal:
    """Tests for run_weight_fractal()."""

    def test_returns_result(self):
        result = run_weight_fractal(_closure())
        assert isinstance(result, WeightFractalResult)

    def test_root_preserved(self):
        result = run_weight_fractal(_closure(root=("ك", "ت", "ب")))
        assert result.root == ("ك", "ت", "ب")

    def test_has_fractal_tree(self):
        result = run_weight_fractal(_closure())
        assert len(result.fractal_tree) == 6

    def test_has_direction_map(self):
        result = run_weight_fractal(_closure())
        assert result.direction_map is not None

    def test_completeness_score_positive(self):
        result = run_weight_fractal(_closure())
        assert result.completeness_score > 0

    def test_is_closed(self):
        result = run_weight_fractal(_closure())
        assert result.is_closed is True

    def test_verb_closure(self):
        cl = _closure(surface="ضَرَبَ", lemma="ضَرَبَ", pos=POS.FI3L, pattern="فَعَلَ")
        result = run_weight_fractal(cl)
        assert result.base_weight.semantic_direction == SemanticDirectionGenus.HADATH


# ══════════════════════════════════════════════════════════════════════
# Expanded Constitution Tests (Art. 4–66)
# ══════════════════════════════════════════════════════════════════════


# ── Formal tuple (Art. 59) ──────────────────────────────────────────


class TestBuildFormalTuple:
    """Tests for build_formal_tuple()."""

    def test_returns_formal_tuple(self):
        ft = build_formal_tuple("فَعْل", radical_count=3)
        assert isinstance(ft, WeightFormalTuple)

    def test_root_positions(self):
        ft = build_formal_tuple("فَعْل", radical_count=3)
        assert ft.root_positions == (1, 2, 3)

    def test_root_positions_quadrilateral(self):
        ft = build_formal_tuple("فَعلَل", radical_count=4)
        assert ft.root_positions == (1, 2, 3, 4)

    def test_syllable_structure_present(self):
        ft = build_formal_tuple("فَعْل", radical_count=3)
        assert len(ft.syllable_structure) > 0

    def test_carrying_capacity_non_empty(self):
        ft = build_formal_tuple("فَعْل", radical_count=3)
        assert len(ft.carrying_capacity) > 0


# ── Weight possibility (Art. 9–17) ─────────────────────────────────


class TestWeightPossibility:
    """Tests for validate_weight_possibility()."""

    def test_returns_result(self):
        p = classify_weight("فَعْل")
        r = validate_weight_possibility(p)
        assert isinstance(r, WeightPossibilityResult)

    def test_structural_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert r.structural == 1.0

    def test_syllabic_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert r.syllabic == 1.0

    def test_morphological_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert r.morphological == 1.0

    def test_semantic_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert r.semantic == 1.0

    def test_generative_score_productive(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert r.generative == 1.0

    def test_traceback_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert r.traceback == 1.0

    def test_aggregate_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        r = validate_weight_possibility(p)
        assert 0.0 < r.aggregate <= 1.0


# ── Minimum Weight Completeness (Art. 18–26) ───────────────────────


class TestWeightMWC:
    """Tests for compute_mwc()."""

    def test_returns_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert isinstance(m, WeightMWCScore)

    def test_stability_productive(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.stability == 1.0

    def test_boundary_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.boundary == 1.0

    def test_constituent_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.constituent == 1.0

    def test_regularity_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.regularity == 1.0

    def test_unity_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.unity == 1.0

    def test_assignability_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.assignability == 1.0

    def test_aggregate_above_theta_1(self):
        p = classify_weight("فَعْل", radical_count=3)
        m = compute_mwc(p)
        assert m.aggregate >= THETA_1


# ── Fractal score (Art. 27–34) ──────────────────────────────────────


class TestWeightFractalScore:
    """Tests for compute_fractal_score()."""

    def test_returns_score(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert isinstance(f, WeightFractalScore)

    def test_identification(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert f.identification == 1.0

    def test_preservation(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert f.preservation == 1.0

    def test_linkage(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert f.linkage == 1.0

    def test_judgement(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert f.judgement == 1.0

    def test_transition(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert f.transition == 1.0

    def test_aggregate_above_theta_2(self):
        p = classify_weight("فَعْل", radical_count=3)
        f = compute_fractal_score(p)
        assert f.aggregate >= THETA_2


# ── Direction suitability (Art. 35–42) ──────────────────────────────


class TestWeightDirectionSuitability:
    """Tests for evaluate_direction_suitability()."""

    def test_returns_suitability(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.MASDAR)
        s = evaluate_direction_suitability(p, d)
        assert isinstance(s, WeightDirectionSuitability)

    def test_permitted_direction_carries(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.MASDAR)
        s = evaluate_direction_suitability(p, d)
        assert s.carries is True

    def test_prohibited_direction_does_not_carry(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.ISM_FA3IL)
        s = evaluate_direction_suitability(p, d)
        assert s.carries is False

    def test_aggregate_range(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.MASDAR)
        s = evaluate_direction_suitability(p, d)
        assert 0.0 <= s.aggregate <= 1.0

    def test_structural_suitability_from_matrix(self):
        p = classify_weight("فَعْل")
        d = _direction(deriv=DerivationalDirection.MASDAR)
        s = evaluate_direction_suitability(p, d)
        assert s.structural_suitability > 0


# ── Verb doors (Art. 43–46) ─────────────────────────────────────────


class TestVerbDoors:
    """Tests for classify_verb_door()."""

    def test_fa3ala_yaf3ulu(self):
        door = classify_verb_door("فَعَلَ", "يَفْعُلُ")
        assert door is not None
        assert door.bab == ThulathiBab.FA3ALA_YAF3ULU

    def test_fa3ala_yaf3ilu(self):
        door = classify_verb_door("فَعَلَ", "يَفْعِلُ")
        assert door is not None
        assert door.bab == ThulathiBab.FA3ALA_YAF3ILU

    def test_fa3ala_yaf3alu(self):
        door = classify_verb_door("فَعَلَ", "يَفْعَلُ")
        assert door is not None
        assert door.bab == ThulathiBab.FA3ALA_YAF3ALU

    def test_fa3ila_yaf3alu(self):
        door = classify_verb_door("فَعِلَ", "يَفْعَلُ")
        assert door is not None
        assert door.bab == ThulathiBab.FA3ILA_YAF3ALU

    def test_fa3ula_yaf3ulu(self):
        door = classify_verb_door("فَعُلَ", "يَفْعُلُ")
        assert door is not None
        assert door.bab == ThulathiBab.FA3ULA_YAF3ULU

    def test_unknown_door_returns_none(self):
        door = classify_verb_door("xxx", "yyy")
        assert door is None

    def test_returns_verb_door_type(self):
        door = classify_verb_door("فَعَلَ", "يَفْعُلُ")
        assert isinstance(door, VerbDoor)

    def test_has_example(self):
        door = classify_verb_door("فَعَلَ", "يَفْعُلُ")
        assert door is not None
        assert len(door.example_root) > 0


# ── Augmented weight validation (Art. 47–50) ────────────────────────


class TestAugmentedWeight:
    """Tests for validate_augmented_weight()."""

    def test_augmented_valid(self):
        p = classify_weight("إفعال", radical_count=3)
        assert validate_augmented_weight(p) is True

    def test_non_augmented_passes(self):
        p = classify_weight("فَعْل", radical_count=3)
        assert validate_augmented_weight(p) is True

    def test_augmented_needs_augmentation_letters(self):
        # Force an augmented class with no augmentation letters
        p = WeightProfile(
            pattern="x",
            weight_class=WeightClass.THULATHI_MAZEED,
            radical_count=3,
            augmentation_letters=(),
            weight_kind=WeightKind.PRODUCTIVE,
        )
        assert validate_augmented_weight(p) is False


# ── Weight validation (Art. 63–64) ──────────────────────────────────


class TestWeightValidation:
    """Tests for validate_weight_acceptance()."""

    def test_returns_result(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert isinstance(v, WeightValidationResult)

    def test_standard_weight_accepted(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert v.status == WeightValidationStatus.ACCEPTED

    def test_has_acceptance_scores(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert len(v.acceptance_scores) == 6

    def test_has_rejection_flags(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert len(v.rejection_flags) == 5

    def test_rejected_has_reason(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert v.reason != ""

    def test_acceptance_scores_all_high(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert all(s >= 1.0 for s in v.acceptance_scores)

    def test_rejection_flags_all_false(self):
        p = classify_weight("فَعْل", radical_count=3)
        v = validate_weight_acceptance(p)
        assert not any(v.rejection_flags)


# ── Expanded run_weight_fractal integration ─────────────────────────


class TestRunWeightFractalExpanded:
    """Integration tests for the enriched run_weight_fractal()."""

    def test_has_mwc_score(self):
        result = run_weight_fractal(_closure())
        assert result.mwc_score is not None
        assert isinstance(result.mwc_score, WeightMWCScore)

    def test_has_fractal_score(self):
        result = run_weight_fractal(_closure())
        assert result.fractal_score is not None
        assert isinstance(result.fractal_score, WeightFractalScore)

    def test_has_possibility_result(self):
        result = run_weight_fractal(_closure())
        assert result.possibility_result is not None
        assert isinstance(result.possibility_result, WeightPossibilityResult)

    def test_has_validation(self):
        result = run_weight_fractal(_closure())
        assert result.validation is not None
        assert isinstance(result.validation, WeightValidationResult)

    def test_mwc_aggregate_positive(self):
        result = run_weight_fractal(_closure())
        assert result.mwc_score is not None
        assert result.mwc_score.aggregate > 0

    def test_fractal_score_aggregate_positive(self):
        result = run_weight_fractal(_closure())
        assert result.fractal_score is not None
        assert result.fractal_score.aggregate > 0

    def test_possibility_aggregate_positive(self):
        result = run_weight_fractal(_closure())
        assert result.possibility_result is not None
        assert result.possibility_result.aggregate > 0

    def test_validation_status_accepted(self):
        result = run_weight_fractal(_closure())
        assert result.validation is not None
        assert result.validation.status == WeightValidationStatus.ACCEPTED

    def test_weight_kind_in_profile(self):
        result = run_weight_fractal(_closure())
        assert result.base_weight.weight_kind == WeightKind.PRODUCTIVE

    def test_formal_tuple_in_profile(self):
        result = run_weight_fractal(_closure())
        assert result.base_weight.formal_tuple is not None
