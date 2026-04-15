"""Syntax router (E5) — واجهة النحو.

Endpoints for syntactic parsing and i'rāb analysis.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import TextRequest
from api.schemas.responses import SyntaxIrabResponse, SyntaxParseResponse
from arabic_engine.signifier.root_pattern import batch_closure
from arabic_engine.signifier.unicode_norm import normalize, tokenize
from arabic_engine.syntax.syntax import analyse

router = APIRouter()


@router.post("/parse", response_model=SyntaxParseResponse)
async def parse_syntax(req: TextRequest) -> SyntaxParseResponse:
    """Parse syntactic structure of Arabic text."""
    text = normalize(req.text)
    tokens = tokenize(text)
    closures = batch_closure(tokens)
    nodes = analyse(closures)
    return SyntaxParseResponse(
        tokens=tokens,
        nodes=[
            {
                "surface": n.surface,
                "case": n.case.name,
                "role": n.role.name,
                "governor": n.governor,
            }
            for n in nodes
        ],
    )


@router.post("/irab", response_model=SyntaxIrabResponse)
async def analyze_irab(req: TextRequest) -> SyntaxIrabResponse:
    """Analyze i'rāb (grammatical case marking) of Arabic text."""
    text = normalize(req.text)
    tokens = tokenize(text)
    closures = batch_closure(tokens)
    nodes = analyse(closures)
    return SyntaxIrabResponse(
        tokens=tokens,
        irab=[
            {
                "token": n.surface,
                "case": n.case.name,
                "role": n.role.name,
            }
            for n in nodes
        ],
    )
