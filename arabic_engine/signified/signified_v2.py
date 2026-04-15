"""Backward-compatibility shim — this module has moved to arabic_engine.semantics.

.. deprecated::
    Use ``arabic_engine.semantics.signified_v2`` instead.
"""

import arabic_engine.semantics.signified_v2 as _mod
import sys

sys.modules[__name__] = _mod
