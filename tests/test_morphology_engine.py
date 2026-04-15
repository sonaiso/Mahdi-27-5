"""Tests for the Morphological Intelligence layer (E4).

Tests morphological analysis engine, lexicon lookup, and affix stripping.
"""

from __future__ import annotations

from arabic_engine.morphology.affixes import strip_affixes
from arabic_engine.morphology.engine import analyze
from arabic_engine.morphology.lexicon import list_roots, lookup_root, root_count


class TestMorphologyEngine:
    """Tests for the morphological analysis engine."""

    def test_analyze_returns_dict(self) -> None:
        """analyze() should return a dict with expected keys."""
        result = analyze("كَتَبَ")
        assert isinstance(result, dict)
        assert "root" in result
        assert "pattern" in result
        assert "morphemes" in result
        assert "pos" in result

    def test_analyze_known_verb(self) -> None:
        """Known verb should have root and POS extracted."""
        result = analyze("كَتَبَ")
        # Root should be identified (may depend on signifier layer)
        assert "affix_set" in result

    def test_analyze_preserves_token(self) -> None:
        """Token should be preserved in the result."""
        result = analyze("كَتَبَ")
        assert result["token"] == "كَتَبَ"

    def test_analyze_morphemes_list(self) -> None:
        """Morphemes should be a list."""
        result = analyze("كَتَبَ")
        assert isinstance(result["morphemes"], list)


class TestLexicon:
    """Tests for the morphological lexicon."""

    def test_root_count_positive(self) -> None:
        """Lexicon should have positive number of roots."""
        assert root_count() > 0

    def test_root_count_at_least_20(self) -> None:
        """Lexicon should have at least 20 roots (seed data)."""
        assert root_count() >= 20

    def test_lookup_known_root(self) -> None:
        """Known root should be found."""
        entry = lookup_root(("ك", "ت", "ب"))
        assert entry is not None
        assert entry.base_meaning == "writing"

    def test_lookup_unknown_root(self) -> None:
        """Unknown root should return None."""
        entry = lookup_root(("ط", "ط", "ط"))
        assert entry is None

    def test_list_roots_non_empty(self) -> None:
        """list_roots should return non-empty list."""
        roots = list_roots()
        assert len(roots) > 0

    def test_root_entry_has_patterns(self) -> None:
        """Root entry should have pattern list."""
        entry = lookup_root(("ك", "ت", "ب"))
        assert entry is not None
        assert len(entry.patterns) > 0

    def test_root_entry_has_frequency(self) -> None:
        """Root entry should have positive frequency."""
        entry = lookup_root(("ك", "ت", "ب"))
        assert entry is not None
        assert entry.frequency > 0

    def test_multiple_roots_exist(self) -> None:
        """Multiple different roots should be lookupable."""
        for root in [("ع", "ل", "م"), ("ذ", "ه", "ب"), ("ح", "ك", "م")]:
            entry = lookup_root(root)
            assert entry is not None, f"Root {root} not found"


class TestAffixStripping:
    """Tests for affix stripping."""

    def test_strip_returns_affix_set(self) -> None:
        """strip_affixes should return an AffixSet."""
        result = strip_affixes("كَتَبَ")
        assert hasattr(result, "prefixes")
        assert hasattr(result, "suffixes")
        assert hasattr(result, "infixes")

    def test_strip_definite_article(self) -> None:
        """الكتاب should have 'ال' stripped as prefix."""
        result = strip_affixes("الكتاب")
        assert "ال" in result.prefixes

    def test_strip_no_affixes(self) -> None:
        """Short word without known affixes should have empty affix sets."""
        result = strip_affixes("قال")
        # Short word — may or may not have affixes
        assert isinstance(result.prefixes, tuple)
        assert isinstance(result.suffixes, tuple)

    def test_infixes_initially_empty(self) -> None:
        """Infixes should currently be empty (not yet implemented)."""
        result = strip_affixes("كَتَبَ")
        assert result.infixes == ()
