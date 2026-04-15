"""Unified pipeline — orchestrator, hypothesis graph, constraints, element layers.

This package consolidates the execution machinery previously scattered
across ``runtime/``, ``hypothesis/``, ``constraints/``, and ``element_layers/``.

Entry points
------------
* :func:`arabic_engine.pipeline.run` — Main v3 pipeline (convenience re-export).
* :func:`arabic_engine.pipeline.orchestrator.run` — Fractal Kernel pipeline.
* :mod:`arabic_engine.pipeline.hypothesis` — Staged hypothesis generation.
* :mod:`arabic_engine.pipeline.constraints` — Scoring, pruning, propagation, revision.
* :mod:`arabic_engine.pipeline.element_layers` — 7-layer element analysis.
"""

from arabic_engine.main_pipeline import PipelineResult as PipelineResult
from arabic_engine.main_pipeline import run as run
from arabic_engine.main_pipeline import verify_contracts as verify_contracts

__all__ = [
    "PipelineResult",
    "run",
    "verify_contracts",
]
