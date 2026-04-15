"""Tests for the Semantic Structuring layer (E6).

Tests semantic frames, concept relations, and denotation maps.
"""

from __future__ import annotations

from arabic_engine.core.enums import SemanticFrameType, SemanticRelationType
from arabic_engine.core.types import DenotationMap, SemanticConceptRelation, SemanticFrame


class TestSemanticFrame:
    """Tests for SemanticFrame dataclass."""

    def test_create_action_frame(self) -> None:
        """ACTION frame should be constructible."""
        frame = SemanticFrame(
            frame_type=SemanticFrameType.ACTION,
            predicate="كَتَبَ",
            participants=(("agent", "زَيْد"), ("patient", "الرِّسَالَة")),
        )
        assert frame.frame_type == SemanticFrameType.ACTION
        assert frame.predicate == "كَتَبَ"
        assert len(frame.participants) == 2

    def test_create_state_frame(self) -> None:
        """STATE frame should be constructible."""
        frame = SemanticFrame(
            frame_type=SemanticFrameType.STATE,
            predicate="جالس",
            participants=(("experiencer", "زَيْد"),),
        )
        assert frame.frame_type == SemanticFrameType.STATE

    def test_frame_is_frozen(self) -> None:
        """SemanticFrame should be immutable."""
        frame = SemanticFrame(
            frame_type=SemanticFrameType.ACTION,
            predicate="كتب",
            participants=(),
        )
        try:
            frame.predicate = "قرأ"  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestConceptRelation:
    """Tests for SemanticConceptRelation dataclass."""

    def test_create_hypernym(self) -> None:
        """HYPERNYM relation should be constructible."""
        rel = SemanticConceptRelation(
            source_id="C001",
            target_id="C002",
            relation_type=SemanticRelationType.HYPERNYM,
            confidence=0.9,
        )
        assert rel.relation_type == SemanticRelationType.HYPERNYM
        assert rel.confidence == 0.9

    def test_create_synonym(self) -> None:
        """SYNONYM relation should be constructible."""
        rel = SemanticConceptRelation(
            source_id="C003",
            target_id="C004",
            relation_type=SemanticRelationType.SYNONYM,
            confidence=0.85,
        )
        assert rel.relation_type == SemanticRelationType.SYNONYM

    def test_confidence_in_range(self) -> None:
        """Confidence should be in [0, 1]."""
        rel = SemanticConceptRelation("C1", "C2", SemanticRelationType.CAUSAL, 0.75)
        assert 0 <= rel.confidence <= 1


class TestDenotationMap:
    """Tests for DenotationMap dataclass."""

    def test_create_denotation_map(self) -> None:
        """DenotationMap should be constructible."""
        dmap = DenotationMap(
            signifier="كتاب",
            denotations=(("book", 0.9), ("writing", 0.7)),
            primary_meaning="book",
        )
        assert dmap.signifier == "كتاب"
        assert dmap.primary_meaning == "book"
        assert len(dmap.denotations) == 2


class TestSemanticFrameTypeEnum:
    """Tests for SemanticFrameType enum."""

    def test_all_frame_types_exist(self) -> None:
        """All expected frame types should exist."""
        expected = ["ACTION", "STATE", "TRANSFER", "COGNITION",
                    "EVALUATION", "EXISTENCE"]
        for name in expected:
            assert hasattr(SemanticFrameType, name)


class TestConceptRelationTypeEnum:
    """Tests for SemanticRelationType enum."""

    def test_all_relation_types_exist(self) -> None:
        """All expected relation types should exist."""
        expected = ["HYPERNYM", "HYPONYM", "MERONYM", "HOLONYM",
                    "SYNONYM", "ANTONYM", "CAUSAL", "TEMPORAL"]
        for name in expected:
            assert hasattr(SemanticRelationType, name)
