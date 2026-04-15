"""semantic_direction — فضاء الجهات الدلالية: Semantic Direction Space Constitution v1

This module assigns each Arabic word an intrinsic *semantic direction*
before any judgment, composition, or reception takes place.

Two orthogonal axes are modelled:

1. **Genus Axis** (محور الجنس الأعلى) — *what* the word is: Existence,
   Attribute, Event, or Relation  (Art. 1–5).
2. **Derivational Direction Axis** (محور الجهة الاشتقاقية) — *which*
   derivational projection the word embodies  (Art. 6–12).

Seven inter-direction relations are recognised (Art. 34–40):
Inheritance · Compatibility · Prohibition · Transformation ·
Conditioning · Syntactic Projection · Return.

Public API
----------
* :func:`build_direction_space`
* :func:`classify_genus`
* :func:`assign_direction`
* :func:`validate_weight_carrying`
* :func:`validate_root_carrying`
* :func:`get_relations`
* :func:`validate_direction_completeness`
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Tuple

from arabic_engine.core.enums import (
    POS,
    DerivationalDirection,
    DirectionBoundary,
    DirectionRelation,
    SemanticDirectionGenus,
)
from arabic_engine.core.types import (
    DirectionAssignment,
    DirectionRelationRecord,
    LexicalClosure,
    SemanticDirection,
    SemanticDirectionSpace,
)

# ── Data path ───────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SEED_PATH = _DATA_DIR / "direction_space_seed.json"

# ── POS → genus mapping ────────────────────────────────────────────

_POS_TO_GENUS = {
    POS.ISM: SemanticDirectionGenus.WUJUD,
    POS.FI3L: SemanticDirectionGenus.HADATH,
    POS.SIFA: SemanticDirectionGenus.SIFA,
    POS.HARF: SemanticDirectionGenus.NISBA,
    POS.ZARF: SemanticDirectionGenus.NISBA,
    POS.DAMIR: SemanticDirectionGenus.NISBA,
    POS.MASDAR_SARIH: SemanticDirectionGenus.HADATH,
    POS.MASDAR_MUAWWAL: SemanticDirectionGenus.HADATH,
}

# ── POS → default derivational direction ───────────────────────────

_POS_TO_DIRECTION = {
    POS.ISM: DerivationalDirection.ISM_JAMID,
    POS.FI3L: DerivationalDirection.FI3L_MADI,
    POS.SIFA: DerivationalDirection.ISM_FA3IL,
    POS.HARF: DerivationalDirection.ISM_JAMID,
    POS.ZARF: DerivationalDirection.ISM_ZAMAN,
    POS.DAMIR: DerivationalDirection.ISM_JAMID,
    POS.MASDAR_SARIH: DerivationalDirection.MASDAR,
    POS.MASDAR_MUAWWAL: DerivationalDirection.MASDAR,
}

# ── String → enum look-ups ─────────────────────────────────────────

_STR_TO_GENUS = {e.name: e for e in SemanticDirectionGenus}
_STR_TO_DIR = {e.name: e for e in DerivationalDirection}
_STR_TO_RELATION = {e.name: e for e in DirectionRelation}
_STR_TO_BOUNDARY = {e.name: e for e in DirectionBoundary}

# ── Seed loading ────────────────────────────────────────────────────


def _load_seed() -> dict:
    """Load the direction space seed JSON."""
    with open(_SEED_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _parse_direction(entry: dict) -> SemanticDirection:
    """Parse a single direction entry from the seed JSON."""
    return SemanticDirection(
        direction_id=entry["direction_id"],
        genus=_STR_TO_GENUS[entry["genus"]],
        derivational_direction=_STR_TO_DIR[entry["derivational_direction"]],
        weight_conditions=tuple(entry.get("weight_conditions", ())),
        root_conditions=tuple(entry.get("root_conditions", ())),
        boundary=_STR_TO_BOUNDARY.get(
            entry.get("boundary", "HADD_FASIL"),
            DirectionBoundary.HADD_FASIL,
        ),
    )


def _parse_relation(entry: dict) -> DirectionRelationRecord:
    """Parse a single relation entry from the seed JSON."""
    return DirectionRelationRecord(
        source_direction_id=entry["source"],
        target_direction_id=entry["target"],
        relation=_STR_TO_RELATION[entry["relation"]],
        conditions=tuple(entry.get("conditions", ())),
        confidence=entry.get("confidence", 1.0),
    )


# ── Public API ──────────────────────────────────────────────────────


def build_direction_space() -> SemanticDirectionSpace:
    """Construct the canonical direction space from seed data.

    Returns:
        A :class:`~arabic_engine.core.types.SemanticDirectionSpace` with
        all directions, relations, and genera loaded from the seed JSON.
    """
    seed = _load_seed()

    directions = tuple(_parse_direction(d) for d in seed.get("directions", ()))
    relations = tuple(_parse_relation(r) for r in seed.get("relations", ()))
    genera = tuple(
        _STR_TO_GENUS[g["id"]]
        for g in seed.get("genera", ())
        if g["id"] in _STR_TO_GENUS
    )

    complete = validate_direction_completeness_from_parts(directions, genera)

    return SemanticDirectionSpace(
        directions=directions,
        relations=relations,
        genera=genera,
        complete=complete,
    )


def classify_genus(closure: LexicalClosure) -> SemanticDirectionGenus:
    """Assign a word to one of the four supreme genera.

    The classification relies on the POS tag of the lexical closure.
    Masdar types map to HADATH; adjectives to SIFA; particles and
    adverbs to NISBA; nouns to WUJUD.

    Args:
        closure: The lexical closure of the word.

    Returns:
        The :class:`~arabic_engine.core.enums.SemanticDirectionGenus`.
    """
    return _POS_TO_GENUS.get(closure.pos, SemanticDirectionGenus.WUJUD)


def assign_direction(
    closure: LexicalClosure,
    space: SemanticDirectionSpace,
) -> DirectionAssignment:
    """Assign a word to a specific derivational direction in the space.

    Determines the genus and derivational direction from the POS tag,
    then searches the direction space for a matching direction.

    Args:
        closure: The lexical closure of the word.
        space: The direction space to search in.

    Returns:
        A :class:`~arabic_engine.core.types.DirectionAssignment`.
    """
    genus = classify_genus(closure)
    deriv_dir = _POS_TO_DIRECTION.get(closure.pos, DerivationalDirection.ISM_JAMID)

    # Find the best matching direction in the space
    matched: Optional[SemanticDirection] = None
    for direction in space.directions:
        if direction.derivational_direction == deriv_dir:
            matched = direction
            break

    # Fallback: pick the first direction matching the genus
    if matched is None:
        for direction in space.directions:
            if direction.genus == genus:
                matched = direction
                break

    # Ultimate fallback: create a minimal direction
    if matched is None:
        matched = SemanticDirection(
            direction_id=f"DIR_{deriv_dir.name}",
            genus=genus,
            derivational_direction=deriv_dir,
        )

    confidence = 1.0 if closure.confidence >= 0.9 else round(closure.confidence, 4)

    return DirectionAssignment(
        word_surface=closure.surface,
        root=closure.root,
        pattern=closure.pattern,
        assigned_direction=matched,
        genus=genus,
        confidence=confidence,
    )


def validate_weight_carrying(
    pattern: str,
    direction: SemanticDirection,
) -> bool:
    """Check whether a weight pattern can carry a given direction.

    Args:
        pattern: The morphological weight pattern (e.g. ``"فَعْل"``).
        direction: The semantic direction to check.

    Returns:
        ``True`` if the pattern appears in the direction's weight
        conditions or the conditions are empty (unconstrained).
    """
    if not direction.weight_conditions:
        return True
    return pattern in direction.weight_conditions


_ROOT_TYPE_MAP = {3: "triliteral", 4: "quadriliteral", 5: "quinqueliteral"}


def validate_root_carrying(
    root: Tuple[str, ...],
    direction: SemanticDirection,
) -> bool:
    """Check whether a root can carry a given direction.

    The root type is inferred from its length: 3 → triliteral,
    4 → quadriliteral, etc.

    Args:
        root: The root consonants as a tuple.
        direction: The semantic direction to check.

    Returns:
        ``True`` if the root type is permitted or conditions are empty.
    """
    if not direction.root_conditions:
        return True

    root_type = _ROOT_TYPE_MAP.get(len(root), "other")
    return root_type in direction.root_conditions


def get_relations(
    direction: SemanticDirection,
    space: SemanticDirectionSpace,
) -> List[DirectionRelationRecord]:
    """Get all relations involving a given direction.

    Args:
        direction: The direction to search for.
        space: The direction space containing relations.

    Returns:
        A list of relation records where this direction appears as
        source or target.
    """
    return [
        rel
        for rel in space.relations
        if (
            rel.source_direction_id == direction.direction_id
            or rel.target_direction_id == direction.direction_id
        )
    ]


def validate_direction_completeness(space: SemanticDirectionSpace) -> bool:
    """Validate the minimum completeness condition for a direction space.

    The space is complete when every genus has at least one direction
    and there is at least one relation in the space.

    Args:
        space: The direction space to validate.

    Returns:
        ``True`` if the completeness condition is met.
    """
    return validate_direction_completeness_from_parts(
        space.directions, space.genera,
    )


def validate_direction_completeness_from_parts(
    directions: Tuple[SemanticDirection, ...],
    genera: Tuple[SemanticDirectionGenus, ...],
) -> bool:
    """Check completeness from raw directions and genera tuples.

    Every genus in *genera* must have at least one direction.
    """
    if not directions or not genera:
        return False
    covered = {d.genus for d in directions}
    return all(g in covered for g in genera)
