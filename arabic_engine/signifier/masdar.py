"""Backward-compatibility shim — this module has moved to arabic_engine.morphology.

.. deprecated::
    Use ``arabic_engine.morphology.masdar`` instead.
"""

import arabic_engine.morphology.masdar as _mod
import sys

sys.modules[__name__] = _mod
