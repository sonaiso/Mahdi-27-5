"""Verb Fractal Constitution — دستور الفعل الفراكتالي (v1).

This package formalises the Arabic verb as a fractal epistemic
node.  It provides:

* **bab_registry** — registry of trilateral gates and augmented patterns
* **analyzer** — surface form → VerbProfile
* **threshold** — minimal threshold validation (8 conditions)
* **derivatives** — derivative chain builder
* **nasikh** — nāsikh verb classification
* **fractal_node** — complete fractal node construction
"""

from __future__ import annotations

from .analyzer import (
    analyze as analyze,
)
from .bab_registry import (
    all_mazid_babs as all_mazid_babs,
)
from .bab_registry import (
    all_thulathi_babs as all_thulathi_babs,
)
from .bab_registry import (
    find_bab_by_id as find_bab_by_id,
)
from .bab_registry import (
    get_mazid_bab as get_mazid_bab,
)
from .bab_registry import (
    get_thulathi_bab as get_thulathi_bab,
)
from .bab_registry import (
    lookup_verb as lookup_verb,
)
from .bab_registry import (
    match_pattern as match_pattern,
)
from .derivatives import (
    build as build_derivatives,
)
from .fractal_node import (
    build as build_fractal_node,
)
from .nasikh import (
    all_kada as all_kada,
)
from .nasikh import (
    all_kana as all_kana,
)
from .nasikh import (
    all_zanna as all_zanna,
)
from .nasikh import (
    classify as classify_nasikh,
)
from .nasikh import (
    is_nasikh as is_nasikh,
)
from .threshold import (
    validate as validate_threshold,
)

__all__ = [
    "all_kada",
    "all_kana",
    "all_mazid_babs",
    "all_thulathi_babs",
    "all_zanna",
    "analyze",
    "build_derivatives",
    "build_fractal_node",
    "classify_nasikh",
    "find_bab_by_id",
    "get_mazid_bab",
    "get_thulathi_bab",
    "is_nasikh",
    "lookup_verb",
    "match_pattern",
    "validate_threshold",
]
