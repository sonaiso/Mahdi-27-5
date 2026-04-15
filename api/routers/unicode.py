"""Unicode router (E1) — واجهة اليونيكود.

Endpoints for Unicode normalization and atom analysis.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import TextRequest
from api.schemas.responses import NormalizeResponse, UnicodeAnalyzeResponse
from arabic_engine.signifier.unicode_norm import normalize

router = APIRouter()


@router.post("/normalize", response_model=NormalizeResponse)
async def normalize_text(req: TextRequest) -> NormalizeResponse:
    """Normalize Arabic text (NFC, remove tatweel, collapse whitespace)."""
    result = normalize(req.text)
    return NormalizeResponse(
        normalized=result,
        original_length=len(req.text),
        normalized_length=len(result),
    )


@router.post("/analyze", response_model=UnicodeAnalyzeResponse)
async def analyze_unicode(req: TextRequest) -> UnicodeAnalyzeResponse:
    """Analyze Unicode code points and structure of Arabic text."""
    atoms = [
        {"char": ch, "code_point": ord(ch), "name": _char_name(ch)}
        for ch in req.text
    ]
    return UnicodeAnalyzeResponse(
        text=req.text,
        atoms=atoms,
        code_points=[ord(ch) for ch in req.text],
    )


def _char_name(ch: str) -> str:
    """Return the Unicode name for a character, or 'UNKNOWN'."""
    import unicodedata

    try:
        return unicodedata.name(ch)
    except ValueError:
        return "UNKNOWN"
