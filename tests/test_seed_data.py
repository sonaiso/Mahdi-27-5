from __future__ import annotations

from arabic_engine.cognition.seed_data import DEFAULT_CONFLICT_RULE, DEFAULT_METHODS
from arabic_engine.core.enums import MethodFamily
from arabic_engine.core.types import ConflictRuleNode, MethodNode


def test_default_methods_has_five_entries() -> None:
    assert len(DEFAULT_METHODS) == 5


def test_default_methods_keys() -> None:
    assert set(DEFAULT_METHODS.keys()) == {
        "rational",
        "scientific",
        "linguistic",
        "mathematical",
        "physical",
    }


def test_all_methods_are_method_nodes() -> None:
    for value in DEFAULT_METHODS.values():
        assert isinstance(value, MethodNode)


def test_rational_method_family() -> None:
    assert DEFAULT_METHODS["rational"].method_family == MethodFamily.RATIONAL


def test_scientific_requires_experiment() -> None:
    assert DEFAULT_METHODS["scientific"].requires_experiment is True


def test_mathematical_requires_formal_proof() -> None:
    assert DEFAULT_METHODS["mathematical"].requires_formal_proof is True


def test_linguistic_requires_linguistic_anchor() -> None:
    assert DEFAULT_METHODS["linguistic"].requires_linguistic_anchor is True


def test_physical_requires_experiment_and_proof() -> None:
    m = DEFAULT_METHODS["physical"]
    assert m.requires_experiment is True
    assert m.requires_formal_proof is True


def test_all_methods_have_unique_node_ids() -> None:
    ids = [m.node_id for m in DEFAULT_METHODS.values()]
    assert len(ids) == len(set(ids))


def test_all_methods_have_scope() -> None:
    for m in DEFAULT_METHODS.values():
        assert isinstance(m.scope, str) and len(m.scope) > 0


def test_conflict_rule_is_conflict_rule_node() -> None:
    assert isinstance(DEFAULT_CONFLICT_RULE, ConflictRuleNode)


def test_conflict_rule_has_node_id() -> None:
    assert DEFAULT_CONFLICT_RULE.node_id == "conflict:default"


def test_conflict_rule_has_rule_name() -> None:
    assert DEFAULT_CONFLICT_RULE.rule_name == "default_conflict_v1"


def test_conflict_rule_priority_order_contains_reality() -> None:
    assert "Reality" in DEFAULT_CONFLICT_RULE.priority_order


def test_conflict_rule_action() -> None:
    assert DEFAULT_CONFLICT_RULE.action_on_conflict == "downgrade_or_reject"
