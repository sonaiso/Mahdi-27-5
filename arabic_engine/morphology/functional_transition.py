"""الانتقال الوظيفي المنضبط — Functional Transition loader and DSL evaluator.

This module bridges the JSON dataset (``arabic_engine/data/transitions_seed_v1.json``)
and the rest of the engine by:

1. **Loading** the JSON seed file and returning a list of typed
   :class:`~arabic_engine.core.types.FunctionalTransitionRecord` objects.

2. **Parsing** free-form snake_case condition strings into
   :class:`~arabic_engine.core.enums.ConditionToken` values (the DSL).

3. **Looking up** transitions by source cell, target cell, or class.

Public API
----------
* :data:`CONDITION_TOKEN_MAP`  — ``{str: ConditionToken}`` mapping for the DSL
* :func:`parse_condition`      — convert a snake_case string to :class:`ConditionToken`
* :func:`load_seed_dataset`    — load and validate the bundled JSON seed file
* :func:`by_source`            — filter records by source cell
* :func:`by_target`            — filter records by target cell
* :func:`by_class`             — filter records by transition class
"""

from __future__ import annotations

import json
import re
from importlib.resources import files
from typing import Dict, List, Optional

from arabic_engine.core.enums import (
    CellType,
    ConditionToken,
    EvidenceType,
    FuncTransitionClass,
    ReversibleValue,
)
from arabic_engine.core.types import FunctionalTransitionRecord

# ── DSL mapping: snake_case string → ConditionToken ──────────────────

#: Maps every snake_case condition string that appears in the seed dataset
#: to its corresponding :class:`~arabic_engine.core.enums.ConditionToken`.
#: This is the formal Condition DSL registry.
CONDITION_TOKEN_MAP: Dict[str, ConditionToken] = {
    token.name.lower(): token for token in ConditionToken
}


def parse_condition(text: str) -> ConditionToken:
    """Convert a snake_case condition string to a :class:`ConditionToken`.

    The lookup is case-insensitive and normalises any whitespace or hyphens
    to underscores before matching.

    Parameters
    ----------
    text:
        A condition string such as ``"glide_loses_consonantal_load"`` or
        ``"GLIDE_LOSES_CONSONANTAL_LOAD"``.

    Returns
    -------
    ConditionToken

    Raises
    ------
    ValueError
        If ``text`` does not map to a known :class:`ConditionToken`.
    """
    key = re.sub(r"[\s\-]+", "_", text.strip()).lower()
    token = CONDITION_TOKEN_MAP.get(key)
    if token is None:
        raise ValueError(
            f"Unknown condition token: {text!r}. "
            f"Known tokens: {sorted(CONDITION_TOKEN_MAP)}"
        )
    return token


# ── Internal helpers ─────────────────────────────────────────────────

def _parse_cell(value: str) -> CellType:
    try:
        return CellType[value]
    except KeyError:
        raise ValueError(f"Unknown CellType: {value!r}") from None


def _parse_class(value: Optional[str]) -> FuncTransitionClass:
    if not value:
        raise ValueError("Transition_Class is required but missing or empty")
    try:
        return FuncTransitionClass[value]
    except KeyError:
        raise ValueError(f"Unknown FuncTransitionClass: {value!r}") from None


def _parse_reversible(value: str) -> ReversibleValue:
    try:
        return ReversibleValue[value]
    except KeyError:
        raise ValueError(f"Unknown ReversibleValue: {value!r}") from None


def _parse_evidence(value: Optional[str]) -> Optional[EvidenceType]:
    if not value:
        return None
    try:
        return EvidenceType[value]
    except KeyError:
        raise ValueError(f"Unknown EvidenceType: {value!r}") from None


def _record_from_dict(raw: dict) -> FunctionalTransitionRecord:
    """Build a :class:`FunctionalTransitionRecord` from a raw JSON dict."""
    tr_id: str = raw["Transition_ID"]
    if not re.match(r"^TR_\d{3}$", tr_id):
        raise ValueError(f"Invalid Transition_ID format: {tr_id!r}")

    priority = int(raw["Priority"])
    if not (1 <= priority <= 5):
        raise ValueError(f"Priority must be 1–5, got {priority} in {tr_id}")

    preconditions = frozenset(
        parse_condition(c) for c in raw["Preconditions"]
    )
    blocking_conditions = frozenset(
        parse_condition(c) for c in raw.get("Blocking_Conditions", [])
    )

    return FunctionalTransitionRecord(
        transition_id=tr_id,
        source_cell=_parse_cell(raw["Source_Cell"]),
        target_cell=_parse_cell(raw["Target_Cell"]),
        transition_class=_parse_class(raw.get("Transition_Class")),
        preconditions=preconditions,
        blocking_conditions=blocking_conditions,
        priority=priority,
        reversible=_parse_reversible(raw["Reversible"]),
        surface_form=raw["Surface_Form"],
        deep_form=raw["Deep_Form"],
        evidence_type=_parse_evidence(raw.get("Evidence_Type")),
        notes=raw.get("Notes", ""),
    )


# ── Public loader ─────────────────────────────────────────────────────

def load_seed_dataset() -> List[FunctionalTransitionRecord]:
    """Load and validate the bundled seed dataset.

    Reads ``arabic_engine/data/transitions_seed_v1.json``, converts every
    transition entry to a :class:`~arabic_engine.core.types.FunctionalTransitionRecord`,
    and returns them sorted by
    :attr:`~arabic_engine.core.types.FunctionalTransitionRecord.transition_id`.

    Returns
    -------
    list[FunctionalTransitionRecord]
        All 33 seed transition records, sorted by ``Transition_ID``.

    Raises
    ------
    ValueError
        If any record fails schema validation.
    """
    data_pkg = files("arabic_engine.data")
    raw_text = data_pkg.joinpath("transitions_seed_v1.json").read_text(encoding="utf-8")
    payload = json.loads(raw_text)
    records = [_record_from_dict(r) for r in payload["transitions"]]
    return sorted(records, key=lambda r: r.transition_id)


# ── Filter helpers ────────────────────────────────────────────────────

def by_source(
    records: List[FunctionalTransitionRecord],
    cell: CellType,
) -> List[FunctionalTransitionRecord]:
    """Return records whose ``source_cell`` matches *cell*."""
    return [r for r in records if r.source_cell is cell]


def by_target(
    records: List[FunctionalTransitionRecord],
    cell: CellType,
) -> List[FunctionalTransitionRecord]:
    """Return records whose ``target_cell`` matches *cell*."""
    return [r for r in records if r.target_cell is cell]


def by_class(
    records: List[FunctionalTransitionRecord],
    transition_class: FuncTransitionClass,
) -> List[FunctionalTransitionRecord]:
    """Return records belonging to the given *transition_class*."""
    return [r for r in records if r.transition_class is transition_class]
