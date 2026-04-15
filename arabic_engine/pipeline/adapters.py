"""Legacy adapters — تحويل نتائج النواة الفراكتالية إلى الصيغة القديمة.

Maps :class:`~arabic_engine.core.trace.KernelRuntimeState` back to the
legacy :class:`~arabic_engine.runtime_pipeline.RuntimeState` so that
existing tests and callers continue to work.
"""

from __future__ import annotations

from arabic_engine.core.enums import ActivationStage
from arabic_engine.core.trace import KernelRuntimeState
from arabic_engine.runtime_pipeline import (
    AxisActivation,
    CaseResolution,
    ConceptUnit,
    FactorAssignment,
    JudgementResult,
    PipelineStage,
    RelationUnit,
    RoleAssignment,
    RuntimeState,
    TraceEntry,
    UtteranceUnit,
)


def to_legacy_state(kernel: KernelRuntimeState) -> RuntimeState:
    """Convert a KernelRuntimeState to a legacy RuntimeState.

    This is the **compatibility facade**: the new engine runs the
    Fractal Kernel pipeline and then maps results into the old data
    structures so that ``run_pipeline()`` in ``runtime_pipeline.py``
    can return the familiar ``RuntimeState``.

    Parameters
    ----------
    kernel : KernelRuntimeState
        Output of :func:`arabic_engine.runtime.orchestrator.run`.

    Returns
    -------
    RuntimeState
        Legacy-compatible result.
    """
    state = RuntimeState(raw_text=kernel.input_text)

    # ── Map segmentation → utterance units ──────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.SIGNAL, []):
        if h.hypothesis_type == "segmentation":
            state.utterance_units.append(
                UtteranceUnit(
                    token=str(h.get("token_text", "")),
                    pattern_candidate="",
                    syntactic_potential="",
                    semantic_trigger="",
                )
            )

    # ── Map concept hypotheses ──────────────────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.CONCEPT, []):
        state.concepts.append(
            ConceptUnit(
                label=str(h.get("label", "")),
                concept_type=str(h.get("semantic_type", "")),
                determination_degree=str(h.get("determination", "")),
                referability=str(h.get("referentiality", "")),
            )
        )

    # ── Map axis hypotheses ─────────────────────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.AXIS, []):
        state.axes.append(
            AxisActivation(
                axis_name=str(h.get("axis_name", "")),
                value=str(h.get("axis_value", "")),
            )
        )

    # ── Map relation hypotheses ─────────────────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.RELATION, []):
        state.relations.append(
            RelationUnit(
                relation_type=str(h.get("relation_type", "")),
                source=str(h.get("source_label", "")),
                target=str(h.get("target_label", "")),
            )
        )

    # ── Map role hypotheses ─────────────────────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.ROLE, []):
        state.roles.append(
            RoleAssignment(
                token=str(h.get("token_label", "")),
                role=str(h.get("role", "")),
            )
        )

    # ── Map factor hypotheses ───────────────────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.FACTOR, []):
        state.factors.append(
            FactorAssignment(
                token=str(h.get("governed_role", "")),
                factor=str(h.get("factor", "")),
                factor_type=str(h.get("factor_type", "")),
            )
        )

    # ── Map case hypotheses ─────────────────────────────────────────
    for h in kernel.hypotheses.hypotheses.get(ActivationStage.CASE, []):
        state.case_resolutions.append(
            CaseResolution(
                token=str(h.get("role", "")),
                role=str(h.get("role", "")),
                factor=str(h.get("factor", "")),
                case_state=str(h.get("case_state", "")),
                justification=str(h.get("justification", "")),
            )
        )

    # ── Map judgement ───────────────────────────────────────────────
    j = kernel.decisions.judgement
    if j is not None:
        state.judgement = JudgementResult(
            proposition_type=str(j.get("proposition_type", "")),
            rank=str(j.get("rank", "")),
            confidence=j.confidence,
        )

    # ── Map traces ──────────────────────────────────────────────────
    _STAGE_MAP = {
        ActivationStage.SIGNAL: PipelineStage.UTTERANCE,
        ActivationStage.MORPHOLOGY: PipelineStage.UTTERANCE,
        ActivationStage.CONCEPT: PipelineStage.CONCEPT,
        ActivationStage.AXIS: PipelineStage.AXIS,
        ActivationStage.RELATION: PipelineStage.RELATION,
        ActivationStage.ROLE: PipelineStage.ROLE,
        ActivationStage.FACTOR: PipelineStage.FACTOR,
        ActivationStage.CASE: PipelineStage.CASE,
        ActivationStage.JUDGEMENT: PipelineStage.JUDGEMENT,
    }

    for dt in kernel.decisions.trace:
        legacy_stage = _STAGE_MAP.get(dt.stage, PipelineStage.JUDGEMENT)
        state.trace.append(
            TraceEntry(
                stage=legacy_stage,
                input_summary=", ".join(dt.input_refs) if dt.input_refs else "",
                output_summary=", ".join(dt.output_refs) if dt.output_refs else "",
                rule_activated=", ".join(dt.applied_rules) if dt.applied_rules else "",
                conflict=dt.justification,
            )
        )

    return state
