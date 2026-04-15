"""Request schemas — مخططات الطلبات.

Pydantic models for API request bodies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    """Generic text input request."""

    text: str = Field(..., min_length=1, description="Arabic text to analyze")


class TokenRequest(BaseModel):
    """Single token input request."""

    token: str = Field(..., min_length=1, description="Single Arabic token")


class WordRequest(BaseModel):
    """Single word input request."""

    word: str = Field(..., min_length=1, description="Single Arabic word")


class TokensRequest(BaseModel):
    """Multiple tokens input request."""

    tokens: List[str] = Field(..., min_length=1, description="List of Arabic tokens")


class PropositionRequest(BaseModel):
    """Proposition input for cognitive evaluation."""

    subject: str = Field(..., description="Subject of proposition")
    predicate: str = Field(..., description="Predicate of proposition")
    object: Optional[str] = Field(None, description="Object of proposition")
    polarity: bool = Field(True, description="Truth polarity")


class JudgementRequest(BaseModel):
    """Input for judgement evaluation."""

    input: Dict[str, Any] = Field(..., description="Judgement input data")


class PipelineRequest(BaseModel):
    """Full pipeline input request."""

    text: str = Field(..., min_length=1, description="Arabic text for full pipeline analysis")
