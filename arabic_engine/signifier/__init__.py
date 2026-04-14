"""Signifier layer — الدال: normalisation, phonology, root/pattern, D_min.

Public sub-modules
------------------
* :mod:`arabic_engine.signifier.unicode_norm` — Unicode normalisation and
  tokenisation for Arabic text.
* :mod:`arabic_engine.signifier.phonology` — Phonological analysis:
  consonant/vowel classification and syllabification.
* :mod:`arabic_engine.signifier.root_pattern` — Tri-literal root and
  morphological pattern extraction.
* :mod:`arabic_engine.signifier.dmin` — D_min minimal complete
  phonological model (الأدنى المكتمل).
* :mod:`arabic_engine.signifier.transition` — قانون الانتقال بين الخانات:
  formal cell-transition engine with matrix, stability check, and
  optimality-driven transition solver.
* :mod:`arabic_engine.signifier.functional_transition` — الانتقال الوظيفي
  المنضبط: JSON-Schema-backed functional transition loader, Condition DSL,
  and filter helpers.
"""

__all__ = [
    "unicode_norm",
    "phonology",
    "root_pattern",
    "dmin",
    "transition",
    "functional_transition",
]
