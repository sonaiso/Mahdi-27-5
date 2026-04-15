"""Pipeline router — واجهة الخط الكامل.

Full pipeline endpoint that runs all layers E1→E8 in sequence.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import PipelineRequest
from api.schemas.responses import PipelineResponse
from arabic_engine.pipeline import run

router = APIRouter()


@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(req: PipelineRequest) -> PipelineResponse:
    """Run the full Arabic Engine pipeline on input text."""
    result = run(req.text)

    # Serialize closures
    closures = [
        {
            "surface": c.surface,
            "lemma": c.lemma,
            "root": list(c.root),
            "pattern": c.pattern,
            "pos": c.pos.name,
            "confidence": c.confidence,
        }
        for c in result.closures
    ]

    # Serialize syntax nodes
    syntax_nodes = [
        {
            "surface": n.surface,
            "case": n.case.name,
            "role": n.role.name,
            "governor": n.governor,
        }
        for n in result.syntax_nodes
    ]

    # Serialize concepts
    concepts = [
        {
            "concept_id": c.concept_id,
            "label": c.label,
            "semantic_type": c.semantic_type.name,
        }
        for c in result.concepts
    ]

    # Serialize dalala links
    dalala_links = [
        {
            "signifier": lnk.signifier,
            "signified": lnk.signified,
            "dalala_type": lnk.dalala_type.name,
            "confidence": lnk.confidence,
            "accepted": lnk.accepted,
        }
        for lnk in result.dalala_links
    ]

    # Proposition
    prop = None
    if result.proposition:
        prop = {
            "subject": result.proposition.subject,
            "predicate": result.proposition.predicate,
            "object": result.proposition.object,
            "polarity": result.proposition.polarity,
        }

    # Time/Space
    ts = None
    if result.time_space:
        ts = {
            "time_ref": result.time_space.time_ref.name,
            "space_ref": result.time_space.space_ref.name,
        }

    # Evaluation
    ev = None
    if result.eval_result:
        ev = {
            "truth_state": result.eval_result.truth_state.name,
            "guidance_state": result.eval_result.guidance_state.name,
            "confidence": result.eval_result.confidence,
        }

    # Inferences
    inferences = [
        {
            "rule": inf.rule,
            "conclusion_subject": inf.conclusion_subject,
            "conclusion_predicate": inf.conclusion_predicate,
            "valid": inf.valid,
            "confidence": inf.confidence,
        }
        for inf in (result.inferences or [])
    ]

    return PipelineResponse(
        tokens=result.tokens,
        closures=closures,
        syntax_nodes=syntax_nodes,
        concepts=concepts,
        dalala_links=dalala_links,
        proposition=prop,
        time_space=ts,
        semantic_roles=result.semantic_roles,
        evaluation=ev,
        inferences=inferences,
        explanation=result.explanation,
    )
