"""Kernel runtime state — three-layer state model for the hypothesis graph.

Instead of a monolithic "mega-state" object, the runtime state is split
into three composable layers:

* :class:`SignalState` — raw Unicode atoms and normalised signal units
* :class:`HypothesisState` — hypothesis nodes + support/conflict/constraint edges
* :class:`DecisionState` — activated (stabilised) nodes, suspensions, and trace

The top-level :class:`KernelRuntimeState` composes all three.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .enums import ActivationStage, HypothesisStatus
from .types import (
    ActivationRecord,
    ConflictEdge,
    ConstraintEdge,
    DecisionTrace,
    HypothesisNode,
    SignalUnit,
    SupportEdge,
    UnicodeAtom,
)


@dataclass
class SignalState:
    """حالة الإشارة — signal-layer state.

    Holds the raw Unicode atoms and the normalised signal units
    produced by the signal layer.
    """

    atoms: List[UnicodeAtom] = field(default_factory=list)
    signal_units: List[SignalUnit] = field(default_factory=list)


@dataclass
class HypothesisState:
    """حالة الفرضيات — hypothesis-graph state.

    Holds all hypothesis nodes (keyed by stage) together with
    the three edge types that link them.
    """

    hypotheses: Dict[ActivationStage, List[HypothesisNode]] = field(
        default_factory=dict
    )
    constraint_edges: List[ConstraintEdge] = field(default_factory=list)
    support_edges: List[SupportEdge] = field(default_factory=list)
    conflict_edges: List[ConflictEdge] = field(default_factory=list)

    # ── helpers ──────────────────────────────────────────────────

    def add_hypothesis(self, node: HypothesisNode) -> None:
        """Insert a hypothesis into the stage-keyed dict."""
        self.hypotheses.setdefault(node.stage, []).append(node)

    def all_hypotheses(self) -> List[HypothesisNode]:
        """Return a flat list of every hypothesis across all stages."""
        return [h for nodes in self.hypotheses.values() for h in nodes]

    def active_hypotheses(
        self, stage: Optional[ActivationStage] = None
    ) -> List[HypothesisNode]:
        """Return hypotheses that are still ACTIVE (optionally filtered by stage)."""
        if stage is not None:
            return [
                h
                for h in self.hypotheses.get(stage, [])
                if h.status == HypothesisStatus.ACTIVE
            ]
        return [
            h
            for h in self.all_hypotheses()
            if h.status == HypothesisStatus.ACTIVE
        ]


@dataclass
class DecisionState:
    """حالة القرار — decision / activation state.

    Tracks which hypotheses have been stabilised, suspended, or
    revised, plus the full trace log.
    """

    activated: List[HypothesisNode] = field(default_factory=list)
    suspended: List[HypothesisNode] = field(default_factory=list)
    activation_log: List[ActivationRecord] = field(default_factory=list)
    trace: List[DecisionTrace] = field(default_factory=list)
    judgement: Optional[HypothesisNode] = None


@dataclass
class KernelRuntimeState:
    """حالة التشغيل الكلية — top-level runtime state.

    Composes the three sub-states into a single object that the
    orchestrator threads through each processing stage.
    """

    input_text: str = ""
    signal: SignalState = field(default_factory=SignalState)
    hypotheses: HypothesisState = field(default_factory=HypothesisState)
    decisions: DecisionState = field(default_factory=DecisionState)
    iteration: int = 0
    metadata: Dict[str, object] = field(default_factory=dict)
