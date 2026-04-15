"""Backward-compatibility shim — unicode_norm has moved to arabic_engine.signal.

.. deprecated::
    Use ``arabic_engine.signal.unicode_norm`` instead.
"""

from arabic_engine.signal.unicode_norm import *  # noqa: F401, F403
