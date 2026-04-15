"""Signal processing layer — Unicode atom decomposition and normalization.

Provides the first stage of the Fractal Kernel pipeline: breaking raw
text into typed atoms, normalizing, and producing segmentation candidates.

Since v3, this package also owns low-level Unicode normalisation and
tokenisation (moved from ``signifier.unicode_norm``).
"""

from arabic_engine.signal.normalization import normalize_atoms as normalize_atoms
from arabic_engine.signal.segmentation import segment as segment
from arabic_engine.signal.unicode_atoms import decompose as decompose
from arabic_engine.signal.unicode_norm import normalize as normalize
from arabic_engine.signal.unicode_norm import tokenize as tokenize

__all__ = ["decompose", "normalize", "normalize_atoms", "segment", "tokenize"]
