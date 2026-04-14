"""Signal processing layer — Unicode atom decomposition and normalization.

Provides the first stage of the Fractal Kernel pipeline: breaking raw
text into typed atoms, normalizing, and producing segmentation candidates.
"""

from arabic_engine.signal.normalization import normalize_atoms as normalize_atoms
from arabic_engine.signal.segmentation import segment as segment
from arabic_engine.signal.unicode_atoms import decompose as decompose

__all__ = ["decompose", "normalize_atoms", "segment"]
