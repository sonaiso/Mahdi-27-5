"""Episode Validator — محقق الخبرة المعرفية.

Implements the five-layer validation logic described in the schema
specification (sections 5–7):

* **validate_episode** — the main validator (section 5).
* **validate_linguistic_carrier** — checks the منطوق / مفهوم layer (section 6).
* **conflict_resolution_hint** — returns a resolution hint for the
  utterance-concept pair (section 7).
* **validate_all** — batch validator over all episodes (section 8).

The validator reads the graph, evaluates the ten conditions, derives
``validation_state`` and ``epistemic_rank``, and writes ``GapNode``
objects back into the graph for every detected error.

Design notes
------------
* All logic is pure: the validator never mutates global state.
* The validator **does** mutate the :class:`KnowledgeEpisodeNode` object
  stored in the graph (``validation_state`` and ``epistemic_rank``) by
  replacing the node via :meth:`~KnowledgeGraph._update_episode_state`.
  This is correct because :class:`KnowledgeEpisodeNode` is intentionally
  *mutable* to hold the two validator-written fields.
* Gap nodes are replaced (not accumulated) on each validation run.
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.cognition.knowledge_graph import KnowledgeGraph
from arabic_engine.core.enums import (
    CarrierClass,
    ContaminationLevel,
    EpistemicRank,
    GapSeverity,
    JudgementType,
    MethodFamily,
    PathKind,
    ValidationState,
)
from arabic_engine.core.types import (
    EpisodeValidationResult,
    EpistemicConceptNode,
    GapNode,
    KnowledgeEpisodeNode,
    LinguisticCarrierNode,
    MethodNode,
    OpinionTraceNode,
    PriorInfoNode,
    ProofPathNode,
    RealityAnchorNode,
    SenseTraceNode,
    UtteranceNode,
)

# ── Internal helpers ──────────────────────────────────────────────────

_FATAL_ERRORS = frozenset({
    "Missing RealityAnchor",
    "Missing SenseTrace",
    "Missing PriorInfo",
    "Opinion contamination",
    "Invalid LinguisticCarrier",
})

_CONFLICT_ERRORS_SUBSTR = ("Conflict", "not suitable")

# carrier_type string → CarrierClass member (lower-case names)
_CARRIER_STR: dict[str, CarrierClass] = {
    "utterance": CarrierClass.UTTERANCE,
    "concept": CarrierClass.CONCEPT,
    "both": CarrierClass.BOTH,
}

# JudgementType names that are incompatible with the scientific method
_SCIENTIFIC_INCOMPATIBLE = frozenset({
    JudgementType.NORMATIVE.name.lower(),
    JudgementType.PURE_LINGUISTIC.name.lower(),
    JudgementType.METAPHYSICAL.name.lower(),
})

# JudgementType names that resolve to TRUE_NON_CERTAIN when valid
_NON_CERTAIN_JUDGEMENTS = frozenset({
    JudgementType.ESSENCE.name.lower(),
    JudgementType.ATTRIBUTE.name.lower(),
    JudgementType.RELATION.name.lower(),
    JudgementType.CAUSAL.name.lower(),
    JudgementType.INTERPRETIVE.name.lower(),
    JudgementType.FORMAL.name.lower(),
})

# PathKind names that qualify for CERTAIN rank
_CERTAIN_PATH_KINDS = frozenset({
    PathKind.HISSI.name.lower(),
    PathKind.AQLI.name.lower(),
    PathKind.FORMAL.name.lower(),
})


def _gap_id(episode_id: str, error: str) -> str:
    return episode_id + "::" + error.replace(" ", "_")


# ══════════════════════════════════════════════════════════════════════
# Main validator
# ══════════════════════════════════════════════════════════════════════

class EpisodeValidator:
    """محقق الخبرة المعرفية — validates a single KnowledgeEpisode in a graph.

    Usage::

        validator = EpisodeValidator(graph)
        result = validator.validate_episode("ke:0001")

    The validator is stateless with respect to episodes: every call to
    :meth:`validate_episode` is independent.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        """Initialise the validator against a populated :class:`KnowledgeGraph`.

        Args:
            graph: A graph that has been seeded and has at least one
                   episode assembled via :meth:`~KnowledgeGraph.add_episode`.
        """
        self._graph = graph

    # ── Public API ────────────────────────────────────────────────────

    def validate_episode(self, episode_id: str) -> EpisodeValidationResult:
        """Run the full validation suite against one knowledge episode.

        Implements the ten-condition check from schema section 5.
        Writes ``validation_state``, ``epistemic_rank``, and all
        :class:`~arabic_engine.core.types.GapNode` objects back into
        the graph.

        Args:
            episode_id: The ``node_id`` of the target episode.

        Returns:
            An :class:`~arabic_engine.core.types.EpisodeValidationResult`.

        Raises:
            KeyError: If *episode_id* is not present in the graph.
        """
        ep = self._graph.get_episode(episode_id)
        if ep is None:
            raise KeyError(f"Episode '{episode_id}' not found in graph.")

        errors: List[str] = []

        # ── Condition 1: RealityAnchor ────────────────────────────────
        ra: Optional[RealityAnchorNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "HAS_REALITY_ANCHOR"
        )
        if ra is None:
            errors.append("Missing RealityAnchor")

        # ── Condition 2: SenseTrace ───────────────────────────────────
        st: Optional[SenseTraceNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "HAS_SENSE_TRACE"
        )
        if st is None:
            errors.append("Missing SenseTrace")

        # ── Condition 3: PriorInfo ────────────────────────────────────
        prior_infos: List[PriorInfoNode] = self._graph.neighbours(  # type: ignore[assignment]
            episode_id, "USES_PRIOR_INFO"
        )
        if not prior_infos:
            errors.append("Missing PriorInfo")

        # ── Condition 4: LinkingTrace ─────────────────────────────────
        lt = self._graph.neighbour(episode_id, "HAS_LINKING_TRACE")
        if lt is None:
            errors.append("Missing LinkingTrace")

        # ── Condition 5: JudgementType ────────────────────────────────
        j = self._graph.neighbour(episode_id, "ISSUES")
        if j is None or not ep.judgement_type:
            errors.append("Missing JudgementType")

        # ── Condition 6: MethodFit ────────────────────────────────────
        method: Optional[MethodNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "USES_METHOD"
        )
        if method is None:
            errors.append("Missing MethodFit")

        # ── Condition 7: LinguisticCarrier ────────────────────────────
        carrier: Optional[LinguisticCarrierNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "CARRIED_BY"
        )
        valid_carrier_types = {"utterance", "concept", "both"}
        if carrier is None or ep.carrier_type not in valid_carrier_types:
            errors.append("Invalid LinguisticCarrier")

        # ── Condition 8: ProofPath ────────────────────────────────────
        proof: Optional[ProofPathNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "JUSTIFIED_BY"
        )
        if proof is None:
            errors.append("Missing ProofPath")

        # ── Condition 9: ConflictRule ─────────────────────────────────
        cr = self._graph.neighbour(episode_id, "VALIDATED_BY")
        if cr is None:
            errors.append("Missing ConflictRule")

        # ── Condition 10: Opinion contamination ───────────────────────
        opinions: List[OpinionTraceNode] = self._graph.neighbours(  # type: ignore[assignment]
            episode_id, "MUST_EXCLUDE"
        )
        contaminated = any(
            o.contamination_level in (ContaminationLevel.MEDIUM, ContaminationLevel.HIGH)
            for o in opinions
        )
        if contaminated:
            errors.append("Opinion contamination")

        # ── MethodFit compatibility check ─────────────────────────────
        if (
            method is not None
            and method.method_family is MethodFamily.SCIENTIFIC
            and ep.judgement_type in _SCIENTIFIC_INCOMPATIBLE
        ):
            errors.append("MethodFit failed: scientific method not suitable")

        # ── Derive validation_state ───────────────────────────────────
        ep.validation_state = (
            ValidationState.VALID if not errors else ValidationState.INVALID
        )

        # ── Derive epistemic_rank ─────────────────────────────────────
        ep.epistemic_rank = self._compute_rank(ep, errors, proof)

        # ── Write gap nodes ───────────────────────────────────────────
        self._graph.clear_gaps(episode_id)
        gap_nodes: List[GapNode] = []
        for err in errors:
            gap = GapNode(
                node_id=_gap_id(episode_id, err),
                gap_type=err,
                message=err,
                severity=self._gap_severity(err),
            )
            self._graph.attach_gap(episode_id, gap)
            gap_nodes.append(gap)

        # ── Persist mutated episode ───────────────────────────────────
        self._graph._update_episode_state(ep)

        return EpisodeValidationResult(
            episode_id=episode_id,
            validation_state=ep.validation_state,
            epistemic_rank=ep.epistemic_rank,
            errors=tuple(errors),
            gaps=tuple(gap_nodes),
        )

    def validate_linguistic_carrier(self, episode_id: str) -> dict:
        """Validate the منطوق / مفهوم layer for *episode_id* (schema section 6).

        Returns a dict with keys:
        * ``episode_id``
        * ``carrier_class`` — the carrier class string
        * ``utterance_count`` — number of linked Utterance nodes
        * ``concept_count`` — number of linked Concept nodes
        * ``linguistic_carrier_status`` — ``"ok"`` or ``"invalid"``
        """
        ep = self._graph.get_episode(episode_id)
        if ep is None:
            raise KeyError(f"Episode '{episode_id}' not found in graph.")

        carrier: Optional[LinguisticCarrierNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "CARRIED_BY"
        )
        if carrier is None:
            return {
                "episode_id": episode_id,
                "carrier_class": None,
                "utterance_count": 0,
                "concept_count": 0,
                "linguistic_carrier_status": "invalid",
            }

        lc_id = carrier.node_id
        utterances = self._graph.neighbours(lc_id, "REALIZED_AS")
        u_count = sum(1 for n in utterances if isinstance(n, UtteranceNode))
        c_count = sum(1 for n in utterances if isinstance(n, EpistemicConceptNode))

        cc = carrier.carrier_class
        if cc is CarrierClass.UTTERANCE and u_count >= 1:
            status = "ok"
        elif cc is CarrierClass.CONCEPT and c_count >= 1:
            status = "ok"
        elif cc is CarrierClass.BOTH and u_count >= 1 and c_count >= 1:
            status = "ok"
        else:
            status = "invalid"

        return {
            "episode_id": episode_id,
            "carrier_class": cc.name.lower(),
            "utterance_count": u_count,
            "concept_count": c_count,
            "linguistic_carrier_status": status,
        }

    def conflict_resolution_hint(self, episode_id: str) -> dict:
        """Return a conflict-resolution hint for *episode_id* (schema section 7).

        The rule follows the schema's priority:
        1. Grounded (hissi / aqli / formal proof + reality anchor) → ``"prefer_grounded_reading"``
        2. Only utterance or only concept → ``"no_internal_conflict_check"``
        3. Otherwise → ``"review_needed"``

        Returns a dict with keys:
        * ``episode_id``
        * ``utterance`` — المنطوق text (or ``None``)
        * ``concept`` — المفهوم name (or ``None``)
        * ``reality_kind`` — reality anchor kind (or ``None``)
        * ``proof_kind`` — proof path kind (or ``None``)
        * ``conflict_resolution_hint`` — the hint string
        """
        ep = self._graph.get_episode(episode_id)
        if ep is None:
            raise KeyError(f"Episode '{episode_id}' not found in graph.")

        carrier = self._graph.neighbour(episode_id, "CARRIED_BY")
        utterance_text: Optional[str] = None
        concept_name: Optional[str] = None

        if carrier is not None:
            lc_id = carrier.node_id
            realized = self._graph.neighbours(lc_id, "REALIZED_AS")
            for node in realized:
                if isinstance(node, UtteranceNode):
                    utterance_text = node.text_shakled
                elif isinstance(node, EpistemicConceptNode):
                    concept_name = node.concept_name

        ra = self._graph.neighbour(episode_id, "HAS_REALITY_ANCHOR")
        proof: Optional[ProofPathNode] = self._graph.neighbour(  # type: ignore[assignment]
            episode_id, "JUSTIFIED_BY"
        )

        reality_kind_str = ra.reality_kind.name.lower() if ra is not None else None
        proof_kind_str = proof.path_kind.name.lower() if proof is not None else None

        # Determine hint
        if utterance_text is None or concept_name is None:
            hint = "no_internal_conflict_check"
        elif (
            proof is not None
            and proof.path_kind.name.lower() in _CERTAIN_PATH_KINDS
            and ra is not None
        ):
            hint = "prefer_grounded_reading"
        else:
            hint = "review_needed"

        return {
            "episode_id": episode_id,
            "utterance": utterance_text,
            "concept": concept_name,
            "reality_kind": reality_kind_str,
            "proof_kind": proof_kind_str,
            "conflict_resolution_hint": hint,
        }

    def validate_all(self) -> List[EpisodeValidationResult]:
        """Run the full validation suite on every episode in the graph.

        Returns a list of :class:`~arabic_engine.core.types.EpisodeValidationResult`
        objects sorted by (validation_state, epistemic_rank, episode_id)
        to match the ordering of the batch query (schema section 8).
        """
        results = [
            self.validate_episode(ep.node_id)
            for ep in self._graph.all_episodes()
        ]
        return sorted(
            results,
            key=lambda r: (
                r.validation_state.name,
                r.epistemic_rank.name if r.epistemic_rank else "",
                r.episode_id,
            ),
        )

    # ── Private helpers ───────────────────────────────────────────────

    def _compute_rank(
        self,
        ep: KnowledgeEpisodeNode,
        errors: List[str],
        proof: Optional[ProofPathNode],
    ) -> Optional[EpistemicRank]:
        """Derive the EpistemicRank from the error list and episode metadata."""
        # Fatal structural errors → rejected (None signals methodological rejection)
        if any(e in _FATAL_ERRORS for e in errors):
            return None

        # Method/conflict mismatch → impossible
        if any(
            any(substr in e for substr in _CONFLICT_ERRORS_SUBSTR)
            for e in errors
        ):
            return EpistemicRank.IMPOSSIBLE

        # Valid existence judgement with strong proof → certain
        if (
            not errors
            and ep.judgement_type == JudgementType.EXISTENCE.name.lower()
            and proof is not None
            and proof.path_kind.name.lower() in _CERTAIN_PATH_KINDS
        ):
            return EpistemicRank.CERTAIN

        # Valid essence/attribute/relation/… → true non-certain
        if not errors and ep.judgement_type in _NON_CERTAIN_JUDGEMENTS:
            return EpistemicRank.TRUE_NON_CERTAIN

        return EpistemicRank.PROBABILISTIC_DOUBT

    @staticmethod
    def _gap_severity(error: str) -> GapSeverity:
        """Return the GapSeverity for a given error string."""
        if error in (
            "Missing RealityAnchor",
            "Missing SenseTrace",
            "Missing PriorInfo",
            "Invalid LinguisticCarrier",
        ):
            return GapSeverity.FATAL
        if error == "Opinion contamination":
            return GapSeverity.HIGH
        return GapSeverity.MEDIUM
