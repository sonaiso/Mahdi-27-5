"""World model — a minimal knowledge base of facts (v2).

Provides the *W* in the evaluation function  E : P × W → V.

The world model stores ground-truth facts and allows the evaluation
layer to compare incoming propositions against known reality, raising
or lowering confidence accordingly.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from arabic_engine.core.enums import TruthState, ValidationState
from arabic_engine.core.types import Proposition, WorldFact

_next_fact_id = 0


class WorldModel:
    """An in-memory fact store representing the current world state.

    The world model stores ground-truth :class:`~arabic_engine.core.types.WorldFact`
    objects and exposes query methods used by the evaluation layer to raise
    or lower confidence based on known reality.

    Facts are indexed by *subject* string for O(1) subject-based lookups.

    Example::

        wm = WorldModel()
        wm.add_fact("زَيْد", "كَتَبَ", "رِسَالَة", TruthState.CERTAIN)
        fact = wm.matches(proposition)
    """

    def __init__(self) -> None:
        """Initialise an empty world model."""
        self._facts: Dict[int, WorldFact] = {}
        self._index: Dict[str, List[int]] = {}  # subject → fact_ids

    # ── Mutation ─────────────────────────────────────────────────

    def add_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
        truth_state: TruthState = TruthState.CERTAIN,
        source: str = "axiom",
    ) -> WorldFact:
        """Insert a new fact and return it.

        Args:
            subject: The subject of the fact (e.g. ``"زَيْد"``).
            predicate: The predicate (e.g. ``"كَتَبَ"``).
            obj: The object of the fact (e.g. ``"رِسَالَة"``).
            truth_state: Epistemic status of the fact.  Defaults to
                ``TruthState.CERTAIN``.
            source: Provenance label (e.g. ``"axiom"``, ``"witness"``).

        Returns:
            The newly created :class:`~arabic_engine.core.types.WorldFact`.
        """
        global _next_fact_id
        _next_fact_id += 1
        fact = WorldFact(
            fact_id=_next_fact_id,
            subject=subject,
            predicate=predicate,
            obj=obj,
            truth_state=truth_state,
            source=source,
        )
        self._facts[fact.fact_id] = fact
        self._index.setdefault(subject, []).append(fact.fact_id)
        return fact

    # ── Query ────────────────────────────────────────────────────

    def lookup(
        self,
        subject: str,
        predicate: Optional[str] = None,
    ) -> List[WorldFact]:
        """Return facts matching *subject* (and optionally *predicate*).

        Args:
            subject: Subject string to look up in the index.
            predicate: Optional predicate filter.  When provided, only
                facts whose predicate equals this value are returned.

        Returns:
            A (possibly empty) list of matching
            :class:`~arabic_engine.core.types.WorldFact` objects.
        """
        ids = self._index.get(subject, [])
        results = [self._facts[fid] for fid in ids]
        if predicate is not None:
            results = [f for f in results if f.predicate == predicate]
        return results

    def matches(self, proposition: Proposition) -> Optional[WorldFact]:
        """Check if a proposition is supported by a known fact.

        Args:
            proposition: The proposition to look up.

        Returns:
            The first matching :class:`~arabic_engine.core.types.WorldFact`
            if found, or ``None`` when no matching fact exists.
        """
        candidates = self.lookup(proposition.subject, proposition.predicate)
        for fact in candidates:
            if fact.obj == proposition.obj:
                return fact
        return None

    def confidence_adjustment(self, proposition: Proposition) -> float:
        """Return a confidence multiplier based on world-model support.

        The multiplier is applied to the dalāla confidence score produced
        by the evaluation layer.

        Returns:
            A float in ``[0.0, 1.0]`` according to the following table:

            ============  ========  =================================
            Match found?  State     Multiplier
            ============  ========  =================================
            Yes           CERTAIN   1.0
            Yes           PROBABLE  0.8
            Yes           FALSE     0.1 (contradicted)
            Yes           Other     0.5
            No            —         0.5 (no evidence)
            ============  ========  =================================
        """
        fact = self.matches(proposition)
        if fact is None:
            return 0.5  # no evidence
        if fact.truth_state == TruthState.CERTAIN:
            return 1.0
        if fact.truth_state == TruthState.PROBABLE:
            return 0.8
        if fact.truth_state == TruthState.FALSE:
            return 0.1
        return 0.5

    def apply_validated_proposition(
        self,
        proposition: Proposition,
        validation_state: ValidationState,
        source: str = "pipeline",
    ) -> dict:
        """Update world facts only when validation state is VALID."""
        if validation_state != ValidationState.VALID:
            return {
                "applied": False,
                "reason": f"validation_state={validation_state.name}",
                "fact_id": None,
            }
        fact = self.add_fact(
            subject=proposition.subject,
            predicate=proposition.predicate,
            obj=proposition.obj,
            truth_state=TruthState.CERTAIN,
            source=source,
        )
        return {"applied": True, "reason": "validated", "fact_id": fact.fact_id}

    @property
    def all_facts(self) -> List[WorldFact]:
        """All facts currently held in the world model.

        Returns:
            A list of every :class:`~arabic_engine.core.types.WorldFact`
            in insertion order.
        """
        return list(self._facts.values())
