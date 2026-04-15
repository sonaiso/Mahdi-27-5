"""Backward-compatibility shim — this module has moved to arabic_engine.validation.

.. deprecated::
    Use ``arabic_engine.validation.contracts`` instead.
"""

import arabic_engine.validation.contracts as _mod
import sys

sys.modules[__name__] = _mod
