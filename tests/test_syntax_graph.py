"""Tests for the Syntax Graph layer (E5).

Tests dependency relations, syntax tree types, and governance relations.
"""

from __future__ import annotations

from arabic_engine.core.enums import DependencyRelation
from arabic_engine.core.types import DependencyArc, GovernanceRelation, SyntaxTree


class TestDependencyArc:
    """Tests for DependencyArc dataclass."""

    def test_create_arc(self) -> None:
        """DependencyArc should be constructible."""
        arc = DependencyArc(
            head_index=0,
            dependent_index=1,
            relation=DependencyRelation.ISNAD,
            label="predication",
        )
        assert arc.head_index == 0
        assert arc.dependent_index == 1
        assert arc.relation == DependencyRelation.ISNAD

    def test_arc_is_frozen(self) -> None:
        """DependencyArc should be immutable (frozen)."""
        arc = DependencyArc(
            head_index=0,
            dependent_index=1,
            relation=DependencyRelation.ISNAD,
            label="test",
        )
        try:
            arc.head_index = 5  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestSyntaxTree:
    """Tests for SyntaxTree dataclass."""

    def test_create_tree(self) -> None:
        """SyntaxTree should be constructible."""
        arc = DependencyArc(0, 1, DependencyRelation.ISNAD, "pred")
        tree = SyntaxTree(
            tokens=("كَتَبَ", "زَيْدٌ"),
            arcs=(arc,),
            root_index=0,
        )
        assert len(tree.tokens) == 2
        assert len(tree.arcs) == 1
        assert tree.root_index == 0


class TestGovernanceRelation:
    """Tests for GovernanceRelation dataclass."""

    def test_create_governance(self) -> None:
        """GovernanceRelation should be constructible."""
        gov = GovernanceRelation(
            governor_index=0,
            governed_index=1,
            effect="رفع",
            governor_type="فعل",
        )
        assert gov.effect == "رفع"
        assert gov.governor_type == "فعل"


class TestDependencyRelationEnum:
    """Tests for DependencyRelation enum."""

    def test_all_relations_exist(self) -> None:
        """All expected dependency relations should exist."""
        expected = ["ISNAD", "IDAFA", "TAQYID", "SILA", "ATAF",
                    "BADAL", "TAWKID", "NIDA", "ISTITHNA", "TAMYIZ", "HAL"]
        for name in expected:
            assert hasattr(DependencyRelation, name)

    def test_isnad_is_predication(self) -> None:
        """ISNAD should represent predication."""
        assert DependencyRelation.ISNAD.name == "ISNAD"
