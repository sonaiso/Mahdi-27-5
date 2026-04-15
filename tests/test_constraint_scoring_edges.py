"""Tests for build_constraint_edges — constraint edge construction.

Covers:
- Role ↔ case compatibility constraints (فاعل → رفع, مفعول → نصب, etc.)
- Declension constraints (مبني words cannot have رفع/نصب/جر)
- Edge cases: empty input, missing payload keys, unknown roles
"""

from __future__ import annotations

from arabic_engine.constraints.propagation import get_constraint_edges
from arabic_engine.constraints.scoring import _ROLE_CASE_COMPAT, build_constraint_edges
from arabic_engine.core.enums import (
    ActivationStage,
    ConstraintStrength,
)
from arabic_engine.core.types import HypothesisNode


def _make(
    node_id: str,
    stage: ActivationStage = ActivationStage.MORPHOLOGY,
    source_refs: tuple[str, ...] = (),
    payload: tuple[tuple[str, object], ...] = (),
    confidence: float = 0.8,
) -> HypothesisNode:
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="test",
        stage=stage,
        source_refs=source_refs,
        payload=payload,
        confidence=confidence,
    )


# ═══════════════════════════════════════════════════════════════════════
# build_constraint_edges — Role ↔ Case compatibility
# ═══════════════════════════════════════════════════════════════════════


class TestRoleCaseCompatibility:
    """Role ↔ case compatibility constraints."""

    def test_compatible_role_case_no_edge(self):
        """فاعل + رفع is compatible — no constraint edge emitted."""
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 0

    def test_incompatible_role_case_emits_edge(self):
        """فاعل + نصب is incompatible — STRONG constraint edge emitted."""
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 1
        assert edges[0].relation == "role_case_incompatible"
        assert edges[0].strength == ConstraintStrength.STRONG

    def test_mafool_nasb_compatible(self):
        """مفعول + نصب is compatible — no edge."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "مفعول"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 0

    def test_mafool_raf3_incompatible(self):
        """مفعول + رفع is incompatible."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "مفعول"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 1
        assert edges[0].relation == "role_case_incompatible"

    def test_mudaf_ilayhi_jar_compatible(self):
        """مضاف_إليه + جر is compatible."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "مضاف_إليه"), ("case_state", "جر")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 0

    def test_mudaf_ilayhi_nasb_incompatible(self):
        """مضاف_إليه + نصب is incompatible."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "مضاف_إليه"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 1

    def test_hal_nasb_compatible(self):
        """حال + نصب is compatible."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "حال"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 0

    def test_munada_accepts_multiple_cases(self):
        """منادى accepts بناء, نصب, and مبني."""
        for case_val in ("بناء", "نصب", "مبني"):
            role_h = _make("R1", stage=ActivationStage.ROLE)
            case_h = _make(
                "K1",
                stage=ActivationStage.CASE,
                source_refs=("R1",),
                payload=(("role", "منادى"), ("case_state", case_val)),
            )
            edges = build_constraint_edges([role_h, case_h])
            assert len(edges) == 0, f"منادى + {case_val} should be compatible"

    def test_munada_jar_incompatible(self):
        """منادى + جر is incompatible."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "منادى"), ("case_state", "جر")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 1

    def test_unknown_role_no_edge(self):
        """Role not in _ROLE_CASE_COMPAT should not generate an edge."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "unknown_role"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 0

    def test_missing_role_no_edge(self):
        """Case hypothesis with no role payload should not crash."""
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("case_state", "رفع"),),
        )
        edges = build_constraint_edges([case_h])
        assert isinstance(edges, list)

    def test_missing_case_state_no_edge(self):
        """Case hypothesis with no case_state payload should not crash."""
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"),),
        )
        edges = build_constraint_edges([case_h])
        # role = "فاعل", case_state defaults to "" which is not in {"رفع"}
        # but source_ref R1 is not in by_id since there's no hypothesis with id R1
        # so no edge
        assert isinstance(edges, list)

    def test_all_known_roles_covered(self):
        """Every role in _ROLE_CASE_COMPAT has at least one valid case."""
        for role, valid_cases in _ROLE_CASE_COMPAT.items():
            assert len(valid_cases) > 0, f"Role {role} has empty valid cases"

    def test_edge_ids_unique(self):
        """Multiple edges should have unique IDs."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h1 = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        case_h2 = _make(
            "K2",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "مفعول"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([role_h, case_h1, case_h2])
        ids = [e.edge_id for e in edges]
        assert len(ids) == len(set(ids)), "Edge IDs must be unique"

    def test_edge_references_correct_nodes(self):
        """Edge source_ref and target_ref should point to correct nodes."""
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([role_h, case_h])
        assert len(edges) == 1
        assert edges[0].source_ref == "R1"
        assert edges[0].target_ref == "K1"


# ═══════════════════════════════════════════════════════════════════════
# build_constraint_edges — Declension constraints
# ═══════════════════════════════════════════════════════════════════════


class TestDeclensionConstraints:
    """مبني/معرب declension constraints."""

    def test_mabni_word_with_raf3_emits_edge(self):
        """مبني word + رفع case is incompatible — MODERATE constraint edge."""
        concept_h = _make("C1", stage=ActivationStage.CONCEPT)
        axis_h = _make(
            "A1",
            stage=ActivationStage.AXIS,
            source_refs=("C1",),
            payload=(("axis_name", "مبني/معرب"), ("axis_value", "مبني")),
        )
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "unknown_role"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([concept_h, axis_h, role_h, case_h])
        decl_edges = [e for e in edges if e.relation == "declension_case_incompatible"]
        assert len(decl_edges) == 1
        assert decl_edges[0].strength == ConstraintStrength.MODERATE

    def test_mabni_word_with_nasb_emits_edge(self):
        """مبني word + نصب case is incompatible."""
        concept_h = _make("C1", stage=ActivationStage.CONCEPT)
        axis_h = _make(
            "A1",
            stage=ActivationStage.AXIS,
            source_refs=("C1",),
            payload=(("axis_name", "مبني/معرب"), ("axis_value", "مبني")),
        )
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "unknown_role"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([concept_h, axis_h, role_h, case_h])
        decl_edges = [e for e in edges if e.relation == "declension_case_incompatible"]
        assert len(decl_edges) == 1

    def test_mabni_word_with_jar_emits_edge(self):
        """مبني word + جر case is incompatible."""
        concept_h = _make("C1", stage=ActivationStage.CONCEPT)
        axis_h = _make(
            "A1",
            stage=ActivationStage.AXIS,
            source_refs=("C1",),
            payload=(("axis_name", "مبني/معرب"), ("axis_value", "مبني")),
        )
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "unknown_role"), ("case_state", "جر")),
        )
        edges = build_constraint_edges([concept_h, axis_h, role_h, case_h])
        decl_edges = [e for e in edges if e.relation == "declension_case_incompatible"]
        assert len(decl_edges) == 1

    def test_mabni_word_with_mabni_case_no_edge(self):
        """مبني word + مبني case is compatible — no declension edge."""
        concept_h = _make("C1", stage=ActivationStage.CONCEPT)
        axis_h = _make(
            "A1",
            stage=ActivationStage.AXIS,
            source_refs=("C1",),
            payload=(("axis_name", "مبني/معرب"), ("axis_value", "مبني")),
        )
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "حرف_جر"), ("case_state", "مبني")),
        )
        edges = build_constraint_edges([concept_h, axis_h, role_h, case_h])
        decl_edges = [e for e in edges if e.relation == "declension_case_incompatible"]
        assert len(decl_edges) == 0

    def test_murab_word_with_raf3_no_edge(self):
        """معرب word + رفع — no declension edge."""
        concept_h = _make("C1", stage=ActivationStage.CONCEPT)
        axis_h = _make(
            "A1",
            stage=ActivationStage.AXIS,
            source_refs=("C1",),
            payload=(("axis_name", "مبني/معرب"), ("axis_value", "معرب")),
        )
        role_h = _make("R1", stage=ActivationStage.ROLE, source_refs=("C1",))
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([concept_h, axis_h, role_h, case_h])
        decl_edges = [e for e in edges if e.relation == "declension_case_incompatible"]
        assert len(decl_edges) == 0


# ═══════════════════════════════════════════════════════════════════════
# build_constraint_edges — Edge cases
# ═══════════════════════════════════════════════════════════════════════


class TestBuildConstraintEdgesEdgeCases:
    """Edge cases for build_constraint_edges."""

    def test_empty_hypotheses(self):
        """Empty input should return empty list."""
        edges = build_constraint_edges([])
        assert edges == []

    def test_no_case_hypotheses(self):
        """Input with no CASE-stage hypotheses produces no edges."""
        h1 = _make("H1", stage=ActivationStage.MORPHOLOGY)
        h2 = _make("H2", stage=ActivationStage.CONCEPT)
        edges = build_constraint_edges([h1, h2])
        assert edges == []

    def test_case_without_source_ref_in_index(self):
        """Case hypothesis referencing non-existent source should not crash."""
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("NONEXISTENT",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        edges = build_constraint_edges([case_h])
        # The edge would only be emitted if source_ref is in by_id
        assert isinstance(edges, list)

    def test_multiple_case_hypotheses(self):
        """Multiple case hypotheses produce independent edges."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h1 = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        case_h2 = _make(
            "K2",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "مفعول"), ("case_state", "رفع")),
        )
        edges = build_constraint_edges([role_h, case_h1, case_h2])
        assert len(edges) == 2


# ═══════════════════════════════════════════════════════════════════════
# get_constraint_edges — convenience wrapper
# ═══════════════════════════════════════════════════════════════════════


class TestGetConstraintEdges:
    """Tests for propagation.get_constraint_edges convenience function."""

    def test_returns_same_as_build(self):
        """get_constraint_edges is a thin wrapper around build_constraint_edges."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "نصب")),
        )
        hyps = [role_h, case_h]
        direct = build_constraint_edges(hyps)
        via_wrapper = get_constraint_edges(hyps)
        assert len(direct) == len(via_wrapper)
        for d, w in zip(direct, via_wrapper):
            assert d.edge_id == w.edge_id
            assert d.relation == w.relation

    def test_empty_input(self):
        """Empty input returns empty list."""
        assert get_constraint_edges([]) == []

    def test_no_violations_returns_empty(self):
        """Compatible hypotheses produce no constraint edges."""
        role_h = _make("R1", stage=ActivationStage.ROLE)
        case_h = _make(
            "K1",
            stage=ActivationStage.CASE,
            source_refs=("R1",),
            payload=(("role", "فاعل"), ("case_state", "رفع")),
        )
        assert get_constraint_edges([role_h, case_h]) == []
