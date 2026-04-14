"""Comprehensive tests for arabic_engine.signifier.unicode_norm."""

from __future__ import annotations

import unicodedata
import unittest

from arabic_engine.core.types import Grapheme
from arabic_engine.signifier.unicode_norm import (
    normalize,
    normalize_hamza,
    to_graphemes,
    tokenize,
)


# ── helpers / constants ──────────────────────────────────────────────
_TATWEEL = "\u0640"
_FATHA = "\u064E"       # Arabic fathah
_SHADDA = "\u0651"      # Arabic shadda
_DAMMA = "\u064F"       # Arabic dammah
_KASRA = "\u0650"       # Arabic kasra
_FATHATAN = "\u064B"    # Arabic fathatan
_DAMMATAN = "\u064C"    # Arabic dammatan


class TestNormalize(unittest.TestCase):
    """Tests for normalize()."""

    def test_tatweel_removal(self):
        # tatweel between two letters is removed
        self.assertEqual(normalize(f"\u0643{_TATWEEL}\u0628"), "\u0643\u0628")

    def test_multiple_tatweels(self):
        self.assertEqual(
            normalize(f"\u0643{_TATWEEL}{_TATWEEL}{_TATWEEL}\u0628"),
            "\u0643\u0628",
        )

    def test_whitespace_collapsing(self):
        self.assertEqual(normalize("\u0643  \u0628"), "\u0643 \u0628")

    def test_leading_trailing_whitespace(self):
        self.assertEqual(normalize("  \u0643 \u0628  "), "\u0643 \u0628")

    def test_tabs_and_newlines(self):
        self.assertEqual(normalize("\u0643\t\n\u0628"), "\u0643 \u0628")

    def test_strip_tashkil_true(self):
        text = f"\u0643{_FATHA}\u062A{_FATHA}\u0628{_FATHA}"
        self.assertEqual(normalize(text, strip_tashkil=True), "\u0643\u062A\u0628")

    def test_strip_tashkil_false_preserves_marks(self):
        text = f"\u0643{_FATHA}\u062A{_FATHA}\u0628{_FATHA}"
        self.assertEqual(normalize(text, strip_tashkil=False), text)

    def test_empty_string(self):
        self.assertEqual(normalize(""), "")

    def test_nfc_normalization(self):
        # Build a string in NFD form; normalize should convert to NFC
        nfd = unicodedata.normalize("NFD", "\u00E9")  # é decomposed
        result = normalize(nfd)
        self.assertEqual(result, "\u00E9")
        self.assertTrue(unicodedata.is_normalized("NFC", result))

    def test_strip_tashkil_removes_shadda(self):
        text = f"\u0634{_SHADDA}"
        self.assertEqual(normalize(text, strip_tashkil=True), "\u0634")


class TestNormalizeHamza(unittest.TestCase):
    """Tests for normalize_hamza()."""

    def test_alef_madda(self):
        self.assertEqual(normalize_hamza("\u0622"), "\u0627")

    def test_alef_hamza_above(self):
        self.assertEqual(normalize_hamza("\u0623"), "\u0627")

    def test_alef_hamza_below(self):
        self.assertEqual(normalize_hamza("\u0625"), "\u0627")

    def test_no_hamza_unchanged(self):
        plain = "\u0643\u062A\u0628"
        self.assertEqual(normalize_hamza(plain), plain)

    def test_mixed_text(self):
        text = "\u0623\u0647\u0644\u0627"
        self.assertEqual(normalize_hamza(text), "\u0627\u0647\u0644\u0627")

    def test_multiple_hamza_variants(self):
        text = "\u0622\u0623\u0625"
        self.assertEqual(normalize_hamza(text), "\u0627\u0627\u0627")


class TestTokenize(unittest.TestCase):
    """Tests for tokenize()."""

    def test_basic_split(self):
        tokens = tokenize("\u0643\u062A\u0628 \u0632\u064A\u062F")
        self.assertEqual(tokens, ["\u0643\u062A\u0628", "\u0632\u064A\u062F"])

    def test_multiple_spaces(self):
        tokens = tokenize("\u0643\u062A\u0628   \u0632\u064A\u062F")
        self.assertEqual(tokens, ["\u0643\u062A\u0628", "\u0632\u064A\u062F"])

    def test_empty_string(self):
        self.assertEqual(tokenize(""), [])

    def test_single_word(self):
        self.assertEqual(tokenize("\u0643\u062A\u0628"), ["\u0643\u062A\u0628"])

    def test_tatweel_removed_before_split(self):
        text = f"\u0643{_TATWEEL}\u062A\u0628"
        self.assertEqual(tokenize(text), ["\u0643\u062A\u0628"])


class TestToGraphemes(unittest.TestCase):
    """Tests for to_graphemes()."""

    def test_plain_consonant(self):
        gs = to_graphemes("\u0643")
        self.assertEqual(len(gs), 1)
        self.assertEqual(gs[0], Grapheme(base=0x0643, marks=()))

    def test_consonant_with_fatha(self):
        gs = to_graphemes(f"\u0643{_FATHA}")
        self.assertEqual(len(gs), 1)
        self.assertEqual(gs[0], Grapheme(base=0x0643, marks=(0x064E,)))
        self.assertEqual(gs[0].char, f"\u0643{_FATHA}")

    def test_consonant_shadda_fatha(self):
        gs = to_graphemes(f"\u0643{_SHADDA}{_FATHA}")
        self.assertEqual(len(gs), 1)
        self.assertEqual(gs[0], Grapheme(base=0x0643, marks=(0x0651, 0x064E)))

    def test_empty_string(self):
        self.assertEqual(to_graphemes(""), [])

    def test_multiple_graphemes(self):
        text = f"\u0643{_FATHA}\u062A{_DAMMA}\u0628{_KASRA}"
        gs = to_graphemes(text)
        self.assertEqual(len(gs), 3)
        self.assertEqual(gs[0].base, 0x0643)
        self.assertEqual(gs[1].base, 0x062A)
        self.assertEqual(gs[2].base, 0x0628)
        self.assertEqual(gs[0].marks, (0x064E,))
        self.assertEqual(gs[1].marks, (0x064F,))
        self.assertEqual(gs[2].marks, (0x0650,))

    def test_char_property_round_trip(self):
        text = f"\u0643{_SHADDA}{_FATHA}"
        gs = to_graphemes(text)
        self.assertEqual(gs[0].char, text)


if __name__ == "__main__":
    unittest.main()
