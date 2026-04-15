"""Response schemas — مخططات الاستجابات.

Pydantic models for API response bodies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NormalizeResponse(BaseModel):
    """Response for Unicode normalization."""

    normalized: str
    original_length: int
    normalized_length: int


class UnicodeAnalyzeResponse(BaseModel):
    """Response for Unicode analysis."""

    text: str
    atoms: List[Dict[str, Any]]
    code_points: List[int]


class DiacriticAnalyzeResponse(BaseModel):
    """Response for diacritical analysis."""

    token: str
    mark_count: int
    is_fully_voweled: bool
    is_partially_voweled: bool
    consistency: str
    bindings: List[Dict[str, Any]]


class DiacriticValidateResponse(BaseModel):
    """Response for diacritical validation."""

    token: str
    is_valid: bool
    violations: List[str]


class SyllableSegmentResponse(BaseModel):
    """Response for syllable segmentation."""

    word: str
    pattern: str
    syllable_count: int
    mora_count: int
    is_valid: bool
    syllables: List[Dict[str, Any]]


class SyllableValidateResponse(BaseModel):
    """Response for syllable validation."""

    word: str
    is_valid: bool
    violations: List[str]


class MorphologyAnalyzeResponse(BaseModel):
    """Response for morphological analysis."""

    token: str
    root: List[str]
    pattern: str
    pos: str
    morphemes: List[Dict[str, Any]]
    affix_set: Dict[str, Any]


class RootLookupResponse(BaseModel):
    """Response for root lookup."""

    root: List[str]
    found: bool
    patterns: List[str] = Field(default_factory=list)
    base_meaning: str = ""


class SyntaxParseResponse(BaseModel):
    """Response for syntax parsing."""

    tokens: List[str]
    nodes: List[Dict[str, Any]]


class SyntaxIrabResponse(BaseModel):
    """Response for i'rāb analysis."""

    tokens: List[str]
    irab: List[Dict[str, Any]]


class SemanticMapResponse(BaseModel):
    """Response for semantic mapping."""

    concepts: List[Dict[str, Any]]
    links: List[Dict[str, Any]]


class DalalaResponse(BaseModel):
    """Response for dalāla analysis."""

    links: List[Dict[str, Any]]


class CognitionEvaluateResponse(BaseModel):
    """Response for cognitive evaluation."""

    truth_state: str
    guidance_state: str
    confidence: float
    inferences: List[Dict[str, Any]]


class JudgementResponse(BaseModel):
    """Response for judgement."""

    verdict: Dict[str, Any]
    trace: Dict[str, Any]


class PipelineResponse(BaseModel):
    """Response for full pipeline analysis."""

    tokens: List[str]
    closures: List[Dict[str, Any]]
    syntax_nodes: List[Dict[str, Any]]
    concepts: List[Dict[str, Any]]
    dalala_links: List[Dict[str, Any]]
    proposition: Optional[Dict[str, Any]] = None
    time_space: Optional[Dict[str, Any]] = None
    semantic_roles: Optional[Dict[str, Any]] = None
    evaluation: Optional[Dict[str, Any]] = None
    inferences: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    error_code: str = "ANALYSIS_ERROR"
