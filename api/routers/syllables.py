"""Syllables router (E3) — واجهة المقاطع.

Endpoints for syllable segmentation and validation.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import WordRequest
from api.schemas.responses import SyllableSegmentResponse, SyllableValidateResponse
from arabic_engine.syllables.segmenter import segment
from arabic_engine.syllables.validator import validate_analysis

router = APIRouter()


@router.post("/segment", response_model=SyllableSegmentResponse)
async def segment_syllables(req: WordRequest) -> SyllableSegmentResponse:
    """Segment an Arabic word into phonological syllables."""
    result = segment(req.word)
    syllables = [
        {
            "onset": s.onset,
            "nucleus": s.nucleus,
            "coda": s.coda,
            "type": s.syllable_type.name,
            "weight": s.weight.name,
            "text": s.text,
        }
        for s in result.pattern.syllables
    ]
    return SyllableSegmentResponse(
        word=result.word,
        pattern=result.pattern.pattern,
        syllable_count=len(result.pattern.syllables),
        mora_count=result.mora_count,
        is_valid=result.is_valid,
        syllables=syllables,
    )


@router.post("/validate", response_model=SyllableValidateResponse)
async def validate_syllables(req: WordRequest) -> SyllableValidateResponse:
    """Validate syllable structure of an Arabic word."""
    analysis = segment(req.word)
    is_valid, violations = validate_analysis(analysis)
    return SyllableValidateResponse(
        word=req.word,
        is_valid=is_valid,
        violations=violations,
    )
