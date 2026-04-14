"""Tests for arabic_engine.runtime_pipeline — the eight-stage operational bridge."""

from __future__ import annotations

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
    activate_axes,
    assign_roles,
    build_judgement,
    build_relations,
    resolve_case,
    resolve_concepts,
    resolve_factors,
    resolve_utterance_units,
    run_pipeline,
)

# ── Fixtures / helpers ──────────────────────────────────────────────────


def _state(text: str = "ذهب الطالبُ إلى المدرسة") -> RuntimeState:
    """Return a fresh RuntimeState with the given text."""
    return RuntimeState(raw_text=text)


def _run_up_to_utterance(text: str = "ذهب الطالبُ إلى المدرسة") -> RuntimeState:
    state = _state(text)
    resolve_utterance_units(state)
    return state


def _run_up_to_concepts(text: str = "ذهب الطالبُ إلى المدرسة") -> RuntimeState:
    state = _run_up_to_utterance(text)
    resolve_concepts(state)
    return state


def _run_up_to_roles(text: str = "ذهب الطالبُ إلى المدرسة") -> RuntimeState:
    state = _run_up_to_concepts(text)
    activate_axes(state)
    build_relations(state)
    assign_roles(state)
    return state


# ── PipelineStage enum ──────────────────────────────────────────────────


class TestPipelineStage:
    """Tests for the PipelineStage enum."""

    def test_has_eight_stages(self):
        assert len(PipelineStage) == 8

    def test_stage_names(self):
        expected = {
            "UTTERANCE", "CONCEPT", "AXIS", "RELATION",
            "ROLE", "FACTOR", "CASE", "JUDGEMENT",
        }
        assert {s.name for s in PipelineStage} == expected


# ── Frozen dataclasses ──────────────────────────────────────────────────


class TestTraceEntry:
    """Tests for TraceEntry dataclass."""

    def test_creation(self):
        entry = TraceEntry(
            stage=PipelineStage.UTTERANCE,
            input_summary="raw",
            output_summary="3 units",
        )
        assert entry.stage == PipelineStage.UTTERANCE
        assert entry.rule_activated == ""
        assert entry.conflict == ""

    def test_frozen(self):
        entry = TraceEntry(
            stage=PipelineStage.UTTERANCE,
            input_summary="a",
            output_summary="b",
        )
        try:
            entry.stage = PipelineStage.CONCEPT  # type: ignore[misc]
            assert False, "Should raise"
        except AttributeError:
            pass


class TestUtteranceUnit:
    """Tests for UtteranceUnit dataclass."""

    def test_defaults(self):
        u = UtteranceUnit(token="كَتَبَ")
        assert u.pattern_candidate == ""
        assert u.syntactic_potential == ""
        assert u.semantic_trigger == ""

    def test_frozen(self):
        u = UtteranceUnit(token="x")
        try:
            u.token = "y"  # type: ignore[misc]
            assert False, "Should raise"
        except AttributeError:
            pass


class TestConceptUnit:
    """Tests for ConceptUnit dataclass."""

    def test_defaults(self):
        c = ConceptUnit(label="test")
        assert c.concept_type == ""
        assert c.determination_degree == ""
        assert c.referability == ""


class TestAxisActivation:
    """Tests for AxisActivation dataclass."""

    def test_creation(self):
        a = AxisActivation(axis_name="معرفة/نكرة", value="معرفة")
        assert a.axis_name == "معرفة/نكرة"
        assert a.value == "معرفة"


class TestRelationUnit:
    """Tests for RelationUnit dataclass."""

    def test_creation(self):
        r = RelationUnit(relation_type="إسناد", source="كتب", target="زيد")
        assert r.relation_type == "إسناد"


class TestRoleAssignment:
    """Tests for RoleAssignment dataclass."""

    def test_creation(self):
        r = RoleAssignment(token="كتب", role="فعل")
        assert r.token == "كتب"
        assert r.role == "فعل"


class TestFactorAssignment:
    """Tests for FactorAssignment dataclass."""

    def test_defaults(self):
        f = FactorAssignment(token="x", factor="y")
        assert f.factor_type == ""


class TestCaseResolution:
    """Tests for CaseResolution dataclass."""

    def test_defaults(self):
        c = CaseResolution(token="x", role="فاعل", factor="كتب", case_state="رفع")
        assert c.justification == ""


class TestJudgementResult:
    """Tests for JudgementResult dataclass."""

    def test_defaults(self):
        j = JudgementResult(proposition_type="تقريرية", rank="إخبار")
        assert j.confidence == 1.0
        assert j.details == ""


# ── RuntimeState ────────────────────────────────────────────────────────


class TestRuntimeState:
    """Tests for RuntimeState dataclass."""

    def test_default_fields(self):
        s = RuntimeState()
        assert s.raw_text == ""
        assert s.utterance_units == []
        assert s.concepts == []
        assert s.axes == []
        assert s.relations == []
        assert s.roles == []
        assert s.factors == []
        assert s.case_resolutions == []
        assert s.judgement is None
        assert s.trace == []
        assert s.metadata == {}

    def test_append_trace(self):
        s = RuntimeState()
        s.append_trace(
            PipelineStage.UTTERANCE,
            input_summary="in",
            output_summary="out",
            rule_activated="r1",
            conflict="c1",
        )
        assert len(s.trace) == 1
        assert s.trace[0].stage == PipelineStage.UTTERANCE
        assert s.trace[0].rule_activated == "r1"
        assert s.trace[0].conflict == "c1"

    def test_append_trace_defaults(self):
        s = RuntimeState()
        s.append_trace(
            PipelineStage.CONCEPT,
            input_summary="i",
            output_summary="o",
        )
        assert s.trace[0].rule_activated == ""
        assert s.trace[0].conflict == ""


# ── Stage A: resolve_utterance_units ────────────────────────────────────


class TestResolveUtteranceUnits:
    """Tests for Stage A — resolve_utterance_units."""

    def test_returns_state(self):
        state = _state("test")
        result = resolve_utterance_units(state)
        assert result is state

    def test_single_token(self):
        state = _state("كلمة")
        resolve_utterance_units(state)
        assert len(state.utterance_units) == 1
        assert state.utterance_units[0].token == "كلمة"

    def test_multiple_tokens(self):
        state = _state("ذهب الطالب")
        resolve_utterance_units(state)
        assert len(state.utterance_units) == 2

    def test_empty_text(self):
        state = _state("")
        resolve_utterance_units(state)
        assert state.utterance_units == []

    def test_nominal_token_al_prefix(self):
        """Tokens starting with 'ال' are classified as nominal."""
        state = _state("الكتاب")
        resolve_utterance_units(state)
        u = state.utterance_units[0]
        assert u.syntactic_potential == "nominal"
        assert u.semantic_trigger == "entity"

    def test_nominal_token_ta_marbuta(self):
        """Tokens ending with 'ة' are classified as nominal."""
        state = _state("مدرسة")
        resolve_utterance_units(state)
        u = state.utterance_units[0]
        assert u.syntactic_potential == "nominal"

    def test_verbal_token(self):
        """Tokens not starting with 'ال' and not ending with 'ة' are verbal."""
        state = _state("ذهب")
        resolve_utterance_units(state)
        u = state.utterance_units[0]
        assert u.syntactic_potential == "verbal"
        assert u.semantic_trigger == "event"

    def test_pattern_guess_three_chars(self):
        state = _state("ذهب")
        resolve_utterance_units(state)
        assert state.utterance_units[0].pattern_candidate == "فَعَلَ"

    def test_pattern_guess_four_chars(self):
        state = _state("علّم")
        resolve_utterance_units(state)
        assert state.utterance_units[0].pattern_candidate == "فَعَّلَ"

    def test_pattern_guess_other_length(self):
        state = _state("استخرج")
        resolve_utterance_units(state)
        assert state.utterance_units[0].pattern_candidate == "غير محدد"

    def test_trace_appended(self):
        state = _state("test")
        resolve_utterance_units(state)
        assert len(state.trace) == 1
        assert state.trace[0].stage == PipelineStage.UTTERANCE


# ── Stage B: resolve_concepts ───────────────────────────────────────────


class TestResolveConcepts:
    """Tests for Stage B — resolve_concepts."""

    def test_returns_state(self):
        state = _run_up_to_utterance("كلمة")
        result = resolve_concepts(state)
        assert result is state

    def test_concept_count_matches_units(self):
        state = _run_up_to_utterance("ذهب الطالب")
        resolve_concepts(state)
        assert len(state.concepts) == len(state.utterance_units)

    def test_definite_detection(self):
        """Tokens starting with 'ال' are marked definite."""
        state = _run_up_to_utterance("الكتاب")
        resolve_concepts(state)
        assert state.concepts[0].determination_degree == "definite"

    def test_indefinite_detection(self):
        """Tokens not starting with 'ال' are marked indefinite."""
        state = _run_up_to_utterance("كتاب")
        resolve_concepts(state)
        assert state.concepts[0].determination_degree == "indefinite"

    def test_concept_label_matches_token(self):
        state = _run_up_to_utterance("ذهب")
        resolve_concepts(state)
        assert state.concepts[0].label == "ذهب"

    def test_trace_appended(self):
        state = _run_up_to_utterance("ذهب")
        resolve_concepts(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.CONCEPT]
        assert len(traces) == 1

    def test_empty_input(self):
        state = _run_up_to_utterance("")
        resolve_concepts(state)
        assert state.concepts == []


# ── Stage C: activate_axes ──────────────────────────────────────────────


class TestActivateAxes:
    """Tests for Stage C — activate_axes."""

    def test_returns_state(self):
        state = _run_up_to_concepts("ذهب")
        result = activate_axes(state)
        assert result is state

    def test_six_axes_per_concept(self):
        """Each concept produces 6 axis activations."""
        state = _run_up_to_concepts("ذهب")
        activate_axes(state)
        assert len(state.axes) == 6

    def test_multiple_concepts(self):
        state = _run_up_to_concepts("ذهب الطالب")
        activate_axes(state)
        assert len(state.axes) == 12  # 2 concepts × 6 axes

    def test_definite_concept_axis(self):
        """A definite concept's 'معرفة/نكرة' axis should resolve to 'معرفة'."""
        state = _run_up_to_concepts("الكتاب")
        activate_axes(state)
        marifa_axis = [a for a in state.axes if a.axis_name == "معرفة/نكرة"]
        assert len(marifa_axis) == 1
        assert marifa_axis[0].value == "معرفة"

    def test_indefinite_concept_axis(self):
        """An indefinite concept's 'معرفة/نكرة' axis should resolve to 'نكرة'."""
        state = _run_up_to_concepts("كتاب")
        activate_axes(state)
        marifa_axis = [a for a in state.axes if a.axis_name == "معرفة/نكرة"]
        assert marifa_axis[0].value == "نكرة"

    def test_trace_appended(self):
        state = _run_up_to_concepts("ذهب")
        activate_axes(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.AXIS]
        assert len(traces) == 1

    def test_empty_concepts(self):
        state = _run_up_to_concepts("")
        activate_axes(state)
        assert state.axes == []


# ── Stage D: build_relations ────────────────────────────────────────────


class TestBuildRelations:
    """Tests for Stage D — build_relations."""

    def test_returns_state(self):
        state = _run_up_to_utterance("ذهب الطالب")
        result = build_relations(state)
        assert result is state

    def test_relation_count(self):
        """N tokens produce N-1 relations."""
        state = _run_up_to_utterance("ذهب الطالب إلى")
        build_relations(state)
        assert len(state.relations) == 2

    def test_single_token_no_relations(self):
        state = _run_up_to_utterance("كلمة")
        build_relations(state)
        assert state.relations == []

    def test_verbal_to_nominal_is_isnad(self):
        """A verbal token followed by a nominal token produces 'إسناد'."""
        state = _run_up_to_utterance("ذهب الطالب")
        build_relations(state)
        assert state.relations[0].relation_type == "إسناد"

    def test_preposition_is_zarfiyya(self):
        """A preposition token (verbal) followed by a verbal token produces 'ظرفية'."""
        # "إلى" is classified as verbal (no "ال" prefix, no "ة" suffix),
        # and "كتب" is also verbal, so the first إسناد rule does not match,
        # but the preposition check does.
        state = _run_up_to_utterance("إلى كتب")
        build_relations(state)
        assert state.relations[0].relation_type == "ظرفية"

    def test_source_and_target(self):
        state = _run_up_to_utterance("ذهب الطالب")
        build_relations(state)
        assert state.relations[0].source == "ذهب"
        assert state.relations[0].target == "الطالب"

    def test_trace_appended(self):
        state = _run_up_to_utterance("ذهب الطالب")
        build_relations(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.RELATION]
        assert len(traces) == 1


# ── Stage E: assign_roles ──────────────────────────────────────────────


class TestAssignRoles:
    """Tests for Stage E — assign_roles."""

    def test_returns_state(self):
        state = _run_up_to_utterance("ذهب الطالب")
        result = assign_roles(state)
        assert result is state

    def test_verbal_first_token_is_fi3l(self):
        """First verbal token should be assigned role 'فعل'."""
        state = _run_up_to_utterance("ذهب الطالب")
        assign_roles(state)
        assert state.roles[0].role == "فعل"

    def test_nominal_first_token_is_mubtada(self):
        """First nominal token should be assigned role 'مبتدأ'."""
        state = _run_up_to_utterance("الطالبُ ذهب")
        assign_roles(state)
        assert state.roles[0].role == "مبتدأ"

    def test_second_token_after_verbal_is_fa3il(self):
        state = _run_up_to_utterance("ذهب الطالب")
        assign_roles(state)
        assert state.roles[1].role == "فاعل"

    def test_second_token_after_nominal_is_khabar(self):
        state = _run_up_to_utterance("الطالبُ ذهب")
        assign_roles(state)
        assert state.roles[1].role == "خبر"

    def test_preposition_is_harf_jar(self):
        state = _run_up_to_utterance("ذهب الطالب إلى")
        assign_roles(state)
        assert state.roles[2].role == "حرف_جر"

    def test_remaining_token_is_maf3ul(self):
        """Tokens beyond position 1 that are not prepositions get 'مفعول'."""
        state = _run_up_to_utterance("ذهب الطالب المدرسة")
        assign_roles(state)
        assert state.roles[2].role == "مفعول"

    def test_trace_appended(self):
        state = _run_up_to_utterance("ذهب")
        assign_roles(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.ROLE]
        assert len(traces) == 1


# ── Stage F: resolve_factors ────────────────────────────────────────────


class TestResolveFactors:
    """Tests for Stage F — resolve_factors."""

    def test_returns_state(self):
        state = _run_up_to_roles("ذهب الطالب")
        result = resolve_factors(state)
        assert result is state

    def test_fi3l_factor_is_self(self):
        state = _run_up_to_roles("ذهب الطالب")
        resolve_factors(state)
        fi3l_factor = state.factors[0]
        assert fi3l_factor.factor == "ذاتي"
        assert fi3l_factor.factor_type == "فعل"

    def test_fa3il_governed_by_verb(self):
        state = _run_up_to_roles("ذهب الطالب")
        resolve_factors(state)
        fa3il_factor = state.factors[1]
        assert fa3il_factor.factor == "ذهب"
        assert fa3il_factor.factor_type == "فعل"

    def test_mubtada_factor(self):
        state = _run_up_to_roles("الطالبُ ذهب")
        resolve_factors(state)
        assert state.factors[0].factor == "ابتداء"
        assert state.factors[0].factor_type == "عامل_معنوي"

    def test_khabar_factor(self):
        state = _run_up_to_roles("الطالبُ ذهب")
        resolve_factors(state)
        assert state.factors[1].factor == "ابتداء"

    def test_harf_jar_factor(self):
        state = _run_up_to_roles("ذهب الطالب إلى")
        resolve_factors(state)
        jar_factor = state.factors[2]
        assert jar_factor.factor == "إلى"
        assert jar_factor.factor_type == "حرف_جر"

    def test_maf3ul_factor(self):
        state = _run_up_to_roles("ذهب الطالب المدرسة")
        resolve_factors(state)
        maf3ul = state.factors[2]
        assert maf3ul.factor == "مقدر"
        assert maf3ul.factor_type == "عامل_مقدر"

    def test_trace_appended(self):
        state = _run_up_to_roles("ذهب")
        resolve_factors(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.FACTOR]
        assert len(traces) == 1


# ── Stage G: resolve_case ──────────────────────────────────────────────


class TestResolveCase:
    """Tests for Stage G — resolve_case."""

    def test_returns_state(self):
        state = _run_up_to_roles("ذهب الطالب")
        resolve_factors(state)
        result = resolve_case(state)
        assert result is state

    def test_fa3il_is_raf3(self):
        state = _run_up_to_roles("ذهب الطالب")
        resolve_factors(state)
        resolve_case(state)
        fa3il_case = state.case_resolutions[1]
        assert fa3il_case.case_state == "رفع"

    def test_fi3l_is_mabni(self):
        state = _run_up_to_roles("ذهب الطالب")
        resolve_factors(state)
        resolve_case(state)
        assert state.case_resolutions[0].case_state == "مبني"

    def test_maf3ul_is_nasb(self):
        state = _run_up_to_roles("ذهب الطالب المدرسة")
        resolve_factors(state)
        resolve_case(state)
        assert state.case_resolutions[2].case_state == "نصب"

    def test_mubtada_is_raf3(self):
        state = _run_up_to_roles("الطالبُ ذهب")
        resolve_factors(state)
        resolve_case(state)
        assert state.case_resolutions[0].case_state == "رفع"

    def test_justification_populated(self):
        state = _run_up_to_roles("ذهب الطالب")
        resolve_factors(state)
        resolve_case(state)
        for cr in state.case_resolutions:
            assert cr.justification != ""

    def test_trace_appended(self):
        state = _run_up_to_roles("ذهب")
        resolve_factors(state)
        resolve_case(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.CASE]
        assert len(traces) == 1


# ── Stage H: build_judgement ────────────────────────────────────────────


class TestBuildJudgement:
    """Tests for Stage H — build_judgement."""

    def test_returns_state(self):
        state = _state("ذهب")
        resolve_utterance_units(state)
        result = build_judgement(state)
        assert result is state

    def test_non_empty_input_is_taqririya(self):
        state = _state("ذهب")
        resolve_utterance_units(state)
        build_judgement(state)
        assert state.judgement is not None
        assert state.judgement.proposition_type == "تقريرية"

    def test_empty_input_is_undetermined(self):
        state = _state("")
        resolve_utterance_units(state)
        build_judgement(state)
        assert state.judgement is not None
        assert state.judgement.proposition_type == "غير محدد"

    def test_rank_is_ikhbar(self):
        state = _state("ذهب")
        resolve_utterance_units(state)
        build_judgement(state)
        assert state.judgement.rank == "إخبار"

    def test_confidence_is_one(self):
        state = _state("ذهب")
        resolve_utterance_units(state)
        build_judgement(state)
        assert state.judgement.confidence == 1.0

    def test_trace_appended(self):
        state = _state("ذهب")
        resolve_utterance_units(state)
        build_judgement(state)
        traces = [t for t in state.trace if t.stage == PipelineStage.JUDGEMENT]
        assert len(traces) == 1


# ── Full pipeline: run_pipeline ─────────────────────────────────────────


class TestRunPipeline:
    """Tests for run_pipeline — the full eight-stage pipeline."""

    def test_returns_runtime_state(self):
        result = run_pipeline("ذهب الطالب")
        assert isinstance(result, RuntimeState)

    def test_all_stages_produce_trace(self):
        result = run_pipeline("ذهب الطالب إلى المدرسة")
        assert len(result.trace) == 8

    def test_trace_stage_order(self):
        result = run_pipeline("ذهب الطالب")
        stages = [t.stage for t in result.trace]
        expected = [
            PipelineStage.UTTERANCE,
            PipelineStage.CONCEPT,
            PipelineStage.AXIS,
            PipelineStage.RELATION,
            PipelineStage.ROLE,
            PipelineStage.FACTOR,
            PipelineStage.CASE,
            PipelineStage.JUDGEMENT,
        ]
        assert stages == expected

    def test_judgement_populated(self):
        result = run_pipeline("ذهب الطالب")
        assert result.judgement is not None

    def test_utterance_units_populated(self):
        result = run_pipeline("ذهب الطالب")
        assert len(result.utterance_units) == 2

    def test_concepts_populated(self):
        result = run_pipeline("ذهب الطالب")
        assert len(result.concepts) == 2

    def test_roles_populated(self):
        result = run_pipeline("ذهب الطالب")
        assert len(result.roles) == 2

    def test_factors_populated(self):
        result = run_pipeline("ذهب الطالب")
        assert len(result.factors) == 2

    def test_case_resolutions_populated(self):
        result = run_pipeline("ذهب الطالب")
        assert len(result.case_resolutions) == 2

    def test_empty_text(self):
        result = run_pipeline("")
        assert result.utterance_units == []
        assert result.concepts == []
        assert result.judgement is not None
        assert result.judgement.proposition_type == "غير محدد"

    def test_single_token(self):
        result = run_pipeline("كتب")
        assert len(result.utterance_units) == 1
        assert len(result.relations) == 0

    def test_metadata_defaults_to_empty(self):
        result = run_pipeline("ذهب")
        assert result.metadata == {}

    def test_raw_text_preserved(self):
        text = "ذهب الطالبُ إلى المدرسة"
        result = run_pipeline(text)
        assert result.raw_text == text
