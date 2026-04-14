"""Tests for core enums and types."""

from __future__ import annotations

from arabic_engine.core.enums import POS, GuidanceState, TruthState


class TestEnums:
    """Basic enum sanity checks."""

    def test_truth_state_has_certain(self):
        assert TruthState.CERTAIN is not None

    def test_guidance_state_exists(self):
        assert hasattr(GuidanceState, "NOT_APPLICABLE")

    def test_pos_has_ism(self):
        assert POS.ISM is not None

    def test_pos_has_fi3l(self):
        assert POS.FI3L is not None
