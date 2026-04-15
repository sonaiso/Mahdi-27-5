"""Backward-compatibility shim — this module has moved to arabic_engine.semantics.

.. deprecated::
    Use ``arabic_engine.semantics.masdar_bridge`` instead.
"""

import arabic_engine.semantics.masdar_bridge as _mod
import sys

sys.modules[__name__] = _mod
