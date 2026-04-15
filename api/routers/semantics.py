"""Semantics router (E6) — واجهة الدلالة.

Endpoints for semantic mapping and dalāla analysis.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import TextRequest
from api.schemas.responses import DalalaResponse, SemanticMapResponse
from arabic_engine.linkage.dalala import full_validation
from arabic_engine.signified.ontology import batch_map
from arabic_engine.signifier.root_pattern import batch_closure
from arabic_engine.signifier.unicode_norm import normalize, tokenize

router = APIRouter()


@router.post("/map", response_model=SemanticMapResponse)
async def map_semantics(req: TextRequest) -> SemanticMapResponse:
    """Map Arabic tokens to semantic concepts."""
    text = normalize(req.text)
    tokens = tokenize(text)
    closures = batch_closure(tokens)
    concepts = batch_map(closures)
    return SemanticMapResponse(
        concepts=[
            {
                "concept_id": c.concept_id,
                "label": c.label,
                "semantic_type": c.semantic_type.name,
            }
            for c in concepts
        ],
        links=[],
    )


@router.post("/dalala", response_model=DalalaResponse)
async def analyze_dalala(req: TextRequest) -> DalalaResponse:
    """Analyze dalāla (signification) links."""
    text = normalize(req.text)
    tokens = tokenize(text)
    closures = batch_closure(tokens)
    concepts = batch_map(closures)
    links = full_validation(closures, concepts)
    return DalalaResponse(
        links=[
            {
                "signifier": lnk.signifier,
                "signified": lnk.signified,
                "dalala_type": lnk.dalala_type.name,
                "confidence": lnk.confidence,
                "accepted": lnk.accepted,
            }
            for lnk in links
        ],
    )
