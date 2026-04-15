# Unified State Model — Arabic Engine

## Purpose

The Arabic Engine uses multiple status/state enums across its three
pipeline systems.  Each enum serves a **distinct domain** and should
not be merged.  This document clarifies the relationships and
provides the canonical mapping between them.

## Enum Domains

| Enum | Domain | Values | Used By |
|------|--------|--------|---------|
| `PipelineStatus` | Main pipeline final result | SUCCESS, SUSPEND, FAILURE | `pipeline.py` → `PipelineResult.status` |
| `LayerGateDecision` | Per-layer gate output | PASS, REJECT, SUSPEND, COMPLETE | `pipeline.py` → gate records |
| `TransitionGateStatus` | 7-layer element transition | PASSED, BLOCKED, INSUFFICIENT_DATA | `layers/transition_rules.py` |
| `HypothesisStatus` | Hypothesis lifecycle | ACTIVE, PRUNED, STABILIZED, SUSPENDED, REVISED | `signal/`, `constraints/`, `runtime/` |
| `ValidationState` | Epistemic validation | VALID, INVALID, PENDING | `cognition/epistemic_v1.py` |

## Mapping: Gate Decision → Pipeline Status

| LayerGateDecision | PipelineStatus | Notes |
|-------------------|----------------|-------|
| PASS | SUCCESS (continues) | Layer succeeded, chain continues |
| COMPLETE | SUCCESS (final) | Final layer completed |
| SUSPEND | SUSPEND | Incomplete output, chain may continue degraded |
| REJECT | FAILURE | Blocking error, chain halts |

## Mapping: Transition Gate → Gate Decision

| TransitionGateStatus | LayerGateDecision | Notes |
|---------------------|-------------------|-------|
| PASSED | PASS | Transition allowed |
| BLOCKED | REJECT | Transition blocked |
| INSUFFICIENT_DATA | SUSPEND | Cannot decide yet |

## Mapping: Hypothesis → Gate Decision

| HypothesisStatus | LayerGateDecision | Notes |
|------------------|-------------------|-------|
| ACTIVE | PASS | Hypothesis is live |
| STABILIZED | COMPLETE | Hypothesis confirmed |
| SUSPENDED | SUSPEND | Hypothesis paused |
| PRUNED | REJECT | Hypothesis eliminated |
| REVISED | PASS | Hypothesis updated, continues |

## Mapping: Validation → Pipeline Status

| ValidationState | PipelineStatus | Notes |
|-----------------|----------------|-------|
| VALID | SUCCESS | Epistemically verified |
| PENDING | SUSPEND | Awaiting further validation |
| INVALID | FAILURE | Epistemically rejected |

## Design Principles

1. **No merging** — each enum stays in its domain.
2. **Mapping is explicit** — the `STATUS_MAPPINGS` dict in
   `core/types.py` codifies these relationships.
3. **SUSPEND is shared** — this concept spans all domains by design.
4. **Domain boundaries are tested** — see `tests/test_state_mapping.py`.
