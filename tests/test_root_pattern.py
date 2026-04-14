"""Comprehensive tests for arabic_engine.signifier.root_pattern."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import POS
from arabic_engine.core.types import LexicalClosure, RootPattern
from arabic_engine.signifier.root_pattern import (
    batch_closure,
    extract_root_pattern,
    lexical_closure,
)

# ── extract_root_pattern ───────────────────────────────────────────


class TestExtractRootPattern:
    """Tests for extract_root_pattern()."""

    def test_known_diacritized_verb(self):
        result = extract_root_pattern("كَتَبَ")
        assert result is not None
        assert isinstance(result, RootPattern)

    def test_known_undiacritized_verb(self):
        result = extract_root_pattern("كتب")
        assert result is not None
        assert result.root == ("ك", "ت", "ب")
        assert result.pattern == "فَعَلَ"

    def test_unknown_token_returns_none(self):
        assert extract_root_pattern("مجهول") is None

    def test_root_field(self):
        result = extract_root_pattern("كَتَبَ")
        assert result.root == ("ك", "ت", "ب")

    def test_pattern_field(self):
        result = extract_root_pattern("كَتَبَ")
        assert result.pattern == "فَعَلَ"

    def test_root_id_field(self):
        result = extract_root_pattern("كَتَبَ")
        assert result.root_id == 1

    def test_pattern_id_field(self):
        result = extract_root_pattern("كَتَبَ")
        assert result.pattern_id == 1

    def test_noun_diacritized(self):
        result = extract_root_pattern("زَيْدٌ")
        assert result is not None
        assert result.root == ("ز", "ي", "د")
        assert result.pattern == "فَعْل"
        assert result.root_id == 2

    def test_noun_with_article(self):
        result = extract_root_pattern("الرسالة")
        assert result is not None
        assert result.root == ("ر", "س", "ل")
        assert result.pattern == "فِعَالَة"

    def test_frozen_dataclass(self):
        result = extract_root_pattern("كتب")
        with pytest.raises(AttributeError):
            result.root = ("x",)


# ── lexical_closure ────────────────────────────────────────────────


class TestLexicalClosure:
    """Tests for lexical_closure()."""

    def test_known_verb(self):
        lc = lexical_closure("كَتَبَ")
        assert lc.surface == "كَتَبَ"
        assert lc.lemma == "كَتَبَ"
        assert lc.root == ("ك", "ت", "ب")
        assert lc.pattern == "فَعَلَ"
        assert lc.pos is POS.FI3L

    def test_known_noun(self):
        lc = lexical_closure("زَيْدٌ")
        assert lc.surface == "زَيْدٌ"
        assert lc.lemma == "زَيْد"
        assert lc.pos is POS.ISM
        assert lc.lemma_id == 2

    def test_known_noun_with_article(self):
        lc = lexical_closure("الرِّسَالَةَ")
        assert lc.lemma == "رِسَالَة"
        assert lc.pos is POS.ISM
        assert lc.root_id == 3
        assert lc.pattern_id == 3

    def test_known_zarf(self):
        lc = lexical_closure("أَمْسَ")
        assert lc.pos is POS.ZARF
        assert lc.lemma == "أَمْس"
        assert lc.root == ("أ", "م", "س")

    def test_known_zarf_ghadan(self):
        lc = lexical_closure("غَدًا")
        assert lc.pos is POS.ZARF
        assert lc.root == ("غ", "د", "و")
        assert lc.lemma == "غَد"

    def test_unknown_token_fallback(self):
        lc = lexical_closure("مجهول")
        assert lc.surface == "مجهول"
        assert lc.lemma == "مجهول"
        assert lc.root == ()
        assert lc.pattern == ""
        assert lc.pos is POS.UNKNOWN

    def test_unknown_token_default_ids(self):
        lc = lexical_closure("مجهول")
        assert lc.lemma_id == 0
        assert lc.root_id == 0
        assert lc.pattern_id == 0
        assert lc.pos_id == 0

    def test_known_token_pos_id_matches_enum(self):
        lc = lexical_closure("كَتَبَ")
        assert lc.pos_id == POS.FI3L.value

    def test_returns_lexical_closure_type(self):
        assert isinstance(lexical_closure("كتب"), LexicalClosure)


# ── batch_closure ──────────────────────────────────────────────────


class TestBatchClosure:
    """Tests for batch_closure()."""

    def test_empty_list(self):
        assert batch_closure([]) == []

    def test_length_matches_input(self):
        tokens = ["كتب", "زيد", "الرسالة"]
        assert len(batch_closure(tokens)) == 3

    def test_order_preserved(self):
        tokens = ["كتب", "زيد"]
        results = batch_closure(tokens)
        assert results[0].surface == "كتب"
        assert results[1].surface == "زيد"

    def test_mixed_known_and_unknown(self):
        tokens = ["كتب", "مجهول"]
        results = batch_closure(tokens)
        assert results[0].pos is POS.FI3L
        assert results[1].pos is POS.UNKNOWN

    def test_all_unknown(self):
        results = batch_closure(["foo", "bar"])
        assert all(r.pos is POS.UNKNOWN for r in results)
        assert all(r.root == () for r in results)

    def test_single_token(self):
        results = batch_closure(["أمس"])
        assert len(results) == 1
        assert results[0].pos is POS.ZARF
