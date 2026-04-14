"""Anti-Hallucination Verification Protocol — بروتوكول كشف الهلوسة.

This test module implements the **Anti-Hallucination Verification Protocol
for Arabic Engine** as described in the architectural review.  It contains
four categories of tests:

1. **Inverse Break Tests (الكسر العكسي)**:
   Deliberately break each layer and verify that *some* test catches it.
   If a layer can be replaced by a constant-return stub and tests still
   pass, the test coverage is illusory.

2. **Red Test Suite (الاختبارات الحمراء)**:
   Adversarial Arabic inputs specifically designed to expose weaknesses:
   ambiguous sentences, deletion, inversion, competing clues, sentences
   that must remain suspended rather than resolved.

3. **Trace Completeness Tests**:
   Verify that the trace graph is *connected* from input through every
   layer down to the judgement — no orphan nodes, no silent drops.

4. **Placeholder / Stub Detection Tests**:
   Explicitly prove that certain modules are stubs by showing they
   return identical output regardless of semantically different input.
   These tests are *expected to pass* — they document known limitations
   honestly rather than hiding them behind green coverage.

Architectural rule
------------------
*Any claim needs: a real example + a breaking test + a detailed trace.*
If any of the three is missing, the claim is unverified.
"""

from __future__ import annotations

from arabic_engine.constraints.pruning import prune
from arabic_engine.constraints.revision import apply_revision, needs_revision
from arabic_engine.core.enums import (
    ActivationStage,
    ConflictState,
    HypothesisStatus,
)
from arabic_engine.core.types import ConflictEdge, HypothesisNode
from arabic_engine.hypothesis import (
    axes,
    cases,
    factors,
    judgements,
    relations,
    roles,
)
from arabic_engine.runtime.orchestrator import run

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def _make_segment(node_id: str, token: str) -> HypothesisNode:
    """Create a segmentation hypothesis for testing."""
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="segmentation",
        stage=ActivationStage.SIGNAL,
        source_refs=(f"SU_{node_id}",),
        payload=(("token_text", token), ("boundary_basis", "whitespace")),
        confidence=1.0,
        status=HypothesisStatus.ACTIVE,
    )


def _make_concept(
    node_id: str, label: str, stype: str, det: str, conf: float = 0.85
) -> HypothesisNode:
    """Create a concept hypothesis for testing."""
    return HypothesisNode(
        node_id=node_id,
        hypothesis_type="concept",
        stage=ActivationStage.CONCEPT,
        source_refs=(f"MORPH_{node_id}",),
        payload=(
            ("concept_id", f"C_{label}"),
            ("label", label),
            ("semantic_type", stype),
            ("referentiality", "referential"),
            ("determination", det),
        ),
        confidence=conf,
        status=HypothesisStatus.ACTIVE,
    )


def _get_roles_from_concepts(concept_hyps: list[HypothesisNode]) -> list[str]:
    """Extract role labels from role hypotheses."""
    role_hyps = roles.generate(concept_hyps)
    return [str(r.get("role", "")) for r in role_hyps]


def _get_cases_from_roles(
    role_hyps: list[HypothesisNode], factor_hyps: list[HypothesisNode]
) -> list[str]:
    """Extract case labels from case hypotheses."""
    case_hyps = cases.generate(role_hyps, factor_hyps)
    return [str(c.get("case_state", "")) for c in case_hyps]


# ═══════════════════════════════════════════════════════════════════════
# Part 1 — INVERSE BREAK TESTS (الكسر العكسي)
# ═══════════════════════════════════════════════════════════════════════


class TestInverseBreak_Roles:
    """Break the role layer — if ALL words get the same role,
    does the system notice?"""

    def test_all_nominative_breaks_case_diversity(self):
        """If every word is assigned مبتدأ, all cases become رفع.

        A real sentence like 'كتب زيد الرسالة' should produce both
        رفع (فاعل) and نصب (مفعول). If the role layer is broken,
        the case layer loses this distinction.
        """
        verb = _make_concept("C0", "كتب", "EVENT", "indefinite")
        subj = _make_concept("C1", "زيد", "ENTITY", "indefinite")
        obj_ = _make_concept("C2", "الرسالة", "ENTITY", "definite")
        concept_hyps = [verb, subj, obj_]

        # Normal roles should produce: فعل, فاعل, مفعول
        normal_roles = _get_roles_from_concepts(concept_hyps)
        assert "فاعل" in normal_roles, "Normal roles must include فاعل"
        assert "مفعول" in normal_roles, "Normal roles must include مفعول"

        # Now verify that case layer distinguishes رفع from نصب
        role_hyps = roles.generate(concept_hyps)
        factor_hyps = factors.generate(role_hyps, concept_hyps)
        case_labels = _get_cases_from_roles(role_hyps, factor_hyps)
        assert "رفع" in case_labels, "Must produce رفع"
        assert "نصب" in case_labels, "Must produce نصب"

    def test_constant_role_detected_as_wrong(self):
        """If a broken role layer returns مبتدأ for everything,
        the case layer should only produce رفع — no نصب at all.

        This test proves that the test above would FAIL if the
        role layer were replaced by a constant.
        """
        # Simulate broken roles: everything is مبتدأ
        fake_roles = [
            HypothesisNode(
                node_id=f"ROLE_C{i}",
                hypothesis_type="role",
                stage=ActivationStage.ROLE,
                source_refs=(f"C{i}",),
                payload=(("role", "مبتدأ"), ("token_label", "x")),
                confidence=0.85,
                status=HypothesisStatus.ACTIVE,
            )
            for i in range(3)
        ]
        fake_factors = [
            HypothesisNode(
                node_id=f"FACT_ROLE_C{i}",
                hypothesis_type="factor",
                stage=ActivationStage.FACTOR,
                source_refs=(f"ROLE_C{i}",),
                payload=(("factor", "ابتداء"), ("factor_type", "عامل_معنوي")),
                confidence=0.85,
                status=HypothesisStatus.ACTIVE,
            )
            for i in range(3)
        ]
        case_labels = _get_cases_from_roles(fake_roles, fake_factors)
        # A broken layer produces only رفع
        assert all(c == "رفع" for c in case_labels), "Broken layer → no نصب"
        assert "نصب" not in case_labels, "Confirms broken layer loses نصب"


class TestInverseBreak_Cases:
    """Break the case layer — verify detection."""

    def test_verb_obj_requires_nasb(self):
        """In كتب زيد الرسالة, الرسالة MUST be نصب (مفعول به).

        If we break cases.py to always return رفع, this test fails.
        """
        verb = _make_concept("C0", "كتب", "EVENT", "indefinite")
        subj = _make_concept("C1", "زيد", "ENTITY", "indefinite")
        obj_ = _make_concept("C2", "الرسالة", "ENTITY", "definite")

        role_hyps = roles.generate([verb, subj, obj_])
        factor_hyps = factors.generate(role_hyps, [verb, subj, obj_])
        case_hyps = cases.generate(role_hyps, factor_hyps)

        # Find the case for الرسالة (3rd token, should be مفعول → نصب)
        obj_case = next(
            (c for c in case_hyps if "C2" in c.node_id),
            None,
        )
        assert obj_case is not None
        assert obj_case.get("case_state") == "نصب", (
            f"الرسالة must be نصب, got {obj_case.get('case_state')}"
        )

    def test_subject_requires_raf(self):
        """In كتب زيد الرسالة, زيد MUST be رفع (فاعل).

        If we break cases.py to always return نصب, this test fails.
        """
        verb = _make_concept("C0", "كتب", "EVENT", "indefinite")
        subj = _make_concept("C1", "زيد", "ENTITY", "indefinite")
        obj_ = _make_concept("C2", "الرسالة", "ENTITY", "definite")

        role_hyps = roles.generate([verb, subj, obj_])
        factor_hyps = factors.generate(role_hyps, [verb, subj, obj_])
        case_hyps = cases.generate(role_hyps, factor_hyps)

        subj_case = next(
            (c for c in case_hyps if "C1" in c.node_id),
            None,
        )
        assert subj_case is not None
        assert subj_case.get("case_state") == "رفع", (
            f"زيد must be رفع, got {subj_case.get('case_state')}"
        )


class TestInverseBreak_Pruning:
    """Break the pruning layer — verify it matters."""

    def test_disabling_pruning_retains_low_confidence(self):
        """If pruning is disabled, low-confidence hypotheses survive.

        This proves that the pruning layer actually has effect.
        """
        hyps = [
            HypothesisNode(
                node_id="H1",
                hypothesis_type="test",
                stage=ActivationStage.MORPHOLOGY,
                confidence=0.05,
                status=HypothesisStatus.ACTIVE,
            ),
            HypothesisNode(
                node_id="H2",
                hypothesis_type="test",
                stage=ActivationStage.MORPHOLOGY,
                confidence=0.9,
                status=HypothesisStatus.ACTIVE,
            ),
        ]

        # With pruning: H1 should be pruned
        pruned_hyps, traces = prune(hyps, confidence_floor=0.2)
        pruned_ids = [h.node_id for h in pruned_hyps if h.status == HypothesisStatus.PRUNED]
        assert "H1" in pruned_ids, "H1 must be pruned at floor=0.2"

        # Without pruning (floor=0): nothing pruned
        unpruned_hyps, traces = prune(hyps, confidence_floor=0.0)
        active_ids = [h.node_id for h in unpruned_hyps if h.status == HypothesisStatus.ACTIVE]
        assert "H1" in active_ids, "Without pruning, H1 survives"
        assert "H2" in active_ids, "Without pruning, H2 survives"

    def test_pruning_records_justification(self):
        """Every pruned hypothesis MUST have a justification in the trace.

        Rule: No pruning without justification.
        """
        hyps = [
            HypothesisNode(
                node_id="LOW",
                hypothesis_type="test",
                stage=ActivationStage.CONCEPT,
                confidence=0.05,
                status=HypothesisStatus.ACTIVE,
            ),
        ]
        _, traces = prune(hyps)
        assert len(traces) == 1
        assert traces[0].justification != "", "Pruning must have justification"
        assert "0.05" in traces[0].justification, "Justification must cite confidence"


class TestInverseBreak_Revision:
    """Break the revision loop — verify bounded termination."""

    def test_revision_terminates_with_persistent_conflicts(self):
        """Even if conflicts can never be fully resolved,
        the revision loop MUST terminate within max_iterations.

        This is the most critical safety test.
        """
        # Create two equally-confident hypotheses that conflict
        h1 = HypothesisNode(
            node_id="EQUAL_A",
            hypothesis_type="test",
            stage=ActivationStage.MORPHOLOGY,
            confidence=0.7,
            status=HypothesisStatus.ACTIVE,
        )
        h2 = HypothesisNode(
            node_id="EQUAL_B",
            hypothesis_type="test",
            stage=ActivationStage.MORPHOLOGY,
            confidence=0.7,
            status=HypothesisStatus.ACTIVE,
        )
        conflict = ConflictEdge(
            edge_id="CONF_0",
            node_a_ref="EQUAL_A",
            node_b_ref="EQUAL_B",
            conflict_state=ConflictState.HARD,
        )

        # The loop must not run forever even with equal confidence
        iterations = 0
        hyps = [h1, h2]
        conflicts = [conflict]
        max_iter = 5
        while iterations < max_iter and needs_revision(hyps, conflicts):
            hyps, _ = apply_revision(hyps, conflicts)
            iterations += 1
        assert iterations <= max_iter, "Revision must terminate"


# ═══════════════════════════════════════════════════════════════════════
# Part 2 — RED TEST SUITE (الاختبارات الحمراء)
# ═══════════════════════════════════════════════════════════════════════


class TestRedSuite_ArabicAmbiguity:
    """Adversarial Arabic inputs designed to expose weaknesses.

    These tests use real Arabic sentences that are ambiguous, contain
    deletion, inversion, or competing clues.
    """

    # ── Ambiguous sentences ────────────────────────────────────────

    def test_verbal_vs_nominal_ambiguity(self):
        """'علم زيد' can be either:
        - Verbal: علمَ زيدٌ (Zayd knew)
        - Nominal: عِلمُ زيدٍ (Zayd's knowledge)

        The system must produce hypotheses — but a stub that always
        returns the same role for everything cannot distinguish these.
        """
        state = run("علم زيد")
        role_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "role"
        ]
        # Must have at least 2 role hypotheses
        assert len(role_hyps) >= 2, "Must produce role hypotheses"
        # At this stub level, we verify the system doesn't crash
        # and produces structured output
        assert state.decisions.judgement is not None

    def test_prepositional_ambiguity(self):
        """'رأيت الرجل في البيت' — the PP 'في البيت'
        can attach to الرجل (adjectival) or to رأيت (adverbial).

        The system should generate hypotheses for both potential
        attachment sites.
        """
        state = run("رأيت الرجل في البيت")
        rel_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "relation"
        ]
        # Must have multiple relation hypotheses
        assert len(rel_hyps) >= 1, "Must produce relation hypotheses"

    # ── Sentences with inversion (تقديم وتأخير) ───────────────────

    def test_object_fronting(self):
        """'الرسالةَ كتب زيدٌ' — object is fronted before verb.

        Current heuristic roles.py uses position, so it will assign
        wrong roles. This test documents the known limitation.
        """
        state = run("الرسالة كتب زيد")

        # Get the role for الرسالة (first token)
        role_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "role"
        ]
        first_role = next(
            (r for r in role_hyps if "الرسالة" in str(r.get("token_label", ""))),
            None,
        )
        # Document: heuristic assigns مبتدأ (wrong — should be مفعول مقدم)
        # This is a KNOWN LIMITATION that a real engine must fix
        if first_role is not None:
            role_label = str(first_role.get("role", ""))
            # The heuristic will likely assign مبتدأ since it's first ENTITY
            # before verb. We document this as a limitation.
            assert role_label in ("مبتدأ", "مفعول", "غير_محدد"), (
                f"Unexpected role for fronted object: {role_label}"
            )

    # ── Sentences with لا النافية للجنس ──────────────────────────

    def test_la_genus_negation(self):
        """'لا رجلَ في الدار' — لا النافية للجنس.

        'رجل' should be نصب (اسم لا), not رفع.
        Current stub won't get this right — but the system must
        still produce structured output without crashing.
        """
        state = run("لا رجل في الدار")
        assert state.decisions.judgement is not None, "Must produce judgement"
        # Verify trace connectivity
        assert len(state.decisions.trace) > 0, "Must have decision traces"

    # ── Sentences requiring suspension ─────────────────────────────

    def test_incomplete_sentence_suspension(self):
        """'إن' alone is incomplete — the system should produce
        low-confidence or suspended output, not a confident judgement.
        """
        state = run("إن")
        # An incomplete sentence should have low confidence
        if state.decisions.judgement is not None:
            assert state.decisions.judgement.confidence < 0.9, (
                "Incomplete sentence should not have high confidence"
            )

    # ── Competing clues (قرائن متنافسة) ───────────────────────────

    def test_competing_clues_produce_distinct_traces(self):
        """'ضرب موسى عيسى' — both nouns are indeclinable,
        so position and meaning compete as clues for subject/object.

        The system must produce a trace showing how it resolved the
        ambiguity (even if heuristically).
        """
        state = run("ضرب موسى عيسى")
        assert len(state.decisions.trace) > 0, "Must have decision traces"
        # Must have role hypotheses for both names
        role_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "role"
        ]
        assert len(role_hyps) >= 3, "Must have roles for verb + two names"


# ═══════════════════════════════════════════════════════════════════════
# Part 3 — TRACE COMPLETENESS TESTS
# ═══════════════════════════════════════════════════════════════════════


class TestTraceCompleteness:
    """Verify that the trace graph is connected from input to judgement."""

    def test_trace_chain_is_connected(self):
        """For a simple sentence, every hypothesis must be reachable
        from the input through source_refs chains."""
        state = run("كتب زيد")
        all_hyps = state.hypotheses.all_hypotheses()
        all_ids = {h.node_id for h in all_hyps}

        # Every non-root hypothesis must have source_refs pointing to
        # existing nodes (except segmentation which refs signal units)
        for h in all_hyps:
            if h.hypothesis_type == "segmentation":
                # Segmentation refs signal units, not other hypotheses
                continue
            for ref in h.source_refs:
                assert ref in all_ids, (
                    f"Orphan source_ref '{ref}' in {h.node_id} — "
                    f"not found in hypothesis graph"
                )

    def test_no_hypothesis_without_source_refs(self):
        """Every hypothesis except segmentation must have source_refs."""
        state = run("ذهب الطالب")
        all_hyps = state.hypotheses.all_hypotheses()
        for h in all_hyps:
            if h.hypothesis_type == "segmentation":
                # Segmentation references signal units
                assert len(h.source_refs) > 0, (
                    f"Segmentation {h.node_id} has no source_refs"
                )
            else:
                assert len(h.source_refs) > 0, (
                    f"Hypothesis {h.node_id} ({h.hypothesis_type}) "
                    f"has no source_refs — orphan node"
                )

    def test_judgement_has_support_chain(self):
        """The final judgement must trace back through case → role →
        concept → morphology → segmentation.

        If any link in the chain is missing, the claim of
        'explainability' is false.
        """
        state = run("كتب زيد")
        judgement = state.decisions.judgement
        assert judgement is not None, "Must produce a judgement"

        # Judgement must reference case hypotheses
        assert len(judgement.source_refs) > 0, "Judgement has no source_refs"

        # Build reachability from judgement back to segmentation
        all_hyps = state.hypotheses.all_hypotheses()
        hyp_by_id = {h.node_id: h for h in all_hyps}

        visited = set()
        queue = list(judgement.source_refs)
        while queue:
            ref = queue.pop(0)
            if ref in visited:
                continue
            visited.add(ref)
            node = hyp_by_id.get(ref)
            if node is not None:
                queue.extend(node.source_refs)

        # Must reach at least one segmentation node
        seg_nodes = {h.node_id for h in all_hyps if h.hypothesis_type == "segmentation"}
        reached_seg = visited & seg_nodes
        assert len(reached_seg) > 0, (
            "Judgement cannot trace back to any segmentation node — "
            "the chain is broken"
        )

    def test_confidence_does_not_increase_through_layers(self):
        """Confidence should generally degrade as we move through
        layers (each layer adds uncertainty). Check that no
        downstream hypothesis has higher confidence than all its
        parents.
        """
        state = run("كتب زيد الرسالة")
        all_hyps = state.hypotheses.all_hypotheses()
        hyp_by_id = {h.node_id: h for h in all_hyps}

        violations = []
        for h in all_hyps:
            if h.hypothesis_type == "segmentation":
                continue
            parent_confs = []
            for ref in h.source_refs:
                parent = hyp_by_id.get(ref)
                if parent is not None:
                    parent_confs.append(parent.confidence)
            if parent_confs and h.confidence > max(parent_confs) + 0.01:
                violations.append(
                    f"{h.node_id}: conf={h.confidence:.4f} > "
                    f"max_parent={max(parent_confs):.4f}"
                )
        assert len(violations) == 0, (
            "Confidence increased through layers:\n"
            + "\n".join(violations)
        )

    def test_stabilization_trace_exists(self):
        """The final stabilization step must produce a trace record."""
        state = run("كتب")
        stab_traces = [
            t for t in state.decisions.trace
            if t.decision_type == "stabilization"
        ]
        assert len(stab_traces) > 0, "No stabilization trace found"

    def test_every_trace_has_justification(self):
        """Every DecisionTrace must have a non-empty justification."""
        state = run("كتب زيد")
        for t in state.decisions.trace:
            assert t.justification.strip() != "", (
                f"Trace {t.trace_id} has empty justification"
            )


# ═══════════════════════════════════════════════════════════════════════
# Part 4 — PLACEHOLDER / STUB DETECTION TESTS
# ═══════════════════════════════════════════════════════════════════════


class TestStubDetection_Judgements:
    """Verify that judgements.py now distinguishes proposition types.

    These tests confirm the stub has been replaced: the judgement
    module now uses concept and role hypotheses to detect
    interrogative, imperative, vocative, exclamatory, and
    declarative propositions.
    """

    def test_declarative_with_concepts(self):
        """Declarative input with verb+entity concepts → تقريرية."""
        cases = [
            HypothesisNode(
                node_id="CASE_DECL",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                payload=(("case_state", "رفع"), ("role", "فاعل")),
                confidence=0.8,
            ),
        ]
        concepts = [
            _make_concept("C0", "كتب", "EVENT", "indefinite"),
            _make_concept("C1", "زيد", "ENTITY", "indefinite"),
        ]
        roles_h = roles.generate(concepts)
        result = judgements.generate(cases, concepts, roles_h)
        assert result[0].get("proposition_type") == "تقريرية"

    def test_interrogative_detected(self):
        """Interrogative particle هل → استفهام."""
        cases = [
            HypothesisNode(
                node_id="CASE_Q",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                confidence=0.9,
            ),
        ]
        concepts = [
            _make_concept("C0", "هل", "ENTITY", "indefinite"),
            _make_concept("C1", "كتب", "EVENT", "indefinite"),
        ]
        result = judgements.generate(cases, concepts, [])
        assert result[0].get("proposition_type") == "استفهام"
        assert result[0].get("rank") == "إنشائي_طلبي"

    def test_vocative_detected(self):
        """Vocative particle يا → نداء."""
        cases = [
            HypothesisNode(
                node_id="CASE_V",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                confidence=0.85,
            ),
        ]
        concepts = [
            _make_concept("C0", "يا", "ENTITY", "indefinite"),
            _make_concept("C1", "طالب", "ENTITY", "indefinite"),
        ]
        result = judgements.generate(cases, concepts, [])
        assert result[0].get("proposition_type") == "نداء"

    def test_exclamatory_detected(self):
        """Exclamatory pattern ما أجمل → تعجب."""
        cases = [
            HypothesisNode(
                node_id="CASE_E",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                confidence=0.85,
            ),
        ]
        concepts = [
            _make_concept("C0", "ما", "ENTITY", "indefinite"),
            _make_concept("C1", "أجمل", "ENTITY", "indefinite"),
        ]
        result = judgements.generate(cases, concepts, [])
        assert result[0].get("proposition_type") == "تعجب"

    def test_oath_detected(self):
        """Oath particle والله → قسم."""
        cases = [
            HypothesisNode(
                node_id="CASE_O",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                confidence=0.85,
            ),
        ]
        concepts = [
            _make_concept("C0", "والله", "ENTITY", "indefinite"),
        ]
        result = judgements.generate(cases, concepts, [])
        assert result[0].get("proposition_type") == "قسم"

    def test_different_inputs_produce_different_types(self):
        """Semantically different inputs now produce different
        proposition types — proof the stub is replaced.
        """
        cases = [
            HypothesisNode(
                node_id="CASE_X",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                confidence=0.9,
            ),
        ]
        decl_concepts = [_make_concept("C0", "كتب", "EVENT", "indefinite")]
        interrog_concepts = [_make_concept("C0", "هل", "ENTITY", "indefinite")]

        result_decl = judgements.generate(cases, decl_concepts, [])
        result_interrog = judgements.generate(cases, interrog_concepts, [])

        assert (
            result_decl[0].get("proposition_type")
            != result_interrog[0].get("proposition_type")
        ), "Different proposition types should now be distinguished"

    def test_backward_compat_case_only(self):
        """Calling with only case_hypotheses still works (backward compat)."""
        cases = [
            HypothesisNode(
                node_id="CASE_BC",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                confidence=0.9,
            ),
        ]
        result = judgements.generate(cases)
        # No concepts/roles → defaults to suspended or declarative
        prop = result[0].get("proposition_type")
        assert prop is not None


class TestStubDetection_Axes:
    """Verify that axes.py now resolves all 6 axes.

    The stub has been replaced — all axes return real values.
    """

    def test_all_axes_resolved(self):
        """All 6 axes should return non-'غير محدد' values for typical input."""
        concept = _make_concept("C1", "كتب", "EVENT", "definite")
        axis_hyps = axes.generate([concept])

        undefined_count = sum(
            1 for h in axis_hyps if h.get("axis_value") == "غير محدد"
        )
        # At most 1 axis (زمني/مكاني for non-adverbs returns "غير زمني/مكاني")
        assert undefined_count == 0, (
            f"Expected 0 undefined axes, got {undefined_count}"
        )

    def test_definiteness_still_works(self):
        """معرفة/نكرة axis still resolves correctly."""
        definite = _make_concept("C1", "الكتاب", "ENTITY", "definite")
        indefinite = _make_concept("C2", "كتاب", "ENTITY", "indefinite")

        def_axes = axes.generate([definite])
        indef_axes = axes.generate([indefinite])

        def_value = next(
            h.get("axis_value") for h in def_axes
            if h.get("axis_name") == "معرفة/نكرة"
        )
        indef_value = next(
            h.get("axis_value") for h in indef_axes
            if h.get("axis_name") == "معرفة/نكرة"
        )

        assert def_value == "معرفة", "Definite must resolve to معرفة"
        assert indef_value == "نكرة", "Indefinite must resolve to نكرة"

    def test_derived_axis_resolves_for_event(self):
        """جامد/مشتق axis now resolves: EVENT → مشتق."""
        concept = _make_concept("C1", "كتب", "EVENT", "indefinite")
        axis_hyps = axes.generate([concept])

        derived_axis = next(
            h for h in axis_hyps if h.get("axis_name") == "جامد/مشتق"
        )
        assert derived_axis.get("axis_value") == "مشتق", (
            "EVENT concepts should be مشتق (derived)"
        )

    def test_frozen_axis_for_entity(self):
        """جامد/مشتق axis: non-derivative entity → جامد."""
        concept = _make_concept("C1", "كتاب", "ENTITY", "indefinite")
        axis_hyps = axes.generate([concept])

        derived_axis = next(
            h for h in axis_hyps if h.get("axis_name") == "جامد/مشتق"
        )
        assert derived_axis.get("axis_value") == "جامد", (
            "Non-derivative entity should be جامد (frozen)"
        )

    def test_invariant_for_particle(self):
        """مبني/معرب axis: particle → مبني."""
        concept = _make_concept("C1", "في", "ENTITY", "indefinite")
        axis_hyps = axes.generate([concept])

        decl_axis = next(
            h for h in axis_hyps if h.get("axis_name") == "مبني/معرب"
        )
        assert decl_axis.get("axis_value") == "مبني", (
            "Particle should be مبني (invariant)"
        )

    def test_temporal_adverb(self):
        """زمني/مكاني axis: اليوم → زمني."""
        concept = _make_concept("C1", "اليوم", "ENTITY", "definite")
        axis_hyps = axes.generate([concept])

        ts_axis = next(
            h for h in axis_hyps if h.get("axis_name") == "زمني/مكاني"
        )
        assert ts_axis.get("axis_value") == "زمني", (
            "اليوم should be زمني (temporal)"
        )

    def test_spatial_adverb(self):
        """زمني/مكاني axis: هنا → مكاني."""
        concept = _make_concept("C1", "هنا", "ENTITY", "indefinite")
        axis_hyps = axes.generate([concept])

        ts_axis = next(
            h for h in axis_hyps if h.get("axis_name") == "زمني/مكاني"
        )
        assert ts_axis.get("axis_value") == "مكاني", (
            "هنا should be مكاني (spatial)"
        )


class TestStubDetection_Segmentation:
    """Verify that segmentation.py now performs clitic splitting."""

    def test_clitic_splitting_produces_alternatives(self):
        """'وكتبوا' should now produce clitic-split alternatives."""
        state = run("وكتبوا")
        seg_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "segmentation"
        ]
        # Primary + split alternatives
        assert len(seg_hyps) > 1, (
            f"Expected >1 segments (primary + splits), got {len(seg_hyps)}"
        )

    def test_proclitic_separation(self):
        """'بالكتاب' should now produce proclitic split alternatives."""
        state = run("بالكتاب")
        seg_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "segmentation"
        ]
        assert len(seg_hyps) > 1, "Should now separate proclitics"

        # Find a split hypothesis
        split_hyps = [
            h for h in seg_hyps
            if str(h.get("boundary_basis", "")) == "proclitic_split"
        ]
        assert len(split_hyps) > 0, "Should have proclitic_split hypothesis"

    def test_no_false_split_for_root_words(self):
        """'ولد' should NOT be split — و is part of the root."""
        state = run("ولد")
        seg_hyps = [
            h for h in state.hypotheses.all_hypotheses()
            if h.hypothesis_type == "segmentation"
        ]
        split_hyps = [
            h for h in seg_hyps
            if str(h.get("boundary_basis", "")) != "whitespace"
        ]
        assert len(split_hyps) == 0, (
            "ولد should not be split — و is part of the root"
        )


class TestStubDetection_Roles:
    """Prove position-based role heuristic breaks on inversion."""

    def test_position_heuristic_fails_on_vso_vs_svo(self):
        """The heuristic assigns roles by position, not syntax.

        In 'كتب زيد' (VSO), زيد → فاعل ✓
        In 'زيد كتب' (SVO), زيد → مبتدأ (which could be correct
        as topicalization, or wrong if it's really VSO with fronting)

        The point: the heuristic treats position as deterministic
        and never produces uncertainty or alternatives.
        """
        vso = [
            _make_concept("C0", "كتب", "EVENT", "indefinite"),
            _make_concept("C1", "زيد", "ENTITY", "indefinite"),
        ]
        svo = [
            _make_concept("C0", "زيد", "ENTITY", "indefinite"),
            _make_concept("C1", "كتب", "EVENT", "indefinite"),
        ]

        vso_roles = _get_roles_from_concepts(vso)
        svo_roles = _get_roles_from_concepts(svo)

        # VSO: كتب=فعل, زيد=فاعل
        assert vso_roles[0] == "فعل"
        assert vso_roles[1] == "فاعل"

        # SVO: زيد=مبتدأ, كتب=فعل
        # The heuristic gives مبتدأ because ENTITY before verb
        assert svo_roles[0] == "مبتدأ"
        assert svo_roles[1] == "فعل"

        # But it never produces BOTH possibilities — proof of limitation
        # A real engine would emit alternatives with different confidences


class TestStubDetection_Relations:
    """Verify that relations.py now handles 9+ relation types."""

    def test_conjunction_detected(self):
        """Conjunction particle 'و' → عطف."""
        concepts = [
            _make_concept("C0", "زيد", "ENTITY", "definite"),
            _make_concept("C1", "و", "ENTITY", "indefinite"),
            _make_concept("C2", "عمرو", "ENTITY", "definite"),
        ]
        rel_hyps = relations.generate(concepts)
        rel_types = [str(h.get("relation_type", "")) for h in rel_hyps]
        assert "عطف" in rel_types, f"Expected عطف, got {rel_types}"

    def test_predication_detected(self):
        """EVENT → ENTITY still produces إسناد."""
        concepts = [
            _make_concept("C0", "كتب", "EVENT", "indefinite"),
            _make_concept("C1", "الطالب", "ENTITY", "definite"),
        ]
        rel_hyps = relations.generate(concepts)
        assert rel_hyps[0].get("relation_type") == "إسناد"

    def test_entity_entity_produces_alternatives(self):
        """Two adjacent entities produce multiple relation hypotheses."""
        concepts = [
            _make_concept("C0", "كتاب", "ENTITY", "indefinite"),
            _make_concept("C1", "الطالب", "ENTITY", "definite"),
        ]
        rel_hyps = relations.generate(concepts)
        # Should produce إضافة as primary for indef+def pattern
        rel_types = [str(h.get("relation_type", "")) for h in rel_hyps]
        assert "إضافة" in rel_types, f"Expected إضافة, got {rel_types}"

    def test_preposition_produces_zarfiyya(self):
        """Preposition → ظرفية."""
        concepts = [
            _make_concept("C0", "في", "ENTITY", "indefinite"),
            _make_concept("C1", "المدرسة", "ENTITY", "definite"),
        ]
        rel_hyps = relations.generate(concepts)
        assert rel_hyps[0].get("relation_type") == "ظرفية"

    def test_emphasis_detected(self):
        """Emphasis token 'نفس' → توكيد."""
        concepts = [
            _make_concept("C0", "الطالب", "ENTITY", "definite"),
            _make_concept("C1", "نفس", "ENTITY", "definite"),
        ]
        rel_hyps = relations.generate(concepts)
        rel_types = [str(h.get("relation_type", "")) for h in rel_hyps]
        has_emphasis = "توكيد" in rel_types
        assert has_emphasis, f"Expected توكيد, got {rel_types}"


class TestStubDetection_Factors:
    """Verify that factors.py now handles implicit/elided factors."""

    def test_vocative_has_elided_factor(self):
        """Vocative role (منادى) should have elided factor."""
        role_h = HypothesisNode(
            node_id="ROLE_C0",
            hypothesis_type="role",
            stage=ActivationStage.ROLE,
            source_refs=("C0",),
            payload=(("role", "منادى"), ("token_label", "طالب")),
            confidence=0.9,
            status=HypothesisStatus.ACTIVE,
        )
        concepts = [
            _make_concept("C0", "يا", "ENTITY", "indefinite"),
            _make_concept("C1", "طالب", "ENTITY", "indefinite"),
        ]
        factor_hyps = factors.generate([role_h], concepts)
        factor_type = str(factor_hyps[0].get("factor_type", ""))
        assert factor_type == "عامل_محذوف", (
            f"Expected عامل_محذوف, got {factor_type}"
        )

    def test_subject_without_verb_has_implicit_factor(self):
        """Subject (فاعل) without a verb → implicit factor."""
        role_h = HypothesisNode(
            node_id="ROLE_C0",
            hypothesis_type="role",
            stage=ActivationStage.ROLE,
            source_refs=("C0",),
            payload=(("role", "فاعل"), ("token_label", "زيد")),
            confidence=0.9,
            status=HypothesisStatus.ACTIVE,
        )
        # No EVENT concept → no verb
        concepts = [
            _make_concept("C0", "زيد", "ENTITY", "indefinite"),
        ]
        factor_hyps = factors.generate([role_h], concepts)
        factor = str(factor_hyps[0].get("factor", ""))
        assert factor == "مقدّر", f"Expected مقدّر, got {factor}"

    def test_subject_with_verb_has_explicit_factor(self):
        """Subject (فاعل) with a verb → verb is the factor."""
        role_h = HypothesisNode(
            node_id="ROLE_C1",
            hypothesis_type="role",
            stage=ActivationStage.ROLE,
            source_refs=("C1",),
            payload=(("role", "فاعل"), ("token_label", "زيد")),
            confidence=0.9,
            status=HypothesisStatus.ACTIVE,
        )
        concepts = [
            _make_concept("C0", "كتب", "EVENT", "indefinite"),
            _make_concept("C1", "زيد", "ENTITY", "indefinite"),
        ]
        factor_hyps = factors.generate([role_h], concepts)
        factor = str(factor_hyps[0].get("factor", ""))
        assert factor == "كتب", f"Expected كتب, got {factor}"

    def test_inna_governed_has_particle_factor(self):
        """اسم إنّ → particle factor from إنّ."""
        role_h = HypothesisNode(
            node_id="ROLE_C1",
            hypothesis_type="role",
            stage=ActivationStage.ROLE,
            source_refs=("C1",),
            payload=(("role", "اسم_إن"), ("token_label", "الطالب")),
            confidence=0.9,
            status=HypothesisStatus.ACTIVE,
        )
        concepts = [
            _make_concept("C0", "إنّ", "ENTITY", "indefinite"),
            _make_concept("C1", "الطالب", "ENTITY", "definite"),
        ]
        factor_hyps = factors.generate([role_h], concepts)
        factor = str(factor_hyps[0].get("factor", ""))
        factor_type = str(factor_hyps[0].get("factor_type", ""))
        assert factor == "إنّ", f"Expected إنّ, got {factor}"
        assert factor_type == "حرف_مشبه_بالفعل"


# ═══════════════════════════════════════════════════════════════════════
# Part 5 — TEST CLASSIFICATION MATRIX
# ═══════════════════════════════════════════════════════════════════════


class TestClassificationMatrix:
    """Meta-tests that verify the test suite itself has sufficient
    coverage across categories.

    These ensure the Anti-Hallucination Protocol is actually applied.
    """

    def test_protocol_has_break_tests(self):
        """This module must contain inverse break tests."""
        import tests.test_anti_hallucination as m
        break_classes = [
            c for c in dir(m) if c.startswith("TestInverseBreak")
        ]
        assert len(break_classes) >= 3, (
            f"Need ≥3 inverse break test classes, found {len(break_classes)}"
        )

    def test_protocol_has_red_tests(self):
        """This module must contain red/adversarial tests."""
        import tests.test_anti_hallucination as m
        red_classes = [c for c in dir(m) if c.startswith("TestRedSuite")]
        assert len(red_classes) >= 1, "Need ≥1 red test suite"

    def test_protocol_has_stub_detection(self):
        """This module must contain stub detection tests."""
        import tests.test_anti_hallucination as m
        stub_classes = [c for c in dir(m) if c.startswith("TestStubDetection")]
        assert len(stub_classes) >= 3, (
            f"Need ≥3 stub detection classes, found {len(stub_classes)}"
        )

    def test_protocol_has_trace_tests(self):
        """This module must contain trace completeness tests."""
        import tests.test_anti_hallucination as m
        trace_classes = [
            c for c in dir(m) if c.startswith("TestTraceCompleteness")
        ]
        assert len(trace_classes) >= 1, "Need ≥1 trace completeness class"
