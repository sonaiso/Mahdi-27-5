"""tests/test_mufrad_closure.py — end-to-end tests for mufrad closure.

Covers:
* Full closure of known Arabic words
* Determinism — same word always produces the same result
* Hierarchical structure (genus > direction > weight > root)
* Fractal mirror of (E, K, F, C) origin structure
* All closure dimensions computed
* is_closed flag
* closure_confidence
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import SemanticDirectionGenus
from arabic_engine.core.types import MufradClosureResult
from arabic_engine.mufrad_closure import close_mufrad

# ── Known words with expected genus ─────────────────────────────────

_KNOWN_WORDS = [
    ("كَتَبَ", SemanticDirectionGenus.HADATH),       # verb → event
    ("كِتابة", SemanticDirectionGenus.HADATH),       # masdar → event
    ("زَيْدٌ", SemanticDirectionGenus.WUJUD),        # noun → existence
    ("جَميل", SemanticDirectionGenus.WUJUD),         # not in mini-lexicon → default WUJUD
]

# ── Basic functionality ─────────────────────────────────────────────


class TestCloseMufradBasic:
    """Basic tests for close_mufrad()."""

    def test_returns_result(self):
        result = close_mufrad("كَتَبَ")
        assert isinstance(result, MufradClosureResult)

    def test_surface_preserved(self):
        result = close_mufrad("كَتَبَ")
        assert result.surface == "كَتَبَ"

    def test_normalized_is_string(self):
        result = close_mufrad("كَتَبَ")
        assert isinstance(result.normalized, str)
        assert len(result.normalized) > 0

    def test_lexical_closure_present(self):
        result = close_mufrad("كَتَبَ")
        assert result.lexical_closure is not None

    def test_direction_assignment_present(self):
        result = close_mufrad("كَتَبَ")
        assert result.direction_assignment is not None

    def test_weight_fractal_present(self):
        result = close_mufrad("كَتَبَ")
        assert result.weight_fractal is not None

    def test_concept_present(self):
        result = close_mufrad("كَتَبَ")
        assert result.concept is not None

    def test_dalala_link_present(self):
        result = close_mufrad("كَتَبَ")
        assert result.dalala_link is not None


# ── Closure completeness ────────────────────────────────────────────


class TestClosureCompleteness:
    """Verify that known words are fully closed."""

    def test_kataba_is_closed(self):
        result = close_mufrad("كَتَبَ")
        assert result.is_closed is True

    def test_confidence_positive(self):
        result = close_mufrad("كَتَبَ")
        assert result.closure_confidence > 0

    def test_confidence_bounded(self):
        result = close_mufrad("كَتَبَ")
        assert 0 <= result.closure_confidence <= 1.0

    def test_unknown_word_graceful(self):
        result = close_mufrad("xyz_unknown")
        assert isinstance(result, MufradClosureResult)
        # Unknown words should still produce a result (even if not closed)
        assert result.surface == "xyz_unknown"


# ── Determinism ─────────────────────────────────────────────────────


class TestDeterminism:
    """Same word always produces the same result."""

    def test_deterministic(self):
        r1 = close_mufrad("كَتَبَ")
        r2 = close_mufrad("كَتَبَ")
        assert r1.surface == r2.surface
        assert r1.normalized == r2.normalized
        assert r1.is_closed == r2.is_closed
        assert r1.closure_confidence == r2.closure_confidence

    def test_deterministic_direction(self):
        r1 = close_mufrad("كَتَبَ")
        r2 = close_mufrad("كَتَبَ")
        if r1.direction_assignment and r2.direction_assignment:
            assert r1.direction_assignment.genus == r2.direction_assignment.genus


# ── Hierarchical structure ──────────────────────────────────────────


class TestHierarchy:
    """Verify genus > direction > weight > root hierarchy."""

    @pytest.mark.parametrize("word,expected_genus", _KNOWN_WORDS)
    def test_genus_correct(self, word, expected_genus):
        result = close_mufrad(word)
        if result.direction_assignment:
            assert result.direction_assignment.genus == expected_genus

    def test_direction_has_genus(self):
        result = close_mufrad("كَتَبَ")
        if result.direction_assignment:
            assert isinstance(result.direction_assignment.genus, SemanticDirectionGenus)

    def test_weight_has_class(self):
        result = close_mufrad("كَتَبَ")
        if result.weight_fractal:
            assert result.weight_fractal.base_weight.weight_class is not None

    def test_root_in_closure(self):
        result = close_mufrad("كَتَبَ")
        if result.lexical_closure:
            assert len(result.lexical_closure.root) > 0


# ── Fractal structure ───────────────────────────────────────────────


class TestFractalStructure:
    """Verify fractal tree mirrors (E, K, F, C) origin structure."""

    def test_fractal_tree_has_six_phases(self):
        result = close_mufrad("كَتَبَ")
        if result.weight_fractal:
            assert len(result.weight_fractal.fractal_tree) == 6

    def test_fractal_tree_is_chain(self):
        result = close_mufrad("كَتَبَ")
        if result.weight_fractal and result.weight_fractal.fractal_tree:
            tree = result.weight_fractal.fractal_tree
            # First node has no parent
            assert tree[0].parent is None
            # Last node has no children
            assert tree[-1].children == ()


# ── Multiple words ──────────────────────────────────────────────────


class TestMultipleWords:
    """Test closure for multiple known Arabic words."""

    @pytest.mark.parametrize("word", [w for w, _ in _KNOWN_WORDS])
    def test_word_produces_result(self, word):
        result = close_mufrad(word)
        assert isinstance(result, MufradClosureResult)
        assert result.surface == word

    @pytest.mark.parametrize("word", [w for w, _ in _KNOWN_WORDS])
    def test_word_has_direction(self, word):
        result = close_mufrad(word)
        assert result.direction_assignment is not None

    @pytest.mark.parametrize("word", [w for w, _ in _KNOWN_WORDS])
    def test_word_has_weight(self, word):
        result = close_mufrad(word)
        assert result.weight_fractal is not None


# ── Immutability ────────────────────────────────────────────────────


class TestImmutability:
    """MufradClosureResult should be frozen."""

    def test_frozen(self):
        result = close_mufrad("كَتَبَ")
        with pytest.raises(AttributeError):
            result.surface = "changed"  # type: ignore[misc]
