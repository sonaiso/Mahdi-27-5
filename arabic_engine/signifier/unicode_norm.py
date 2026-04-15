"""Backward-compatibility shim — unicode_norm has moved to arabic_engine.signal.

.. deprecated::
    Use ``arabic_engine.signal.unicode_norm`` instead.
"""

import arabic_engine.signal.unicode_norm as _mod
import sys

sys.modules[__name__] = _mod
