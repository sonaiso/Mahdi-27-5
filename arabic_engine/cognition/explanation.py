"""Explainable output builder for v3 pipeline results."""

from __future__ import annotations

from typing import Dict, List

from arabic_engine.core.types import EvaluationResult, InferenceResult, Proposition


def build_explanation(
    proposition: Proposition,
    semantic_roles: Dict[str, str],
    evaluation: EvaluationResult,
    inferences: List[InferenceResult],
    world_update: Dict[str, object],
) -> Dict[str, object]:
    """Build a compact explanation payload tied to explicit evidence/rules."""
    activated_rules = [item.rule_name for item in inferences]
    rank_name = (
        evaluation.epistemic_rank.name
        if evaluation.epistemic_rank is not None
        else "NONE"
    )
    return {
        "why_agent": (
            f"Assigned from syntax role FA3IL: {semantic_roles.get('agent', '')}"
            if semantic_roles.get("agent")
            else "No explicit agent role was detected."
        ),
        "why_judgement": (
            "Descriptive judgement derived from extracted proposition "
            f"({proposition.subject}, {proposition.predicate}, {proposition.obj})."
        ),
        "why_rank": (
            f"Epistemic rank={rank_name} "
            f"after validation_state={evaluation.validation_state.name} "
            f"and confidence={evaluation.confidence:.4f}."
        ),
        "evidence": {
            "semantic_roles": semantic_roles,
            "activated_rules": activated_rules,
            "world_update": world_update,
        },
    }
