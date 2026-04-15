"""Tests for arabic_engine/linkage/masdar_bridge.py."""

from __future__ import annotations

from arabic_engine.core.enums import (
    DalalaType,
    DerivationTarget,
    KawnType,
    MasdarBab,
    MasdarType,
    SemanticType,
)
from arabic_engine.core.types import (
    Concept,
    FractalMasdarNode,
    MasdarDerivation,
    MasdarRecord,
)
from arabic_engine.linkage.masdar_bridge import (
    KawnBridge,
    build_bridge,
    trace_fractal_path,
    validate_masdar_link,
)


def _masdar() -> MasdarRecord:
    return MasdarRecord(
        masdar_id="m1",
        surface="كِتابة",
        root=("ك", "ت", "ب"),
        pattern="فِعالة",
        masdar_type=MasdarType.ORIGINAL,
        masdar_bab=MasdarBab.FA3L,
        verb_form="كَتَبَ",
    )


def _jamid_concept() -> Concept:
    return Concept(concept_id=1, label="كتاب", semantic_type=SemanticType.ENTITY)


def _fi3l_concept() -> Concept:
    return Concept(concept_id=2, label="كتب", semantic_type=SemanticType.EVENT)


def _derivation(
    target_type: DerivationTarget = DerivationTarget.ISM_FA3IL,
) -> MasdarDerivation:
    return MasdarDerivation(
        source_masdar_id="m1",
        target_type=target_type,
        target_surface="كاتب",
        target_pattern="فاعل",
    )


def _fractal_node(derivations: list | None = None) -> FractalMasdarNode:
    return FractalMasdarNode(
        node_id="fn1",
        masdar=_masdar(),
        transformational_links=derivations if derivations is not None else [],
    )


# ── KawnBridge ──────────────────────────────────────────────────────


def test_kawn_bridge_incomplete():
    bridge = KawnBridge(masdar=_masdar())
    assert not bridge.is_complete


def test_kawn_bridge_complete():
    bridge = KawnBridge(
        masdar=_masdar(),
        jamid_concept=_jamid_concept(),
        fi3l_concept=_fi3l_concept(),
    )
    assert bridge.is_complete


def test_kawn_bridge_type():
    bridge = KawnBridge(masdar=_masdar())
    assert bridge.bridge_kawn_type == KawnType.MASDAR_BRIDGE


def test_kawn_bridge_links_initially_empty():
    bridge = KawnBridge(masdar=_masdar())
    assert bridge.links == []


# ── build_bridge ────────────────────────────────────────────────────


def test_build_bridge_returns_complete():
    bridge = build_bridge(_jamid_concept(), _masdar(), _fi3l_concept())
    assert bridge.is_complete


def test_build_bridge_creates_two_links():
    bridge = build_bridge(_jamid_concept(), _masdar(), _fi3l_concept())
    assert len(bridge.links) == 2


def test_build_bridge_links_are_masdar_bridge_type():
    bridge = build_bridge(_jamid_concept(), _masdar(), _fi3l_concept())
    for link in bridge.links:
        assert link.dalala_type == DalalaType.MASDAR_BRIDGE


def test_build_bridge_links_accepted():
    bridge = build_bridge(_jamid_concept(), _masdar(), _fi3l_concept())
    for link in bridge.links:
        assert link.accepted is True


def test_build_bridge_confidence():
    bridge = build_bridge(_jamid_concept(), _masdar(), _fi3l_concept())
    confidences = sorted(link.confidence for link in bridge.links)
    assert confidences == [0.9, 0.95]


# ── trace_fractal_path ──────────────────────────────────────────────


def test_trace_fractal_path_matches():
    d = _derivation(DerivationTarget.ISM_FA3IL)
    node = _fractal_node(derivations=[d])
    result = trace_fractal_path(node, "ISM_FA3IL")
    assert len(result) == 1
    assert result[0].target_surface == "كاتب"


def test_trace_fractal_path_no_match():
    d = _derivation(DerivationTarget.ISM_FA3IL)
    node = _fractal_node(derivations=[d])
    result = trace_fractal_path(node, "ISM_MAF3UL")
    assert result == []


# ── validate_masdar_link ────────────────────────────────────────────


def test_validate_masdar_link_root_overlap():
    masdar = _masdar()
    concept = Concept(
        concept_id=10,
        label="كتاب",
        semantic_type=SemanticType.ENTITY,
    )
    link = validate_masdar_link(masdar, concept)
    assert link.confidence == 0.85


def test_validate_masdar_link_no_overlap():
    masdar = _masdar()
    concept = Concept(
        concept_id=20,
        label="شمس",
        semantic_type=SemanticType.ENTITY,
    )
    link = validate_masdar_link(masdar, concept)
    assert link.confidence == 0.5


def test_validate_masdar_link_type():
    link = validate_masdar_link(_masdar(), _jamid_concept())
    assert link.dalala_type == DalalaType.MASDAR_BRIDGE
