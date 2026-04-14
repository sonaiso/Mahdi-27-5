"""arabic_engine — Arabic Computational Language Engine.

حزمة المحرك العربي للتحليل اللغوي الحاسوبي.

This package implements a full computational Arabic language analysis
pipeline based on the *Atomic Beginning Law* (قانون البداية الذرية)
and *Ascending Closure* (الإغلاق الصاعد).  Every linguistic structure
is encoded as a discrete, numerically representable object, making the
complete composition a computable function over ℕ.

Architecture overview
---------------------
The engine is organised into five vertical layers:

* **Signifier** (``arabic_engine.signifier``) — Unicode normalisation,
  phonological analysis (D_min model), root/pattern extraction.
* **Signified** (``arabic_engine.signified``) — Ontological mapping of
  lexical entries to typed concept nodes.
* **Linkage** (``arabic_engine.linkage``) — Dalāla (signification)
  validation: mutābaqa, taḍammun, iltizām, isnād.
* **Syntax** (``arabic_engine.syntax``) — Heuristic i'rāb (case/role)
  assignment and dependency relations.
* **Cognition** (``arabic_engine.cognition``) — Proposition building,
  truth/guidance evaluation, time/space tagging, inference, world model.

The ``arabic_engine.pipeline.run`` function composes all layers into a
single callable that accepts raw Arabic text and returns a
:class:`~arabic_engine.pipeline.PipelineResult`.

Quick start
-----------
>>> from arabic_engine.pipeline import run
>>> result = run("كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ")
>>> result.proposition.subject
'زَيْد'

See Also
--------
* ``arabic_engine.pipeline`` — top-level pipeline entry-point.
* ``arabic_engine.signifier.dmin`` — D_min phonological model.
* ``arabic_engine.cognition.mafhum`` — Mafhūm (implied meaning) analysis.
* ``arabic_engine.closure`` — General Closure (Ch. 19) verification.
"""

from __future__ import annotations

__version__ = "2.0.0"
__all__ = ["__version__"]
