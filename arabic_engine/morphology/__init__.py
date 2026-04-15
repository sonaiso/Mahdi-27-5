"""Morphological Intelligence layer (E4) — الصرف: engine, lexicon, affixes.

Public sub-modules
------------------
* :mod:`arabic_engine.morphology.engine` — Advanced morphological analysis
  engine that builds on the existing signifier layer to provide richer
  root extraction, pattern matching, and feature extraction.
* :mod:`arabic_engine.morphology.lexicon` — Lexicon interface for looking
  up roots, patterns, and base meanings.
* :mod:`arabic_engine.morphology.affixes` — Prefix, suffix, and infix
  stripping and classification for Arabic morphology.
"""

__all__ = [
    "engine",
    "lexicon",
    "affixes",
]
