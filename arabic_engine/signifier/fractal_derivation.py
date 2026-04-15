"""fractal_derivation — دالة التوليد الاشتقاقي الفراكتالية: Fractal Derivation Function Spec v1

This module implements the constrained fractal derivation function 𝒟(R,W,S,C)
which takes a root, weight pattern, semantic direction, and constraints, then
produces a valid derived word or blocks derivation when guards fail.

It sits after the three constitutions:
* Epistemic Reception Constitution v1
* Semantic Direction Space Constitution v1
* Weight Fractal Constitution v1

And before Lexeme Fractal Constitution v2.

The function runs nine sequential phases with guards (Art. 12):
ROOT_CHECK → WEIGHT_CHECK → DIRECTION_CHECK → ROOT_WEIGHT_COMPAT →
WEIGHT_DIRECTION_COMPAT → CANDIDATE_BUILD → STRUCTURAL_VERIFY →
SEMANTIC_VERIFY → FINAL_DECISION

Public API
----------
* :func:`derive`
* :func:`derive_all_directions`
* :func:`validate_derivation_input`
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Tuple

from arabic_engine.core.enums import (
    DerivationalDirection,
    DerivationFailureReason,
    DerivationGuard,
    DerivationPhase,
    SemanticDirectionGenus,
    WeightCarryingMode,
)
from arabic_engine.core.types import (
    DerivationCandidate,
    DerivationInput,
    DerivationTrace,
    DirectionAssignment,
    FractalDerivationResult,
    GuardResult,
    SemanticDirection,
    WeightProfile,
)
from arabic_engine.signified.semantic_direction import (
    build_direction_space,
    validate_root_carrying,
)
from arabic_engine.signifier.weight_fractal import (
    build_weight_direction_map,
    check_weight_carrying,
    classify_weight,
)

# ── Data paths ──────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_RULES_PATH = _DATA_DIR / "root_derivation_rules.json"

# ── Arabic letter set ───────────────────────────────────────────────

_ARABIC_LETTERS = set(
    "ءابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    "ؤئإأآة"
)

# ── Cached data ─────────────────────────────────────────────────────

_RULES_CACHE: Optional[dict] = None
_SPACE_CACHE = None


def _load_rules() -> dict:
    """Load the root derivation rules JSON."""
    global _RULES_CACHE
    if _RULES_CACHE is None:
        with open(_RULES_PATH, encoding="utf-8") as fh:
            _RULES_CACHE = json.load(fh)
    return _RULES_CACHE


def _get_space():
    """Get or build the singleton direction space."""
    global _SPACE_CACHE
    if _SPACE_CACHE is None:
        _SPACE_CACHE = build_direction_space()
    return _SPACE_CACHE


# ── Direction lookup helper ─────────────────────────────────────────


def _find_direction(
    deriv_dir: DerivationalDirection,
) -> SemanticDirection:
    """Find a SemanticDirection matching the given derivational direction."""
    space = _get_space()
    for d in space.directions:
        if d.derivational_direction == deriv_dir:
            return d
    # Fallback: create a minimal direction
    return SemanticDirection(
        direction_id=f"DIR_{deriv_dir.name}",
        genus=SemanticDirectionGenus.WUJUD,
        derivational_direction=deriv_dir,
    )


# ── Guard functions (internal) ──────────────────────────────────────


def _validate_root(root: Tuple[str, ...]) -> GuardResult:
    """Guard: validate root consonants (Art. 13, 22)."""
    if not root:
        return GuardResult(
            guard=DerivationGuard.GUARD_ROOT_VALID,
            passed=False,
            message="Root is empty",
        )
    if len(root) < 3 or len(root) > 5:
        return GuardResult(
            guard=DerivationGuard.GUARD_ROOT_VALID,
            passed=False,
            message=f"Root has {len(root)} consonants; expected 3–5",
        )
    for ch in root:
        if ch not in _ARABIC_LETTERS:
            return GuardResult(
                guard=DerivationGuard.GUARD_ROOT_VALID,
                passed=False,
                message=f"Invalid root consonant: {ch!r}",
            )
    return GuardResult(
        guard=DerivationGuard.GUARD_ROOT_VALID,
        passed=True,
        message="Root is valid",
    )


def _validate_weight(pattern: str) -> GuardResult:
    """Guard: validate weight pattern (Art. 14, 23)."""
    if not pattern:
        return GuardResult(
            guard=DerivationGuard.GUARD_WEIGHT_VALID,
            passed=False,
            message="Weight pattern is empty",
        )
    # Check if the pattern is recognized in our rules or can be classified
    rules = _load_rules()
    patterns_db = rules.get("patterns", {})
    # Also classify to ensure it's a valid weight
    try:
        classify_weight(pattern)
    except (ValueError, KeyError, TypeError):
        return GuardResult(
            guard=DerivationGuard.GUARD_WEIGHT_VALID,
            passed=False,
            message=f"Weight pattern cannot be classified: {pattern!r}",
        )

    is_known = pattern in patterns_db
    return GuardResult(
        guard=DerivationGuard.GUARD_WEIGHT_VALID,
        passed=True,
        message=f"Weight pattern valid (known={is_known}): {pattern}",
    )


def _validate_direction(direction: DerivationalDirection) -> GuardResult:
    """Guard: validate derivational direction (Art. 15, 24)."""
    if not isinstance(direction, DerivationalDirection):
        return GuardResult(
            guard=DerivationGuard.GUARD_DIRECTION_VALID,
            passed=False,
            message=f"Invalid direction type: {type(direction).__name__}",
        )
    return GuardResult(
        guard=DerivationGuard.GUARD_DIRECTION_VALID,
        passed=True,
        message=f"Direction valid: {direction.name}",
    )


def _check_root_carries_direction(
    root: Tuple[str, ...],
    direction: DerivationalDirection,
) -> GuardResult:
    """Guard: root carries the target direction (Art. 16, 25.1)."""
    sem_dir = _find_direction(direction)
    carries = validate_root_carrying(root, sem_dir)
    if not carries:
        return GuardResult(
            guard=DerivationGuard.GUARD_ROOT_CARRIES_DIRECTION,
            passed=False,
            message=f"Root {root} does not carry direction {direction.name}",
        )
    return GuardResult(
        guard=DerivationGuard.GUARD_ROOT_CARRIES_DIRECTION,
        passed=True,
        message=f"Root {root} carries direction {direction.name}",
    )


def _check_weight_carries_direction(
    pattern: str,
    direction: DerivationalDirection,
) -> GuardResult:
    """Guard: weight pattern carries the target direction (Art. 17, 25.2)."""
    profile = classify_weight(pattern)
    sem_dir = _find_direction(direction)
    mode = check_weight_carrying(profile, sem_dir)

    if mode == WeightCarryingMode.MUMTANI3:
        return GuardResult(
            guard=DerivationGuard.GUARD_WEIGHT_CARRIES_DIRECTION,
            passed=False,
            message=(
                f"Weight {pattern} cannot carry direction {direction.name} "
                f"(mode={mode.name})"
            ),
        )
    return GuardResult(
        guard=DerivationGuard.GUARD_WEIGHT_CARRIES_DIRECTION,
        passed=True,
        message=(
            f"Weight {pattern} carries direction {direction.name} "
            f"(mode={mode.name})"
        ),
    )


def _check_structural_compatibility(
    root: Tuple[str, ...],
    pattern: str,
) -> GuardResult:
    """Guard: root radical count matches pattern slot count (Art. 16)."""
    rules = _load_rules()
    patterns_db = rules.get("patterns", {})

    if pattern in patterns_db:
        expected_count = patterns_db[pattern].get("radical_count", 3)
        if len(root) != expected_count:
            return GuardResult(
                guard=DerivationGuard.GUARD_STRUCTURAL_COMPATIBILITY,
                passed=False,
                message=(
                    f"Root has {len(root)} radicals but pattern {pattern} "
                    f"expects {expected_count}"
                ),
            )

    return GuardResult(
        guard=DerivationGuard.GUARD_STRUCTURAL_COMPATIBILITY,
        passed=True,
        message=f"Structural compatibility: root({len(root)}) ↔ pattern({pattern})",
    )


# ── Candidate building ─────────────────────────────────────────────


def _build_candidate(
    root: Tuple[str, ...],
    pattern: str,
    direction: DerivationalDirection,
) -> Optional[DerivationCandidate]:
    """Build a candidate surface form by mapping root into pattern slots (Art. 18)."""
    rules = _load_rules()
    patterns_db = rules.get("patterns", {})

    if pattern not in patterns_db:
        return None

    entry = patterns_db[pattern]
    slots = entry.get("slots", [])

    # Map C1, C2, C3, C4, C5 to root consonants
    surface_chars: List[str] = []
    for slot in slots:
        if slot.startswith("C") and len(slot) == 2 and slot[1].isdigit():
            idx = int(slot[1]) - 1
            if idx < len(root):
                surface_chars.append(root[idx])
            else:
                return None  # Not enough root consonants
        else:
            surface_chars.append(slot)

    surface = "".join(surface_chars)

    # Build syllable representation (simplified: split at vowels)
    syllables: List[str] = []
    current = ""
    for ch in surface:
        current += ch
        if ch in {"ا", "و", "ي", "ة"} or ord(ch) in {0x064E, 0x064F, 0x0650}:
            syllables.append(current)
            current = ""
    if current:
        syllables.append(current)

    return DerivationCandidate(
        surface=surface,
        root=root,
        pattern=pattern,
        direction=direction,
        syllables=tuple(syllables),
    )


# ── Verification functions ──────────────────────────────────────────


def _verify_structural(candidate: DerivationCandidate) -> GuardResult:
    """Guard: structural verification of the candidate (Art. 19)."""
    if not candidate.surface:
        return GuardResult(
            guard=DerivationGuard.GUARD_STRUCTURAL_COMPATIBILITY,
            passed=False,
            message="Candidate surface is empty",
        )

    # Check that root consonants appear in the surface
    for ch in candidate.root:
        if ch not in candidate.surface:
            return GuardResult(
                guard=DerivationGuard.GUARD_STRUCTURAL_COMPATIBILITY,
                passed=False,
                message=f"Root consonant {ch!r} not found in surface {candidate.surface!r}",
            )

    return GuardResult(
        guard=DerivationGuard.GUARD_STRUCTURAL_COMPATIBILITY,
        passed=True,
        message=f"Structural verification passed for {candidate.surface!r}",
    )


def _verify_semantic(
    candidate: DerivationCandidate,
    direction: DerivationalDirection,
) -> GuardResult:
    """Guard: semantic verification — pattern+direction consistency (Art. 20).

    Uses the direction_affinity field from the derivation rules as the
    primary check.  The weight-direction map from ``weight_fractal`` was
    already validated in Phase 5 (WEIGHT_DIRECTION_COMPAT), so this
    phase ensures the *semantic* match between the morphological output
    type and the intended direction.
    """
    rules = _load_rules()
    patterns_db = rules.get("patterns", {})

    if candidate.pattern in patterns_db:
        affinity = patterns_db[candidate.pattern].get("direction_affinity", [])
        if affinity and direction.name not in affinity:
            return GuardResult(
                guard=DerivationGuard.GUARD_SEMANTIC_COMPATIBILITY,
                passed=False,
                message=(
                    f"Pattern {candidate.pattern} has affinity {affinity} "
                    f"but direction is {direction.name}"
                ),
            )

    # Also cross-check via weight-direction map (non-blocking: the
    # carrying check in Phase 5 is the authoritative gatekeeper; the
    # direction_space weight_conditions may use fully-vocalized pattern
    # names that don't match the bare input pattern.)
    profile = classify_weight(candidate.pattern)
    mapping = build_weight_direction_map(profile)
    if direction in mapping.prohibited_directions:
        return GuardResult(
            guard=DerivationGuard.GUARD_SEMANTIC_COMPATIBILITY,
            passed=False,
            message=(
                f"Weight {candidate.pattern} prohibits direction {direction.name}"
            ),
        )

    return GuardResult(
        guard=DerivationGuard.GUARD_SEMANTIC_COMPATIBILITY,
        passed=True,
        message=f"Semantic verification passed for {direction.name}",
    )


def _verify_recoverability(
    candidate: DerivationCandidate,
    root: Tuple[str, ...],
    pattern: str,
    direction: DerivationalDirection,
) -> GuardResult:
    """Guard: output recoverability — trace back to root+weight+direction (Art. 42–44)."""
    # Check root consonants are preserved
    for ch in root:
        if ch not in candidate.surface:
            return GuardResult(
                guard=DerivationGuard.GUARD_OUTPUT_RECOVERABLE,
                passed=False,
                message=f"Cannot recover root consonant {ch!r} from {candidate.surface!r}",
            )

    # Check candidate records match input
    if candidate.root != root:
        return GuardResult(
            guard=DerivationGuard.GUARD_OUTPUT_RECOVERABLE,
            passed=False,
            message="Candidate root does not match input root",
        )
    if candidate.pattern != pattern:
        return GuardResult(
            guard=DerivationGuard.GUARD_OUTPUT_RECOVERABLE,
            passed=False,
            message="Candidate pattern does not match input pattern",
        )
    if candidate.direction != direction:
        return GuardResult(
            guard=DerivationGuard.GUARD_OUTPUT_RECOVERABLE,
            passed=False,
            message="Candidate direction does not match input direction",
        )

    return GuardResult(
        guard=DerivationGuard.GUARD_OUTPUT_RECOVERABLE,
        passed=True,
        message=f"Output {candidate.surface!r} is recoverable",
    )


# ── Failure result helper ───────────────────────────────────────────


def _failure_result(
    inp: DerivationInput,
    guards: List[GuardResult],
    reasons: Tuple[DerivationFailureReason, ...],
    phase: DerivationPhase,
    *,
    weight_profile: Optional[WeightProfile] = None,
    direction_assignment: Optional[DirectionAssignment] = None,
    candidate: Optional[DerivationCandidate] = None,
) -> FractalDerivationResult:
    """Build a failure result with full trace."""
    trace = DerivationTrace(
        input=inp,
        guard_results=tuple(guards),
        candidate=candidate,
        weight_profile=weight_profile,
        direction_assignment=direction_assignment,
        phase_reached=phase,
    )
    return FractalDerivationResult(
        success=False,
        failure_reasons=reasons,
        trace=trace,
        confidence=0.0,
        is_recoverable=False,
    )


# ── Public API ──────────────────────────────────────────────────────


def derive(inp: DerivationInput) -> FractalDerivationResult:
    """Run the fractal derivation function 𝒟(R,W,S,C) → L or ∅.

    Executes all nine derivation phases with guards.  On success, returns
    the derived surface form.  On failure, returns ∅ with failure reasons
    and a full audit trace.

    Args:
        inp: A :class:`~arabic_engine.core.types.DerivationInput`.

    Returns:
        A :class:`~arabic_engine.core.types.FractalDerivationResult`.
    """
    guards: List[GuardResult] = []

    # Phase 1: ROOT_CHECK
    g = _validate_root(inp.root)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.ROOT_FAILURE,),
            DerivationPhase.ROOT_CHECK,
        )

    # Phase 2: WEIGHT_CHECK
    g = _validate_weight(inp.weight_pattern)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.WEIGHT_FAILURE,),
            DerivationPhase.WEIGHT_CHECK,
        )

    # Classify weight for later use
    weight_profile = classify_weight(inp.weight_pattern, radical_count=len(inp.root))

    # Phase 3: DIRECTION_CHECK
    g = _validate_direction(inp.direction)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.SEMANTIC_FAILURE,),
            DerivationPhase.DIRECTION_CHECK,
            weight_profile=weight_profile,
        )

    # Phase 4: ROOT_WEIGHT_COMPAT
    g = _check_structural_compatibility(inp.root, inp.weight_pattern)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.ROOT_FAILURE,),
            DerivationPhase.ROOT_WEIGHT_COMPAT,
            weight_profile=weight_profile,
        )

    # Phase 5: WEIGHT_DIRECTION_COMPAT
    g_root = _check_root_carries_direction(inp.root, inp.direction)
    guards.append(g_root)
    g_weight = _check_weight_carries_direction(inp.weight_pattern, inp.direction)
    guards.append(g_weight)

    failures: List[DerivationFailureReason] = []
    if not g_root.passed:
        failures.append(DerivationFailureReason.ROOT_FAILURE)
    if not g_weight.passed:
        failures.append(DerivationFailureReason.WEIGHT_FAILURE)
    if failures:
        if len(failures) > 1:
            failures.append(DerivationFailureReason.TOTAL_FAILURE)
        return _failure_result(
            inp, guards, tuple(failures),
            DerivationPhase.WEIGHT_DIRECTION_COMPAT,
            weight_profile=weight_profile,
        )

    # Phase 6: CANDIDATE_BUILD
    candidate = _build_candidate(inp.root, inp.weight_pattern, inp.direction)
    if candidate is None:
        return _failure_result(
            inp, guards, (DerivationFailureReason.WEIGHT_FAILURE,),
            DerivationPhase.CANDIDATE_BUILD,
            weight_profile=weight_profile,
        )

    # Phase 7: STRUCTURAL_VERIFY
    g = _verify_structural(candidate)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.SYLLABIC_FAILURE,),
            DerivationPhase.STRUCTURAL_VERIFY,
            weight_profile=weight_profile,
            candidate=candidate,
        )

    # Phase 8: SEMANTIC_VERIFY
    g = _verify_semantic(candidate, inp.direction)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.SEMANTIC_FAILURE,),
            DerivationPhase.SEMANTIC_VERIFY,
            weight_profile=weight_profile,
            candidate=candidate,
        )

    # Phase 9: FINAL_DECISION — recoverability
    g = _verify_recoverability(candidate, inp.root, inp.weight_pattern, inp.direction)
    guards.append(g)
    if not g.passed:
        return _failure_result(
            inp, guards, (DerivationFailureReason.RECOVERY_FAILURE,),
            DerivationPhase.FINAL_DECISION,
            weight_profile=weight_profile,
            candidate=candidate,
        )

    # Build direction assignment for the trace
    sem_dir = _find_direction(inp.direction)
    direction_assignment = DirectionAssignment(
        word_surface=candidate.surface,
        root=inp.root,
        pattern=inp.weight_pattern,
        assigned_direction=sem_dir,
        genus=sem_dir.genus,
        confidence=1.0,
    )

    # Success
    trace = DerivationTrace(
        input=inp,
        guard_results=tuple(guards),
        candidate=candidate,
        weight_profile=weight_profile,
        direction_assignment=direction_assignment,
        phase_reached=DerivationPhase.FINAL_DECISION,
    )

    return FractalDerivationResult(
        success=True,
        surface=candidate.surface,
        candidate=candidate,
        trace=trace,
        confidence=1.0,
        is_recoverable=True,
    )


def derive_all_directions(
    root: Tuple[str, ...],
    pattern: str,
) -> Tuple[FractalDerivationResult, ...]:
    """Try all derivational directions for a root+pattern and return results.

    Args:
        root: The root consonants.
        pattern: The morphological weight pattern.

    Returns:
        A tuple of :class:`FractalDerivationResult` for every direction,
        including both successes and failures.
    """
    results: List[FractalDerivationResult] = []
    for direction in DerivationalDirection:
        inp = DerivationInput(
            root=root,
            weight_pattern=pattern,
            direction=direction,
        )
        results.append(derive(inp))
    return tuple(results)


def validate_derivation_input(
    inp: DerivationInput,
) -> Tuple[GuardResult, ...]:
    """Run only validation guards (phases 1–5) without building a candidate.

    Useful for pre-checking whether a derivation attempt is likely to
    succeed before committing to candidate generation.

    Args:
        inp: The derivation input to validate.

    Returns:
        A tuple of :class:`GuardResult` for each guard executed.
    """
    guards: List[GuardResult] = []

    guards.append(_validate_root(inp.root))
    if not guards[-1].passed:
        return tuple(guards)

    guards.append(_validate_weight(inp.weight_pattern))
    if not guards[-1].passed:
        return tuple(guards)

    guards.append(_validate_direction(inp.direction))
    if not guards[-1].passed:
        return tuple(guards)

    guards.append(_check_structural_compatibility(inp.root, inp.weight_pattern))
    if not guards[-1].passed:
        return tuple(guards)

    guards.append(_check_root_carries_direction(inp.root, inp.direction))
    guards.append(_check_weight_carries_direction(inp.weight_pattern, inp.direction))

    return tuple(guards)
