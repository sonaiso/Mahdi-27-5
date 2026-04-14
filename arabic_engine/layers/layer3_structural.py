"""Layer 3 — القوام البنيوي (Structural Profile).

Locates the phonological unit within the syllable, the root, and
the morphological pattern.  Scores constitutiveness vs. dependency
and computes fitness for each root position (فاء / عين / لام).
"""

from __future__ import annotations

from typing import Optional, Tuple

from arabic_engine.core.enums import StrictLayerID, TransitionGateStatus
from arabic_engine.core.types import (
    RootPattern,
    StructuralProfileRecord,
    Syllable,
    TransitionGate,
)

# ── Augmentation letters (حروف الزيادة — سألتمونيها) ────────────────
_AUGMENTATION_LETTERS = set("سألتمونيها")
_AUGMENTATION_CODEPOINTS = {ord(c) for c in _AUGMENTATION_LETTERS}

# ── Scoring constants ────────────────────────────────────────────────
_ROOT_CONSTITUTIVE_WEIGHT = 0.7
_ONSET_WEIGHT = 0.2
_CODA_WEIGHT = 0.1


def assign_syllable_slot(
    codepoint: int,
    syllable: Optional[Syllable],
) -> str:
    """موضع مقطعي — onset / nucleus / coda.

    Checks whether the codepoint appears in the syllable's onset,
    nucleus, or coda tuple.
    """
    if syllable is None:
        return "unknown"
    if codepoint in syllable.onset:
        return "onset"
    if codepoint in syllable.nucleus:
        return "nucleus"
    if codepoint in syllable.coda:
        return "coda"
    return "unknown"


def assign_root_slot(
    char: str,
    root_pattern: Optional[RootPattern],
) -> str:
    """موضع جذري — fa / ayn / lam / none.

    Returns the root-slot name if the character matches a root
    consonant, or "none" otherwise.
    """
    if root_pattern is None or not root_pattern.root:
        return "none"
    root = root_pattern.root
    if len(root) >= 1 and char == root[0]:
        return "fa"
    if len(root) >= 2 and char == root[1]:
        return "ayn"
    if len(root) >= 3 and char == root[2]:
        return "lam"
    return "none"


def assess_constitutiveness(
    syllable_slot: str,
    root_slot: str,
) -> float:
    """المقومية — how constitutive is this element?

    Root consonants in onset position score highest.
    """
    score = 0.0
    if root_slot in ("fa", "ayn", "lam"):
        score += _ROOT_CONSTITUTIVE_WEIGHT
    if syllable_slot == "onset":
        score += _ONSET_WEIGHT
    elif syllable_slot == "coda":
        score += _CODA_WEIGHT
    return min(1.0, score)


def assess_dependency(
    syllable_slot: str,
    root_slot: str,
) -> float:
    """التبعية — how dependent (non-root / augmented) is this element?"""
    if root_slot in ("fa", "ayn", "lam"):
        return 0.0
    score = 0.5
    if syllable_slot == "nucleus":
        score += 0.3
    elif syllable_slot == "unknown":
        score += 0.2
    return min(1.0, score)


def assess_attachment(codepoint: int) -> float:
    """قابلية الإلصاق — attachment capacity.

    Certain prefix/suffix letters (ال، ت، ي) have high attachment.
    """
    # Definite article ال, common affixes
    _HIGH_ATTACH = {0x0627, 0x0644}  # ا، ل
    _MED_ATTACH = {0x062A, 0x064A, 0x0646}  # ت، ي، ن
    if codepoint in _HIGH_ATTACH:
        return 0.8
    if codepoint in _MED_ATTACH:
        return 0.6
    return 0.2


def assess_augmentation(codepoint: int) -> float:
    """قابلية الزيادة — augmentation capacity.

    Letters from سألتمونيها have high augmentation potential.
    """
    if codepoint in _AUGMENTATION_CODEPOINTS:
        return 0.8
    return 0.1


def compute_root_position_fitness(
    char: str,
    root_pattern: Optional[RootPattern],
) -> Tuple[float, float, float]:
    """ملاءمة فاء / عين / لام — fitness for each root position."""
    if root_pattern is None or not root_pattern.root:
        return (0.0, 0.0, 0.0)
    root = root_pattern.root
    fa = 1.0 if len(root) >= 1 and char == root[0] else 0.0
    ayn = 1.0 if len(root) >= 2 and char == root[1] else 0.0
    lam = 1.0 if len(root) >= 3 and char == root[2] else 0.0
    return (fa, ayn, lam)


def build_structural_profile(
    codepoint: int,
    char: str,
    syllable: Optional[Syllable] = None,
    root_pattern: Optional[RootPattern] = None,
) -> StructuralProfileRecord:
    """بناء سجل القوام البنيوي."""
    syl_slot = assign_syllable_slot(codepoint, syllable)
    root_slot = assign_root_slot(char, root_pattern)
    const_score = assess_constitutiveness(syl_slot, root_slot)
    dep_score = assess_dependency(syl_slot, root_slot)
    attach = assess_attachment(codepoint)
    augment = assess_augmentation(codepoint)
    fa_fit, ayn_fit, lam_fit = compute_root_position_fitness(char, root_pattern)

    return StructuralProfileRecord(
        syllable_slot=syl_slot,
        root_slot=root_slot,
        constitutiveness_score=const_score,
        dependency_score=dep_score,
        attachment_score=attach,
        augmentation_score=augment,
        fa_fitness=fa_fit,
        ayn_fitness=ayn_fit,
        lam_fitness=lam_fit,
    )


def check_gate_3_to_4(record: StructuralProfileRecord) -> TransitionGate:
    """بوابة الانتقال من الطبقة 3 إلى الطبقة 4.

    Conditions — at least one of:
    1. Has a root_slot
    2. Has a syllable_slot
    3. Has constitutiveness_score or dependency_score
    """
    has_root = record.root_slot != "none"
    has_syllable = record.syllable_slot != "unknown"
    has_scores = record.constitutiveness_score > 0 or record.dependency_score > 0

    c1 = has_root or has_syllable or has_scores

    conditions = (c1,)
    failures: list[str] = []
    if not c1:
        failures.append("no_structural_position")

    status = (
        TransitionGateStatus.PASSED
        if all(conditions)
        else TransitionGateStatus.BLOCKED
    )

    return TransitionGate(
        source_layer=StrictLayerID.STRUCTURAL,
        target_layer=StrictLayerID.TRANSFORMATION,
        conditions_met=conditions,
        gate_status=status,
        failure_reasons=tuple(failures),
    )
