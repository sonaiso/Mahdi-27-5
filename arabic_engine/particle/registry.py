"""Particle registry — السجل المركزي للحروف.

Loads the canonical particle catalog from ``data/particle_catalog.json``
and provides lookup, classification, and membership queries.

This module **replaces** all scattered ``frozenset`` definitions that
were previously duplicated across ``hypothesis/roles.py``,
``hypothesis/factors.py``, ``hypothesis/relations.py``,
``hypothesis/judgements.py``, and ``hypothesis/axes.py``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from arabic_engine.core.enums import ParticleRelationType, ParticleType
from arabic_engine.core.types import ParticleRecord

_CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "particle_catalog.json"

# ── Catalog loading ─────────────────────────────────────────────────


@lru_cache(maxsize=1)
def load_catalog() -> Dict[str, ParticleRecord]:
    """Load the particle catalog and return a dict keyed by surface form.

    Returns
    -------
    dict[str, ParticleRecord]
        Mapping from particle surface form to its record.
    """
    with open(_CATALOG_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)

    catalog: Dict[str, ParticleRecord] = {}
    for entry in raw:
        record = ParticleRecord(
            form=entry["form"],
            particle_type=ParticleType[entry["particle_type"]],
            relation_type=ParticleRelationType[entry["relation_type"]],
            scope=entry["scope"],
            direction=entry["direction"],
            effect=entry["effect"],
        )
        catalog[record.form] = record
    return catalog


# ── Public API ──────────────────────────────────────────────────────


def lookup(form: str) -> Optional[ParticleRecord]:
    """Look up a particle by its surface form.

    Parameters
    ----------
    form : str
        The surface form (e.g. ``"في"``, ``"من"``, ``"هل"``).

    Returns
    -------
    ParticleRecord | None
        The particle record, or ``None`` if not found.
    """
    return load_catalog().get(form)


def classify(form: str) -> Optional[ParticleType]:
    """Classify a surface form into its particle type.

    Parameters
    ----------
    form : str
        The surface form.

    Returns
    -------
    ParticleType | None
        The particle type, or ``None`` if the form is not a particle.
    """
    record = lookup(form)
    return record.particle_type if record is not None else None


def is_particle(form: str) -> bool:
    """Check whether a surface form is a known particle.

    Parameters
    ----------
    form : str
        The surface form.

    Returns
    -------
    bool
        ``True`` if the form appears in the catalog.
    """
    return form in load_catalog()


def all_forms() -> frozenset[str]:
    """Return the set of all known particle surface forms.

    Returns
    -------
    frozenset[str]
        Every particle form in the catalog.
    """
    return frozenset(load_catalog().keys())


def forms_by_type(ptype: ParticleType) -> frozenset[str]:
    """Return all particle forms of a given type.

    Parameters
    ----------
    ptype : ParticleType
        The particle type to filter on.

    Returns
    -------
    frozenset[str]
        All forms matching *ptype*.
    """
    return frozenset(
        r.form for r in load_catalog().values() if r.particle_type is ptype
    )
