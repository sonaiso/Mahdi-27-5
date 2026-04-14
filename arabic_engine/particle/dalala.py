"""Particle signification — دلالة الحرف (مطابقة، تضمن، التزام).

Implements the three modes of signification for particles:

* **مطابقة (mutābaqah)** — the relation/direction the particle exactly matches.
* **تضمّن (taḍammun)** — the scope, conditions, and term types it implies.
* **التزام (iltizām)** — the syntactic positions and effects it commits to.
"""

from __future__ import annotations

from typing import Dict, List

from arabic_engine.core.types import ParticleRecord

# ── Mutābaqah — المطابقة ────────────────────────────────────────────


def mutabaqa(record: ParticleRecord) -> str:
    """Return the relation or direction the particle exactly matches.

    For example:
    - ``في``  → ``ظرفية``
    - ``من``  → ``ابتداء``
    - ``لا``  → ``نفي``

    Parameters
    ----------
    record : ParticleRecord
        The particle record.

    Returns
    -------
    str
        The matched direction (جهة المطابقة).
    """
    return record.direction


# ── Taḍammun — التضمّن ──────────────────────────────────────────────


def tadammun(record: ParticleRecord) -> Dict[str, str]:
    """Return the implied scope, conditions, and term types.

    Parameters
    ----------
    record : ParticleRecord
        The particle record.

    Returns
    -------
    dict[str, str]
        Keys: ``scope``, ``relation_type``, ``particle_type``.
    """
    return {
        "scope": record.scope,
        "relation_type": record.relation_type.name,
        "particle_type": record.particle_type.name,
    }


# ── Iltizām — الالتزام ─────────────────────────────────────────────


def iltizam(record: ParticleRecord) -> List[str]:
    """Return the syntactic positions/effects the particle commits to.

    Parameters
    ----------
    record : ParticleRecord
        The particle record.

    Returns
    -------
    list[str]
        List of commitments the particle enforces.
    """
    commitments: List[str] = []

    # Effect commitment
    if record.effect and record.effect != "none":
        commitments.append(f"يلتزم_بـ_{record.effect}")

    # Scope commitment
    if record.scope == "noun":
        commitments.append("يفتح_موضع_اسم")
    elif record.scope == "verb":
        commitments.append("يفتح_موضع_فعل")
    elif record.scope == "clause":
        commitments.append("يفتح_موضع_جملة")

    # Direction commitment
    if record.direction:
        commitments.append(f"يوجّه_إلى_{record.direction}")

    return commitments
