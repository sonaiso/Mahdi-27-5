"""Tests for the Judgement Constitution layer (E8).

Tests judgement records, traces, reviewable verdicts, and related enums.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    CriterionType,
    JudgementRank,
    ReasoningMode,
    ReviewStatus,
)
from arabic_engine.core.types import (
    CriterionSelection,
    JudgementTrace,
    JudgementVerdict,
    ReasoningChain,
    ReviewableVerdict,
)


class TestJudgementVerdict:
    """Tests for JudgementVerdict dataclass."""

    def test_create_record(self) -> None:
        """JudgementVerdict should be constructible."""
        rec = JudgementVerdict(
            judgement_id="J001",
            content="الحكم بأن زيدًا كتب الرسالة",
            rank=JudgementRank.DEFINITIVE,
            reason="Direct evidence from proposition",
            review_status=ReviewStatus.APPROVED,
            confidence=0.95,
            timestamp="2026-04-15T20:00:00Z",
        )
        assert rec.judgement_id == "J001"
        assert rec.rank == JudgementRank.DEFINITIVE
        assert rec.review_status == ReviewStatus.APPROVED

    def test_record_is_frozen(self) -> None:
        """JudgementVerdict should be immutable."""
        rec = JudgementVerdict(
            judgement_id="J002",
            content="test",
            rank=JudgementRank.PROBABLE,
            reason="test",
            review_status=ReviewStatus.PENDING,
            confidence=0.5,
            timestamp="2026-01-01T00:00:00Z",
        )
        try:
            rec.confidence = 0.9  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestJudgementTrace:
    """Tests for JudgementTrace dataclass."""

    def test_create_trace(self) -> None:
        """JudgementTrace should be constructible."""
        chain = ReasoningChain(
            steps=(("evaluate proposition", 0.9),),
            mode=ReasoningMode.DEDUCTIVE,
            premises=("Subject identified",),
            conclusion="Judgement reached",
            overall_confidence=0.9,
        )
        criterion = CriterionSelection(
            criterion=CriterionType.SEMANTIC,
            reason="Semantic evaluation",
            weight=0.8,
            applicable=True,
        )
        trace = JudgementTrace(
            judgement_id="J001",
            evidence=("dalala_link_1", "syntax_node_2"),
            reasoning_chain=chain,
            criteria_used=(criterion,),
            layers_consulted=("E5", "E6", "E7"),
        )
        assert trace.judgement_id == "J001"
        assert len(trace.evidence) == 2
        assert len(trace.layers_consulted) == 3


class TestReviewableVerdict:
    """Tests for ReviewableVerdict dataclass."""

    def test_create_verdict(self) -> None:
        """ReviewableVerdict should be constructible."""
        rec = JudgementVerdict(
            judgement_id="J001",
            content="test",
            rank=JudgementRank.PREDOMINANT,
            reason="test",
            review_status=ReviewStatus.PENDING,
            confidence=0.8,
            timestamp="2026-01-01T00:00:00Z",
        )
        chain = ReasoningChain(
            steps=(),
            mode=ReasoningMode.DEDUCTIVE,
            premises=(),
            conclusion="test",
            overall_confidence=0.8,
        )
        trace = JudgementTrace(
            judgement_id="J001",
            evidence=(),
            reasoning_chain=chain,
            criteria_used=(),
            layers_consulted=(),
        )
        verdict = ReviewableVerdict(
            judgement=rec,
            trace=trace,
            is_reviewable=True,
        )
        assert verdict.is_reviewable is True
        assert verdict.judgement.rank == JudgementRank.PREDOMINANT

    def test_verdict_with_history(self) -> None:
        """Verdict can have review history."""
        rec = JudgementVerdict(
            judgement_id="J001",
            content="test",
            rank=JudgementRank.DOUBTFUL,
            reason="test",
            review_status=ReviewStatus.CONTESTED,
            confidence=0.3,
            timestamp="2026-01-01T00:00:00Z",
        )
        chain = ReasoningChain(
            steps=(),
            mode=ReasoningMode.ABDUCTIVE,
            premises=(),
            conclusion="test",
            overall_confidence=0.3,
        )
        trace = JudgementTrace("J001", (), chain, (), ())
        verdict = ReviewableVerdict(
            judgement=rec,
            trace=trace,
            is_reviewable=True,
            review_history=("contested_2026-01-01", "revised_2026-01-02"),
        )
        assert len(verdict.review_history) == 2


class TestJudgementRankEnum:
    """Tests for JudgementRank enum."""

    def test_all_ranks_exist(self) -> None:
        """All expected judgement ranks should exist."""
        expected = ["DEFINITIVE", "PREDOMINANT", "PROBABLE", "POSSIBLE", "DOUBTFUL"]
        for name in expected:
            assert hasattr(JudgementRank, name)

    def test_rank_ordering(self) -> None:
        """Ranks should be defined in decreasing certainty order."""
        ranks = list(JudgementRank)
        assert ranks[0].name == "DEFINITIVE"
        assert ranks[-1].name == "DOUBTFUL"


class TestReviewStatusEnum:
    """Tests for ReviewStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """All expected review statuses should exist."""
        expected = ["PENDING", "APPROVED", "CONTESTED", "REVISED", "FINAL"]
        for name in expected:
            assert hasattr(ReviewStatus, name)
