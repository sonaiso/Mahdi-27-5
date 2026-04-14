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
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    POS,
    DerivationalDirection,
    SemanticDirectionGenus,
    WeightCarryingMode,
    WeightClass,
    WeightFractalPhase,
)
from arabic_engine.core.types import (
    LexicalClosure,
    SemanticDirection,
    WeightDirectionMapping,
    WeightFractalResult,
    WeightProfile,
)
from arabic_engine.signifier.weight_fractal import (
    build_fractal_tree,
    build_weight_direction_map,
    check_weight_carrying,
    classify_weight,
    run_weight_fractal,
    validate_weight_non_arbitrariness,
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
