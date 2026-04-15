"""Diacritic Logic layer (E2) — التشكيل: analysis, validation, and rules.

Public sub-modules
------------------
* :mod:`arabic_engine.diacritics.analyzer` — Decompose a token into its
  diacritical marks with type and position classification.
* :mod:`arabic_engine.diacritics.validator` — Validate diacritical
  consistency (no conflicting marks on one consonant, etc.).
* :mod:`arabic_engine.diacritics.rules` — Rule functions that bind
  each diacritical mark to its base consonant and classify its role.
"""

__all__ = [
    "analyzer",
    "validator",
    "rules",
]
