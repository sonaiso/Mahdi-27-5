"""Signifier layer — backward-compatibility shims.

.. deprecated::
    Modules have moved:

    * ``unicode_norm`` → :mod:`arabic_engine.signal.unicode_norm`
    * ``phonology``, ``root_pattern``, ``dmin``, ``masdar``, ``aeu``,
      ``transition``, ``functional_transition`` → :mod:`arabic_engine.morphology`

    Import from the new locations instead.
"""

__all__ = [
    "unicode_norm",
    "phonology",
    "root_pattern",
    "dmin",
    "transition",
    "functional_transition",
]
