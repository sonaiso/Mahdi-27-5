"""Morphology router (E4) — واجهة الصرف.

Endpoints for morphological analysis and root lookup.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import TokenRequest
from api.schemas.responses import MorphologyAnalyzeResponse, RootLookupResponse
from arabic_engine.morphology.engine import analyze
from arabic_engine.morphology.lexicon import lookup_root

router = APIRouter()


@router.post("/analyze", response_model=MorphologyAnalyzeResponse)
async def analyze_morphology(req: TokenRequest) -> MorphologyAnalyzeResponse:
    """Perform full morphological analysis on an Arabic token."""
    result = analyze(req.token)
    morphemes = [
        {
            "text": m.text,
            "type": m.morpheme_type.name,
            "features": list(m.features),
            "position": m.position,
        }
        for m in result["morphemes"]
    ]
    affix = result["affix_set"]
    return MorphologyAnalyzeResponse(
        token=req.token,
        root=list(result["root"]),
        pattern=result["pattern"],
        pos=result["pos"].name,
        morphemes=morphemes,
        affix_set={
            "prefixes": list(affix.prefixes),
            "suffixes": list(affix.suffixes),
            "infixes": list(affix.infixes),
        },
    )


@router.post("/root", response_model=RootLookupResponse)
async def lookup_root_endpoint(req: TokenRequest) -> RootLookupResponse:
    """Look up a root in the morphological lexicon."""
    root = tuple(req.token)
    entry = lookup_root(root)
    if entry:
        return RootLookupResponse(
            root=list(entry.root),
            found=True,
            patterns=list(entry.patterns),
            base_meaning=entry.base_meaning,
        )
    return RootLookupResponse(
        root=list(root),
        found=False,
    )
