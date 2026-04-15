"""Backward-compatibility shim — layers has been renamed to element_layers.

.. deprecated::
    Use ``arabic_engine.element_layers`` instead.
"""

import warnings as _warnings  # noqa: E402

_warnings.warn(
    "arabic_engine.layers has been renamed to arabic_engine.element_layers. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

from arabic_engine.element_layers import *  # noqa: E402, F401, F403
