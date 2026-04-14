"""Tests for arabic_engine.cognition.explanation.build_explanation."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    EpistemicRank,
    TruthState,
    ValidationState,
)
from arabic_engine.core.types import EvaluationResult, InferenceResult, Proposition
from arabic_engine.cognition.explanation import build_explanation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prop(subject: str = "S", predicate: str = "P", obj: str = "O") -> Proposition:
    return Proposition(subject=subject, predicate=predicate, obj=obj)


def _eval(
    *,
    rank: EpistemicRank | None = EpistemicRank.CERTAIN,
    confidence: float = 0.95,
    validation: ValidationState = ValidationState.VALID,
) -> EvaluationResult:
    return EvaluationResult(
        truth_state=TruthState.CERTAIN,
        epistemic_rank=rank,
        confidence=confidence,
        validation_state=validation,
    )


def _inference(name: str = "rule_1") -> InferenceResult:
    return InferenceResult(
        rule_name=name,
        premises=[_prop()],
        conclusion=_prop(),
        confidence=1.0,
        valid=True,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBuildExplanation:
    """Unit tests for build_explanation."""

    # 1. Agent present -------------------------------------------------------
    def test_why_agent_with_agent(self):
        result = build_explanation(
            _prop(), {"agent": "زيد"}, _eval(), [], {},
        )
        assert "FA3IL" in result["why_agent"]
        assert "زيد" in result["why_agent"]

    # 2. No agent ------------------------------------------------------------
    def test_why_agent_without_agent(self):
        result = build_explanation(_prop(), {}, _eval(), [], {})
        assert result["why_agent"] == "No explicit agent role was detected."

    def test_why_agent_empty_string(self):
        result = build_explanation(_prop(), {"agent": ""}, _eval(), [], {})
        assert result["why_agent"] == "No explicit agent role was detected."

    # 3. why_judgement contains subject, predicate, obj ----------------------
    def test_why_judgement_contains_proposition_parts(self):
        result = build_explanation(
            _prop("الكتاب", "يقرأ", "الطالب"), {}, _eval(), [], {},
        )
        assert "الكتاب" in result["why_judgement"]
        assert "يقرأ" in result["why_judgement"]
        assert "الطالب" in result["why_judgement"]

    def test_why_judgement_prefix(self):
        result = build_explanation(_prop(), {}, _eval(), [], {})
        assert result["why_judgement"].startswith("Descriptive judgement")

    # 4. why_rank with epistemic_rank set ------------------------------------
    def test_why_rank_with_rank(self):
        result = build_explanation(
            _prop(), {}, _eval(rank=EpistemicRank.CERTAIN), [], {},
        )
        assert "rank=CERTAIN" in result["why_rank"]

    def test_why_rank_includes_validation_state(self):
        result = build_explanation(
            _prop(), {}, _eval(validation=ValidationState.PENDING), [], {},
        )
        assert "validation_state=PENDING" in result["why_rank"]

    def test_why_rank_includes_confidence(self):
        result = build_explanation(
            _prop(), {}, _eval(confidence=0.1234), [], {},
        )
        assert "confidence=0.1234" in result["why_rank"]

    # 5. why_rank with epistemic_rank=None -----------------------------------
    def test_why_rank_none_rank(self):
        result = build_explanation(
            _prop(), {}, _eval(rank=None), [], {},
        )
        assert "rank=NONE" in result["why_rank"]

    # 6. evidence.activated_rules matches rule_names -------------------------
    def test_activated_rules_match_inferences(self):
        infs = [_inference("modus_ponens"), _inference("transitivity")]
        result = build_explanation(_prop(), {}, _eval(), infs, {})
        assert result["evidence"]["activated_rules"] == [
            "modus_ponens",
            "transitivity",
        ]

    # 7. Empty inferences -> empty activated_rules ---------------------------
    def test_empty_inferences(self):
        result = build_explanation(_prop(), {}, _eval(), [], {})
        assert result["evidence"]["activated_rules"] == []

    # 8. Multiple inferences -------------------------------------------------
    def test_multiple_inferences_order(self):
        names = ["r1", "r2", "r3", "r4"]
        infs = [_inference(n) for n in names]
        result = build_explanation(_prop(), {}, _eval(), infs, {})
        assert result["evidence"]["activated_rules"] == names

    # 9. evidence contains semantic_roles and world_update -------------------
    def test_evidence_semantic_roles(self):
        roles = {"agent": "زيد", "patient": "الكتاب"}
        result = build_explanation(_prop(), roles, _eval(), [], {})
        assert result["evidence"]["semantic_roles"] is roles

    def test_evidence_world_update(self):
        update = {"new_fact": True, "count": 7}
        result = build_explanation(_prop(), {}, _eval(), [], update)
        assert result["evidence"]["world_update"] is update

    # 10. All expected top-level keys present --------------------------------
    def test_all_top_level_keys(self):
        result = build_explanation(_prop(), {}, _eval(), [], {})
        assert set(result.keys()) == {
            "why_agent",
            "why_judgement",
            "why_rank",
            "evidence",
        }

    def test_evidence_sub_keys(self):
        result = build_explanation(_prop(), {}, _eval(), [], {})
        assert set(result["evidence"].keys()) == {
            "semantic_roles",
            "activated_rules",
            "world_update",
        }
