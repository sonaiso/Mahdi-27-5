"""Main pipeline — orchestrates all layers of the Arabic engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from arabic_engine.cognition.epistemic_v1 import validate_episode
from arabic_engine.cognition.evaluation import build_proposition, evaluate
from arabic_engine.cognition.explanation import build_explanation
from arabic_engine.cognition.inference_rules import InferenceEngine
from arabic_engine.cognition.time_space import tag as time_space_tag
from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.contracts import verify_contracts  # noqa: F401 — re-export
from arabic_engine.core.enums import (
    CarrierType,
    JudgementType,
    LinkKind,
    MethodFamily,
    ProofPathKind,
    RealityKind,
    SenseModality,
    TraceMode,
    ValidationOutcome,
    ValidationState,
)
from arabic_engine.core.types import (
    Concept,
    ConceptNode,
    ConceptRecord,
    ConflictRuleRecord,
    DalalaLink,
    DirectionAssignment,
    EvalResult,
    EvaluationResult,
    InferenceResult,
    JudgementRecord,
    KnowledgeEpisode,
    KnowledgeEpisodeInput,
    LayerTraceRecord,
    LexicalClosure,
    LinguisticCarrierRecord,
    LinkingTraceRecord,
    LinkOperation,
    MethodRecord,
    PerceptTrace,
    PriorInfoRecord,
    PriorKnowledgeUnit,
    ProofPathRecord,
    Proposition,
    RealityAnchorRecord,
    SenseTraceRecord,
    SyntaxNode,
    TimeSpaceTag,
    UtteranceRecord,
    WeightFractalResult,
)
from arabic_engine.linkage.dalala import full_validation
from arabic_engine.linkage.semantic_roles import derive_semantic_roles
from arabic_engine.signified.ontology import batch_map
from arabic_engine.signified.semantic_direction import (
    assign_direction as _assign_direction,
)
from arabic_engine.signified.semantic_direction import (
    build_direction_space,
)
from arabic_engine.signifier.root_pattern import batch_closure
from arabic_engine.signifier.unicode_norm import normalize, tokenize
from arabic_engine.signifier.weight_fractal import (
    run_weight_fractal as _run_weight_fractal,
)
from arabic_engine.syntax.syntax import analyse as syntax_analyse

# ── Pipeline result ─────────────────────────────────────────────────

@dataclass
class PipelineResult:
    """Container for the full analysis of a single sentence."""

    raw: str
    normalised: str
    tokens: List[str]
    closures: List[LexicalClosure]
    syntax_nodes: List[SyntaxNode]
    concepts: List[Concept]
    dalala_links: List[DalalaLink]
    proposition: Proposition
    time_space: TimeSpaceTag
    eval_result: EvalResult
    percept_trace: PerceptTrace
    prior_knowledge: List[PriorKnowledgeUnit]
    link_operations: List[LinkOperation]
    concept_nodes: List[ConceptNode]
    semantic_roles: Dict[str, str]
    knowledge_episode: KnowledgeEpisode
    evaluation_result: EvaluationResult
    inferences: List[InferenceResult] = field(default_factory=list)
    world_adjustment: float = 0.5
    world_update: Dict[str, object] = field(default_factory=dict)
    explanation: Dict[str, object] = field(default_factory=dict)
    layer_traces: List[LayerTraceRecord] = field(default_factory=list)
    direction_assignments: List[DirectionAssignment] = field(default_factory=list)
    weight_fractals: List[WeightFractalResult] = field(default_factory=list)


def _to_validation_state(outcome: ValidationOutcome) -> ValidationState:
    if outcome == ValidationOutcome.VALID:
        return ValidationState.VALID
    if outcome == ValidationOutcome.PENDING:
        return ValidationState.PENDING
    return ValidationState.INVALID


def _build_knowledge_episode(
    text: str,
    proposition: Proposition,
    semantic_roles: Dict[str, str],
) -> KnowledgeEpisode:
    judgement_type = (
        JudgementType.EXISTENCE
        if proposition.predicate is not None and proposition.predicate != ""
        else JudgementType.INTERPRETIVE
    )
    reality_anchor = RealityAnchorRecord(
        anchor_id="RA_pipeline",
        kind=RealityKind.MATERIAL,
        description=f"Sentence reality anchor from input: {text}",
    )
    sense_trace = SenseTraceRecord(
        trace_id="ST_pipeline",
        modality=SenseModality.VISUAL,
        mode=TraceMode.DIRECT,
        description="Direct textual perception from input sentence.",
    )
    prior_infos = (
        PriorInfoRecord(
            info_id="PI_pipeline_syntax",
            content=f"Semantic roles observed: {semantic_roles}",
            source="pipeline.syntax.semantic_roles",
        ),
    )
    linking_trace = LinkingTraceRecord(
        link_id="LT_pipeline",
        kind=LinkKind.CONTEXTUAL,
        description="Linked morphology + syntax + dalala into proposition.",
    )
    judgement = JudgementRecord(
        judgement_id="JD_pipeline",
        judgement_type=judgement_type,
        content=(
            f"subject={proposition.subject};"
            f"predicate={proposition.predicate};"
            f"object={proposition.obj}"
        ),
    )
    method = MethodRecord(
        method_id="M_pipeline",
        family=MethodFamily.RATIONAL,
        name="Pipeline Rational Method",
        domain_fit=(
            JudgementType.EXISTENCE,
            JudgementType.ESSENCE,
            JudgementType.ATTRIBUTE,
            JudgementType.RELATION,
            JudgementType.INTERPRETIVE,
        ),
    )
    carrier = LinguisticCarrierRecord(
        carrier_id="LC_pipeline",
        carrier_type=CarrierType.BOTH,
        utterance=UtteranceRecord(utterance_id="UT_pipeline", text=text),
        concept=ConceptRecord(concept_record_id="CR_pipeline", label=text),
    )
    proof_path = ProofPathRecord(
        path_id="PP_pipeline",
        kind=ProofPathKind.DIRECT_PROOF,
        steps=("normalize", "morphology", "syntax", "dalala", "judgement"),
        method_fit=MethodFamily.RATIONAL,
    )
    conflict_rule = ConflictRuleRecord(
        rule_id="CF_pipeline_default",
        prefer_concept=True,
        rationale="Prefer concept when utterance/concept mismatch appears.",
    )
    return KnowledgeEpisode(
        episode_id="KE_pipeline",
        reality_anchor=reality_anchor,
        sense_trace=sense_trace,
        prior_infos=prior_infos,
        opinion_traces=(),
        linking_trace=linking_trace,
        judgement=judgement,
        method=method,
        carrier=carrier,
        proof_path=proof_path,
        conflict_rule=conflict_rule,
    )


# ── Pipeline ────────────────────────────────────────────────────────

def run(
    text: str,
    *,
    world: Optional[WorldModel] = None,
    inference_engine: Optional[InferenceEngine] = None,
    analyze_layers: bool = False,
) -> PipelineResult:
    """Execute the full v3 pipeline on *text*."""
    # L0 — Normalise
    normalised = normalize(text)

    # L1 — Tokenize
    tokens = tokenize(text)

    # L2 — Lexical Closure
    closures = batch_closure(tokens)

    # L2b — Optional strict 7-layer element analysis
    layer_traces: List[LayerTraceRecord] = []
    if analyze_layers:
        from arabic_engine.layers.layer_pipeline import analyze_word as _analyze_word
        from arabic_engine.signifier.root_pattern import extract_root_pattern

        for closure in closures:
            rp = extract_root_pattern(closure.surface)
            traces = _analyze_word(closure.surface, root_pattern=rp)
            layer_traces.extend(traces)

    # L3 — Syntax (v2)
    syntax_nodes = syntax_analyse(closures)

    # L3b — Semantic Direction Assignment
    _direction_space = build_direction_space()
    direction_assignments = [_assign_direction(cl, _direction_space) for cl in closures]

    # L3c — Weight Fractal Analysis
    weight_fractals = [_run_weight_fractal(cl) for cl in closures]

    # L4 — Ontological Mapping
    concepts = batch_map(closures)

    # L5 — Dalāla Validation
    links = full_validation(closures, concepts)

    # L6 — Judgment
    proposition = build_proposition(closures, concepts, links)

    # L7 — Time/Space (v2)
    ts_tag = time_space_tag(closures, proposition)

    # L7b — Semantic roles
    semantic_roles = derive_semantic_roles(closures, syntax_nodes)

    # L8 — Evaluation
    eval_result = evaluate(proposition, links)

    # L8b — Build epistemic knowledge episode
    episode = _build_knowledge_episode(text, proposition, semantic_roles)
    episode_input = KnowledgeEpisodeInput(
        episode_id=episode.episode_id,
        reality_anchor=episode.reality_anchor,
        sense_trace=episode.sense_trace,
        prior_infos=episode.prior_infos,
        opinion_traces=episode.opinion_traces,
        linking_trace=episode.linking_trace,
        judgement=episode.judgement,
        method=episode.method,
        carrier=episode.carrier,
        proof_path=episode.proof_path,
        conflict_rule=episode.conflict_rule,
    )
    validation = validate_episode(episode_input)
    validation_state = _to_validation_state(validation.outcome)
    evaluation_result = EvaluationResult(
        truth_state=eval_result.truth_state,
        epistemic_rank=validation.rank,
        confidence=eval_result.confidence,
        validation_state=validation_state,
        consistency="; ".join(validation.messages),
    )

    # L9 — Inference (v2)
    inferences: List[InferenceResult] = []
    if inference_engine is not None:
        inferences = inference_engine.run([proposition])

    # L10 — World-Model adjustment (v2)
    adjustment = 0.5
    world_update: Dict[str, object] = {
        "applied": False,
        "reason": "no_world_model",
        "fact_id": None,
    }
    if world is not None:
        adjustment = world.confidence_adjustment(proposition)
        # Blend world-model confidence with dalāla confidence
        eval_result.confidence = round(
            eval_result.confidence * adjustment, 4
        )
        evaluation_result = EvaluationResult(
            truth_state=evaluation_result.truth_state,
            epistemic_rank=evaluation_result.epistemic_rank,
            confidence=eval_result.confidence,
            validation_state=evaluation_result.validation_state,
            consistency=evaluation_result.consistency,
        )
        world_update = world.apply_validated_proposition(
            proposition,
            validation_state=evaluation_result.validation_state,
            source="pipeline.v3",
        )

    explanation = build_explanation(
        proposition=proposition,
        semantic_roles=semantic_roles,
        evaluation=evaluation_result,
        inferences=inferences,
        world_update=world_update,
    )

    link_operations = [
        LinkOperation(
            operation_id=f"LO_{idx}",
            operation_type=link.dalala_type,
            source=link.source_lemma,
            target=str(link.target_concept_id),
            accepted=link.accepted,
            confidence=link.confidence,
        )
        for idx, link in enumerate(links, start=1)
    ]
    concept_nodes = [
        ConceptNode(
            concept_id=f"C_{concept.concept_id}",
            label=concept.label,
            semantic_type=concept.semantic_type,
            properties=concept.properties,
        )
        for concept in concepts
    ]
    prior_knowledge = [
        PriorKnowledgeUnit(
            unit_id=f"PK_{idx}",
            content=f"Token '{cl.surface}' -> lemma '{cl.lemma}'",
            source="lexical_closure",
            weight=cl.confidence,
        )
        for idx, cl in enumerate(closures, start=1)
    ]
    percept_trace = PerceptTrace(
        raw_text=text,
        normalized_text=normalised,
        tokens=tuple(tokens),
        trace_quality=1.0 if tokens else 0.0,
    )

    return PipelineResult(
        raw=text,
        normalised=normalised,
        tokens=tokens,
        closures=closures,
        syntax_nodes=syntax_nodes,
        concepts=concepts,
        dalala_links=links,
        proposition=proposition,
        time_space=ts_tag,
        eval_result=eval_result,
        percept_trace=percept_trace,
        prior_knowledge=prior_knowledge,
        link_operations=link_operations,
        concept_nodes=concept_nodes,
        semantic_roles=semantic_roles,
        knowledge_episode=episode,
        evaluation_result=evaluation_result,
        inferences=inferences,
        world_adjustment=adjustment,
        world_update=world_update,
        explanation=explanation,
        layer_traces=layer_traces,
        direction_assignments=direction_assignments,
        weight_fractals=weight_fractals,
    )
