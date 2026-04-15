"""Backward-compatibility shim — this module has moved to arabic_engine.pipeline.constraints.

.. deprecated::
    Use ``arabic_engine.pipeline.constraints.scoring`` instead.
"""

import arabic_engine.pipeline.constraints.scoring as _mod
import sys

sys.modules[__name__] = _mod
