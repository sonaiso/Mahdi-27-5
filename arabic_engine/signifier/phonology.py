"""Backward-compatibility shim — this module has moved to arabic_engine.morphology.

.. deprecated::
    Use ``arabic_engine.morphology.phonology`` instead.
"""

import arabic_engine.morphology.phonology as _mod
import sys

sys.modules[__name__] = _mod
