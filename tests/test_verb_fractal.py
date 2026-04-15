"""Tests for verb fractal node builder — Module 8."""

from arabic_engine.core.enums import (
    POS,
    VerbCompleteness,
    VerbFractalStage,
    VerbTense,
)
from arabic_engine.verb.fractal_node import build


class TestBuildFractalNode:
    def test_kataba_full_node(self):
        node = build("كَتَبَ", pattern="فَعَلَ")
        assert node is not None
        # Profile
        assert node.profile.root == ("ك", "ت", "ب")
        assert node.profile.tense == VerbTense.MADI
        assert node.profile.completeness == VerbCompleteness.KAMIL
        # Threshold
        assert node.threshold.is_complete is True
        # Derivatives
        assert node.derivatives.masdar != ""
        assert node.derivatives.ism_fa3il != ""
        # Fractal stage (complete = RADD)
        assert node.fractal_stage == VerbFractalStage.RADD
        # Coherence links
        assert len(node.coherence_links) == 6
        stage_names = [link[0] for link in node.coherence_links]
        assert VerbFractalStage.TA3YIN.name in stage_names
        assert VerbFractalStage.RADD.name in stage_names

    def test_nasara(self):
        node = build("نَصَرَ", pattern="فَعَلَ")
        assert node is not None
        assert node.profile.root == ("ن", "ص", "ر")

    def test_non_verb_returns_none(self):
        node = build("زَيْد", pattern="فَعْل", pos=POS.ISM)
        assert node is None

    def test_unknown_returns_none(self):
        node = build("غَرِيب_جِدًّا")
        assert node is None


class TestFractalStages:
    def test_all_six_stages_have_evidence(self):
        node = build("كَتَبَ", pattern="فَعَلَ")
        assert node is not None
        stage_names = {link[0] for link in node.coherence_links}
        expected = {s.name for s in VerbFractalStage}
        assert expected == stage_names


class TestFractalNodeImmutability:
    def test_frozen(self):
        node = build("كَتَبَ", pattern="فَعَلَ")
        assert node is not None
        try:
            node.fractal_stage = VerbFractalStage.TA3YIN  # type: ignore[misc]
            assert False, "Should not allow mutation"
        except AttributeError:
            pass
