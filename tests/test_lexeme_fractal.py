"""tests/test_lexeme_fractal.py — tests for the Lexeme Fractal Constitution v2.

Covers:
* Conceptual type classification (Art. 24)
* Composition readiness scoring (Art. 53–59)
* Lexeme validation / acceptance-rejection (Art. 58, 60–61)
* Signification triad (Art. 42–45)
* Six-phase fractal cycle (Art. 46–52)
* Pipeline integration via close_mufrad
* Immutability of result types
* Edge cases
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    POS,
    ConceptualType,
    LexemeAcceptanceCode,
    LexemeFractalPhase,
    LexemePillar,
    SemanticDirectionGenus,
    SignificationMode,
)
from arabic_engine.core.types import (
    CompositionReadiness,
    DirectionAssignment,
    Lexeme,
    LexemeFractalNode,
    LexemeFractalResult,
    LexicalClosure,
    SemanticDirection,
    SignificationTriad,
    WeightFractalResult,
    WeightProfile,
)
from arabic_engine.signifier.lexeme_fractal import (
    build_signification_triad,
    classify_conceptual_type,
    compute_readiness,
    run_lexeme_fractal,
    validate_lexeme,
)

# ── Fixtures ────────────────────────────────────────────────────────


def _make_closure(
    *,
    surface: str = "كَتَبَ",
    lemma: str = "كَتَبَ",
    root: tuple = ("ك", "ت", "ب"),
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


def _make_direction(
    genus: SemanticDirectionGenus = SemanticDirectionGenus.HADATH,
) -> DirectionAssignment:
    return DirectionAssignment(
        word_surface="كَتَبَ",
        root=("ك", "ت", "ب"),
        pattern="فَعَلَ",
        assigned_direction=SemanticDirection(
            direction_id="d_hadath",
            genus=genus,
            derivational_direction=None,
        ),
        genus=genus,
        confidence=1.0,
    )


def _make_weight(*, is_closed: bool = True) -> WeightFractalResult:
    return WeightFractalResult(
        root=("ك", "ت", "ب"),
        base_weight=WeightProfile(
            pattern="فَعَلَ",
            weight_class=None,
            radical_count=3,
            augmentation_letters=(),
            semantic_direction=SemanticDirectionGenus.HADATH,
            carrying_mode=None,
        ),
        completeness_score=1.0 if is_closed else 0.3,
        is_closed=is_closed,
    )


# ── Enum completeness ──────────────────────────────────────────────


class TestEnums:
    """Verify new enums have the expected members."""

    def test_conceptual_type_count(self):
        assert len(ConceptualType) == 9

    def test_lexeme_pillar_count(self):
        assert len(LexemePillar) == 6

    def test_lexeme_fractal_phase_count(self):
        assert len(LexemeFractalPhase) == 6

    def test_signification_mode_count(self):
        assert len(SignificationMode) == 3

    def test_acceptance_code_count(self):
        # 7 acceptance + 5 rejection = 12
        assert len(LexemeAcceptanceCode) == 12


# ── Conceptual type classification ──────────────────────────────────


class TestConceptualTypeClassification:
    """Verify POS + genus → ConceptualType mapping (Art. 24)."""

    def test_verb_hadath(self):
        c = _make_closure(pos=POS.FI3L)
        assert classify_conceptual_type(c, SemanticDirectionGenus.HADATH) == (
            ConceptualType.FA3ILIYYA
        )

    def test_noun_wujud(self):
        c = _make_closure(pos=POS.ISM)
        assert classify_conceptual_type(c, SemanticDirectionGenus.WUJUD) == (
            ConceptualType.KULLI
        )

    def test_noun_sifa(self):
        c = _make_closure(pos=POS.ISM)
        assert classify_conceptual_type(c, SemanticDirectionGenus.SIFA) == (
            ConceptualType.SIFA
        )

    def test_harf_relational(self):
        c = _make_closure(pos=POS.HARF)
        assert classify_conceptual_type(c, SemanticDirectionGenus.NISBA) == (
            ConceptualType.ALA2IQIYYA
        )

    def test_masdar(self):
        c = _make_closure(pos=POS.MASDAR_SARIH)
        assert classify_conceptual_type(c, SemanticDirectionGenus.HADATH) == (
            ConceptualType.MASDARIYYA
        )

    def test_damir_particular(self):
        c = _make_closure(pos=POS.DAMIR)
        assert classify_conceptual_type(c, SemanticDirectionGenus.WUJUD) == (
            ConceptualType.JUZ2I
        )

    def test_zarf_temporal(self):
        c = _make_closure(pos=POS.ZARF)
        assert classify_conceptual_type(c, SemanticDirectionGenus.WUJUD) == (
            ConceptualType.ZAMANIYYA
        )

    def test_infers_genus_from_pos(self):
        """If genus is None, it is inferred from POS."""
        c = _make_closure(pos=POS.FI3L)
        ct = classify_conceptual_type(c, None)
        assert ct == ConceptualType.FA3ILIYYA


# ── Composition readiness ───────────────────────────────────────────


class TestCompositionReadiness:
    """Verify readiness scoring formula (Art. 53–59)."""

    def test_full_readiness(self):
        c = _make_closure()
        r = compute_readiness(c, _make_direction(), _make_weight())
        assert r.overall == 1.0
        assert r.is_ready is True

    def test_no_direction_reduces_score(self):
        c = _make_closure()
        r = compute_readiness(c, None, _make_weight())
        assert r.direction_score == 0.0
        assert r.overall < 1.0

    def test_no_weight_reduces_score(self):
        c = _make_closure()
        r = compute_readiness(c, _make_direction(), None)
        assert r.structural_score == 0.0
        assert r.overall < 1.0

    def test_unclosed_weight_reduces_score(self):
        c = _make_closure()
        r = compute_readiness(c, _make_direction(), _make_weight(is_closed=False))
        assert r.structural_score == 0.0

    def test_unknown_pos_reduces_score(self):
        c = _make_closure(pos=POS.UNKNOWN)
        r = compute_readiness(c, _make_direction(), _make_weight())
        assert r.type_score == 0.0
        assert r.pos_score == 0.0

    def test_empty_root_reduces_material(self):
        c = _make_closure(root=())
        r = compute_readiness(c, _make_direction(), _make_weight())
        assert r.material_score == 0.0

    def test_readiness_bounded(self):
        c = _make_closure()
        r = compute_readiness(c, _make_direction(), _make_weight())
        assert 0 <= r.overall <= 1.0

    def test_threshold_at_075(self):
        """Readiness threshold θ_R = 0.75."""
        c = _make_closure()
        r = compute_readiness(c, _make_direction(), _make_weight())
        assert r.is_ready is True  # overall = 1.0 >= 0.75


# ── Lexeme validation ──────────────────────────────────────────────


class TestLexemeValidation:
    """Verify acceptance/rejection criteria (Art. 58, 60–61)."""

    def test_valid_lexeme(self):
        lex = Lexeme(
            material=("ك", "ت", "ب"),
            weight_pattern="فَعَلَ",
            semantic_direction=SemanticDirectionGenus.HADATH,
            conceptual_type=ConceptualType.FA3ILIYYA,
            final_pos=POS.FI3L,
            readiness=1.0,
        )
        valid, accept, reject = validate_lexeme(lex)
        assert valid is True
        assert len(reject) == 0
        assert LexemeAcceptanceCode.MADDA_THABITA in accept
        assert LexemeAcceptanceCode.JAHIZ_LIL_TARKIB in accept

    def test_invalid_empty_material(self):
        lex = Lexeme(
            material=(),
            weight_pattern="فَعَلَ",
            final_pos=POS.FI3L,
            readiness=1.0,
        )
        valid, accept, reject = validate_lexeme(lex)
        assert valid is False
        assert LexemeAcceptanceCode.MADDA_MAFTUHA in reject

    def test_invalid_unknown_pos(self):
        lex = Lexeme(
            material=("ك", "ت", "ب"),
            weight_pattern="فَعَلَ",
            final_pos=POS.UNKNOWN,
            readiness=1.0,
        )
        valid, accept, reject = validate_lexeme(lex)
        assert valid is False
        assert LexemeAcceptanceCode.QISM_GHAYR_THABIT in reject

    def test_invalid_low_readiness(self):
        lex = Lexeme(
            material=("ك", "ت", "ب"),
            weight_pattern="فَعَلَ",
            final_pos=POS.FI3L,
            readiness=0.5,
        )
        valid, accept, reject = validate_lexeme(lex)
        assert valid is False
        assert LexemeAcceptanceCode.GHAYR_JAHIZ in reject

    def test_seven_acceptance_codes(self):
        """Art. 60: 7 acceptance criteria."""
        lex = Lexeme(
            material=("ك", "ت", "ب"),
            weight_pattern="فَعَلَ",
            semantic_direction=SemanticDirectionGenus.HADATH,
            conceptual_type=ConceptualType.FA3ILIYYA,
            final_pos=POS.FI3L,
            readiness=1.0,
        )
        _, accept, _ = validate_lexeme(lex)
        assert len(accept) == 7


# ── Signification triad ────────────────────────────────────────────


class TestSignificationTriad:
    """Verify signification modes differ by POS (Art. 42–45)."""

    def test_verb_triad(self):
        c = _make_closure(pos=POS.FI3L)
        t = build_signification_triad(c)
        assert "event:" in t.mutabaqa
        assert "agent+patient:" in t.tadammun

    def test_noun_triad(self):
        c = _make_closure(pos=POS.ISM)
        t = build_signification_triad(c)
        assert "entity:" in t.mutabaqa
        assert "genus:" in t.tadammun

    def test_particle_triad(self):
        c = _make_closure(pos=POS.HARF)
        t = build_signification_triad(c)
        assert "relation:" in t.mutabaqa
        assert "binding:" in t.tadammun

    def test_masdar_triad(self):
        c = _make_closure(pos=POS.MASDAR_SARIH)
        t = build_signification_triad(c)
        assert "nominalized-event:" in t.mutabaqa

    def test_sifa_triad(self):
        c = _make_closure(pos=POS.SIFA)
        t = build_signification_triad(c)
        assert "attribute:" in t.mutabaqa

    def test_pos_category_preserved(self):
        c = _make_closure(pos=POS.FI3L)
        t = build_signification_triad(c)
        assert t.pos_category == POS.FI3L


# ── Fractal cycle ──────────────────────────────────────────────────


class TestLexemeFractalCycle:
    """Verify the 6-phase fractal cycle (Art. 46–52)."""

    def test_tree_has_six_phases(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        assert len(result.fractal_tree) == 6

    def test_phases_in_order(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        phases = [n.phase for n in result.fractal_tree]
        assert phases == list(LexemeFractalPhase)

    def test_parent_chain(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        tree = result.fractal_tree
        assert tree[0].parent_phase is None
        for i in range(1, len(tree)):
            assert tree[i].parent_phase == tree[i - 1].phase

    def test_result_has_lexeme(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        assert isinstance(result.lexeme, Lexeme)

    def test_result_has_readiness(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        assert isinstance(result.readiness, CompositionReadiness)

    def test_result_has_signification(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        assert isinstance(result.signification, SignificationTriad)

    def test_completeness_bounded(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        assert 0 <= result.completeness_score <= 1.0

    def test_valid_result(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        assert result.is_valid is True
        assert len(result.rejection_codes) == 0

    def test_node_ids_unique(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        ids = [n.node_id for n in result.fractal_tree]
        assert len(ids) == len(set(ids))


# ── Pipeline integration ────────────────────────────────────────────


class TestPipelineIntegration:
    """Verify integration with close_mufrad."""

    def test_lexeme_fractal_present(self):
        from arabic_engine.mufrad_closure import close_mufrad

        result = close_mufrad("كَتَبَ")
        assert result.lexeme_fractal is not None

    def test_lexeme_fractal_is_valid(self):
        from arabic_engine.mufrad_closure import close_mufrad

        result = close_mufrad("كَتَبَ")
        if result.lexeme_fractal:
            assert result.lexeme_fractal.is_valid is True

    def test_lexeme_fractal_tree(self):
        from arabic_engine.mufrad_closure import close_mufrad

        result = close_mufrad("كَتَبَ")
        if result.lexeme_fractal:
            assert len(result.lexeme_fractal.fractal_tree) == 6

    def test_unknown_word_still_has_result(self):
        from arabic_engine.mufrad_closure import close_mufrad

        result = close_mufrad("xyz_unknown")
        assert isinstance(result.surface, str)


# ── Immutability ────────────────────────────────────────────────────


class TestImmutability:
    """Result types should be frozen dataclasses."""

    def test_lexeme_frozen(self):
        lex = Lexeme(material=("ك", "ت", "ب"))
        with pytest.raises(AttributeError):
            lex.material = ("x",)  # type: ignore[misc]

    def test_fractal_node_frozen(self):
        node = LexemeFractalNode(node_id="test")
        with pytest.raises(AttributeError):
            node.phase = LexemeFractalPhase.RADD  # type: ignore[misc]

    def test_readiness_frozen(self):
        r = CompositionReadiness()
        with pytest.raises(AttributeError):
            r.overall = 0.5  # type: ignore[misc]

    def test_signification_frozen(self):
        s = SignificationTriad()
        with pytest.raises(AttributeError):
            s.mutabaqa = "changed"  # type: ignore[misc]

    def test_fractal_result_frozen(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, _make_direction(), _make_weight())
        with pytest.raises(AttributeError):
            result.is_valid = False  # type: ignore[misc]


# ── Edge cases ──────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_no_direction_no_weight(self):
        c = _make_closure()
        result = run_lexeme_fractal(c, None, None)
        assert isinstance(result, LexemeFractalResult)
        assert len(result.fractal_tree) == 6

    def test_empty_root(self):
        c = _make_closure(root=())
        result = run_lexeme_fractal(c)
        assert result.lexeme.material == ()

    def test_unknown_pos(self):
        c = _make_closure(pos=POS.UNKNOWN, pattern="")
        result = run_lexeme_fractal(c)
        assert result.is_valid is False
        assert LexemeAcceptanceCode.QISM_GHAYR_THABIT in result.rejection_codes

    def test_particle_lexeme(self):
        c = _make_closure(
            surface="في",
            lemma="في",
            root=(),
            pattern="",
            pos=POS.HARF,
        )
        result = run_lexeme_fractal(c)
        assert result.lexeme.final_pos == POS.HARF
