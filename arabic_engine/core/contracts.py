"""Backward-compatibility shim — this module has moved to arabic_engine.validation.

.. deprecated::
    Use ``arabic_engine.validation.contracts`` instead.
"""

from arabic_engine.validation.contracts import *  # noqa: F401, F403
from arabic_engine.validation.contracts import _load_contracts  # noqa: F401
