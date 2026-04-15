"""runtime_pipeline — الجسر التشغيلي بين المنطوق والمفهوم.

.. deprecated::
    This module is **deprecated**.  Use the Fractal Kernel orchestrator
    (:func:`arabic_engine.runtime.orchestrator.run`) or the main pipeline
    (:func:`arabic_engine.pipeline.run`) instead.  ``runtime_pipeline``
    will be removed in a future release.

Implements the explicit eight-stage operational bridge:

    Utterance → Concept → Axis → Relation → Role → Factor → Case → Judgement

Each stage is a pure function that receives and returns a shared
:class:`RuntimeState`, appending structured trace entries so that every
decision is auditable.

Usage::

    from arabic_engine.runtime_pipeline import run_pipeline

    result = run_pipeline("ذهب الطالبُ إلى المدرسة")
    print(result.judgement)
    print(result.trace)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

# ── Stage enum ──────────────────────────────────────────────────────


class PipelineStage(Enum):
    """المراحل التشغيلية — operational pipeline stages."""

    UTTERANCE = auto()
    CONCEPT = auto()
    AXIS = auto()
    RELATION = auto()
    ROLE = auto()
    FACTOR = auto()
    CASE = auto()
    JUDGEMENT = auto()


# ── Trace entry ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class TraceEntry:
    """سجل أثر واحد — a single trace log entry.

    Every stage appends at least one :class:`TraceEntry` so the entire
    decision chain is reproducible.
    """

    stage: PipelineStage
    input_summary: str
    output_summary: str
    rule_activated: str = ""
    conflict: str = ""


# ── Data records flowing through the pipeline ───────────────────────


@dataclass(frozen=True)
class UtteranceUnit:
    """وحدة منطوقة — a single token enriched with potential information."""

    token: str
    pattern_candidate: str = ""
    syntactic_potential: str = ""
    semantic_trigger: str = ""


@dataclass(frozen=True)
class ConceptUnit:
    """وحدة مفهومية — concept derived from an utterance unit."""

    label: str
    concept_type: str = ""
    determination_degree: str = ""
    referability: str = ""


@dataclass(frozen=True)
class AxisActivation:
    """تفعيل محور — an axis activated for a concept."""

    axis_name: str
    value: str


@dataclass(frozen=True)
class RelationUnit:
    """وحدة علاقة — a syntactic/semantic relation."""

    relation_type: str
    source: str
    target: str


@dataclass(frozen=True)
class RoleAssignment:
    """تعيين دور — a grammatical role assignment."""

    token: str
    role: str


@dataclass(frozen=True)
class FactorAssignment:
    """تعيين عامل — a grammatical factor (governor) assignment."""

    token: str
    factor: str
    factor_type: str = ""


@dataclass(frozen=True)
class CaseResolution:
    """حل حالة إعرابية — resolved case for a token."""

    token: str
    role: str
    factor: str
    case_state: str
    justification: str = ""


@dataclass(frozen=True)
class JudgementResult:
    """نتيجة الحكم — final judgement for the utterance."""

    proposition_type: str
    rank: str
    confidence: float = 1.0
    details: str = ""


# ── Runtime state ───────────────────────────────────────────────────


@dataclass
class RuntimeState:
    """حالة التشغيل — shared mutable state flowing through the pipeline.

    Each stage reads from previous stages' outputs and writes its own
    results, building up the full analysis incrementally.
    """

    raw_text: str = ""
    utterance_units: List[UtteranceUnit] = field(default_factory=list)
    concepts: List[ConceptUnit] = field(default_factory=list)
    axes: List[AxisActivation] = field(default_factory=list)
    relations: List[RelationUnit] = field(default_factory=list)
    roles: List[RoleAssignment] = field(default_factory=list)
    factors: List[FactorAssignment] = field(default_factory=list)
    case_resolutions: List[CaseResolution] = field(default_factory=list)
    judgement: Optional[JudgementResult] = None
    trace: List[TraceEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ── convenience helpers ──────────────────────────────────────────

    def append_trace(
        self,
        stage: PipelineStage,
        *,
        input_summary: str,
        output_summary: str,
        rule_activated: str = "",
        conflict: str = "",
    ) -> None:
        self.trace.append(
            TraceEntry(
                stage=stage,
                input_summary=input_summary,
                output_summary=output_summary,
                rule_activated=rule_activated,
                conflict=conflict,
            )
        )


# ── Stage A: Utterance ──────────────────────────────────────────────


def resolve_utterance_units(state: RuntimeState) -> RuntimeState:
    """المرحلة A — تحليل المنطوق إلى وحدات قابلة للتفسير.

    Tokenises the raw text and annotates each token with pattern,
    syntactic, and semantic potential information.
    """
    tokens = state.raw_text.split()
    units: List[UtteranceUnit] = []
    for token in tokens:
        units.append(
            UtteranceUnit(
                token=token,
                pattern_candidate=_guess_pattern(token),
                syntactic_potential="nominal" if _is_nominal(token) else "verbal",
                semantic_trigger="entity" if _is_nominal(token) else "event",
            )
        )
    state.utterance_units = units
    state.append_trace(
        PipelineStage.UTTERANCE,
        input_summary=f"raw_text='{state.raw_text}'",
        output_summary=f"{len(units)} utterance units",
    )
    return state


# ── Stage B: Concept ────────────────────────────────────────────────


def resolve_concepts(state: RuntimeState) -> RuntimeState:
    """المرحلة B — تحديد المفهوم الأولي لكل وحدة منطوقة."""
    concepts: List[ConceptUnit] = []
    for unit in state.utterance_units:
        concepts.append(
            ConceptUnit(
                label=unit.token,
                concept_type=unit.semantic_trigger,
                determination_degree="definite" if unit.token.startswith("ال") else "indefinite",
                referability="referential",
            )
        )
    state.concepts = concepts
    state.append_trace(
        PipelineStage.CONCEPT,
        input_summary=f"{len(state.utterance_units)} utterance units",
        output_summary=f"{len(concepts)} concepts",
    )
    return state


# ── Stage C: Axis ──────────────────────────────────────────────────


_AXIS_NAMES = [
    "جامد/مشتق",
    "مبني/معرب",
    "معرفة/نكرة",
    "كلي/جزئي",
    "ثابت/متحول",
    "زمني/مكاني",
]


def activate_axes(state: RuntimeState) -> RuntimeState:
    """المرحلة C — تفعيل المحاور الدلالية لكل مفهوم."""
    activations: List[AxisActivation] = []
    for concept in state.concepts:
        for axis_name in _AXIS_NAMES:
            value = _resolve_axis(concept, axis_name)
            activations.append(AxisActivation(axis_name=axis_name, value=value))
    state.axes = activations
    state.append_trace(
        PipelineStage.AXIS,
        input_summary=f"{len(state.concepts)} concepts",
        output_summary=f"{len(activations)} axis activations",
    )
    return state


# ── Stage D: Relation ──────────────────────────────────────────────


def build_relations(state: RuntimeState) -> RuntimeState:
    """المرحلة D — بناء العلاقات النحوية والدلالية."""
    relations: List[RelationUnit] = []
    units = state.utterance_units
    for i in range(len(units) - 1):
        rel_type = _infer_relation(units[i], units[i + 1])
        relations.append(
            RelationUnit(
                relation_type=rel_type,
                source=units[i].token,
                target=units[i + 1].token,
            )
        )
    state.relations = relations
    state.append_trace(
        PipelineStage.RELATION,
        input_summary=f"{len(units)} tokens",
        output_summary=f"{len(relations)} relations",
    )
    return state


# ── Stage E: Role ──────────────────────────────────────────────────


def assign_roles(state: RuntimeState) -> RuntimeState:
    """المرحلة E — تعيين الأدوار النحوية."""
    roles: List[RoleAssignment] = []
    for i, unit in enumerate(state.utterance_units):
        role = _infer_role(unit, i, state)
        roles.append(RoleAssignment(token=unit.token, role=role))
    state.roles = roles
    state.append_trace(
        PipelineStage.ROLE,
        input_summary=f"{len(state.utterance_units)} tokens",
        output_summary=f"{len(roles)} role assignments",
    )
    return state


# ── Stage F: Factor ────────────────────────────────────────────────


def resolve_factors(state: RuntimeState) -> RuntimeState:
    """المرحلة F — تعيين العامل النحوي."""
    factors: List[FactorAssignment] = []
    for role_asgn in state.roles:
        factor, factor_type = _infer_factor(role_asgn, state)
        factors.append(
            FactorAssignment(
                token=role_asgn.token,
                factor=factor,
                factor_type=factor_type,
            )
        )
    state.factors = factors
    state.append_trace(
        PipelineStage.FACTOR,
        input_summary=f"{len(state.roles)} roles",
        output_summary=f"{len(factors)} factor assignments",
    )
    return state


# ── Stage G: Case ──────────────────────────────────────────────────


def resolve_case(state: RuntimeState) -> RuntimeState:
    """المرحلة G — حل الحالة الإعرابية.

    Combines role and factor to determine the final inflectional case
    for each token.
    """
    resolutions: List[CaseResolution] = []
    for role_asgn, factor_asgn in zip(state.roles, state.factors):
        case_state = _resolve_case_from_role_factor(role_asgn.role, factor_asgn.factor)
        resolutions.append(
            CaseResolution(
                token=role_asgn.token,
                role=role_asgn.role,
                factor=factor_asgn.factor,
                case_state=case_state,
                justification=f"{role_asgn.role} + {factor_asgn.factor} → {case_state}",
            )
        )
    state.case_resolutions = resolutions
    state.append_trace(
        PipelineStage.CASE,
        input_summary=f"{len(state.roles)} roles, {len(state.factors)} factors",
        output_summary=f"{len(resolutions)} case resolutions",
    )
    return state


# ── Stage H: Judgement ─────────────────────────────────────────────


def build_judgement(state: RuntimeState) -> RuntimeState:
    """المرحلة H — تكوين الحكم النهائي."""
    prop_type = "تقريرية" if state.utterance_units else "غير محدد"
    state.judgement = JudgementResult(
        proposition_type=prop_type,
        rank="إخبار",
        confidence=1.0,
        details=f"Based on {len(state.case_resolutions)} case resolutions",
    )
    state.append_trace(
        PipelineStage.JUDGEMENT,
        input_summary=f"{len(state.case_resolutions)} cases",
        output_summary=f"judgement: {prop_type}",
    )
    return state


# ── Full pipeline runner ────────────────────────────────────────────

_STAGES = [
    resolve_utterance_units,
    resolve_concepts,
    activate_axes,
    build_relations,
    assign_roles,
    resolve_factors,
    resolve_case,
    build_judgement,
]


def run_pipeline(text: str) -> RuntimeState:
    """تشغيل السلسلة الكاملة — run the full eight-stage pipeline.

    Parameters
    ----------
    text : str
        Raw Arabic input text.

    Returns
    -------
    RuntimeState
        Final state containing all intermediate results and the trace.
    """
    state = RuntimeState(raw_text=text)
    for stage_fn in _STAGES:
        stage_fn(state)
    return state


# ── Internal helpers (heuristic stubs) ──────────────────────────────


def _guess_pattern(token: str) -> str:
    """Heuristic pattern guess for a token."""
    if len(token) == 3:
        return "فَعَلَ"
    if len(token) == 4:
        return "فَعَّلَ"
    return "غير محدد"


def _is_nominal(token: str) -> bool:
    """Heuristic check if a token is nominal."""
    return token.startswith("ال") or token.endswith("ة")


def _resolve_axis(concept: ConceptUnit, axis_name: str) -> str:
    """Resolve a single axis for a concept (stub)."""
    if axis_name == "معرفة/نكرة":
        return "معرفة" if concept.determination_degree == "definite" else "نكرة"
    return "غير محدد"


def _infer_relation(source: UtteranceUnit, target: UtteranceUnit) -> str:
    """Infer the relation type between two adjacent tokens (stub)."""
    if source.syntactic_potential == "verbal" and target.syntactic_potential == "nominal":
        return "إسناد"
    if source.token in ("إلى", "من", "في", "على", "عن", "ب"):
        return "ظرفية"
    return "تقييد"


def _infer_role(unit: UtteranceUnit, position: int, state: RuntimeState) -> str:
    """Infer grammatical role for a token (stub)."""
    if position == 0 and unit.syntactic_potential == "verbal":
        return "فعل"
    if position == 0 and unit.syntactic_potential == "nominal":
        return "مبتدأ"
    if position == 1 and state.utterance_units[0].syntactic_potential == "verbal":
        return "فاعل"
    if position == 1 and state.utterance_units[0].syntactic_potential == "nominal":
        return "خبر"
    if unit.token in ("إلى", "من", "في", "على", "عن", "ب"):
        return "حرف_جر"
    return "مفعول"


def _infer_factor(role_asgn: RoleAssignment, state: RuntimeState) -> tuple[str, str]:
    """Determine the grammatical factor governing a role (stub)."""
    if role_asgn.role == "فعل":
        return ("ذاتي", "فعل")
    if role_asgn.role == "فاعل":
        return (state.utterance_units[0].token if state.utterance_units else "مقدر", "فعل")
    if role_asgn.role == "مبتدأ":
        return ("ابتداء", "عامل_معنوي")
    if role_asgn.role == "خبر":
        return ("ابتداء", "عامل_معنوي")
    if role_asgn.role == "حرف_جر":
        return (role_asgn.token, "حرف_جر")
    return ("مقدر", "عامل_مقدر")


def _resolve_case_from_role_factor(role: str, factor: str) -> str:
    """Resolve the case marker from role + factor (stub)."""
    _ROLE_CASE_MAP = {
        "فاعل": "رفع",
        "مبتدأ": "رفع",
        "خبر": "رفع",
        "مفعول": "نصب",
        "حرف_جر": "مبني",
        "فعل": "مبني",
    }
    return _ROLE_CASE_MAP.get(role, "غير_محدد")
