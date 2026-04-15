"""Backward-compatibility shim — this module has moved to arabic_engine.morphology.

.. deprecated::
    Use ``arabic_engine.morphology.root_pattern`` instead.
"""

import arabic_engine.morphology.root_pattern as _mod
import sys

sys.modules[__name__] = _mod
