"""Backward-compatibility shim — this module has moved to arabic_engine.pipeline.hypothesis.

.. deprecated::
    Use ``arabic_engine.pipeline.hypothesis.relations`` instead.
"""

import arabic_engine.pipeline.hypothesis.relations as _mod
import sys

sys.modules[__name__] = _mod
