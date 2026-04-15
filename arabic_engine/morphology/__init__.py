"""Morphology layer — الصرف: root/pattern extraction, phonology, D_min, masdar.

This package consolidates morphological analysis modules previously
located under ``arabic_engine.signifier/`` (excluding Unicode
normalisation, which now lives in ``arabic_engine.signal``).

Public sub-modules
------------------
* :mod:`~arabic_engine.morphology.root_pattern` — Tri-literal root and
  morphological pattern extraction.
* :mod:`~arabic_engine.morphology.phonology` — Phonological analysis:
  consonant/vowel classification and syllabification.
* :mod:`~arabic_engine.morphology.dmin` — D_min minimal complete
  phonological model (الأدنى المكتمل).
* :mod:`~arabic_engine.morphology.masdar` — Masdar (verbal noun) analysis.
* :mod:`~arabic_engine.morphology.aeu` — Atomic Epistemic Unit builder.
* :mod:`~arabic_engine.morphology.transition` — Cell-transition engine.
* :mod:`~arabic_engine.morphology.functional_transition` — Functional
  transition loader and condition DSL.
"""

__all__ = [
    "aeu",
    "dmin",
    "functional_transition",
    "masdar",
    "phonology",
    "root_pattern",
    "transition",
]
