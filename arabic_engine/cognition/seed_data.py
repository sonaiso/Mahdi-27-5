"""Seed data — البذرة: bootstrap Methods and ConflictRules for the knowledge graph.

This module defines the five standard :class:`~arabic_engine.core.types.MethodNode`
objects and the default :class:`~arabic_engine.core.types.ConflictRuleNode` that
mirror the Cypher bootstrap (section 3 of the schema specification).

Usage::

    from arabic_engine.cognition.seed_data import DEFAULT_METHODS, DEFAULT_CONFLICT_RULE

    graph = KnowledgeGraph()
    for method in DEFAULT_METHODS.values():
        graph.seed_method(method)
    graph.seed_conflict_rule(DEFAULT_CONFLICT_RULE)

    # or simply:
    graph.seed_defaults()
"""

from __future__ import annotations

from arabic_engine.core.enums import MethodFamily
from arabic_engine.core.types import ConflictRuleNode, MethodNode

# ── Standard methods ──────────────────────────────────────────────────

#: The five standard epistemological methods available in every graph.
DEFAULT_METHODS: dict[str, MethodNode] = {
    "rational": MethodNode(
        node_id="method:rational",
        method_family=MethodFamily.RATIONAL,
        scope="general cognition",
        requires_experiment=False,
        requires_formal_proof=False,
        requires_linguistic_anchor=False,
    ),
    "scientific": MethodNode(
        node_id="method:scientific",
        method_family=MethodFamily.SCIENTIFIC,
        scope="empirical material inquiry",
        requires_experiment=True,
        requires_formal_proof=False,
        requires_linguistic_anchor=False,
    ),
    "linguistic": MethodNode(
        node_id="method:linguistic",
        method_family=MethodFamily.LINGUISTIC,
        scope="utterance/concept analysis",
        requires_experiment=False,
        requires_formal_proof=False,
        requires_linguistic_anchor=True,
    ),
    "mathematical": MethodNode(
        node_id="method:mathematical",
        method_family=MethodFamily.MATHEMATICAL,
        scope="formal symbolic proof",
        requires_experiment=False,
        requires_formal_proof=True,
        requires_linguistic_anchor=False,
    ),
    "physical": MethodNode(
        node_id="method:physical",
        method_family=MethodFamily.PHYSICAL,
        scope="physical law and measurement",
        requires_experiment=True,
        requires_formal_proof=True,
        requires_linguistic_anchor=False,
    ),
}

# ── Default conflict resolution rule ─────────────────────────────────

#: The default conflict-resolution rule applied to all episodes unless
#: a custom rule is specified.
DEFAULT_CONFLICT_RULE: ConflictRuleNode = ConflictRuleNode(
    node_id="conflict:default",
    rule_name="default_conflict_v1",
    priority_order=(
        "Reality > Valid Proof > Concept specialization > Utterance > Suspend"
    ),
    action_on_conflict="downgrade_or_reject",
)
