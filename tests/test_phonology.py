"""Comprehensive tests for arabic_engine.signifier.phonology."""

from __future__ import annotations

from arabic_engine.core.types import Grapheme, Syllable
from arabic_engine.signifier.phonology import (
    get_short_vowel,
    has_shadda,
    is_consonant,
    is_vowel_mark,
    syllabify,
)

# ── Code-point constants ────────────────────────────────────────────
BA = 0x0628
TA = 0x062A
KAF = 0x0643
LAM = 0x0644
MEEM = 0x0645

ALEF = 0x0627
WAW = 0x0648
YA = 0x064A

FATHA = 0x064E
DAMMA = 0x064F
KASRA = 0x0650
SUKUN = 0x0652
SHADDA = 0x0651

FATHATAN = 0x064B
DAMMATAN = 0x064C
KASRATAN = 0x064D


# ── Helpers ─────────────────────────────────────────────────────────
def _g(base: int, *marks: int) -> Grapheme:
    """Shorthand to build a Grapheme."""
    return Grapheme(base=base, marks=tuple(marks))


# ═══════════════════════════════════════════════════════════════════
class TestIsConsonant:
    """Tests for is_consonant()."""

    def test_regular_consonant_ba(self):
        assert is_consonant(_g(BA)) is True

    def test_regular_consonant_kaf(self):
        assert is_consonant(_g(KAF)) is True

    def test_long_vowel_alef(self):
        assert is_consonant(_g(ALEF)) is False

    def test_long_vowel_waw(self):
        assert is_consonant(_g(WAW)) is False

    def test_long_vowel_ya(self):
        assert is_consonant(_g(YA)) is False

    def test_consonant_with_marks(self):
        assert is_consonant(_g(BA, FATHA)) is True


# ═══════════════════════════════════════════════════════════════════
class TestIsVowelMark:
    """Tests for is_vowel_mark()."""

    def test_fatha(self):
        assert is_vowel_mark(FATHA) is True

    def test_damma(self):
        assert is_vowel_mark(DAMMA) is True

    def test_kasra(self):
        assert is_vowel_mark(KASRA) is True

    def test_shadda_not_vowel(self):
        assert is_vowel_mark(SHADDA) is False

    def test_sukun_not_vowel(self):
        assert is_vowel_mark(SUKUN) is False

    def test_consonant_cp_not_vowel(self):
        assert is_vowel_mark(BA) is False

    def test_tanwin_not_short_vowel(self):
        assert is_vowel_mark(FATHATAN) is False
        assert is_vowel_mark(DAMMATAN) is False
        assert is_vowel_mark(KASRATAN) is False


# ═══════════════════════════════════════════════════════════════════
class TestHasShadda:
    """Tests for has_shadda()."""

    def test_with_shadda(self):
        assert has_shadda(_g(BA, SHADDA)) is True

    def test_without_shadda(self):
        assert has_shadda(_g(BA, FATHA)) is False

    def test_no_marks(self):
        assert has_shadda(_g(BA)) is False

    def test_multiple_marks_including_shadda(self):
        assert has_shadda(_g(BA, SHADDA, FATHA)) is True

    def test_multiple_marks_without_shadda(self):
        assert has_shadda(_g(BA, FATHA, KASRA)) is False


# ═══════════════════════════════════════════════════════════════════
class TestGetShortVowel:
    """Tests for get_short_vowel()."""

    def test_fatha_present(self):
        assert get_short_vowel(_g(BA, FATHA)) == FATHA

    def test_damma_present(self):
        assert get_short_vowel(_g(BA, DAMMA)) == DAMMA

    def test_kasra_present(self):
        assert get_short_vowel(_g(BA, KASRA)) == KASRA

    def test_no_marks(self):
        assert get_short_vowel(_g(BA)) is None

    def test_shadda_and_fatha(self):
        """Shadda comes first; fatha should still be found."""
        assert get_short_vowel(_g(BA, SHADDA, FATHA)) == FATHA

    def test_only_shadda(self):
        assert get_short_vowel(_g(BA, SHADDA)) is None

    def test_only_sukun(self):
        assert get_short_vowel(_g(BA, SUKUN)) is None


# ═══════════════════════════════════════════════════════════════════
class TestSyllabify:
    """Tests for syllabify()."""

    def test_empty_input(self):
        assert syllabify([]) == []

    def test_single_consonant_no_vowel(self):
        """A bare consonant produces a syllable with empty nucleus."""
        result = syllabify([_g(BA)])
        assert len(result) == 1
        assert result[0].onset == (BA,)
        assert result[0].nucleus == ()
        assert result[0].coda == ()
        assert result[0].weight == 1

    def test_cv_light_syllable(self):
        """Consonant + short vowel → weight 1."""
        result = syllabify([_g(BA, FATHA)])
        assert len(result) == 1
        syl = result[0]
        assert syl.onset == (BA,)
        assert syl.nucleus == (FATHA,)
        assert syl.coda == ()
        assert syl.weight == 1

    def test_cvc_heavy_syllable(self):
        """Consonant-vowel-consonant → weight 2."""
        # بَبْ  – ba (with fatha) + ba (with sukun, no short vowel)
        graphemes = [_g(BA, FATHA), _g(BA, SUKUN)]
        result = syllabify(graphemes)
        assert len(result) == 1
        syl = result[0]
        assert syl.onset == (BA,)
        assert syl.nucleus == (FATHA,)
        assert syl.coda == (BA,)
        assert syl.weight == 2

    def test_cvv_super_heavy_syllable(self):
        """Consonant + short vowel + long-vowel letter → weight 3."""
        # بَا  – ba (fatha) + alef
        graphemes = [_g(BA, FATHA), _g(ALEF)]
        result = syllabify(graphemes)
        assert len(result) == 1
        syl = result[0]
        assert syl.onset == (BA,)
        assert syl.nucleus == (FATHA, ALEF)
        assert syl.coda == ()
        assert syl.weight == 3

    def test_multi_syllable_two_cv(self):
        """Two CV syllables: كَتَ → ka-ta."""
        graphemes = [_g(KAF, FATHA), _g(TA, FATHA)]
        result = syllabify(graphemes)
        assert len(result) == 2
        assert result[0] == Syllable(onset=(KAF,), nucleus=(FATHA,), coda=(), weight=1)
        assert result[1] == Syllable(onset=(TA,), nucleus=(FATHA,), coda=(), weight=1)

    def test_multi_syllable_cv_cvc(self):
        """كَتَبْ → ka-tab (CV + CVC)."""
        graphemes = [_g(KAF, FATHA), _g(TA, FATHA), _g(BA, SUKUN)]
        result = syllabify(graphemes)
        assert len(result) == 2
        assert result[0].weight == 1  # ka – light
        assert result[1].weight == 2  # tab – heavy
        assert result[1].coda == (BA,)

    def test_syllabify_returns_syllable_instances(self):
        result = syllabify([_g(BA, FATHA)])
        assert isinstance(result[0], Syllable)

    def test_cvv_with_waw(self):
        """بُو → bu + waw → super-heavy."""
        graphemes = [_g(BA, DAMMA), _g(WAW)]
        result = syllabify(graphemes)
        assert len(result) == 1
        assert result[0].nucleus == (DAMMA, WAW)
        assert result[0].weight == 3

    def test_cvv_with_ya(self):
        """بِي → bi + ya → super-heavy."""
        graphemes = [_g(BA, KASRA), _g(YA)]
        result = syllabify(graphemes)
        assert len(result) == 1
        assert result[0].nucleus == (KASRA, YA)
        assert result[0].weight == 3
