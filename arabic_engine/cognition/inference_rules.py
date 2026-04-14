"""Inference rules — simple forward-chaining rule engine (v2).

Applies syllogistic and modus-ponens-style inference rules to
propositions, producing derived conclusions with tracked provenance.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from arabic_engine.core.types import InferenceResult, Proposition

# ── Rule type ───────────────────────────────────────────────────────

RuleFunc = Callable[[List[Proposition]], Optional[InferenceResult]]


# ── Built-in rules ──────────────────────────────────────────────────

def _transitivity_rule(propositions: List[Proposition]) -> Optional[InferenceResult]:
    """If A→B and B→C then A→C (simplified transitivity).

    Matches propositions where the object of one equals the subject
    of another sharing the same predicate.
    """
    for p1 in propositions:
        for p2 in propositions:
            if p1 is p2:
                continue
            if p1.obj == p2.subject and p1.predicate == p2.predicate:
                conclusion = Proposition(
                    subject=p1.subject,
                    predicate=p1.predicate,
                    obj=p2.obj,
                    time=p1.time,
                    polarity=p1.polarity and p2.polarity,
                )
                return InferenceResult(
                    rule_name="transitivity",
                    premises=[p1, p2],
                    conclusion=conclusion,
                    confidence=0.85,
                    valid=True,
                    rule_category="existential",
                    conditions=(
                        "p1.obj == p2.subject",
                        "p1.predicate == p2.predicate",
                    ),
                    outcome="derived transitive proposition",
                    strength=0.85,
                    explanation="Applied transitivity over two aligned propositions.",
                )
    return None


def _negation_rule(propositions: List[Proposition]) -> Optional[InferenceResult]:
    """If both P and ¬P exist, flag contradiction."""
    for p1 in propositions:
        for p2 in propositions:
            if p1 is p2:
                continue
            if (
                p1.subject == p2.subject
                and p1.predicate == p2.predicate
                and p1.obj == p2.obj
                and p1.polarity != p2.polarity
            ):
                return InferenceResult(
                    rule_name="contradiction",
                    premises=[p1, p2],
                    conclusion=p1,  # mark the affirmative as suspect
                    confidence=0.0,
                    valid=False,
                    rule_category="contradiction",
                    conditions=(
                        "same subject",
                        "same predicate",
                        "same object",
                        "opposite polarity",
                    ),
                    outcome="contradiction detected",
                    strength=1.0,
                    explanation=(
                        "Detected both affirmative and negative forms "
                        "of the same proposition."
                    ),
                )
    return None


def _event_existence_rule(propositions: List[Proposition]) -> Optional[InferenceResult]:
    """Derive event_existence: if S did P to O, then the event P exists.

    From a proposition with subject, predicate, and object, conclude
    that the event denoted by the predicate actually took place.
    """
    for p in propositions:
        if p.subject and p.predicate and p.polarity:
            conclusion = Proposition(
                subject=p.predicate,
                predicate="وُجِدَ",     # "existed"
                obj="",
                time=p.time,
                space=p.space,
                polarity=True,
            )
            return InferenceResult(
                rule_name="event_existence",
                premises=[p],
                conclusion=conclusion,
                confidence=0.9,
                valid=True,
                rule_category="existential",
                conditions=(
                    "subject present",
                    "predicate present",
                    "polarity is affirmative",
                ),
                outcome="event existence asserted",
                strength=0.9,
                explanation="From an affirmative event proposition, infer event existence.",
            )
    return None


# ── Rule engine ─────────────────────────────────────────────────────

_DEFAULT_RULES: List[RuleFunc] = [
    _event_existence_rule,
    _transitivity_rule,
    _negation_rule,
]


class InferenceEngine:
    """A simple forward-chaining inference engine.

    The engine holds an ordered list of :data:`RuleFunc` callables.
    Each rule receives the current proposition list and may return a
    single :class:`~arabic_engine.core.types.InferenceResult`, or
    ``None`` if the rule does not fire.

    Default rules (applied in order):

    1. ``event_existence_rule`` — derives that the event denoted by the
       predicate actually took place.
    2. ``transitivity_rule`` — applies A→B, B→C ⇒ A→C.
    3. ``negation_rule`` — flags a contradiction when both P and ¬P exist.

    Example::

        engine = InferenceEngine()
        results = engine.run([proposition])

    Args:
        rules: Optional list of rule callables to use instead of the
            defaults.  Each callable must match the :data:`RuleFunc`
            signature ``(List[Proposition]) -> Optional[InferenceResult]``.
    """

    def __init__(self, rules: Optional[List[RuleFunc]] = None) -> None:
        """Initialise the engine with *rules* (or the built-in defaults).

        Args:
            rules: Custom rule list.  When ``None``, :data:`_DEFAULT_RULES`
                is used.
        """
        self.rules: List[RuleFunc] = rules if rules is not None else list(_DEFAULT_RULES)

    def run(self, propositions: List[Proposition]) -> List[InferenceResult]:
        """Apply all rules once to *propositions* and return derived results.

        Each rule in :attr:`rules` is called with the full proposition list.
        Rules that fire (return a non-``None`` result) contribute to the
        output; rules that do not fire are silently skipped.

        Args:
            propositions: Current set of propositions to reason over.

        Returns:
            A list of :class:`~arabic_engine.core.types.InferenceResult`
            objects, one per rule that fired.  May be empty.
        """
        results: List[InferenceResult] = []
        for rule in self.rules:
            result = rule(propositions)
            if result is not None:
                results.append(result)
        return results

    def run_until_fixed(
        self,
        propositions: List[Proposition],
        max_iterations: int = 10,
    ) -> List[InferenceResult]:
        """Repeatedly apply rules until no new conclusions are derived.

        At each iteration the derived conclusions (from valid results) are
        appended to the working proposition set and the rules are re-run.
        The loop terminates when no rule fires *or* after *max_iterations*
        rounds, whichever comes first.

        Args:
            propositions: Initial proposition set.
            max_iterations: Upper bound on the number of rule-application
                rounds.  Prevents infinite loops in cyclic rule sets.

        Returns:
            All :class:`~arabic_engine.core.types.InferenceResult` objects
            derived across all iterations (accumulated, not de-duplicated).
        """
        all_results: List[InferenceResult] = []
        current = list(propositions)

        for _ in range(max_iterations):
            new_results = self.run(current)
            if not new_results:
                break
            all_results.extend(new_results)
            # Add derived conclusions as new propositions
            current.extend(r.conclusion for r in new_results if r.valid)

        return all_results
