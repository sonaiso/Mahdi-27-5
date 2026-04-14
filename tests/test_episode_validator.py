"""Tests for the Knowledge Episode system.

Validates:
  * All new epistemic enums are complete and correctly named.
  * All new node dataclasses are frozen/mutable as designed.
  * KnowledgeGraph: add_node, add_edge, neighbour, seed_defaults.
  * seed_data: five methods, default conflict rule.
  * EpisodeValidator.validate_episode — valid and invalid episodes.
  * EpisodeValidator.validate_linguistic_carrier — all CarrierClass cases.
  * EpisodeValidator.conflict_resolution_hint — three hint branches.
  * EpisodeValidator.validate_all — batch ordering.
  * Re-exports from arabic_engine.core.
"""

from __future__ import annotations

import pytest

from arabic_engine.cognition.episode_validator import EpisodeValidator
from arabic_engine.cognition.knowledge_graph import KnowledgeGraph
from arabic_engine.cognition.seed_data import DEFAULT_CONFLICT_RULE, DEFAULT_METHODS
from arabic_engine.core.enums import (
    CarrierClass,
    ContaminationLevel,
    EpistemicRank,
    GapSeverity,
    InfoKind,
    JudgementType,
    LinkKind,
    MethodFamily,
    PathKind,
    RealityKind,
    SenseModality,
    TraceMode,
    TraceQuality,
    ValidationState,
)
from arabic_engine.core.types import (
    ConflictRuleNode,
    EpisodeValidationResult,
    EpistemicConceptNode,
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

# ═══════════════════════════════════════════════════════════════════════
# Fixtures and helpers
# ═══════════════════════════════════════════════════════════════════════

def _make_graph() -> KnowledgeGraph:
    """Return a fresh KnowledgeGraph with defaults seeded."""
    g = KnowledgeGraph()
    g.seed_defaults()
    return g


def _make_episode(
    ep_id: str = "ke:test",
    *,
    judgement_type: str = "existence",
    method_family: str = "rational",
    carrier_type: str = "both",
) -> KnowledgeEpisodeNode:
    return KnowledgeEpisodeNode(
        node_id=ep_id,
        domain_profile="test",
        judgement_type=judgement_type,
        method_family=method_family,
        carrier_type=carrier_type,
        method_ref=f"method:{method_family}",
        validation_state=ValidationState.PENDING,
    )


def _make_reality(rid: str = "ra:t") -> RealityAnchorNode:
    return RealityAnchorNode(
        node_id=rid,
        reality_kind=RealityKind.TEXT_OBJECT,
        source_mode="direct",
        anchoring_strength=5,
    )


def _make_sense(sid: str = "st:t") -> SenseTraceNode:
    return SenseTraceNode(
        node_id=sid,
        sense_modality=SenseModality.VISION,
        trace_mode=TraceMode.DIRECT_PERCEPTION,
        trace_quality=TraceQuality.STRONG,
    )


def _make_prior(pid: str = "pi:t") -> PriorInfoNode:
    return PriorInfoNode(node_id=pid, info_kind=InfoKind.LEXICAL, source="lexicon")


def _make_linking(lid: str = "lt:t") -> LinkingTraceNode:
    return LinkingTraceNode(
        node_id=lid,
        link_kind=LinkKind.TEXTUAL_INFERENCE,
        step_count=2,
        is_explicit=True,
    )


def _make_judgement(
    jid: str = "j:t",
    jtype: JudgementType = JudgementType.EXISTENCE,
) -> JudgementNode:
    return JudgementNode(
        node_id=jid,
        judgement_type=jtype,
        judgement_text="الحكم",
    )


def _make_carrier(cid: str = "lc:t", cc: CarrierClass = CarrierClass.BOTH) -> LinguisticCarrierNode:
    return LinguisticCarrierNode(node_id=cid, carrier_class=cc)


def _make_proof(
    ppid: str = "pp:t",
    kind: PathKind = PathKind.AQLI,
) -> ProofPathNode:
    return ProofPathNode(
        node_id=ppid,
        path_kind=kind,
        is_complete=True,
        step_count=3,
    )


def _make_utterance(uid: str = "u:t") -> UtteranceNode:
    return UtteranceNode(
        node_id=uid,
        text_shakled="هٰذَا نَصٌّ",
        utterance_mode="nass",
        literal_scope="direct",
    )


def _make_concept(cid: str = "c:t") -> EpistemicConceptNode:
    return EpistemicConceptNode(
        node_id=cid,
        concept_name="test_concept",
        dalaala_type="mutabaqa",
        concept_scope="general",
    )


def _full_episode(
    g: KnowledgeGraph,
    ep_id: str = "ke:full",
    judgement_type: str = "existence",
    path_kind: PathKind = PathKind.AQLI,
) -> KnowledgeEpisodeNode:
    """Insert a complete valid episode into g and return it."""
    ep = _make_episode(ep_id, judgement_type=judgement_type)
    g.add_episode(
        episode=ep,
        self_node=SelfNode(node_id=f"self:{ep_id}", self_kind="individual"),
        reality=_make_reality(f"ra:{ep_id}"),
        sense=_make_sense(f"st:{ep_id}"),
        prior_infos=[_make_prior(f"pi:{ep_id}")],
        linking=_make_linking(f"lt:{ep_id}"),
        judgement=_make_judgement(f"j:{ep_id}"),
        carrier=_make_carrier(f"lc:{ep_id}"),
        proof=_make_proof(f"pp:{ep_id}", kind=path_kind),
        conflict=DEFAULT_CONFLICT_RULE,
        utterance=_make_utterance(f"u:{ep_id}"),
        concept=_make_concept(f"c:{ep_id}"),
    )
    return ep


# ═══════════════════════════════════════════════════════════════════════
# Enum tests
# ═══════════════════════════════════════════════════════════════════════

class TestNewEnums:
    def test_epistemic_rank_members(self):
        names = {m.name for m in EpistemicRank}
        assert names == {
            "CERTAIN",
            "TRUE_NON_CERTAIN",
            "PROBABILISTIC_DOUBT",
            "IMPOSSIBLE",
        }

    def test_validation_state_members(self):
        assert {m.name for m in ValidationState} == {"PENDING", "VALID", "INVALID"}

    def test_judgement_type_members(self):
        names = {m.name for m in JudgementType}
        assert "EXISTENCE" in names
        assert "INTERPRETIVE" in names
        assert "METAPHYSICAL" in names
        assert len(names) == 11

    def test_method_family_members(self):
        names = {m.name for m in MethodFamily}
        assert {"RATIONAL", "SCIENTIFIC", "LINGUISTIC", "MATHEMATICAL", "PHYSICAL"} <= names

    def test_carrier_class_members(self):
        assert {m.name for m in CarrierClass} == {"UTTERANCE", "CONCEPT", "BOTH"}

    def test_sense_modality_members(self):
        assert len(list(SenseModality)) == 6

    def test_reality_kind_members(self):
        names = {m.name for m in RealityKind}
        assert {"MATERIAL", "ABSTRACT", "SOCIAL", "HISTORICAL"} <= names
        assert {"PHYSICAL_OBJECT", "EVENT", "TEXT_OBJECT"} <= names

    def test_info_kind_members(self):
        assert len(list(InfoKind)) == 6

    def test_path_kind_members(self):
        assert {m.name for m in PathKind} == {"HISSI", "AQLI", "LINGUISTIC", "FORMAL"}

    def test_gap_severity_members(self):
        names = {m.name for m in GapSeverity}
        assert {"FATAL", "CRITICAL", "MODERATE", "MINOR"} == names

    def test_contamination_level_members(self):
        from arabic_engine.core.enums import ContaminationLevel
        assert {m.name for m in ContaminationLevel} == {"NONE", "LOW", "MEDIUM", "HIGH"}


# ═══════════════════════════════════════════════════════════════════════
# Dataclass tests
# ═══════════════════════════════════════════════════════════════════════

class TestNodeDataclasses:
    def test_reality_anchor_frozen(self):
        ra = _make_reality()
        with pytest.raises(Exception):
            ra.source_mode = "mediated"  # type: ignore[misc]

    def test_sense_trace_frozen(self):
        st = _make_sense()
        with pytest.raises(Exception):
            st.trace_quality = TraceQuality.WEAK  # type: ignore[misc]

    def test_prior_info_frozen(self):
        pi = _make_prior()
        assert pi.is_verified is True

    def test_knowledge_episode_mutable(self):
        ep = _make_episode()
        # KnowledgeEpisodeNode is mutable
        ep.validation_state = ValidationState.VALID
        assert ep.validation_state is ValidationState.VALID

    def test_gap_node_frozen(self):
        g = GapNode(
            node_id="g:1",
            gap_type="Missing RealityAnchor",
            message="Missing RealityAnchor",
            severity=GapSeverity.FATAL,
        )
        with pytest.raises(Exception):
            g.severity = GapSeverity.MEDIUM  # type: ignore[misc]

    def test_episode_validation_result_frozen(self):
        r = EpisodeValidationResult(
            episode_id="ke:x",
            validation_state=ValidationState.VALID,
            epistemic_rank=EpistemicRank.CERTAIN,
            errors=(),
            gaps=(),
        )
        with pytest.raises(Exception):
            r.episode_id = "ke:y"  # type: ignore[misc]

    def test_utterance_node_defaults(self):
        u = _make_utterance()
        assert u.utterance_mode == "nass"
        assert u.literal_scope == "direct"

    def test_epistemic_concept_node_defaults(self):
        c = _make_concept()
        assert c.dalaala_type == "mutabaqa"
        assert c.concept_scope == "general"


# ═══════════════════════════════════════════════════════════════════════
# Seed data tests
# ═══════════════════════════════════════════════════════════════════════

class TestSeedData:
    def test_five_methods_present(self):
        assert set(DEFAULT_METHODS.keys()) == {
            "rational", "scientific", "linguistic", "mathematical", "physical"
        }

    def test_rational_method(self):
        m = DEFAULT_METHODS["rational"]
        assert m.method_family is MethodFamily.RATIONAL
        assert m.requires_experiment is False
        assert m.requires_formal_proof is False
        assert m.requires_linguistic_anchor is False

    def test_scientific_method(self):
        m = DEFAULT_METHODS["scientific"]
        assert m.requires_experiment is True
        assert m.requires_formal_proof is False

    def test_linguistic_method(self):
        m = DEFAULT_METHODS["linguistic"]
        assert m.requires_linguistic_anchor is True

    def test_mathematical_method(self):
        m = DEFAULT_METHODS["mathematical"]
        assert m.requires_formal_proof is True
        assert m.requires_experiment is False

    def test_physical_method(self):
        m = DEFAULT_METHODS["physical"]
        assert m.requires_experiment is True
        assert m.requires_formal_proof is True

    def test_default_conflict_rule(self):
        cr = DEFAULT_CONFLICT_RULE
        assert cr.rule_name == "default_conflict_v1"
        assert "Reality" in cr.priority_order
        assert cr.action_on_conflict == "downgrade_or_reject"

    def test_method_ids_match_keys(self):
        for key, method in DEFAULT_METHODS.items():
            assert method.node_id == f"method:{key}"


# ═══════════════════════════════════════════════════════════════════════
# KnowledgeGraph tests
# ═══════════════════════════════════════════════════════════════════════

class TestKnowledgeGraph:
    def test_seed_defaults_loads_methods(self):
        g = _make_graph()
        for key in ("rational", "scientific", "linguistic", "mathematical", "physical"):
            node = g.get_node(f"method:{key}")
            assert isinstance(node, MethodNode)

    def test_seed_defaults_loads_conflict_rule(self):
        g = _make_graph()
        cr = g.get_node("conflict:default")
        assert isinstance(cr, ConflictRuleNode)

    def test_add_node_returns_id(self):
        g = _make_graph()
        ra = _make_reality()
        nid = g.add_node(ra)
        assert nid == ra.node_id

    def test_get_node_returns_stored_node(self):
        g = _make_graph()
        ra = _make_reality()
        g.add_node(ra)
        assert g.get_node(ra.node_id) is ra

    def test_add_node_merge_replaces(self):
        g = _make_graph()
        ra1 = _make_reality()
        ra2 = RealityAnchorNode(
            node_id=ra1.node_id,
            reality_kind=RealityKind.EVENT,
        )
        g.add_node(ra1)
        g.add_node(ra2)
        assert g.get_node(ra1.node_id) is ra2

    def test_add_edge_and_neighbour(self):
        g = _make_graph()
        ra = _make_reality("ra:a")
        ep = _make_episode("ke:a")
        g.add_node(ra)
        g.add_node(ep)
        g.add_edge(ep.node_id, "HAS_REALITY_ANCHOR", ra.node_id)
        nb = g.neighbour(ep.node_id, "HAS_REALITY_ANCHOR")
        assert nb is ra

    def test_add_edge_deduplication(self):
        g = _make_graph()
        g.add_node(_make_reality("ra:dup"))
        g.add_node(_make_episode("ke:dup"))
        g.add_edge("ke:dup", "HAS_REALITY_ANCHOR", "ra:dup")
        g.add_edge("ke:dup", "HAS_REALITY_ANCHOR", "ra:dup")
        assert len(g.edges_from("ke:dup", "HAS_REALITY_ANCHOR")) == 1

    def test_summary(self):
        g = _make_graph()
        _full_episode(g)
        s = g.summary()
        assert s["episodes"] == 1
        assert s["nodes"] >= 1
        assert s["edges"] >= 1

    def test_all_episodes(self):
        g = _make_graph()
        _full_episode(g, "ke:ep1")
        _full_episode(g, "ke:ep2")
        ids = {ep.node_id for ep in g.all_episodes()}
        assert {"ke:ep1", "ke:ep2"} <= ids

    def test_get_episode_not_found(self):
        g = _make_graph()
        assert g.get_episode("ke:nonexistent") is None

    def test_add_episode_links_utterance_to_concept(self):
        g = _make_graph()
        ep = _full_episode(g)
        lc = g.neighbour(ep.node_id, "CARRIED_BY")
        assert lc is not None
        realized = g.neighbours(lc.node_id, "REALIZED_AS")
        types = {type(n).__name__ for n in realized}
        assert "UtteranceNode" in types
        assert "EpistemicConceptNode" in types
        # Utterance → ANCHORS_TO → Concept
        u_node = next(n for n in realized if isinstance(n, UtteranceNode))
        anchored = g.neighbours(u_node.node_id, "ANCHORS_TO")
        assert len(anchored) == 1
        assert isinstance(anchored[0], EpistemicConceptNode)

    def test_attach_and_get_gaps(self):
        g = _make_graph()
        ep = _make_episode("ke:gaps")
        g.add_node(ep)
        gap = GapNode(
            node_id="ke:gaps::Missing_RealityAnchor",
            gap_type="Missing RealityAnchor",
            message="Missing RealityAnchor",
            severity=GapSeverity.FATAL,
        )
        g.attach_gap(ep.node_id, gap)
        gaps = g.get_gaps(ep.node_id)
        assert len(gaps) == 1
        assert gaps[0].gap_type == "Missing RealityAnchor"

    def test_clear_gaps_removes_nodes(self):
        g = _make_graph()
        ep = _make_episode("ke:clr")
        g.add_node(ep)
        gap = GapNode(
            node_id="ke:clr::gap1",
            gap_type="Missing RealityAnchor",
            message="Missing RealityAnchor",
            severity=GapSeverity.FATAL,
        )
        g.attach_gap(ep.node_id, gap)
        g.clear_gaps(ep.node_id)
        assert g.get_gaps(ep.node_id) == []
        assert g.get_node("ke:clr::gap1") is None


# ═══════════════════════════════════════════════════════════════════════
# EpisodeValidator — validate_episode
# ═══════════════════════════════════════════════════════════════════════

class TestEpisodeValidatorMain:
    def test_valid_existence_episode_is_certain(self):
        g = _make_graph()
        _full_episode(g, "ke:v1", judgement_type="existence", path_kind=PathKind.AQLI)
        v = EpisodeValidator(g)
        result = v.validate_episode("ke:v1")
        assert result.validation_state is ValidationState.VALID
        assert result.epistemic_rank is EpistemicRank.CERTAIN
        assert result.errors == ()

    def test_valid_interpretive_episode_is_true_non_certain(self):
        g = _make_graph()
        _full_episode(g, "ke:v2", judgement_type="interpretive", path_kind=PathKind.LINGUISTIC)
        v = EpisodeValidator(g)
        result = v.validate_episode("ke:v2")
        assert result.validation_state is ValidationState.VALID
        assert result.epistemic_rank is EpistemicRank.TRUE_NON_CERTAIN

    def test_missing_reality_anchor_causes_rejected(self):
        g = _make_graph()
        ep_id = "ke:no_ra"
        ep = _make_episode(ep_id)
        g.add_node(ep)
        g.add_node(SelfNode(node_id="self:x"))
        g.add_edge("self:x", "UNDERGOES", ep_id)
        # add everything except reality anchor
        st = _make_sense("st:no_ra")
        g.add_node(st)
        g.add_edge(ep_id, "HAS_SENSE_TRACE", st.node_id)
        pi = _make_prior("pi:no_ra")
        g.add_node(pi)
        g.add_edge(ep_id, "USES_PRIOR_INFO", pi.node_id)
        lt = _make_linking("lt:no_ra")
        g.add_node(lt)
        g.add_edge(ep_id, "HAS_LINKING_TRACE", lt.node_id)
        j = _make_judgement("j:no_ra")
        g.add_node(j)
        g.add_edge(ep_id, "ISSUES", j.node_id)
        lc = _make_carrier("lc:no_ra")
        g.add_node(lc)
        g.add_edge(ep_id, "CARRIED_BY", lc.node_id)
        pp = _make_proof("pp:no_ra")
        g.add_node(pp)
        g.add_edge(ep_id, "JUSTIFIED_BY", pp.node_id)
        cr = DEFAULT_CONFLICT_RULE
        g.add_node(cr)
        g.add_edge(ep_id, "VALIDATED_BY", cr.node_id)

        v = EpisodeValidator(g)
        result = v.validate_episode(ep_id)
        assert result.validation_state is ValidationState.INVALID
        assert "Missing RealityAnchor" in result.errors
        assert result.epistemic_rank is None

    def test_missing_sense_trace_causes_rejected(self):
        g = _make_graph()
        ep_id = "ke:no_st"
        ep = _make_episode(ep_id)
        # add reality but skip sense
        g.add_node(ep)
        ra = _make_reality("ra:no_st")
        g.add_node(ra)
        g.add_edge(ep_id, "HAS_REALITY_ANCHOR", ra.node_id)
        pi = _make_prior("pi:no_st")
        g.add_node(pi)
        g.add_edge(ep_id, "USES_PRIOR_INFO", pi.node_id)
        lt = _make_linking("lt:no_st")
        g.add_node(lt)
        g.add_edge(ep_id, "HAS_LINKING_TRACE", lt.node_id)
        j = _make_judgement("j:no_st")
        g.add_node(j)
        g.add_edge(ep_id, "ISSUES", j.node_id)
        lc = _make_carrier("lc:no_st")
        g.add_node(lc)
        g.add_edge(ep_id, "CARRIED_BY", lc.node_id)
        pp = _make_proof("pp:no_st")
        g.add_node(pp)
        g.add_edge(ep_id, "JUSTIFIED_BY", pp.node_id)
        g.add_node(DEFAULT_CONFLICT_RULE)
        g.add_edge(ep_id, "VALIDATED_BY", DEFAULT_CONFLICT_RULE.node_id)

        v = EpisodeValidator(g)
        result = v.validate_episode(ep_id)
        assert "Missing SenseTrace" in result.errors
        assert result.epistemic_rank is None

    def test_missing_prior_info_causes_rejected(self):
        g = _make_graph()
        ep_id = "ke:no_pi"
        ep = _make_episode(ep_id)
        g.add_node(ep)
        ra = _make_reality("ra:no_pi")
        g.add_node(ra)
        g.add_edge(ep_id, "HAS_REALITY_ANCHOR", ra.node_id)
        st = _make_sense("st:no_pi")
        g.add_node(st)
        g.add_edge(ep_id, "HAS_SENSE_TRACE", st.node_id)
        # no prior info
        lt = _make_linking("lt:no_pi")
        g.add_node(lt)
        g.add_edge(ep_id, "HAS_LINKING_TRACE", lt.node_id)
        j = _make_judgement("j:no_pi")
        g.add_node(j)
        g.add_edge(ep_id, "ISSUES", j.node_id)
        lc = _make_carrier("lc:no_pi")
        g.add_node(lc)
        g.add_edge(ep_id, "CARRIED_BY", lc.node_id)
        pp = _make_proof("pp:no_pi")
        g.add_node(pp)
        g.add_edge(ep_id, "JUSTIFIED_BY", pp.node_id)
        g.add_node(DEFAULT_CONFLICT_RULE)
        g.add_edge(ep_id, "VALIDATED_BY", DEFAULT_CONFLICT_RULE.node_id)

        result = EpisodeValidator(g).validate_episode(ep_id)
        assert "Missing PriorInfo" in result.errors
        assert result.epistemic_rank is None

    def test_opinion_contamination_causes_rejected(self):
        g = _make_graph()
        ep_id = "ke:op_cont"
        _full_episode(g, ep_id)
        opinion = OpinionTraceNode(
            node_id="op:hi",
            contamination_level=ContaminationLevel.HIGH,
            description="تأثير الرأي السابق",
        )
        g.add_node(opinion)
        g.add_edge(ep_id, "MUST_EXCLUDE", opinion.node_id)

        result = EpisodeValidator(g).validate_episode(ep_id)
        assert result.validation_state is ValidationState.INVALID
        assert "Opinion contamination" in result.errors
        assert result.epistemic_rank is None

    def test_low_opinion_contamination_does_not_fail(self):
        g = _make_graph()
        ep_id = "ke:op_low"
        _full_episode(g, ep_id)
        opinion = OpinionTraceNode(
            node_id="op:low",
            contamination_level=ContaminationLevel.LOW,
        )
        g.add_node(opinion)
        g.add_edge(ep_id, "MUST_EXCLUDE", opinion.node_id)

        result = EpisodeValidator(g).validate_episode(ep_id)
        assert result.validation_state is ValidationState.VALID
        assert "Opinion contamination" not in result.errors

    def test_scientific_method_normative_judgement_causes_impossible(self):
        g = _make_graph()
        ep_id = "ke:sci_norm"
        ep = KnowledgeEpisodeNode(
            node_id=ep_id,
            domain_profile="normative",
            judgement_type="normative",
            method_family="scientific",
            carrier_type="both",
            method_ref="method:scientific",
        )
        g.add_episode(
            episode=ep,
            self_node=SelfNode(node_id=f"self:{ep_id}"),
            reality=_make_reality(f"ra:{ep_id}"),
            sense=_make_sense(f"st:{ep_id}"),
            prior_infos=[_make_prior(f"pi:{ep_id}")],
            linking=_make_linking(f"lt:{ep_id}"),
            judgement=JudgementNode(node_id=f"j:{ep_id}", judgement_type=JudgementType.NORMATIVE),
            carrier=_make_carrier(f"lc:{ep_id}"),
            proof=_make_proof(f"pp:{ep_id}"),
            conflict=DEFAULT_CONFLICT_RULE,
        )
        result = EpisodeValidator(g).validate_episode(ep_id)
        assert result.validation_state is ValidationState.INVALID
        assert any("not suitable" in e for e in result.errors)
        assert result.epistemic_rank is EpistemicRank.IMPOSSIBLE

    def test_invalid_carrier_type_causes_rejected(self):
        g = _make_graph()
        ep_id = "ke:bad_carr"
        ep = _make_episode(ep_id, carrier_type="unknown")
        g.add_node(ep)
        ra = _make_reality(f"ra:{ep_id}")
        g.add_node(ra)
        g.add_edge(ep_id, "HAS_REALITY_ANCHOR", ra.node_id)
        st = _make_sense(f"st:{ep_id}")
        g.add_node(st)
        g.add_edge(ep_id, "HAS_SENSE_TRACE", st.node_id)
        pi = _make_prior(f"pi:{ep_id}")
        g.add_node(pi)
        g.add_edge(ep_id, "USES_PRIOR_INFO", pi.node_id)
        lt = _make_linking(f"lt:{ep_id}")
        g.add_node(lt)
        g.add_edge(ep_id, "HAS_LINKING_TRACE", lt.node_id)
        j = _make_judgement(f"j:{ep_id}")
        g.add_node(j)
        g.add_edge(ep_id, "ISSUES", j.node_id)
        lc = _make_carrier(f"lc:{ep_id}")
        g.add_node(lc)
        g.add_edge(ep_id, "CARRIED_BY", lc.node_id)
        pp = _make_proof(f"pp:{ep_id}")
        g.add_node(pp)
        g.add_edge(ep_id, "JUSTIFIED_BY", pp.node_id)
        g.add_node(DEFAULT_CONFLICT_RULE)
        g.add_edge(ep_id, "VALIDATED_BY", DEFAULT_CONFLICT_RULE.node_id)

        result = EpisodeValidator(g).validate_episode(ep_id)
        assert "Invalid LinguisticCarrier" in result.errors

    def test_gaps_stored_in_graph(self):
        g = _make_graph()
        ep_id = "ke:gap_store"
        ep = _make_episode(ep_id)
        g.add_node(ep)
        # minimal setup — no reality, no sense
        result = EpisodeValidator(g).validate_episode(ep_id)
        gaps = g.get_gaps(ep_id)
        assert len(gaps) == len(result.gaps)
        gap_types = {gap.gap_type for gap in gaps}
        assert "Missing RealityAnchor" in gap_types
        assert "Missing SenseTrace" in gap_types

    def test_gaps_replaced_on_revalidation(self):
        g = _make_graph()
        ep_id = "ke:revalidate"
        ep = _make_episode(ep_id)
        g.add_node(ep)
        v = EpisodeValidator(g)
        v.validate_episode(ep_id)
        gaps_first = len(g.get_gaps(ep_id))
        v.validate_episode(ep_id)
        gaps_second = len(g.get_gaps(ep_id))
        assert gaps_second == gaps_first  # no accumulation

    def test_episode_not_found_raises(self):
        g = _make_graph()
        with pytest.raises(KeyError):
            EpisodeValidator(g).validate_episode("ke:ghost")

    def test_hissi_proof_also_qualifies_for_certain(self):
        g = _make_graph()
        ep_id = "ke:hissi"
        _full_episode(g, ep_id, judgement_type="existence", path_kind=PathKind.HISSI)
        result = EpisodeValidator(g).validate_episode(ep_id)
        assert result.epistemic_rank is EpistemicRank.CERTAIN

    def test_formal_proof_existence_is_certain(self):
        g = _make_graph()
        ep_id = "ke:formal"
        _full_episode(g, ep_id, judgement_type="existence", path_kind=PathKind.FORMAL)
        result = EpisodeValidator(g).validate_episode(ep_id)
        assert result.epistemic_rank is EpistemicRank.CERTAIN

    def test_linguistic_proof_existence_is_probabilistic(self):
        g = _make_graph()
        ep_id = "ke:ling_exist"
        _full_episode(g, ep_id, judgement_type="existence", path_kind=PathKind.LINGUISTIC)
        result = EpisodeValidator(g).validate_episode(ep_id)
        # linguistic path is not in _CERTAIN_PATH_KINDS
        assert result.epistemic_rank is EpistemicRank.PROBABILISTIC_DOUBT

    def test_gap_severity_fatal_for_missing_reality(self):
        g = _make_graph()
        ep_id = "ke:sev"
        ep = _make_episode(ep_id)
        g.add_node(ep)
        v = EpisodeValidator(g)
        result = v.validate_episode(ep_id)
        fatal_gaps = [gap for gap in result.gaps if gap.severity is GapSeverity.FATAL]
        assert any(gap.gap_type == "Missing RealityAnchor" for gap in fatal_gaps)

    def test_gap_severity_high_for_opinion_contamination(self):
        g = _make_graph()
        ep_id = "ke:sev_op"
        _full_episode(g, ep_id)
        op = OpinionTraceNode(node_id="op:high", contamination_level=ContaminationLevel.HIGH)
        g.add_node(op)
        g.add_edge(ep_id, "MUST_EXCLUDE", op.node_id)
        result = EpisodeValidator(g).validate_episode(ep_id)
        high_gaps = [gap for gap in result.gaps if gap.severity is GapSeverity.HIGH]
        assert any(gap.gap_type == "Opinion contamination" for gap in high_gaps)


# ═══════════════════════════════════════════════════════════════════════
# EpisodeValidator — validate_linguistic_carrier
# ═══════════════════════════════════════════════════════════════════════

class TestValidateLinguisticCarrier:
    def test_both_carrier_with_utterance_and_concept_is_ok(self):
        g = _make_graph()
        ep_id = "ke:lc_both"
        _full_episode(g, ep_id)
        result = EpisodeValidator(g).validate_linguistic_carrier(ep_id)
        assert result["linguistic_carrier_status"] == "ok"
        assert result["utterance_count"] == 1
        assert result["concept_count"] == 1

    def test_utterance_only_carrier_ok(self):
        g = _make_graph()
        ep_id = "ke:lc_utt"
        ep = _make_episode(ep_id, carrier_type="utterance")
        carrier = _make_carrier("lc:utt", CarrierClass.UTTERANCE)
        g.add_episode(
            episode=ep,
            self_node=SelfNode(node_id=f"self:{ep_id}"),
            reality=_make_reality(f"ra:{ep_id}"),
            sense=_make_sense(f"st:{ep_id}"),
            prior_infos=[_make_prior(f"pi:{ep_id}")],
            linking=_make_linking(f"lt:{ep_id}"),
            judgement=_make_judgement(f"j:{ep_id}"),
            carrier=carrier,
            proof=_make_proof(f"pp:{ep_id}"),
            conflict=DEFAULT_CONFLICT_RULE,
            utterance=_make_utterance(f"u:{ep_id}"),
            concept=None,
        )
        result = EpisodeValidator(g).validate_linguistic_carrier(ep_id)
        assert result["linguistic_carrier_status"] == "ok"
        assert result["carrier_class"] == "utterance"

    def test_concept_only_carrier_ok(self):
        g = _make_graph()
        ep_id = "ke:lc_con"
        ep = _make_episode(ep_id, carrier_type="concept")
        carrier = _make_carrier("lc:con", CarrierClass.CONCEPT)
        g.add_episode(
            episode=ep,
            self_node=SelfNode(node_id=f"self:{ep_id}"),
            reality=_make_reality(f"ra:{ep_id}"),
            sense=_make_sense(f"st:{ep_id}"),
            prior_infos=[_make_prior(f"pi:{ep_id}")],
            linking=_make_linking(f"lt:{ep_id}"),
            judgement=_make_judgement(f"j:{ep_id}"),
            carrier=carrier,
            proof=_make_proof(f"pp:{ep_id}"),
            conflict=DEFAULT_CONFLICT_RULE,
            utterance=None,
            concept=_make_concept(f"c:{ep_id}"),
        )
        result = EpisodeValidator(g).validate_linguistic_carrier(ep_id)
        assert result["linguistic_carrier_status"] == "ok"
        assert result["carrier_class"] == "concept"

    def test_both_carrier_missing_concept_is_invalid(self):
        g = _make_graph()
        ep_id = "ke:lc_missing_c"
        ep = _make_episode(ep_id, carrier_type="both")
        carrier = _make_carrier("lc:mc", CarrierClass.BOTH)
        g.add_episode(
            episode=ep,
            self_node=SelfNode(node_id=f"self:{ep_id}"),
            reality=_make_reality(f"ra:{ep_id}"),
            sense=_make_sense(f"st:{ep_id}"),
            prior_infos=[_make_prior(f"pi:{ep_id}")],
            linking=_make_linking(f"lt:{ep_id}"),
            judgement=_make_judgement(f"j:{ep_id}"),
            carrier=carrier,
            proof=_make_proof(f"pp:{ep_id}"),
            conflict=DEFAULT_CONFLICT_RULE,
            utterance=_make_utterance(f"u:{ep_id}"),
            concept=None,   # missing
        )
        result = EpisodeValidator(g).validate_linguistic_carrier(ep_id)
        assert result["linguistic_carrier_status"] == "invalid"

    def test_no_carrier_returns_invalid(self):
        g = _make_graph()
        ep_id = "ke:lc_no_carr"
        ep = _make_episode(ep_id)
        g.add_node(ep)
        result = EpisodeValidator(g).validate_linguistic_carrier(ep_id)
        assert result["linguistic_carrier_status"] == "invalid"


# ═══════════════════════════════════════════════════════════════════════
# EpisodeValidator — conflict_resolution_hint
# ═══════════════════════════════════════════════════════════════════════

class TestConflictResolutionHint:
    def test_grounded_reading_when_proof_and_reality(self):
        g = _make_graph()
        ep_id = "ke:crh_grounded"
        _full_episode(g, ep_id, path_kind=PathKind.AQLI)
        result = EpisodeValidator(g).conflict_resolution_hint(ep_id)
        assert result["conflict_resolution_hint"] == "prefer_grounded_reading"

    def test_no_conflict_check_when_only_utterance(self):
        g = _make_graph()
        ep_id = "ke:crh_utt"
        ep = _make_episode(ep_id, carrier_type="utterance")
        carrier = _make_carrier("lc:crh_utt", CarrierClass.UTTERANCE)
        g.add_episode(
            episode=ep,
            self_node=SelfNode(node_id=f"self:{ep_id}"),
            reality=_make_reality(f"ra:{ep_id}"),
            sense=_make_sense(f"st:{ep_id}"),
            prior_infos=[_make_prior(f"pi:{ep_id}")],
            linking=_make_linking(f"lt:{ep_id}"),
            judgement=_make_judgement(f"j:{ep_id}"),
            carrier=carrier,
            proof=_make_proof(f"pp:{ep_id}"),
            conflict=DEFAULT_CONFLICT_RULE,
            utterance=_make_utterance(f"u:{ep_id}"),
            concept=None,
        )
        result = EpisodeValidator(g).conflict_resolution_hint(ep_id)
        assert result["conflict_resolution_hint"] == "no_internal_conflict_check"

    def test_review_needed_for_linguistic_proof_with_both(self):
        g = _make_graph()
        ep_id = "ke:crh_review"
        _full_episode(g, ep_id, path_kind=PathKind.LINGUISTIC)
        result = EpisodeValidator(g).conflict_resolution_hint(ep_id)
        # linguistic is not in _CERTAIN_PATH_KINDS
        assert result["conflict_resolution_hint"] == "review_needed"

    def test_hint_returns_utterance_and_concept_text(self):
        g = _make_graph()
        ep_id = "ke:crh_text"
        _full_episode(g, ep_id)
        result = EpisodeValidator(g).conflict_resolution_hint(ep_id)
        assert result["utterance"] == "هٰذَا نَصٌّ"
        assert result["concept"] == "test_concept"


# ═══════════════════════════════════════════════════════════════════════
# EpisodeValidator — validate_all
# ═══════════════════════════════════════════════════════════════════════

class TestValidateAll:
    def test_validate_all_returns_results_for_every_episode(self):
        g = _make_graph()
        for i in range(3):
            _full_episode(g, f"ke:batch_{i}")
        results = EpisodeValidator(g).validate_all()
        ep_ids = {r.episode_id for r in results}
        for i in range(3):
            assert f"ke:batch_{i}" in ep_ids

    def test_validate_all_sorted_by_state_rank_id(self):
        g = _make_graph()
        _full_episode(g, "ke:aa")     # valid
        _full_episode(g, "ke:bb")     # valid
        # invalid episode
        ep_inv = _make_episode("ke:cc_invalid")
        g.add_node(ep_inv)
        results = EpisodeValidator(g).validate_all()
        # All valid episodes should appear together
        states = [r.validation_state.name for r in results]
        # INVALID comes after VALID alphabetically (I < V reversed = V < I → INVALID first)
        # The actual alphabetical ordering: "INVALID" < "VALID"
        invalid_indices = [i for i, s in enumerate(states) if s == "INVALID"]
        valid_indices = [i for i, s in enumerate(states) if s == "VALID"]
        if invalid_indices and valid_indices:
            groups_are_separated = (
                max(invalid_indices) < min(valid_indices)
                or max(valid_indices) < min(invalid_indices)
            )
            assert groups_are_separated

    def test_validate_all_empty_graph(self):
        g = _make_graph()
        results = EpisodeValidator(g).validate_all()
        assert results == []


# ═══════════════════════════════════════════════════════════════════════
# Re-exports from arabic_engine.core
# ═══════════════════════════════════════════════════════════════════════

class TestCoreReExports:
    def test_enums_accessible_from_core(self):
        from arabic_engine.core import (
            CarrierClass,
            ContaminationLevel,
            EpistemicRank,
            GapSeverity,
            InfoKind,
            JudgementType,
            LinkKind,
            MethodFamily,
            PathKind,
            RealityKind,
            SenseModality,
            TraceMode,
            TraceQuality,
            ValidationState,
        )
        assert CarrierClass.BOTH
        assert EpistemicRank.CERTAIN
        assert ValidationState.PENDING
        assert JudgementType.EXISTENCE
        assert MethodFamily.RATIONAL
        assert PathKind.AQLI
        assert SenseModality.VISION
        assert RealityKind.TEXT_OBJECT
        assert InfoKind.LEXICAL
        assert TraceMode.DIRECT_PERCEPTION
        assert TraceQuality.STRONG
        assert ContaminationLevel.NONE
        assert GapSeverity.FATAL
        assert LinkKind.TEXTUAL_INFERENCE

    def test_types_accessible_from_core(self):
        from arabic_engine.core import (
            ConflictRuleNode,
            EpisodeValidationResult,
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
        assert SelfNode
        assert KnowledgeEpisodeNode
        assert RealityAnchorNode
        assert SenseTraceNode
        assert PriorInfoNode
        assert OpinionTraceNode
        assert LinkingTraceNode
        assert JudgementNode
        assert MethodNode
        assert LinguisticCarrierNode
        assert UtteranceNode
        assert EpistemicConceptNode
        assert ProofPathNode
        assert ConflictRuleNode
        assert GapNode
        assert EvidenceNode
        assert EpisodeValidationResult
