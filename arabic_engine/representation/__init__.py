"""arabic_engine.representation — Fractal Representation layer.

This sub-package implements the Fractal Representation Spec v1 (FRS-v1),
which is the first derived specification of the Fractal Core Constitution
(FCC-v1).

Public API
----------
The primary entry-point is
:mod:`arabic_engine.representation.fractal_rep_spec`.
"""

from __future__ import annotations

from arabic_engine.representation.fractal_rep_spec import (
    FractalOrigin as FractalOrigin,
)
from arabic_engine.representation.fractal_rep_spec import (
    FractalRepresentation as FractalRepresentation,
)
from arabic_engine.representation.fractal_rep_spec import (
    LayerTrace as LayerTrace,
)
from arabic_engine.representation.fractal_rep_spec import (
    RepresentationFormat as RepresentationFormat,
)
from arabic_engine.representation.fractal_rep_spec import (
    RepresentationMode as RepresentationMode,
)
from arabic_engine.representation.fractal_rep_spec import (
    build_fractal_representation as build_fractal_representation,
)
from arabic_engine.representation.fractal_rep_spec import (
    validate_fractal_origin as validate_fractal_origin,
)

__all__ = [
    "FractalOrigin",
    "FractalRepresentation",
    "LayerTrace",
    "RepresentationFormat",
    "RepresentationMode",
    "build_fractal_representation",
    "validate_fractal_origin",
]
