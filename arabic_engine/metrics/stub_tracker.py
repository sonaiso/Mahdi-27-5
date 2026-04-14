"""Stub Reduction Rate — معدّل استبدال الـ Stubs.

Maintains a registry of known stubs and their replacement status.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class StubStatus(Enum):
    """Status of a known stub."""

    STUB = auto()  # Still a stub / placeholder
    PARTIAL = auto()  # Some real logic, but not complete
    COMPLETE = auto()  # Fully replaced with real logic


@dataclass(frozen=True)
class StubRecord:
    """A single stub entry in the registry."""

    module: str
    function: str
    status: StubStatus
    description: str = ""


# ── Stub Registry ───────────────────────────────────────────────────
# This is the canonical list of known stubs in the project.
# Update status as stubs are replaced with real implementations.

STUB_REGISTRY: List[StubRecord] = [
    StubRecord(
        module="hypothesis/judgements.py",
        function="generate",
        status=StubStatus.COMPLETE,
        description="Judgement hypothesis — now detects proposition types",
    ),
    StubRecord(
        module="hypothesis/axes.py",
        function="_resolve_axis",
        status=StubStatus.COMPLETE,
        description="Axis resolution — all 6 axes now resolved",
    ),
    StubRecord(
        module="hypothesis/roles.py",
        function="_infer_role",
        status=StubStatus.COMPLETE,
        description="Role inference — now handles particles and inversion",
    ),
    StubRecord(
        module="hypothesis/cases.py",
        function="generate",
        status=StubStatus.COMPLETE,
        description="Case assignment — expanded role-case map",
    ),
    StubRecord(
        module="signal/segmentation.py",
        function="segment",
        status=StubStatus.COMPLETE,
        description="Segmentation — now splits clitics",
    ),
    StubRecord(
        module="constraints/scoring.py",
        function="build_constraint_edges",
        status=StubStatus.COMPLETE,
        description="Constraint edges — now builds real constraints",
    ),
    StubRecord(
        module="hypothesis/relations.py",
        function="generate",
        status=StubStatus.COMPLETE,
        description="Relation hypotheses — 9 patterns with disambiguation",
    ),
    StubRecord(
        module="hypothesis/factors.py",
        function="_infer_factor",
        status=StubStatus.COMPLETE,
        description="Factor inference — handles implicit/elided/particle factors",
    ),
]


def compute_stub_reduction_rate() -> float:
    """Return the fraction of stubs that have been replaced.

    Returns
    -------
    float
        Value between 0.0 (all stubs) and 1.0 (all complete).
    """
    if not STUB_REGISTRY:
        return 1.0
    non_stub = sum(
        1 for r in STUB_REGISTRY if r.status != StubStatus.STUB
    )
    return non_stub / len(STUB_REGISTRY)


def stub_summary() -> dict[str, int]:
    """Return counts by status.

    Returns
    -------
    dict[str, int]
        Keys: "stub", "partial", "complete". Values: counts.
    """
    counts: dict[str, int] = {"stub": 0, "partial": 0, "complete": 0}
    for r in STUB_REGISTRY:
        counts[r.status.name.lower()] += 1
    return counts
