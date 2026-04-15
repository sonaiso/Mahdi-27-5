"""State mapping tests — A4 unified state model coherence.

Verifies that the STATUS_MAPPINGS table is complete, consistent, and
that every mapped value corresponds to a real enum member.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    HypothesisStatus,
    LayerGateDecision,
    PipelineStatus,
    TransitionGateStatus,
    ValidationState,
)
from arabic_engine.core.types import STATUS_MAPPINGS, StatusMapping


_ENUM_REGISTRY = {
    "PipelineStatus": PipelineStatus,
    "LayerGateDecision": LayerGateDecision,
    "TransitionGateStatus": TransitionGateStatus,
    "HypothesisStatus": HypothesisStatus,
    "ValidationState": ValidationState,
}


class TestStatusMappingStructure:
    """STATUS_MAPPINGS is well-formed."""

    def test_mappings_is_tuple(self):
        assert isinstance(STATUS_MAPPINGS, tuple)

    def test_all_entries_are_status_mapping(self):
        for m in STATUS_MAPPINGS:
            assert isinstance(m, StatusMapping)

    def test_minimum_mapping_count(self):
        assert len(STATUS_MAPPINGS) >= 10


class TestStatusMappingValidity:
    """Every mapped value exists in the corresponding enum."""

    def test_from_values_are_real_enum_members(self):
        for m in STATUS_MAPPINGS:
            enum_cls = _ENUM_REGISTRY.get(m.from_domain)
            if enum_cls is not None:
                assert hasattr(enum_cls, m.from_value), (
                    f"{m.from_domain}.{m.from_value} does not exist"
                )

    def test_to_values_are_real_enum_members(self):
        for m in STATUS_MAPPINGS:
            enum_cls = _ENUM_REGISTRY.get(m.to_domain)
            if enum_cls is not None:
                assert hasattr(enum_cls, m.to_value), (
                    f"{m.to_domain}.{m.to_value} does not exist"
                )


class TestStatusMappingCompleteness:
    """All values of mapped source enums are covered."""

    def test_all_gate_decisions_mapped(self):
        mapped = {
            m.from_value for m in STATUS_MAPPINGS
            if m.from_domain == "LayerGateDecision"
        }
        for member in LayerGateDecision:
            assert member.name in mapped, f"{member.name} not mapped"

    def test_all_transition_statuses_mapped(self):
        mapped = {
            m.from_value for m in STATUS_MAPPINGS
            if m.from_domain == "TransitionGateStatus"
        }
        for member in TransitionGateStatus:
            assert member.name in mapped, f"{member.name} not mapped"

    def test_all_validation_states_mapped(self):
        mapped = {
            m.from_value for m in STATUS_MAPPINGS
            if m.from_domain == "ValidationState"
        }
        for member in ValidationState:
            assert member.name in mapped, f"{member.name} not mapped"


class TestStatusMappingConsistency:
    """Cross-domain mappings are coherent."""

    def test_suspend_maps_consistently(self):
        """SUSPEND in any source domain always maps to SUSPEND or equivalent."""
        for m in STATUS_MAPPINGS:
            if "SUSPEND" in m.from_value:
                assert m.to_value in ("SUSPEND",), (
                    f"{m.from_domain}.{m.from_value} maps to "
                    f"{m.to_domain}.{m.to_value}, expected SUSPEND"
                )

    def test_no_duplicate_source_target_pairs(self):
        """No two mappings have identical (from_domain, from_value, to_domain)."""
        seen = set()
        for m in STATUS_MAPPINGS:
            key = (m.from_domain, m.from_value, m.to_domain)
            assert key not in seen, f"Duplicate mapping for {key}"
            seen.add(key)
