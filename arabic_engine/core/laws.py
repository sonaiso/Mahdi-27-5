"""Backward-compatibility shim — this module has moved to arabic_engine.formal.

.. deprecated::
    Use ``arabic_engine.formal.laws`` instead.
"""

import arabic_engine.formal.laws as _mod
import sys

sys.modules[__name__] = _mod
