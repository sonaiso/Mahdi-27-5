"""Backward-compatibility shim — this module has moved to arabic_engine.pipeline.element_layers.

.. deprecated::
    Use ``arabic_engine.pipeline.element_layers.layer4_transformation`` instead.
"""

import arabic_engine.pipeline.element_layers.layer4_transformation as _mod
import sys

sys.modules[__name__] = _mod
