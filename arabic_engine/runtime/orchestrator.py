"""Constraint Orchestrator — المنسق التقييدي التدريجي.

Implements the **Total Arabic Fractal Kernel with Gradual Activation**
via the Layered Hypothesis Graph Architecture.

The orchestrator threads a :class:`~arabic_engine.core.trace.KernelRuntimeState`
through each processing stage:

.. code-block:: text

    Unicode
    → Signal Structuring  (atoms → normalize → segment)
    → Hypothesis Graph    (morph → concept → axis → relation → role → factor → case → judgement)
    → Constraint Engine   (score → prune → propagate → revise)
    → Stabilization

The revision loop is bounded by ``max_iterations`` to guarantee
termination.
"""

from __future__ import annotations

from typing import List

from arabic_engine.constraints.propagation import get_constraint_edges, propagate
from arabic_engine.constraints.pruning import prune
from arabic_engine.constraints.revision import apply_revision, needs_revision
from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.trace import (
    KernelRuntimeState,
    SignalState,
)
from arabic_engine.core.types import DecisionTrace, HypothesisNode
from arabic_engine.hypothesis import (
    axes,
    cases,
    concepts,
    factors,
    judgements,
    morphology,
    relations,
    roles,
)
from arabic_engine.signal.normalization import normalize_atoms
from arabic_engine.signal.segmentation import segment
from arabic_engine.signal.unicode_atoms import decompose


def run(text: str, *, max_iterations: int = 3) -> KernelRuntimeState:
    """Run the full Fractal Kernel pipeline.

    Parameters
    ----------
    text : str
        Raw Arabic input text.
    max_iterations : int
        Maximum number of revision loops (bounded recursion).

    Returns
    -------
    KernelRuntimeState
        Final state with all hypothesis, constraint, and decision data.
    """
    state = KernelRuntimeState(input_text=text)

    # ── Stage 1: Signal Structuring ─────────────────────────────────
    atoms = decompose(text)
    signal_units, norm_traces = normalize_atoms(atoms)
    segments = segment(signal_units)

    state.signal = SignalState(atoms=atoms, signal_units=signal_units)
    state.decisions.trace.extend(norm_traces)

    # Register segment hypotheses
    for seg in segments:
        state.hypotheses.add_hypothesis(seg)

    # ── Stage 2: Hypothesis Graph ───────────────────────────────────
    morph_hyps = morphology.generate(segments)
    for h in morph_hyps:
        state.hypotheses.add_hypothesis(h)

    concept_hyps = concepts.generate(morph_hyps)
    for h in concept_hyps:
        state.hypotheses.add_hypothesis(h)

    axis_hyps = axes.generate(concept_hyps)
    for h in axis_hyps:
        state.hypotheses.add_hypothesis(h)

    relation_hyps = relations.generate(concept_hyps)
    for h in relation_hyps:
        state.hypotheses.add_hypothesis(h)

    role_hyps = roles.generate(concept_hyps)
    for h in role_hyps:
        state.hypotheses.add_hypothesis(h)

    factor_hyps = factors.generate(role_hyps, concept_hyps)
    for h in factor_hyps:
        state.hypotheses.add_hypothesis(h)

    case_hyps = cases.generate(role_hyps, factor_hyps)
    for h in case_hyps:
        state.hypotheses.add_hypothesis(h)

    judgement_hyps = judgements.generate(case_hyps, concept_hyps, role_hyps)
    for h in judgement_hyps:
        state.hypotheses.add_hypothesis(h)

    # ── Stage 3: Constraint Engine ──────────────────────────────────
    all_hyps = state.hypotheses.all_hypotheses()

    # 3a. Prune low-confidence hypotheses
    all_hyps, prune_traces = prune(all_hyps)
    state.decisions.trace.extend(prune_traces)

    # 3b. Propagate constraints (support + conflict edges)
    support_edges, conflict_edges = propagate(all_hyps)
    state.hypotheses.support_edges = support_edges
    state.hypotheses.conflict_edges = conflict_edges
    # Store constraint edges
    state.hypotheses.constraint_edges = get_constraint_edges(all_hyps)

    # 3c. Bounded revision loop
    for iteration in range(max_iterations):
        state.iteration = iteration + 1
        if not needs_revision(all_hyps, conflict_edges):
            break
        all_hyps, rev_traces = apply_revision(all_hyps, conflict_edges)
        state.decisions.trace.extend(rev_traces)
        # Re-propagate after revision
        support_edges, conflict_edges = propagate(all_hyps)
        state.hypotheses.support_edges = support_edges
        state.hypotheses.conflict_edges = conflict_edges

    # ── Stage 4: Stabilization ──────────────────────────────────────
    _stabilize(state, all_hyps)

    return state


def _stabilize(state: KernelRuntimeState, hypotheses: List[HypothesisNode]) -> None:
    """Stabilize all ACTIVE hypotheses and record activated nodes."""
    activated: List[HypothesisNode] = []
    suspended: List[HypothesisNode] = []

    for h in hypotheses:
        if h.status == HypothesisStatus.ACTIVE:
            stabilized = HypothesisNode(
                node_id=h.node_id,
                hypothesis_type=h.hypothesis_type,
                stage=h.stage,
                source_refs=h.source_refs,
                payload=h.payload,
                confidence=h.confidence,
                status=HypothesisStatus.STABILIZED,
            )
            activated.append(stabilized)
        elif h.status == HypothesisStatus.SUSPENDED:
            suspended.append(h)

    state.decisions.activated = activated
    state.decisions.suspended = suspended

    # Set the judgement if one was stabilized
    for h in activated:
        if h.stage == ActivationStage.JUDGEMENT:
            state.decisions.judgement = h
            break

    # Final trace
    state.decisions.trace.append(
        DecisionTrace(
            trace_id="STAB_FINAL",
            stage=ActivationStage.JUDGEMENT,
            decision_type="stabilization",
            input_refs=tuple(h.node_id for h in hypotheses),
            output_refs=tuple(h.node_id for h in activated),
            justification=f"Stabilized {len(activated)} hypotheses, suspended {len(suspended)}",
            confidence=1.0,
        )
    )

    # Rebuild hypothesis dict with final statuses
    state.hypotheses.hypotheses.clear()
    for h in hypotheses:
        # Use the stabilized version if available
        final = next((a for a in activated if a.node_id == h.node_id), None)
        if final is not None:
            state.hypotheses.add_hypothesis(final)
        else:
            state.hypotheses.add_hypothesis(h)
