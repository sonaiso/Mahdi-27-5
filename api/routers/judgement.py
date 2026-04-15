"""Judgement router (E8) — واجهة الحكم.

Endpoints for judgement constitution and trace.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import TextRequest
from api.schemas.responses import JudgementResponse
from arabic_engine.cognition.evaluation import build_proposition, evaluate
from arabic_engine.linkage.dalala import full_validation
from arabic_engine.signified.ontology import batch_map
from arabic_engine.signifier.root_pattern import batch_closure
from arabic_engine.signifier.unicode_norm import normalize, tokenize

router = APIRouter()


@router.post("/judge", response_model=JudgementResponse)
async def judge(req: TextRequest) -> JudgementResponse:
    """Produce a judgement with trace for Arabic text."""
    text = normalize(req.text)
    tokens = tokenize(text)
    closures = batch_closure(tokens)
    concepts = batch_map(closures)
    links = full_validation(closures, concepts)
    proposition = build_proposition(closures, concepts, links)
    eval_result = evaluate(proposition, links)

    return JudgementResponse(
        verdict={
            "subject": proposition.subject,
            "predicate": proposition.predicate,
            "truth_state": eval_result.truth_state.name,
            "guidance_state": eval_result.guidance_state.name,
            "confidence": eval_result.confidence,
        },
        trace={
            "tokens": tokens,
            "closure_count": len(closures),
            "concept_count": len(concepts),
            "link_count": len(links),
            "polarity": proposition.polarity,
        },
    )
