from __future__ import annotations

from arabic_engine.cognition.knowledge_graph import KnowledgeGraph
from arabic_engine.core.enums import (
    CarrierClass,
    InfoKind,
    JudgementType,
    LinkKind,
    MethodFamily,
    PathKind,
    RealityKind,
    SenseModality,
    ValidationState,
)
from arabic_engine.core.types import (
    ConflictRuleNode,
    GapNode,
    JudgementNode,
    KnowledgeEpisodeNode,
    LinguisticCarrierNode,
    LinkingTraceNode,
    MethodNode,
    PriorInfoNode,
    ProofPathNode,
    RealityAnchorNode,
    SelfNode,
    SenseTraceNode,
)


def _make_episode_nodes():
    episode = KnowledgeEpisodeNode(
        node_id="ep:1",
        domain_profile="linguistic",
        judgement_type="khabari",
        method_family="linguistic",
        carrier_type="utterance",
        method_ref="method:linguistic",
    )
    self_node = SelfNode(node_id="self:1")
    reality = RealityAnchorNode(node_id="ra:1", reality_kind=RealityKind.MATERIAL)
    sense = SenseTraceNode(node_id="st:1", sense_modality=SenseModality.AUDITORY)
    prior = PriorInfoNode(node_id="pi:1", info_kind=InfoKind.LEXICAL)
    linking = LinkingTraceNode(node_id="lt:1", link_kind=LinkKind.LOGICAL)
    judgement = JudgementNode(node_id="j:1", judgement_type=JudgementType.EXISTENCE)
    carrier = LinguisticCarrierNode(node_id="lc:1", carrier_class=CarrierClass.UTTERANCE)
    proof = ProofPathNode(node_id="pp:1", path_kind=PathKind.FORMAL)
    conflict = ConflictRuleNode(node_id="cr:1", rule_name="default")
    return (
        episode, self_node, reality, sense, [prior],
        linking, judgement, carrier, proof, conflict,
    )


# ── Basic graph operations ─────────────────────────────────────────


def test_empty_graph() -> None:
    g = KnowledgeGraph()
    s = g.summary()
    assert s["nodes"] == 0
    assert s["edges"] == 0


def test_add_node() -> None:
    g = KnowledgeGraph()
    n = SelfNode(node_id="self:x")
    g.add_node(n)
    assert g.get_node("self:x") is n


def test_add_node_returns_id() -> None:
    g = KnowledgeGraph()
    result = g.add_node(SelfNode(node_id="self:y"))
    assert result == "self:y"


def test_get_node_missing() -> None:
    g = KnowledgeGraph()
    assert g.get_node("nonexistent") is None


def test_all_nodes() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    assert len(g.all_nodes()) == 2


def test_nodes_of_type() -> None:
    g = KnowledgeGraph()
    s = SelfNode(node_id="self:1")
    m = MethodNode(
        node_id="method:test",
        method_family=MethodFamily.RATIONAL,
        scope="test",
    )
    g.add_node(s)
    g.add_node(m)
    result = g.nodes_of_type(SelfNode)
    assert len(result) == 1
    assert result[0] is s


# ── Edge operations ────────────────────────────────────────────────


def test_add_edge() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    g.add_edge("a", "KNOWS", "b")
    edges = g.edges_from("a")
    assert len(edges) == 1


def test_duplicate_edge_ignored() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    g.add_edge("a", "KNOWS", "b")
    g.add_edge("a", "KNOWS", "b")
    assert len(g.edges_from("a")) == 1


def test_edges_from_with_label_filter() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    g.add_node(SelfNode(node_id="c"))
    g.add_edge("a", "KNOWS", "b")
    g.add_edge("a", "LIKES", "c")
    assert len(g.edges_from("a", label="KNOWS")) == 1


def test_edges_to() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    g.add_edge("a", "KNOWS", "b")
    edges = g.edges_to("b")
    assert len(edges) == 1


def test_neighbour_ids() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    g.add_edge("a", "KNOWS", "b")
    assert g.neighbour_ids("a", "KNOWS") == ["b"]


def test_neighbour_single() -> None:
    g = KnowledgeGraph()
    b = SelfNode(node_id="b")
    g.add_node(SelfNode(node_id="a"))
    g.add_node(b)
    g.add_edge("a", "KNOWS", "b")
    assert g.neighbour("a", "KNOWS") is b


def test_neighbour_none() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    assert g.neighbour("a", "KNOWS") is None


def test_neighbours_multiple() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="a"))
    g.add_node(SelfNode(node_id="b"))
    g.add_node(SelfNode(node_id="c"))
    g.add_edge("a", "KNOWS", "b")
    g.add_edge("a", "KNOWS", "c")
    assert len(g.neighbours("a", "KNOWS")) == 2


# ── Episode operations ─────────────────────────────────────────────


def test_add_episode() -> None:
    g = KnowledgeGraph()
    nodes = _make_episode_nodes()
    g.add_episode(*nodes)
    s = g.summary()
    assert s["nodes"] > 0
    assert s["edges"] > 0
    assert s["episodes"] == 1


def test_all_episodes() -> None:
    g = KnowledgeGraph()
    nodes = _make_episode_nodes()
    g.add_episode(*nodes)
    assert len(g.all_episodes()) == 1


def test_get_episode() -> None:
    g = KnowledgeGraph()
    nodes = _make_episode_nodes()
    g.add_episode(*nodes)
    ep = g.get_episode("ep:1")
    assert ep is not None
    assert ep.node_id == "ep:1"


def test_get_episode_not_found() -> None:
    g = KnowledgeGraph()
    g.add_node(SelfNode(node_id="not_an_episode"))
    assert g.get_episode("not_an_episode") is None


# ── Seed defaults ──────────────────────────────────────────────────


def test_seed_defaults() -> None:
    g = KnowledgeGraph()
    g.seed_defaults()
    assert g.summary()["nodes"] == 6  # 5 methods + 1 conflict rule


# ── Gap management ─────────────────────────────────────────────────


def test_attach_gap() -> None:
    g = KnowledgeGraph()
    nodes = _make_episode_nodes()
    g.add_episode(*nodes)
    gap = GapNode(node_id="gap:1", gap_type="missing_evidence")
    g.attach_gap("ep:1", gap)
    assert len(g.get_gaps("ep:1")) == 1


def test_clear_gaps() -> None:
    g = KnowledgeGraph()
    nodes = _make_episode_nodes()
    g.add_episode(*nodes)
    gap = GapNode(node_id="gap:2", gap_type="missing_evidence")
    g.attach_gap("ep:1", gap)
    g.clear_gaps("ep:1")
    assert len(g.get_gaps("ep:1")) == 0


# ── Summary / repr ─────────────────────────────────────────────────


def test_summary() -> None:
    g = KnowledgeGraph()
    s = g.summary()
    assert "nodes" in s
    assert "edges" in s
    assert "episodes" in s


def test_repr() -> None:
    g = KnowledgeGraph()
    assert "KnowledgeGraph(" in repr(g)


# ── Update episode state ──────────────────────────────────────────


def test_update_episode_state() -> None:
    g = KnowledgeGraph()
    nodes = _make_episode_nodes()
    g.add_episode(*nodes)
    ep = g.get_episode("ep:1")
    assert ep is not None
    ep.validation_state = ValidationState.VALID
    g._update_episode_state(ep)
    updated = g.get_episode("ep:1")
    assert updated is not None
    assert updated.validation_state == ValidationState.VALID
