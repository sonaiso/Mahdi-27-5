"""Knowledge Graph — شبكة المعرفة: in-memory graph store for KnowledgeEpisode nodes.

Provides an adjacency-list graph whose nodes are the ten epistemic
building blocks (RealityAnchor, SenseTrace, PriorInfo, …) and whose
directed edges represent the relationships defined in the schema::

    (:Self)-[:UNDERGOES]->(:KnowledgeEpisode)
    (:KnowledgeEpisode)-[:HAS_REALITY_ANCHOR]->(:RealityAnchor)
    …

The graph is intentionally stored in plain Python dicts and lists so
that it requires no external database.  A running instance stores all
episodes for a session and supports retrieval, filtering, and full
inspection of the relationship network.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from arabic_engine.core.types import (
    ConflictRuleNode,
    EpistemicConceptNode,
    EvidenceNode,
    GapNode,
    JudgementNode,
    KnowledgeEpisodeNode,
    LinguisticCarrierNode,
    LinkingTraceNode,
    MethodNode,
    OpinionTraceNode,
    PriorInfoNode,
    ProofPathNode,
    RealityAnchorNode,
    SelfNode,
    SenseTraceNode,
    UtteranceNode,
)

# ── Type aliases ─────────────────────────────────────────────────────

_Node = object  # any of the above node types
_Edge = Tuple[str, str, str]  # (from_id, relationship, to_id)


class KnowledgeGraph:
    """شبكة المعرفة — in-memory directed graph of knowledge episode nodes.

    Every node has a unique string ``node_id``.
    Every edge is a triple ``(from_id, relationship_label, to_id)``.

    The public API mirrors the five-phase operation described in the
    schema documentation:

    1. **seed** — load method and conflict rule dictionaries.
    2. **add_episode** — register a full episode with all its components.
    3. **link** — attach a node to the episode via a named relationship.
    4. **query** — retrieve nodes, edges, and validation results.
    5. **clear** / **reset** — empty the graph.

    Example::

        g = KnowledgeGraph()
        g.seed_defaults()
        ep = g.add_episode(ke, self_node, reality, sense, prior_infos,
                           linking, judgement, carrier, proof, conflict)
    """

    def __init__(self) -> None:
        """Initialise an empty knowledge graph."""
        # node_id → node object
        self._nodes: Dict[str, _Node] = {}
        # list of (from_id, label, to_id) directed edges
        self._edges: List[_Edge] = []

    # ── Node management ───────────────────────────────────────────────

    def add_node(self, node: _Node) -> str:
        """Register a node and return its ``node_id``.

        If a node with the same ID already exists it is silently
        replaced (MERGE semantics matching the Cypher pattern).

        Args:
            node: Any node dataclass with a ``node_id`` attribute.

        Returns:
            The ``node_id`` string.
        """
        nid: str = getattr(node, "node_id")
        self._nodes[nid] = node
        return nid

    def get_node(self, node_id: str) -> Optional[_Node]:
        """Return the node with the given ID, or ``None``."""
        return self._nodes.get(node_id)

    def all_nodes(self) -> List[_Node]:
        """Return all nodes in insertion order."""
        return list(self._nodes.values())

    def nodes_of_type(self, node_type: type) -> List[_Node]:
        """Return all nodes that are instances of *node_type*."""
        return [n for n in self._nodes.values() if isinstance(n, node_type)]

    # ── Edge management ───────────────────────────────────────────────

    def add_edge(self, from_id: str, label: str, to_id: str) -> None:
        """Add a directed edge ``(from_id)-[:label]->(to_id)``.

        Duplicate edges (same triple) are silently ignored.

        Args:
            from_id: ID of the source node.
            label:   Relationship label (e.g. ``"HAS_REALITY_ANCHOR"``).
            to_id:   ID of the target node.
        """
        edge: _Edge = (from_id, label, to_id)
        if edge not in self._edges:
            self._edges.append(edge)

    def edges_from(self, from_id: str, label: Optional[str] = None) -> List[_Edge]:
        """Return edges emanating from *from_id*, optionally filtered by label."""
        return [
            e for e in self._edges
            if e[0] == from_id and (label is None or e[1] == label)
        ]

    def edges_to(self, to_id: str, label: Optional[str] = None) -> List[_Edge]:
        """Return edges pointing at *to_id*, optionally filtered by label."""
        return [
            e for e in self._edges
            if e[2] == to_id and (label is None or e[1] == label)
        ]

    def neighbour_ids(self, from_id: str, label: str) -> List[str]:
        """Return the IDs of all nodes reachable from *from_id* via *label*."""
        return [e[2] for e in self.edges_from(from_id, label)]

    def neighbour(self, from_id: str, label: str) -> Optional[_Node]:
        """Return the first node reachable from *from_id* via *label*, or ``None``."""
        ids = self.neighbour_ids(from_id, label)
        return self._nodes.get(ids[0]) if ids else None

    def neighbours(self, from_id: str, label: str) -> List[_Node]:
        """Return all nodes reachable from *from_id* via *label*."""
        return [self._nodes[i] for i in self.neighbour_ids(from_id, label) if i in self._nodes]

    # ── High-level episode assembly ───────────────────────────────────

    def add_episode(  # noqa: PLR0913
        self,
        episode: KnowledgeEpisodeNode,
        self_node: SelfNode,
        reality: RealityAnchorNode,
        sense: SenseTraceNode,
        prior_infos: Iterable[PriorInfoNode],
        linking: LinkingTraceNode,
        judgement: JudgementNode,
        carrier: LinguisticCarrierNode,
        proof: ProofPathNode,
        conflict: ConflictRuleNode,
        *,
        utterance: Optional[UtteranceNode] = None,
        concept: Optional[EpistemicConceptNode] = None,
        opinions: Optional[Iterable[OpinionTraceNode]] = None,
        evidence: Optional[Iterable[EvidenceNode]] = None,
    ) -> KnowledgeEpisodeNode:
        """Register a complete knowledge episode with all its components.

        This method MERGE-inserts every node and creates all canonical
        relationships in one call.  It mirrors the MERGE pattern from
        the Cypher schema (section 4).

        Args:
            episode:     The :class:`KnowledgeEpisodeNode` to register.
            self_node:   The knowing subject.
            reality:     The reality anchor.
            sense:       The sense trace.
            prior_infos: One or more prior information nodes.
            linking:     The linking trace.
            judgement:   The judgement node.
            carrier:     The linguistic carrier.
            proof:       The proof path.
            conflict:    The conflict rule.
            utterance:   Optional utterance node (منطوق).
            concept:     Optional concept node (مفهوم).
            opinions:    Optional opinion traces that must be excluded.
            evidence:    Optional evidence nodes for the proof path.

        Returns:
            The registered :class:`KnowledgeEpisodeNode`.
        """
        ep_id = self.add_node(episode)
        s_id = self.add_node(self_node)
        self.add_edge(s_id, "UNDERGOES", ep_id)

        ra_id = self.add_node(reality)
        self.add_edge(ep_id, "HAS_REALITY_ANCHOR", ra_id)

        st_id = self.add_node(sense)
        self.add_edge(ep_id, "HAS_SENSE_TRACE", st_id)

        for pi in prior_infos:
            pi_id = self.add_node(pi)
            self.add_edge(ep_id, "USES_PRIOR_INFO", pi_id)

        lt_id = self.add_node(linking)
        self.add_edge(ep_id, "HAS_LINKING_TRACE", lt_id)

        j_id = self.add_node(judgement)
        self.add_edge(ep_id, "ISSUES", j_id)

        # method is looked up by method_ref if already seeded; otherwise skip
        if episode.method_ref and episode.method_ref in self._nodes:
            self.add_edge(ep_id, "USES_METHOD", episode.method_ref)

        lc_id = self.add_node(carrier)
        self.add_edge(ep_id, "CARRIED_BY", lc_id)

        if utterance is not None:
            u_id = self.add_node(utterance)
            self.add_edge(lc_id, "REALIZED_AS", u_id)
            if concept is not None:
                c_id = self.add_node(concept)
                self.add_edge(lc_id, "REALIZED_AS", c_id)
                self.add_edge(u_id, "ANCHORS_TO", c_id)
        elif concept is not None:
            c_id = self.add_node(concept)
            self.add_edge(lc_id, "REALIZED_AS", c_id)

        pp_id = self.add_node(proof)
        self.add_edge(ep_id, "JUSTIFIED_BY", pp_id)

        if evidence:
            for ev in evidence:
                ev_id = self.add_node(ev)
                self.add_edge(pp_id, "SUPPORTED_BY", ev_id)

        cr_id = self.add_node(conflict)
        self.add_edge(ep_id, "VALIDATED_BY", cr_id)

        if opinions:
            for op in opinions:
                op_id = self.add_node(op)
                self.add_edge(ep_id, "MUST_EXCLUDE", op_id)

        return episode

    # ── Gap management ────────────────────────────────────────────────

    def attach_gap(self, episode_id: str, gap: GapNode) -> None:
        """Register a gap node and link it to the episode.

        This method only adds; call :meth:`clear_gaps` first if you need
        to replace all existing gaps (as the validator does).
        """
        g_id = self.add_node(gap)
        self.add_edge(episode_id, "HAS_GAP", g_id)

    def clear_gaps(self, episode_id: str) -> None:
        """Remove all HAS_GAP edges (and their gap nodes) for *episode_id*."""
        gap_ids = self.neighbour_ids(episode_id, "HAS_GAP")
        self._edges = [
            e for e in self._edges
            if not (e[0] == episode_id and e[1] == "HAS_GAP")
        ]
        for gid in gap_ids:
            self._nodes.pop(gid, None)

    def get_gaps(self, episode_id: str) -> List[GapNode]:
        """Return all GapNode objects linked to *episode_id*."""
        return self.neighbours(episode_id, "HAS_GAP")  # type: ignore[return-value]

    # ── Episode retrieval ─────────────────────────────────────────────

    def all_episodes(self) -> List[KnowledgeEpisodeNode]:
        """Return all KnowledgeEpisodeNode objects in the graph."""
        return self.nodes_of_type(KnowledgeEpisodeNode)  # type: ignore[return-value]

    def get_episode(self, episode_id: str) -> Optional[KnowledgeEpisodeNode]:
        """Return the KnowledgeEpisodeNode with the given ID, or ``None``."""
        node = self.get_node(episode_id)
        if isinstance(node, KnowledgeEpisodeNode):
            return node
        return None

    # ── Seed utilities ────────────────────────────────────────────────

    def seed_method(self, method: MethodNode) -> None:
        """Register a method node so it can be looked up by ``method_ref``."""
        self.add_node(method)

    def seed_conflict_rule(self, rule: ConflictRuleNode) -> None:
        """Register a conflict rule node."""
        self.add_node(rule)

    def seed_defaults(self) -> None:
        """Populate the graph with the five standard methods and default conflict rule.

        This is the equivalent of the Cypher bootstrap (section 3).
        """
        from arabic_engine.cognition.seed_data import (
            DEFAULT_CONFLICT_RULE,
            DEFAULT_METHODS,
        )
        for m in DEFAULT_METHODS.values():
            self.seed_method(m)
        self.seed_conflict_rule(DEFAULT_CONFLICT_RULE)

    # ── Graph inspection ──────────────────────────────────────────────

    def summary(self) -> Dict[str, int]:
        """Return a count of nodes and edges in the graph."""
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "episodes": len(self.all_episodes()),
        }

    def __repr__(self) -> str:
        s = self.summary()
        return (
            f"KnowledgeGraph("
            f"nodes={s['nodes']}, edges={s['edges']}, "
            f"episodes={s['episodes']})"
        )

    # ── Mutation helpers (for validator write-back) ───────────────────

    def _update_episode_state(
        self,
        episode: KnowledgeEpisodeNode,
    ) -> None:
        """Replace the stored episode node (needed because KnowledgeEpisodeNode is mutable).

        Called by :class:`~arabic_engine.cognition.episode_validator.EpisodeValidator`
        after writing ``validation_state`` and ``epistemic_rank`` back to
        the episode.
        """
        self._nodes[episode.node_id] = episode
