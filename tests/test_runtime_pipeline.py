from __future__ import annotations

import dataclasses

from arabic_engine.runtime_pipeline import (
    ConceptUnit,
    PipelineStage,
    RuntimeState,
    TraceEntry,
    UtteranceUnit,
    activate_axes,
    assign_roles,
    build_relations,
    resolve_case,
    resolve_concepts,
    resolve_factors,
    resolve_utterance_units,
    run_pipeline,
)

_SAMPLE = "ذهب الطالبُ إلى المدرسة"


# ── run_pipeline ───────────────────────────────────────────────────


def test_run_pipeline_returns_runtime_state() -> None:
    result = run_pipeline(_SAMPLE)
    assert isinstance(result, RuntimeState)


def test_run_pipeline_has_judgement() -> None:
    result = run_pipeline(_SAMPLE)
    assert result.judgement is not None


def test_run_pipeline_has_trace() -> None:
    result = run_pipeline(_SAMPLE)
    assert isinstance(result.trace, list) and len(result.trace) > 0


def test_run_pipeline_trace_has_8_entries() -> None:
    result = run_pipeline(_SAMPLE)
    assert len(result.trace) == 8


def test_run_pipeline_utterance_units() -> None:
    result = run_pipeline(_SAMPLE)
    assert len(result.utterance_units) == len(_SAMPLE.split())


def test_run_pipeline_concepts_match_tokens() -> None:
    result = run_pipeline(_SAMPLE)
    assert len(result.concepts) == len(_SAMPLE.split())


# ── resolve_utterance_units ────────────────────────────────────────


def test_resolve_utterance_units_creates_units() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    assert len(state.utterance_units) == len(_SAMPLE.split())
    assert all(isinstance(u, UtteranceUnit) for u in state.utterance_units)


def test_resolve_utterance_units_appends_trace() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    assert len(state.trace) == 1
    assert state.trace[0].stage == PipelineStage.UTTERANCE


# ── resolve_concepts ───────────────────────────────────────────────


def test_resolve_concepts_creates_concept_units() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    resolve_concepts(state)
    assert all(isinstance(c, ConceptUnit) for c in state.concepts)


def test_resolve_concepts_definite_detection() -> None:
    state = RuntimeState(raw_text="الكتاب")
    resolve_utterance_units(state)
    resolve_concepts(state)
    assert state.concepts[0].determination_degree == "definite"


# ── activate_axes ──────────────────────────────────────────────────


def test_activate_axes_creates_activations() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    resolve_concepts(state)
    activate_axes(state)
    n_concepts = len(state.concepts)
    assert len(state.axes) == n_concepts * 6


# ── build_relations ────────────────────────────────────────────────


def test_build_relations_adjacent_pairs() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    build_relations(state)
    assert len(state.relations) == len(_SAMPLE.split()) - 1


# ── assign_roles ───────────────────────────────────────────────────


def test_assign_roles_first_verbal() -> None:
    state = RuntimeState(raw_text="ذهب الطالب")
    resolve_utterance_units(state)
    assign_roles(state)
    assert state.roles[0].role == "فعل"


def test_assign_roles_first_nominal() -> None:
    state = RuntimeState(raw_text="الطالب ذهب")
    resolve_utterance_units(state)
    assign_roles(state)
    assert state.roles[0].role == "مبتدأ"


# ── resolve_factors ────────────────────────────────────────────────


def test_resolve_factors() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    assign_roles(state)
    resolve_factors(state)
    assert len(state.factors) > 0


# ── resolve_case ───────────────────────────────────────────────────


def test_resolve_case_creates_resolutions() -> None:
    state = RuntimeState(raw_text=_SAMPLE)
    resolve_utterance_units(state)
    assign_roles(state)
    resolve_factors(state)
    resolve_case(state)
    assert len(state.case_resolutions) > 0


# ── build_judgement ────────────────────────────────────────────────


def test_build_judgement_sets_proposition_type() -> None:
    result = run_pipeline(_SAMPLE)
    assert result.judgement is not None
    assert result.judgement.proposition_type == "تقريرية"


def test_build_judgement_empty_input() -> None:
    result = run_pipeline("")
    assert result.judgement is not None
    assert result.judgement.proposition_type == "غير محدد"


# ── PipelineStage enum ─────────────────────────────────────────────


def test_pipeline_stage_enum() -> None:
    assert len(PipelineStage) == 8


# ── TraceEntry frozen ──────────────────────────────────────────────


def test_trace_entry_frozen() -> None:
    assert dataclasses.is_dataclass(TraceEntry)
    fields = dataclasses.fields(TraceEntry)
    assert len(fields) > 0
    # frozen dataclasses raise FrozenInstanceError on attribute assignment
    entry = TraceEntry(
        stage=PipelineStage.UTTERANCE,
        input_summary="x",
        output_summary="y",
    )
    try:
        entry.stage = PipelineStage.CONCEPT  # type: ignore[misc]
        frozen = False
    except (dataclasses.FrozenInstanceError, AttributeError):
        frozen = True
    assert frozen
