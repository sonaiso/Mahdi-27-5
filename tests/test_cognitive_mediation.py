"""Tests for the Cognitive Mediation layer (E7).

Tests cognitive state, reasoning chains, and criterion selection.
"""

from __future__ import annotations

from arabic_engine.core.enums import CriterionType, ReasoningMode
from arabic_engine.core.types import CognitiveState, CriterionSelection, ReasoningChain


class TestCognitiveState:
    """Tests for CognitiveState dataclass."""

    def test_create_state(self) -> None:
        """CognitiveState should be constructible."""
        state = CognitiveState(
            reasoning_mode=ReasoningMode.DEDUCTIVE,
            active_criteria=(CriterionType.SEMANTIC,),
            intermediate_conclusions=("premise_1_validated",),
            confidence=0.85,
        )
        assert state.reasoning_mode == ReasoningMode.DEDUCTIVE
        assert state.confidence == 0.85

    def test_state_is_frozen(self) -> None:
        """CognitiveState should be immutable."""
        state = CognitiveState(
            reasoning_mode=ReasoningMode.DEDUCTIVE,
            active_criteria=(),
            intermediate_conclusions=(),
            confidence=0.5,
        )
        try:
            state.confidence = 0.9  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass

    def test_multiple_criteria(self) -> None:
        """State can have multiple active criteria."""
        state = CognitiveState(
            reasoning_mode=ReasoningMode.ANALOGICAL,
            active_criteria=(CriterionType.SEMANTIC, CriterionType.SYNTACTIC),
            intermediate_conclusions=(),
            confidence=0.7,
        )
        assert len(state.active_criteria) == 2


class TestReasoningChain:
    """Tests for ReasoningChain dataclass."""

    def test_create_chain(self) -> None:
        """ReasoningChain should be constructible."""
        chain = ReasoningChain(
            steps=(("step_1: validate subject", 0.9), ("step_2: apply rule", 0.85)),
            mode=ReasoningMode.DEDUCTIVE,
            premises=("All men are mortal", "Socrates is a man"),
            conclusion="Socrates is mortal",
            overall_confidence=0.85,
        )
        assert len(chain.steps) == 2
        assert chain.conclusion == "Socrates is mortal"

    def test_chain_confidence_in_range(self) -> None:
        """Overall confidence should be in [0, 1]."""
        chain = ReasoningChain(
            steps=(),
            mode=ReasoningMode.INDUCTIVE,
            premises=(),
            conclusion="test",
            overall_confidence=0.75,
        )
        assert 0 <= chain.overall_confidence <= 1


class TestCriterionSelection:
    """Tests for CriterionSelection dataclass."""

    def test_create_selection(self) -> None:
        """CriterionSelection should be constructible."""
        sel = CriterionSelection(
            criterion=CriterionType.EPISTEMIC,
            reason="Knowledge-based evaluation required",
            weight=0.9,
            applicable=True,
        )
        assert sel.criterion == CriterionType.EPISTEMIC
        assert sel.applicable is True

    def test_not_applicable(self) -> None:
        """CriterionSelection can be non-applicable."""
        sel = CriterionSelection(
            criterion=CriterionType.PRAGMATIC,
            reason="No context available",
            weight=0.0,
            applicable=False,
        )
        assert sel.applicable is False


class TestReasoningModeEnum:
    """Tests for ReasoningMode enum."""

    def test_all_modes_exist(self) -> None:
        """All expected reasoning modes should exist."""
        expected = ["DEDUCTIVE", "INDUCTIVE", "ABDUCTIVE", "ANALOGICAL"]
        for name in expected:
            assert hasattr(ReasoningMode, name)


class TestCriterionTypeEnum:
    """Tests for CriterionType enum."""

    def test_all_criteria_exist(self) -> None:
        """All expected criterion types should exist."""
        expected = ["SEMANTIC", "SYNTACTIC", "PRAGMATIC", "EPISTEMIC", "NORMATIVE"]
        for name in expected:
            assert hasattr(CriterionType, name)
