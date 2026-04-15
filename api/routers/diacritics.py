"""Diacritics router (E2) — واجهة التشكيل.

Endpoints for diacritical analysis and validation.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.requests import TextRequest
from api.schemas.responses import DiacriticAnalyzeResponse, DiacriticValidateResponse
from arabic_engine.diacritics.analyzer import analyze
from arabic_engine.diacritics.validator import validate

router = APIRouter()


@router.post("/analyze", response_model=DiacriticAnalyzeResponse)
async def analyze_diacritics(req: TextRequest) -> DiacriticAnalyzeResponse:
    """Analyze diacritical marks on an Arabic token."""
    result = analyze(req.text)
    bindings = [
        {
            "base_char": b.base_char,
            "base_index": b.base_index,
            "marks": [{"code_point": m.code_point, "type": m.mark_type.name}
                      for m in b.marks],
            "consistency": b.consistency.name,
            "role": b.role.name,
        }
        for b in result.bindings
    ]
    return DiacriticAnalyzeResponse(
        token=result.token,
        mark_count=result.mark_count,
        is_fully_voweled=result.is_fully_voweled,
        is_partially_voweled=result.is_partially_voweled,
        consistency=result.consistency.name,
        bindings=bindings,
    )


@router.post("/validate", response_model=DiacriticValidateResponse)
async def validate_diacritics(req: TextRequest) -> DiacriticValidateResponse:
    """Validate diacritical consistency on an Arabic token."""
    is_valid, violations = validate(req.text)
    return DiacriticValidateResponse(
        token=req.text,
        is_valid=is_valid,
        violations=violations,
    )
