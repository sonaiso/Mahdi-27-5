"""Backward-compatibility shim — this module has moved to arabic_engine.pipeline.hypothesis.

.. deprecated::
    Use ``arabic_engine.pipeline.hypothesis.morphology`` instead.
"""

import arabic_engine.pipeline.hypothesis.morphology as _mod
import sys

sys.modules[__name__] = _mod
