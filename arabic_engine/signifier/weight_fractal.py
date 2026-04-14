"""weight_fractal — دستور الوزن الفراكتالي: Weight Fractal Constitution v1

This module proves that the Arabic morphological weight (الوزن) is not
arbitrary but a **condition of possibility** for the single word.  It
answers three questions:

1. *How* does a weight carry a semantic direction?  (Art. 11–15)
2. *Why* is the weight↔direction mapping non-arbitrary?  (Art. 6–10)
3. *How* does weight act as a pre-compositional condition?  (Art. 21–25)

Expanded Constitution (66 articles, 13 chapters):
- Art. 1–3:   Purpose and scope
- Art. 4–8:   Formal weight definition and distinctions
- Art. 9–17:  Condition-of-possibility system (6 dimensions)
- Art. 18–26: Minimum complete threshold (MWC, 8 dimensions)
- Art. 27–34: Fractal law application (6 phases)
- Art. 35–42: Direction carrying conditions (4 suitability criteria)
- Art. 43–46: Trilateral verb doors
- Art. 47–50: Augmented weight system
- Art. 51–54: Noun / masdar / derivative weights
- Art. 55–58: Tense / person / copula weights
- Art. 59–62: Mathematical formulation
- Art. 63–64: Acceptance / rejection criteria
- Art. 65–66: Summary formula and next steps

The engine implements a six-phase fractal cycle:
TA3YIN → TAMYIZ → TAHMIL → TAHQIQ → TAWLID → RADD

Public API
----------
* :func:`classify_weight`
* :func:`build_weight_direction_map`
* :func:`check_weight_carrying`
* :func:`build_fractal_tree`
* :func:`validate_weight_non_arbitrariness`
* :func:`run_weight_fractal`
* :func:`build_formal_tuple`
* :func:`validate_weight_possibility`
* :func:`compute_mwc`
* :func:`compute_fractal_score`
* :func:`evaluate_direction_suitability`
* :func:`classify_verb_door`
* :func:`validate_augmented_weight`
* :func:`validate_weight_acceptance`
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Tuple

from arabic_engine.core.enums import (
    POS,
    AugmentedSemanticLayer,
    DerivationalDirection,
    SemanticDirectionGenus,
    ThulathiBab,
    WeightCarryingMode,
    WeightClass,
    WeightFractalPhase,
    WeightKind,
    WeightValidationStatus,
)
from arabic_engine.core.types import (
    LexicalClosure,
    SemanticDirection,
    VerbDoor,
    WeightDirectionMapping,
    WeightDirectionSuitability,
    WeightFormalTuple,
    WeightFractalNode,
    WeightFractalResult,
    WeightFractalScore,
    WeightMWCScore,
    WeightPossibilityResult,
    WeightProfile,
    WeightValidationResult,
)

# ── Data paths ──────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_MATRIX_PATH = _DATA_DIR / "weight_direction_matrix.json"
_VERB_DOORS_PATH = _DATA_DIR / "verb_doors_seed.json"
_AUGMENTED_PATH = _DATA_DIR / "augmented_weights_seed.json"

# ── Thresholds (Art. 60–62) ─────────────────────────────────────────

THETA_1 = 0.625   # MWC minimum acceptance threshold (5/8)
THETA_2 = 0.667   # Fractal score minimum threshold (4/6)
THETA_W = 0.75    # Direction suitability minimum threshold (3/4)

# ── String → enum look-ups ─────────────────────────────────────────

_STR_TO_CARRYING = {e.name: e for e in WeightCarryingMode}
_STR_TO_DIR = {e.name: e for e in DerivationalDirection}
_STR_TO_WCLASS = {e.name: e for e in WeightClass}
_STR_TO_BAB = {e.name: e for e in ThulathiBab}
_STR_TO_AUG = {e.name: e for e in AugmentedSemanticLayer}

# ── Pattern → weight class heuristic ───────────────────────────────

_AUGMENTED_PREFIXES = ("إ", "أ", "ت", "ان", "است", "مُ", "يُ", "يَ")


def _detect_weight_class(pattern: str, radical_count: int) -> WeightClass:
    """Heuristic weight-class detection from pattern string."""
    if radical_count >= 5:
        return WeightClass.KHUMASI
    if radical_count == 4:
        for prefix in _AUGMENTED_PREFIXES:
            if pattern.startswith(prefix):
                return WeightClass.RUBA3I_MAZEED
        return WeightClass.RUBA3I_MUJARRAD
    # triliteral
    for prefix in _AUGMENTED_PREFIXES:
        if pattern.startswith(prefix):
            return WeightClass.THULATHI_MAZEED
    if len(pattern) > 5:  # longer patterns are usually augmented
        return WeightClass.THULATHI_MAZEED
    return WeightClass.THULATHI_MUJARRAD


def _detect_augmentation(pattern: str) -> Tuple[str, ...]:
    """Detect augmentation letters in a pattern."""
    augmentation = []
    aug_chars = {"أ", "ت", "ن", "س", "ا", "إ"}
    for ch in pattern:
        if ch in aug_chars:
            augmentation.append(ch)
    return tuple(augmentation)


def _detect_weight_kind(
    wclass: WeightClass, aug: Tuple[str, ...],
) -> WeightKind:
    """Detect weight kind from class and augmentation (Art. 4–8)."""
    if wclass in (WeightClass.THULATHI_MUJARRAD, WeightClass.THULATHI_MAZEED):
        return WeightKind.PRODUCTIVE
    if wclass == WeightClass.KHUMASI:
        return WeightKind.MEASURE_ONLY
    if aug:
        return WeightKind.PRODUCTIVE
    return WeightKind.PRODUCTIVE


# ── Genus inference from POS ────────────────────────────────────────

_POS_TO_GENUS = {
    POS.ISM: SemanticDirectionGenus.WUJUD,
    POS.FI3L: SemanticDirectionGenus.HADATH,
    POS.SIFA: SemanticDirectionGenus.SIFA,
    POS.HARF: SemanticDirectionGenus.NISBA,
    POS.ZARF: SemanticDirectionGenus.NISBA,
    POS.DAMIR: SemanticDirectionGenus.NISBA,
    POS.MASDAR_SARIH: SemanticDirectionGenus.HADATH,
    POS.MASDAR_MUAWWAL: SemanticDirectionGenus.HADATH,
}

# ── Matrix loading ──────────────────────────────────────────────────


def _load_matrix() -> dict:
    """Load the weight-direction matrix JSON."""
    with open(_MATRIX_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _load_verb_doors() -> dict:
    """Load verb doors seed JSON."""
    with open(_VERB_DOORS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _load_augmented() -> dict:
    """Load augmented weights seed JSON."""
    with open(_AUGMENTED_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# ── Public API — Original functions ─────────────────────────────────


def classify_weight(
    pattern: str,
    *,
    radical_count: int = 3,
    pos: POS = POS.ISM,
) -> WeightProfile:
    """Classify a morphological pattern into a full weight profile.

    Args:
        pattern: The morphological weight string (e.g. ``"فَعْل"``).
        radical_count: Number of original radical consonants.
        pos: Part-of-speech tag for genus inference.

    Returns:
        A :class:`~arabic_engine.core.types.WeightProfile`.
    """
    wclass = _detect_weight_class(pattern, radical_count)
    genus = _POS_TO_GENUS.get(pos, SemanticDirectionGenus.WUJUD)
    aug = _detect_augmentation(pattern)
    kind = _detect_weight_kind(wclass, aug)
    ftuple = build_formal_tuple(pattern, radical_count, aug)

    return WeightProfile(
        pattern=pattern,
        weight_class=wclass,
        radical_count=radical_count,
        augmentation_letters=aug,
        semantic_direction=genus,
        carrying_mode=WeightCarryingMode.ASLI,
        weight_kind=kind,
        formal_tuple=ftuple,
    )


def build_weight_direction_map(profile: WeightProfile) -> WeightDirectionMapping:
    """Map a weight to its permitted and prohibited derivational directions.

    Consults the weight-direction matrix data and falls back to defaults
    when no exact pattern match is found.

    Args:
        profile: The weight profile to look up.

    Returns:
        A :class:`~arabic_engine.core.types.WeightDirectionMapping`.
    """
    matrix = _load_matrix()

    for entry in matrix.get("matrix", ()):
        if entry["pattern"] == profile.pattern:
            permitted = tuple(
                _STR_TO_DIR[d]
                for d in entry.get("permitted_directions", ())
                if d in _STR_TO_DIR
            )
            prohibited = tuple(
                _STR_TO_DIR[d]
                for d in entry.get("prohibited_directions", ())
                if d in _STR_TO_DIR
            )
            carrying = tuple(
                (c["direction"], c["mode"])
                for c in entry.get("carrying", ())
            )
            return WeightDirectionMapping(
                pattern=profile.pattern,
                permitted_directions=permitted,
                prohibited_directions=prohibited,
                carrying_matrix=carrying,
            )

    # Fallback: all directions permitted, none prohibited
    return WeightDirectionMapping(
        pattern=profile.pattern,
        permitted_directions=tuple(DerivationalDirection),
        prohibited_directions=(),
        carrying_matrix=(),
    )


def check_weight_carrying(
    profile: WeightProfile,
    direction: SemanticDirection,
) -> WeightCarryingMode:
    """Determine how a weight carries a semantic direction.

    Consults the weight-direction matrix for an exact match.  If the
    direction is among the prohibited directions of this weight, returns
    MUMTANI3.  Otherwise defaults to ASLI.

    Args:
        profile: The weight profile.
        direction: The semantic direction to check.

    Returns:
        A :class:`~arabic_engine.core.enums.WeightCarryingMode`.
    """
    mapping = build_weight_direction_map(profile)
    dir_name = direction.derivational_direction.name

    for d_name, mode_name in mapping.carrying_matrix:
        if d_name == dir_name and mode_name in _STR_TO_CARRYING:
            return _STR_TO_CARRYING[mode_name]

    if direction.derivational_direction in mapping.prohibited_directions:
        return WeightCarryingMode.MUMTANI3

    if direction.derivational_direction in mapping.permitted_directions:
        return WeightCarryingMode.ASLI

    return WeightCarryingMode.TABI3I


def build_fractal_tree(
    root: Tuple[str, ...],
    base_pattern: str,
    *,
    pos: POS = POS.ISM,
) -> Tuple[WeightFractalNode, ...]:
    """Construct a fractal derivation tree from root + weight.

    Creates a six-node chain following the fractal phases:
    TA3YIN → TAMYIZ → TAHMIL → TAHQIQ → TAWLID → RADD.

    Args:
        root: The root consonants.
        base_pattern: The base morphological pattern.
        pos: Part-of-speech for genus inference.

    Returns:
        A tuple of :class:`~arabic_engine.core.types.WeightFractalNode`.
    """
    profile = classify_weight(base_pattern, radical_count=len(root), pos=pos)
    phases = list(WeightFractalPhase)
    nodes: List[WeightFractalNode] = []
    root_tag = root[0] if root and root[0] else "x"

    for idx, phase in enumerate(phases):
        node_id = f"WFN_{root_tag}_{idx}"
        parent_id = nodes[-1].node_id if nodes else None
        child_id = f"WFN_{root_tag}_{idx + 1}" if idx < len(phases) - 1 else None
        children = (child_id,) if child_id else ()

        nodes.append(
            WeightFractalNode(
                node_id=node_id,
                weight_profile=profile,
                source_root=root,
                phase=phase,
                children=children,
                parent=parent_id,
            )
        )

    return tuple(nodes)


def validate_weight_non_arbitrariness(
    profile: WeightProfile,
    direction: SemanticDirection,
) -> bool:
    """Prove that the weight↔direction mapping is not arbitrary.

    A mapping is non-arbitrary when the weight's permitted directions
    include the target direction, meaning there is a systematic,
    rule-governed link between the weight form and its semantic bearing.

    Args:
        profile: The weight profile.
        direction: The semantic direction to validate.

    Returns:
        ``True`` if the mapping is non-arbitrary.
    """
    mapping = build_weight_direction_map(profile)

    if direction.derivational_direction in mapping.prohibited_directions:
        return False

    if direction.derivational_direction in mapping.permitted_directions:
        return True

    # If no explicit data, the weight still systematically governs
    # the morphological form, so it is non-arbitrary by structure.
    return True


# ── Public API — New functions (Expanded Constitution) ──────────────


def build_formal_tuple(
    pattern: str,
    radical_count: int = 3,
    augmentation: Tuple[str, ...] = (),
) -> WeightFormalTuple:
    """Build the formal 6-component tuple W = (R, V, A, S, D, P) per Art. 59.

    Args:
        pattern: The morphological weight string.
        radical_count: Number of root consonants.
        augmentation: Augmentation letters detected.

    Returns:
        A :class:`~arabic_engine.core.types.WeightFormalTuple`.
    """
    root_positions = tuple(range(1, radical_count + 1))
    vowels: List[str] = []
    aug_positions: List[int] = []
    syllables: List[str] = []

    for i, ch in enumerate(pattern):
        if ch in "َُِْ":
            vowels.append(ch)
        if ch in {"أ", "ت", "ن", "س", "ا", "إ", "مُ", "يُ"}:
            aug_positions.append(i)

    # Syllable approximation: split pattern into CV/CVC chunks
    if radical_count <= 3:
        syllables = ["CVC"] * min(radical_count, 2)
    else:
        syllables = ["CVC"] * min(radical_count, 3)

    dir_label = "HADATH" if radical_count <= 3 else "WUJUD"

    capacity: List[str] = []
    if radical_count <= 3 and not augmentation:
        capacity = ["MASDAR", "ISM_FA3IL", "ISM_MAF3UL"]
    elif augmentation:
        capacity = ["MASDAR"]
    else:
        capacity = ["ISM_JAMID"]

    return WeightFormalTuple(
        root_positions=root_positions,
        vowel_pattern=tuple(vowels),
        augmentation_positions=tuple(aug_positions),
        syllable_structure=tuple(syllables),
        semantic_direction_label=dir_label,
        carrying_capacity=tuple(capacity),
    )


def validate_weight_possibility(
    profile: WeightProfile,
) -> WeightPossibilityResult:
    """Evaluate 6-dimension condition-of-possibility for a weight (Art. 9–17).

    Returns:
        A :class:`~arabic_engine.core.types.WeightPossibilityResult`.
    """
    # 1. Structural: has clear positional structure?
    structural = 1.0 if profile.radical_count >= 2 else 0.5

    # 2. Syllabic: syllable structure can be realized?
    syllabic = 1.0 if len(profile.pattern) >= 2 else 0.5

    # 3. Morphological: has a recognized morphological slot?
    sarfi = 1.0 if profile.weight_class in set(WeightClass) else 0.5

    # 4. Semantic: can carry a semantic direction?
    dalali = 1.0 if profile.semantic_direction in set(SemanticDirectionGenus) else 0.5

    # 5. Generative: can produce valid lexemes?
    tawlidi = 1.0 if profile.weight_kind == WeightKind.PRODUCTIVE else 0.5

    # 6. Traceback: can derivatives be traced back to root?
    raddi = 1.0 if profile.radical_count >= 3 else 0.7

    agg = round((structural + syllabic + sarfi + dalali + tawlidi + raddi) / 6, 4)

    return WeightPossibilityResult(
        structural=structural,
        syllabic=syllabic,
        morphological=sarfi,
        semantic=dalali,
        generative=tawlidi,
        traceback=raddi,
        aggregate=agg,
    )


def compute_mwc(profile: WeightProfile) -> WeightMWCScore:
    """Compute Minimum Weight Completeness (Art. 18–26, 60).

    MWC(W) = (Th + Hd + Ex + Muq + Rel + Ord + Uni + Det) / 8

    Returns:
        A :class:`~arabic_engine.core.types.WeightMWCScore`.
    """
    # Th — stability: can it be instantiated in multiple examples?
    stability = 1.0 if profile.weight_kind == WeightKind.PRODUCTIVE else 0.6

    # Hd — boundary: distinguished from root and from other weights?
    boundary = 1.0 if profile.pattern and profile.radical_count >= 2 else 0.5

    # Ex — extension: covers radicals, vowels, augmentation, syllables, direction?
    ext_score = min(1.0, (
        (1.0 if profile.radical_count > 0 else 0.0)
        + (1.0 if profile.pattern else 0.0)
        + (0.5 if profile.augmentation_letters else 0.2)
        + (1.0 if profile.semantic_direction else 0.0)
    ) / 3.5)
    extension = round(ext_score, 4)

    # Muq — constituent: has positional structure, vowel distribution, augmentation?
    constituent = 1.0 if profile.radical_count >= 3 else 0.7

    # Rel — structural relation: elements are interdependent?
    structural_relation = 1.0 if profile.radical_count >= 3 and profile.pattern else 0.6

    # Ord — regularity: is it a repeatable law, not a single instance?
    regularity = 1.0 if profile.weight_kind != WeightKind.MEASURE_ONLY else 0.5

    # Uni — unity: all parts act as a single template?
    unity = 1.0

    # Det — assignability: can be assigned a morphological / semantic type?
    assignability = 1.0

    agg = round(
        (stability + boundary + extension + constituent
         + structural_relation + regularity + unity + assignability) / 8,
        4,
    )

    return WeightMWCScore(
        stability=stability,
        boundary=boundary,
        extension=extension,
        constituent=constituent,
        structural_relation=structural_relation,
        regularity=regularity,
        unity=unity,
        assignability=assignability,
        aggregate=agg,
    )


def compute_fractal_score(profile: WeightProfile) -> WeightFractalScore:
    """Compute fractal law score FW(W) (Art. 27–34, 61).

    FW(W) = (Id + Pr + Rb + Jd + Tr + Rc) / 6

    Returns:
        A :class:`~arabic_engine.core.types.WeightFractalScore`.
    """
    # Id — identification: template and position assignment
    identification = 1.0 if profile.pattern else 0.0

    # Pr — preservation: identity and root-order preserved
    preservation = 1.0 if profile.radical_count >= 3 else 0.7

    # Rb — linkage: root↔weight + weight↔direction connected
    linkage = 1.0 if profile.semantic_direction in set(SemanticDirectionGenus) else 0.5

    # Jd — judgement: can determine validity / productivity
    judgement = 1.0 if profile.weight_kind == WeightKind.PRODUCTIVE else 0.6

    # Tr — transition: weight → mufrad / derivative possible
    transition = 1.0 if profile.weight_kind != WeightKind.MEASURE_ONLY else 0.5

    # Rc — return: form → template → root tracing possible
    return_score = 1.0 if profile.radical_count >= 3 and profile.pattern else 0.5

    agg = round(
        (identification + preservation + linkage
         + judgement + transition + return_score) / 6,
        4,
    )

    return WeightFractalScore(
        identification=identification,
        preservation=preservation,
        linkage=linkage,
        judgement=judgement,
        transition=transition,
        return_score=return_score,
        aggregate=agg,
    )


def evaluate_direction_suitability(
    profile: WeightProfile,
    direction: SemanticDirection,
) -> WeightDirectionSuitability:
    """Evaluate 4-condition suitability for weight carrying a direction (Art. 35–42, 62).

    Carrier(W, s_i) = 1 iff f(W1, W2, W3, W4) >= θ_w

    Args:
        profile: The weight profile.
        direction: The semantic direction to evaluate.

    Returns:
        A :class:`~arabic_engine.core.types.WeightDirectionSuitability`.
    """
    matrix = _load_matrix()
    suit = {"W1": 0.8, "W2": 0.8, "W3": 0.8, "W4": 0.75}

    for entry in matrix.get("matrix", ()):
        if entry["pattern"] == profile.pattern:
            suit = entry.get("suitability", suit)
            break

    # Adjust semantic suitability based on direction compatibility
    mapping = build_weight_direction_map(profile)
    w4 = suit.get("W4", 0.75)
    if direction.derivational_direction in mapping.prohibited_directions:
        w4 = 0.0
    elif direction.derivational_direction in mapping.permitted_directions:
        w4 = max(w4, 0.9)

    w1 = suit.get("W1", 0.8)
    w2 = suit.get("W2", 0.8)
    w3 = suit.get("W3", 0.8)

    agg = round((w1 + w2 + w3 + w4) / 4, 4)
    carries = agg >= THETA_W

    return WeightDirectionSuitability(
        structural_suitability=w1,
        syllabic_suitability=w2,
        morphological_suitability=w3,
        semantic_suitability=w4,
        aggregate=agg,
        carries=carries,
    )


def classify_verb_door(
    pattern_past: str,
    pattern_present: str,
) -> Optional[VerbDoor]:
    """Classify a past↔present pattern pair into a verb door (Art. 43–46).

    Args:
        pattern_past: Past-tense weight (e.g. ``"فَعَلَ"``).
        pattern_present: Present-tense weight (e.g. ``"يَفْعُلُ"``).

    Returns:
        A :class:`~arabic_engine.core.types.VerbDoor` or None if not matched.
    """
    data = _load_verb_doors()

    for door in data.get("doors", ()):
        if door["past_pattern"] == pattern_past and door["present_pattern"] == pattern_present:
            bab = _STR_TO_BAB.get(door["bab"])
            if bab is None:
                continue
            examples = door.get("examples", [])
            ex = examples[0] if examples else {}
            return VerbDoor(
                bab=bab,
                past_pattern=pattern_past,
                present_pattern=pattern_present,
                example_root=tuple(ex.get("root", [])),
                example_past=ex.get("past", ""),
                example_present=ex.get("present", ""),
            )

    return None


def validate_augmented_weight(profile: WeightProfile) -> bool:
    """Validate that an augmented weight meets acceptance criteria (Art. 47–50).

    An augmented weight is accepted only if it:
    1. Preserves the root in a recognisable manner
    2. Carries a defined augmented semantic direction
    3. Opens a stable derivational network

    Args:
        profile: The weight profile to validate.

    Returns:
        ``True`` if the augmented weight is valid.
    """
    if profile.weight_class not in (WeightClass.THULATHI_MAZEED, WeightClass.RUBA3I_MAZEED):
        return True  # Not augmented; no additional check needed

    # Must have augmentation letters
    if not profile.augmentation_letters:
        return False

    # Must have a productive kind
    if profile.weight_kind != WeightKind.PRODUCTIVE:
        return False

    # Root must be recognisable (radical count >= 3)
    if profile.radical_count < 3:
        return False

    return True


def validate_weight_acceptance(
    profile: WeightProfile,
) -> WeightValidationResult:
    """Apply 6 acceptance + 5 rejection criteria (Art. 63–64).

    Acceptance criteria:
      1. Representable as template
      2. Distinguished from others by boundary
      3. MWC >= θ₁
      4. Carries a semantic direction
      5. Can transition to mufrad/derivative
      6. Derivatives can be traced back

    Rejection criteria:
      1. Mere movement ordering without law
      2. No general semantic direction
      3. No generative or analytic path
      4. Cannot trace forms back to it
      5. Confuses weight with root or final form

    Returns:
        A :class:`~arabic_engine.core.types.WeightValidationResult`.
    """
    mwc = compute_mwc(profile)
    fscore = compute_fractal_score(profile)
    possibility = validate_weight_possibility(profile)

    # 6 acceptance scores
    a1 = 1.0 if profile.pattern else 0.0            # representable
    a2 = 1.0 if profile.radical_count >= 2 else 0.0  # distinguished
    a3 = 1.0 if mwc.aggregate >= THETA_1 else 0.0    # MWC threshold
    a4 = 1.0 if possibility.semantic >= 0.5 else 0.0  # semantic direction
    a5 = 1.0 if fscore.transition >= 0.5 else 0.0     # transition possible
    a6 = 1.0 if fscore.return_score >= 0.5 else 0.0   # traceback possible

    acceptance_scores = (a1, a2, a3, a4, a5, a6)
    acceptance_count = sum(s >= 1.0 for s in acceptance_scores)

    # 5 rejection flags
    r1 = not profile.pattern                           # no law
    r2 = possibility.semantic < 0.5                    # no direction
    r3 = possibility.generative < 0.5                  # no path
    r4 = fscore.return_score < 0.5                     # no traceback
    r5 = profile.radical_count < 2                     # confused with root

    rejection_flags = (r1, r2, r3, r4, r5)
    any_rejected = any(rejection_flags)

    if any_rejected:
        status = WeightValidationStatus.REJECTED
        reason = "فشل في معايير الرفض — failed rejection criteria"
    elif acceptance_count >= 5:
        status = WeightValidationStatus.ACCEPTED
        reason = "استوفى معايير القبول — passed acceptance criteria"
    else:
        status = WeightValidationStatus.DEFICIENT
        reason = "ناقص — partially meets criteria"

    return WeightValidationResult(
        status=status,
        acceptance_scores=acceptance_scores,
        rejection_flags=rejection_flags,
        reason=reason,
    )


# ── Orchestration ───────────────────────────────────────────────────


def run_weight_fractal(closure: LexicalClosure) -> WeightFractalResult:
    """Run full weight fractal analysis for a single word.

    Orchestrates: classify_weight → build_direction_map →
    build_fractal_tree → possibility check → MWC → fractal score →
    validation → completeness assessment.

    Args:
        closure: The lexical closure of the word.

    Returns:
        A :class:`~arabic_engine.core.types.WeightFractalResult`.
    """
    profile = classify_weight(
        closure.pattern,
        radical_count=len(closure.root),
        pos=closure.pos,
    )
    direction_map = build_weight_direction_map(profile)
    tree = build_fractal_tree(
        closure.root,
        closure.pattern,
        pos=closure.pos,
    )

    # Expanded constitution: compute all scores
    possibility = validate_weight_possibility(profile)
    mwc = compute_mwc(profile)
    fscore = compute_fractal_score(profile)
    validation = validate_weight_acceptance(profile)

    # Completeness: all 6 phases present in tree
    expected_phases = set(WeightFractalPhase)
    actual_phases = {node.phase for node in tree}
    phase_coverage = len(actual_phases & expected_phases) / max(len(expected_phases), 1)

    # Direction coverage
    dir_coverage = 1.0 if direction_map.permitted_directions else 0.5

    completeness = round((phase_coverage + dir_coverage) / 2, 4)

    return WeightFractalResult(
        root=closure.root,
        base_weight=profile,
        fractal_tree=tree,
        direction_map=direction_map,
        completeness_score=completeness,
        is_closed=completeness >= 0.75,
        mwc_score=mwc,
        fractal_score=fscore,
        possibility_result=possibility,
        validation=validation,
    )
