"""Backward-compatibility shim — this module has moved to arabic_engine.pipeline.element_layers.

.. deprecated::
    Use ``arabic_engine.pipeline.element_layers.layer2_auditory`` instead.
"""

import arabic_engine.pipeline.element_layers.layer2_auditory as _mod
import sys

sys.modules[__name__] = _mod
