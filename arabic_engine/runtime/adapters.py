"""Backward-compatibility shim — this module has moved to arabic_engine.pipeline.

.. deprecated::
    Use ``arabic_engine.pipeline.adapters`` instead.
"""

import arabic_engine.pipeline.adapters as _mod
import sys

sys.modules[__name__] = _mod
