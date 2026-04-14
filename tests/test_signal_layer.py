"""Tests for the signal layer (unicode_atoms, normalization, segmentation).

Invariants tested
-----------------
1. No Unicode silent loss — every character becomes an atom.
2. No normalization without justification (trace).
3. No segmentation without boundary basis.
4. Signal types are correctly classified.
"""

from __future__ import annotations

from arabic_engine.core.enums import ActivationStage, HypothesisStatus, SignalType
from arabic_engine.signal.normalization import normalize_atoms
from arabic_engine.signal.segmentation import segment
from arabic_engine.signal.unicode_atoms import decompose

# ═══════════════════════════════════════════════════════════════════════
# Unicode atom decomposition
# ═══════════════════════════════════════════════════════════════════════


class TestDecompose:
    """decompose() correctly breaks text into atoms."""

    def test_no_unicode_silent_loss(self):
        """Every character in the input must produce an atom."""
        text = "كَتَبَ"
        atoms = decompose(text)
        assert len(atoms) == len(text)

    def test_empty_input(self):
        atoms = decompose("")
        assert atoms == []

    def test_single_char(self):
        atoms = decompose("ك")
        assert len(atoms) == 1
        assert atoms[0].char == "ك"
        assert atoms[0].codepoint == ord("ك")
        assert atoms[0].position_index == 0

    def test_arabic_letter_classified_as_base_letter(self):
        atoms = decompose("ك")
        assert atoms[0].signal_type == SignalType.BASE_LETTER

    def test_diacritic_classified_as_diacritic(self):
        # Fatha (U+064E)
        atoms = decompose("\u064E")
        assert atoms[0].signal_type == SignalType.DIACRITIC

    def test_whitespace_classified(self):
        atoms = decompose(" ")
        assert atoms[0].signal_type == SignalType.WHITESPACE

    def test_numeral_classified(self):
        atoms = decompose("5")
        assert atoms[0].signal_type == SignalType.NUMERAL

    def test_punctuation_classified(self):
        atoms = decompose(".")
        assert atoms[0].signal_type == SignalType.PUNCTUATION

    def test_atom_ids_unique(self):
        atoms = decompose("كتب")
        ids = [a.atom_id for a in atoms]
        assert len(ids) == len(set(ids))

    def test_combining_class_nonzero_for_diacritics(self):
        atoms = decompose("\u064E")  # Fatha
        assert atoms[0].combining_class > 0

    def test_combining_class_zero_for_base(self):
        atoms = decompose("ك")
        assert atoms[0].combining_class == 0


# ═══════════════════════════════════════════════════════════════════════
# Normalization
# ═══════════════════════════════════════════════════════════════════════


class TestNormalization:
    """normalize_atoms() produces signal units with trace."""

    def test_basic_normalization(self):
        atoms = decompose("كتب الرسالة")
        units, traces = normalize_atoms(atoms)
        assert len(units) == 2
        assert units[0].normalized_text != ""
        assert units[1].normalized_text != ""

    def test_empty_input(self):
        units, traces = normalize_atoms([])
        assert units == []
        assert traces == []

    def test_signal_units_have_valid_spans(self):
        atoms = decompose("كتب")
        units, _ = normalize_atoms(atoms)
        assert len(units) == 1
        assert units[0].source_span[0] >= 0
        assert units[0].source_span[1] >= units[0].source_span[0]

    def test_signal_unit_ids_unique(self):
        atoms = decompose("كتب الرسالة")
        units, _ = normalize_atoms(atoms)
        ids = [u.unit_id for u in units]
        assert len(ids) == len(set(ids))


# ═══════════════════════════════════════════════════════════════════════
# Segmentation
# ═══════════════════════════════════════════════════════════════════════


class TestSegmentation:
    """segment() produces hypothesis nodes with boundary basis."""

    def test_one_hypothesis_per_signal_unit(self):
        atoms = decompose("كتب الرسالة")
        units, _ = normalize_atoms(atoms)
        segs = segment(units)
        assert len(segs) == len(units)

    def test_segmentation_hypotheses_are_active(self):
        atoms = decompose("كتب")
        units, _ = normalize_atoms(atoms)
        segs = segment(units)
        for s in segs:
            assert s.status == HypothesisStatus.ACTIVE

    def test_segmentation_hypotheses_have_boundary_basis(self):
        """No segmentation without boundary basis."""
        atoms = decompose("كتب")
        units, _ = normalize_atoms(atoms)
        segs = segment(units)
        for s in segs:
            assert s.get("boundary_basis") is not None
            assert s.get("boundary_basis") != ""

    def test_segmentation_at_signal_stage(self):
        atoms = decompose("كتب")
        units, _ = normalize_atoms(atoms)
        segs = segment(units)
        for s in segs:
            assert s.stage == ActivationStage.SIGNAL

    def test_segmentation_has_source_refs(self):
        """No hypothesis without source_refs."""
        atoms = decompose("كتب")
        units, _ = normalize_atoms(atoms)
        segs = segment(units)
        for s in segs:
            assert len(s.source_refs) > 0

    def test_empty_input(self):
        segs = segment([])
        assert segs == []
