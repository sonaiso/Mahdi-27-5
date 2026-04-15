"""Syllabic Formation layer (E3) — المقاطع: segmentation, validation, patterns.

Public sub-modules
------------------
* :mod:`arabic_engine.syllables.segmenter` — Segment an Arabic word into
  phonological syllables (CV / CVC / CVV / CVVC / CVCC).
* :mod:`arabic_engine.syllables.validator` — Validate syllable legality
  according to Arabic phonotactic constraints.
* :mod:`arabic_engine.syllables.patterns` — Syllable pattern definitions
  and weight classification for Arabic phonology.
"""

__all__ = [
    "segmenter",
    "validator",
    "patterns",
]
