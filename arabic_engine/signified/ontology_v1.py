"""Backward-compatibility shim — this module has moved to arabic_engine.semantics.

.. deprecated::
    Use ``arabic_engine.semantics.ontology_v1`` instead.
"""

import arabic_engine.semantics.ontology_v1 as _mod
import sys

sys.modules[__name__] = _mod
