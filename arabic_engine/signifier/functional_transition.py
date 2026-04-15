"""Backward-compatibility shim — this module has moved to arabic_engine.morphology.

.. deprecated::
    Use ``arabic_engine.morphology.functional_transition`` instead.
"""

import arabic_engine.morphology.functional_transition as _mod
import sys

sys.modules[__name__] = _mod
