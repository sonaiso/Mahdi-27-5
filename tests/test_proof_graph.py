"""Tests for AxiomRecord, TheoremRecord, ProofDependencyGraph.

Week 1 acceptance criteria — the test passes iff:

    1. Every axiom can be looked up by ID
    2. Every theorem's dependencies are resolvable
    3. ``is_acyclic()`` returns True for the seed graph
    4. ``proof_coverage()`` returns a correct initial value
    5. No dangling dependencies exist in the seed graph
    6. Cyclical graphs are correctly detected
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import OntologicalLayer, ProofStatus
from arabic_engine.core.types import (
    AxiomRecord,
    ProofDependencyGraph,
    TheoremRecord,
)

# ═══════════════════════════════════════════════════════════════════════
# Seed data — 6 axioms + 12 theorems
# ═══════════════════════════════════════════════════════════════════════

SEED_AXIOMS: tuple[AxiomRecord, ...] = (
    AxiomRecord(
        axiom_id="AX_001",
        name="وجود الموضع الصفري القابل للامتلاء",
        formal_statement="∃z (ZeroSlot(z) ∧ Fillable(z))",
        natural_language=(
            "There exists at least one structural zero-slot that is "
            "fillable — not absolute nothingness."
        ),
        layer=OntologicalLayer.CELL,
        dependencies=(),
        implemented_by=("ZeroSlotRecord",),
        status=ProofStatus.ASSUMED,
    ),
    AxiomRecord(
        axiom_id="AX_002",
        name="ضرورة الإشغال الموجب الأول",
        formal_statement="∀z (ZeroSlot(z) ∧ Fillable(z) → ∃x Occupies(x,z))",
        natural_language=(
            "Every fillable zero-slot must admit a first positive "
            "occupancy."
        ),
        layer=OntologicalLayer.CELL,
        dependencies=("AX_001",),
        implemented_by=("ZeroSlotRecord", "occupy_zero_slot"),
        status=ProofStatus.ASSUMED,
    ),
    AxiomRecord(
        axiom_id="AX_003",
        name="الحد الأدنى للتمييز = 3",
        formal_statement=(
            "CompleteDistinction(x,y) → ∃t ≠ x,y; "
            "MinCompleteDistinction = 3"
        ),
        natural_language=(
            "Complete distinction requires at least three elements; "
            "a pair alone yields incomplete judgment."
        ),
        layer=OntologicalLayer.CELL,
        dependencies=(),
        implemented_by=("TriadicBlockRecord", "TriadRecord", "compose"),
        status=ProofStatus.ASSUMED,
    ),
    AxiomRecord(
        axiom_id="AX_004",
        name="عدم تكافؤ الطبقات المتتالية",
        formal_statement="L_n ≢ L_{n+1}; Complete(x ∈ L_n) → RequiresHigherContext(x)",
        natural_language=(
            "No two consecutive ontological layers are equivalent; "
            "completion at layer n requires promotion to n+1."
        ),
        layer=OntologicalLayer.TRANSITION,
        dependencies=(),
        implemented_by=("LayerPromotionRule", "promote"),
        status=ProofStatus.ASSUMED,
    ),
    AxiomRecord(
        axiom_id="AX_005",
        name="الموضع يسبق القيمة",
        formal_statement="Slot ≺ Value",
        natural_language=(
            "The structural position must exist before any value can "
            "occupy it."
        ),
        layer=OntologicalLayer.CELL,
        dependencies=("AX_001",),
        implemented_by=("StructuralSlot",),
        status=ProofStatus.ASSUMED,
    ),
    AxiomRecord(
        axiom_id="AX_006",
        name="القيد شرط تحقق لا جزء من الماهية",
        formal_statement="Core(x) = (Slot, Value); Cond(x) = Ω_x",
        natural_language=(
            "The constraint is an external guard on realisation, not "
            "an intrinsic part of the element's essence."
        ),
        layer=OntologicalLayer.CELL,
        dependencies=("AX_001", "AX_005"),
        implemented_by=("EssenceConditionPair", "validate"),
        status=ProofStatus.ASSUMED,
    ),
)

SEED_THEOREMS: tuple[TheoremRecord, ...] = (
    TheoremRecord(
        theorem_id="TH_001",
        name="الصفر البنيوي ≠ العدم المطلق",
        formal_statement="ZeroSlot ≠ ∅",
        natural_language="The structural zero-slot is not absolute nothingness.",
        axiom_dependencies=("AX_001",),
        proof_sketch="By A1, ZeroSlot is fillable; ∅ is not fillable ⇒ ZeroSlot ≠ ∅.",
        status=ProofStatus.PROVEN,
        test_reference="test_axiom_types.py::TestZeroSlotRecord",
    ),
    TheoremRecord(
        theorem_id="TH_002",
        name="الواحد التأسيسي = أول إشغال موجب",
        formal_statement="OneBase = FirstPositiveOccupancy(ZeroSlot)",
        natural_language=(
            "The foundational unit-one is the first positive "
            "occupancy of a zero-slot."
        ),
        axiom_dependencies=("AX_001", "AX_002"),
        proof_sketch=(
            "By A1+A2, fillable slots must be occupied; "
            "the first occupancy is the unit-one."
        ),
        status=ProofStatus.PROVEN,
        test_reference="test_axiom_types.py::TestZeroSlotRecord",
    ),
    TheoremRecord(
        theorem_id="TH_003",
        name="الزوج وحده لا يكفي للحكم الرتبي",
        formal_statement="PairOnly(x,y) → IncompleteRankJudgment",
        natural_language="A binary pair alone cannot produce a complete rank judgment.",
        axiom_dependencies=("AX_003",),
        proof_sketch="By A3, complete distinction requires 3; a pair has only 2.",
        status=ProofStatus.PROVEN,
        test_reference="test_axiom_types.py::TestTriadicBlockRecord",
    ),
    TheoremRecord(
        theorem_id="TH_004",
        name="الحرف يحتاج سياقًا أعلى",
        formal_statement="Letter → Requires(SyllabicOrHigherContext)",
        natural_language=(
            "A letter (cell-level element) requires promotion "
            "to at least the syllable layer."
        ),
        axiom_dependencies=("AX_004",),
        proof_sketch="By A4, completion at CELL requires TRANSITION or higher context.",
        status=ProofStatus.PROVEN,
        test_reference="test_axiom_types.py::TestLayerPromotionRule",
    ),
    TheoremRecord(
        theorem_id="TH_005",
        name="السكون ≠ الصفر البنيوي",
        formal_statement="Sukun ≠ ZeroStruct; Sukun = 0_V",
        natural_language="Sukun is a vocalic zero, not the structural zero-slot.",
        axiom_dependencies=("AX_001", "AX_005"),
        proof_sketch=(
            "Structural zero is a position; sukun is a modifier "
            "value ⇒ different ontological modes."
        ),
        status=ProofStatus.PROVEN,
        test_reference="test_calculus_v1.py::TestVocalicZero",
    ),
    TheoremRecord(
        theorem_id="TH_006",
        name="كل وصف + مجموعة قواعد → حكم",
        formal_statement="Description(x) + RuleSet → Decision(x)",
        natural_language="Any description combined with a rule set yields a decision (Law 2).",
        axiom_dependencies=(),
        proof_sketch=(
            "By construction: apply_decision_rule maps every "
            "key through its rule function."
        ),
        status=ProofStatus.PROVEN,
        test_reference="test_calculus_v1.py::TestLaw2",
    ),
    TheoremRecord(
        theorem_id="TH_007",
        name="الحدّية والسعة تصنّفان كل عنصر",
        formal_statement="∀x: (L(x), C(x)) → RankType(x) ∈ {LIMITAL, CAPACITIVE, TRANSITIONAL}",
        natural_language=(
            "Every element with limit and capacity scores "
            "receives a rank classification (Law 3)."
        ),
        axiom_dependencies=(),
        proof_sketch="classify_rank covers all cases: L≫C, C≫L, |L-C|≤θ ⇒ exhaustive.",
        status=ProofStatus.PROVEN,
        test_reference="test_calculus_v1.py::TestLaw3",
    ),
    TheoremRecord(
        theorem_id="TH_008",
        name="انعدام القيد → انعدام التفسير",
        formal_statement="Ω(x) = 0 → NoInterpretation(x)",
        natural_language="An element with zero constraint weight cannot be interpreted (Law 4).",
        axiom_dependencies=("AX_006",),
        proof_sketch=(
            "By A6 + Law 4: if Ω=0, the constraint guard "
            "blocks realisation ⇒ no interpretation."
        ),
        status=ProofStatus.PROVEN,
        test_reference="test_calculus_v1.py::TestLaw4",
    ),
    TheoremRecord(
        theorem_id="TH_009",
        name="الاكتمال المحلي → ضرورة الترقية",
        formal_statement="Complete_n(x) → Requires(Level_{n+1})",
        natural_language="Local completion at layer n forces promotion to layer n+1 (Law 5).",
        axiom_dependencies=("AX_004",),
        proof_sketch="By A4, consecutive layers are non-equivalent; completion cannot stay.",
        status=ProofStatus.PROVEN,
        test_reference="test_calculus_v1.py::TestLaw5",
    ),
    TheoremRecord(
        theorem_id="TH_010",
        name="الانتقال يحافظ على الجذر",
        formal_statement="T_r(E) preserves root identity",
        natural_language="Cell transitions never destroy the root identity of the element.",
        axiom_dependencies=(),
        proof_sketch=(
            "Transition cost function penalises root loss "
            "⇒ optimal transition preserves root."
        ),
        status=ProofStatus.ASSUMED,
        test_reference="test_transition.py::TestApplyBestTransition",
    ),
    TheoremRecord(
        theorem_id="TH_011",
        name="التطبيع + الترميز = دالة إجمالية",
        formal_statement="normalize ∘ tokenize ∘ ... ∘ evaluate is total",
        natural_language="The full pipeline composition is a total function on valid Arabic input.",
        axiom_dependencies=(),
        proof_sketch="Each layer is a total function on its input type ⇒ composition is total.",
        status=ProofStatus.PROVEN,
        test_reference="test_pipeline.py::TestPipeline",
    ),
    TheoremRecord(
        theorem_id="TH_012",
        name="الثلاثية الدنيا = (موضع، قيمة، قيد)",
        formal_statement="MinArabicStructure = (Slot, Value, Constraint)",
        natural_language=(
            "The minimum Arabic structural unit is a triple "
            "of slot, value, and constraint."
        ),
        axiom_dependencies=("AX_003", "AX_005", "AX_006"),
        proof_sketch=(
            "By A3 (min distinction = 3), A5 (slot precedes value), "
            "A6 (constraint is external) ⇒ triple is minimal and complete."
        ),
        status=ProofStatus.PROVEN,
        test_reference="test_calculus_v1.py::TestTriadRecord",
    ),
)


def _build_seed_graph() -> ProofDependencyGraph:
    return ProofDependencyGraph(axioms=SEED_AXIOMS, theorems=SEED_THEOREMS)


# ═══════════════════════════════════════════════════════════════════════
# Tests — AxiomRecord
# ═══════════════════════════════════════════════════════════════════════


class TestAxiomRecord:
    """Tests for the AxiomRecord frozen dataclass."""

    def test_construction(self) -> None:
        ax = SEED_AXIOMS[0]
        assert ax.axiom_id == "AX_001"
        assert ax.name == "وجود الموضع الصفري القابل للامتلاء"
        assert ax.layer is OntologicalLayer.CELL

    def test_frozen(self) -> None:
        ax = SEED_AXIOMS[0]
        with pytest.raises(AttributeError):
            ax.axiom_id = "AX_999"  # type: ignore[misc]

    def test_status_is_assumed(self) -> None:
        for ax in SEED_AXIOMS:
            assert ax.status is ProofStatus.ASSUMED

    def test_all_have_formal_statement(self) -> None:
        for ax in SEED_AXIOMS:
            assert ax.formal_statement, f"{ax.axiom_id} missing formal statement"

    def test_all_have_natural_language(self) -> None:
        for ax in SEED_AXIOMS:
            assert ax.natural_language, f"{ax.axiom_id} missing natural language"

    def test_implemented_by_is_tuple(self) -> None:
        for ax in SEED_AXIOMS:
            assert isinstance(ax.implemented_by, tuple)

    def test_dependencies_are_valid_ids(self) -> None:
        """Every axiom dependency must reference another seed axiom."""
        ids = {ax.axiom_id for ax in SEED_AXIOMS}
        for ax in SEED_AXIOMS:
            for dep in ax.dependencies:
                assert dep in ids, (
                    f"{ax.axiom_id} depends on unknown axiom {dep}"
                )

    def test_six_axioms(self) -> None:
        assert len(SEED_AXIOMS) == 6

    def test_unique_ids(self) -> None:
        ids = [ax.axiom_id for ax in SEED_AXIOMS]
        assert len(ids) == len(set(ids))


# ═══════════════════════════════════════════════════════════════════════
# Tests — TheoremRecord
# ═══════════════════════════════════════════════════════════════════════


class TestTheoremRecord:
    """Tests for the TheoremRecord frozen dataclass."""

    def test_construction(self) -> None:
        th = SEED_THEOREMS[0]
        assert th.theorem_id == "TH_001"
        assert th.name == "الصفر البنيوي ≠ العدم المطلق"

    def test_frozen(self) -> None:
        th = SEED_THEOREMS[0]
        with pytest.raises(AttributeError):
            th.theorem_id = "TH_999"  # type: ignore[misc]

    def test_twelve_theorems(self) -> None:
        assert len(SEED_THEOREMS) == 12

    def test_unique_ids(self) -> None:
        ids = [th.theorem_id for th in SEED_THEOREMS]
        assert len(ids) == len(set(ids))

    def test_all_dependencies_property(self) -> None:
        th12 = SEED_THEOREMS[11]  # TH_012
        assert "AX_003" in th12.all_dependencies
        assert "AX_005" in th12.all_dependencies
        assert "AX_006" in th12.all_dependencies

    def test_is_proven_true_for_proven(self) -> None:
        th1 = SEED_THEOREMS[0]  # TH_001 — PROVEN
        assert th1.is_proven is True

    def test_is_proven_false_for_assumed(self) -> None:
        th10 = SEED_THEOREMS[9]  # TH_010 — ASSUMED
        assert th10.is_proven is False

    def test_all_have_proof_sketch(self) -> None:
        for th in SEED_THEOREMS:
            assert th.proof_sketch, f"{th.theorem_id} missing proof sketch"

    def test_axiom_dependencies_are_valid(self) -> None:
        """Every axiom dependency must reference a seed axiom."""
        ax_ids = {ax.axiom_id for ax in SEED_AXIOMS}
        for th in SEED_THEOREMS:
            for dep in th.axiom_dependencies:
                assert dep in ax_ids, (
                    f"{th.theorem_id} depends on unknown axiom {dep}"
                )


# ═══════════════════════════════════════════════════════════════════════
# Tests — ProofDependencyGraph
# ═══════════════════════════════════════════════════════════════════════


class TestProofDependencyGraph:
    """Tests for the proof-dependency DAG."""

    def test_construction(self) -> None:
        g = _build_seed_graph()
        assert len(g.axioms) == 6
        assert len(g.theorems) == 12

    def test_frozen(self) -> None:
        g = _build_seed_graph()
        with pytest.raises(AttributeError):
            g.axioms = ()  # type: ignore[misc]

    # ── Lookup ─────────────────────────────────────────────────────

    def test_get_axiom_found(self) -> None:
        g = _build_seed_graph()
        ax = g.get_axiom("AX_001")
        assert ax is not None
        assert ax.axiom_id == "AX_001"

    def test_get_axiom_not_found(self) -> None:
        g = _build_seed_graph()
        assert g.get_axiom("AX_999") is None

    def test_get_theorem_found(self) -> None:
        g = _build_seed_graph()
        th = g.get_theorem("TH_001")
        assert th is not None
        assert th.theorem_id == "TH_001"

    def test_get_theorem_not_found(self) -> None:
        g = _build_seed_graph()
        assert g.get_theorem("TH_999") is None

    # ── Dependency queries ─────────────────────────────────────────

    def test_dependencies_of(self) -> None:
        g = _build_seed_graph()
        deps = g.dependencies_of("TH_002")
        assert "AX_001" in deps
        assert "AX_002" in deps

    def test_dependencies_of_unknown(self) -> None:
        g = _build_seed_graph()
        assert g.dependencies_of("TH_999") == ()

    def test_dependents_of_ax001(self) -> None:
        g = _build_seed_graph()
        dependents = g.dependents_of("AX_001")
        assert "TH_001" in dependents
        assert "TH_002" in dependents
        assert "TH_005" in dependents

    def test_dependents_of_ax003(self) -> None:
        g = _build_seed_graph()
        dependents = g.dependents_of("AX_003")
        assert "TH_003" in dependents
        assert "TH_012" in dependents

    # ── Structural validation ──────────────────────────────────────

    def test_no_dangling_dependencies(self) -> None:
        g = _build_seed_graph()
        assert g.dangling_dependencies() == ()

    def test_is_acyclic(self) -> None:
        g = _build_seed_graph()
        assert g.is_acyclic() is True

    def test_proof_coverage_initial(self) -> None:
        g = _build_seed_graph()
        cov = g.proof_coverage()
        # 11 of 12 theorems are PROVEN (TH_010 is ASSUMED)
        assert abs(cov - 11 / 12) < 1e-9

    def test_all_proven_false(self) -> None:
        g = _build_seed_graph()
        assert g.all_proven() is False  # TH_010 is ASSUMED

    def test_empty_graph_coverage(self) -> None:
        g = ProofDependencyGraph(axioms=(), theorems=())
        assert g.proof_coverage() == 0.0

    def test_empty_graph_all_proven(self) -> None:
        g = ProofDependencyGraph(axioms=(), theorems=())
        assert g.all_proven() is False

    # ── Cycle detection ────────────────────────────────────────────

    def test_detect_cycle(self) -> None:
        """A graph with theorem-to-theorem cycles must report not acyclic."""
        cyc_a = TheoremRecord(
            theorem_id="CYC_A",
            name="cycle-a",
            formal_statement="A",
            natural_language="a",
            theorem_dependencies=("CYC_B",),
        )
        cyc_b = TheoremRecord(
            theorem_id="CYC_B",
            name="cycle-b",
            formal_statement="B",
            natural_language="b",
            theorem_dependencies=("CYC_A",),
        )
        g = ProofDependencyGraph(axioms=(), theorems=(cyc_a, cyc_b))
        assert g.is_acyclic() is False

    def test_detect_self_cycle(self) -> None:
        cyc = TheoremRecord(
            theorem_id="CYC_SELF",
            name="self-cycle",
            formal_statement="A → A",
            natural_language="s",
            theorem_dependencies=("CYC_SELF",),
        )
        g = ProofDependencyGraph(axioms=(), theorems=(cyc,))
        assert g.is_acyclic() is False

    # ── Dangling dependency detection ──────────────────────────────

    def test_dangling_axiom_dep(self) -> None:
        th = TheoremRecord(
            theorem_id="TH_BAD",
            name="bad",
            formal_statement="X",
            natural_language="x",
            axiom_dependencies=("AX_GHOST",),
        )
        g = ProofDependencyGraph(axioms=(), theorems=(th,))
        assert "AX_GHOST" in g.dangling_dependencies()

    def test_dangling_theorem_dep(self) -> None:
        th = TheoremRecord(
            theorem_id="TH_BAD2",
            name="bad2",
            formal_statement="X",
            natural_language="x",
            theorem_dependencies=("TH_GHOST",),
        )
        g = ProofDependencyGraph(axioms=(), theorems=(th,))
        assert "TH_GHOST" in g.dangling_dependencies()

    # ── Every theorem links to at least one axiom or theorem ───────

    def test_every_seed_theorem_has_dependency_or_standalone(self) -> None:
        """Each seed theorem should have at least a proof_sketch
        (even if no axiom dependency, e.g. TH_006, TH_007, TH_010, TH_011)."""
        for th in SEED_THEOREMS:
            assert th.proof_sketch, (
                f"{th.theorem_id} has no proof sketch"
            )
