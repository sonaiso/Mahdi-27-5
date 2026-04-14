"""Noun Fractal Constitution (دستور الاسم الفراكتالي v1).

The noun subsystem implements the 12 major facets (جهات) that together
establish the noun as the primary epistemological vessel for fixing
existence, differentiation, and classification before composition.

Public API
----------
classify_noun           master classifier — runs all facet resolvers
validate_noun_completeness  minimum-complete-threshold check
run_noun_fractal        execute the 6-stage fractal cycle
build_noun_signification  build mutābaqa / taḍammun / iltizām
"""

from __future__ import annotations

from arabic_engine.noun.constitution import classify_noun, validate_noun_completeness
from arabic_engine.noun.fractal import run_noun_fractal
from arabic_engine.noun.signification import build_noun_signification

__all__ = [
    "classify_noun",
    "validate_noun_completeness",
    "run_noun_fractal",
    "build_noun_signification",
]
