"""Weight engine — استخراج الوزن وتصنيفه.

The weight (الوزن) is the structural template that organises root material,
augmentations, and vowelling into a form classifiable by semantic type.  It
is the epistemic minimum that transforms raw material into a lexeme with a
determinable semantic direction.

Public API
----------
extract_weight         Given a root and surface form, produce a WeightNode.
classify_template_type Nominal / verbal / closed.
compute_completeness   Score 0–1 against the 8 completeness criteria.
compute_recoverability Score 0–1: can we recover root from weight?
assess_productivity    Living / closed / historical.
"""

from __future__ import annotations

from typing import Tuple

from arabic_engine.core.enums import (
    POS,
    ProductivityMode,
    WeightTemplateType,
)
from arabic_engine.core.types import WeightNode

# ── Known Arabic weights ────────────────────────────────────────────

_VERBAL_PATTERNS = frozenset({
    "فَعَلَ", "فَعِلَ", "فَعُلَ",
    "فَعَّلَ", "فَاعَلَ", "أَفْعَلَ",
    "تَفَعَّلَ", "تَفَاعَلَ", "اِفْتَعَلَ", "اِنْفَعَلَ",
    "اِسْتَفْعَلَ", "اِفْعَلَّ", "اِفْعَالَّ",
    "يَفْعَلُ", "يَفْعِلُ", "يَفْعُلُ",
    "اُفْعُلْ", "اِفْعَلْ",
})

_NOMINAL_PATTERNS = frozenset({
    "فَاعِل", "مَفْعُول", "فَعِيل", "فَعْل", "فِعْل", "فُعْل",
    "مَفْعَل", "مِفْعَل", "مِفْعَال", "فَعَّال", "فَعُول",
    "فِعَالَة", "تَفْعِيل", "مُفَاعَلَة", "إِفْعَال",
    "اِفْتِعَال", "اِنْفِعَال", "اِسْتِفْعَال", "تَفَعُّل", "تَفَاعُل",
    "فَاعِلَة", "مَفْعُولَة",
    "أَفْعَل", "فُعْلَى",
})

# Particles and built forms use closed templates
_CLOSED_FORMS = frozenset({
    "في", "من", "إلى", "على", "عن", "ب", "ل", "ك",
    "إن", "أن", "لكن", "لعل", "ليت", "كأن",
    "هل", "ما", "لا", "لم", "لن", "قد", "سوف",
    "هذا", "هذه", "ذلك", "تلك", "هؤلاء",
    "الذي", "التي", "اللذان", "اللتان", "الذين", "اللاتي",
})

_PRODUCTIVE_PATTERNS = frozenset({
    "فَعَلَ", "فَعِلَ", "فَعُلَ", "فَعَّلَ", "أَفْعَلَ", "اِفْتَعَلَ",
    "اِسْتَفْعَلَ", "تَفَعَّلَ", "تَفَاعَلَ",
    "فَاعِل", "مَفْعُول", "فَعِيل", "فَعْل",
    "تَفْعِيل", "إِفْعَال", "اِسْتِفْعَال",
})

_HISTORICAL_PATTERNS = frozenset({
    "اِفْعَلَّ", "اِفْعَالَّ",
})


# ── Weight counter ──────────────────────────────────────────────────
_weight_counter = 0


def _next_weight_id() -> str:
    global _weight_counter
    _weight_counter += 1
    return f"W_{_weight_counter:04d}"


# ── Public API ──────────────────────────────────────────────────────


def extract_weight(
    root: Tuple[str, ...],
    surface: str,
    pattern: str = "",
) -> WeightNode:
    """Extract a WeightNode from root + surface form.

    Parameters
    ----------
    root : tuple of str
        The root radicals, e.g. ``("ك", "ت", "ب")``.
    surface : str
        The surface word form.
    pattern : str
        Optional explicit pattern hint.  If empty the function
        attempts heuristic detection.

    Returns
    -------
    WeightNode
    """
    weight_form = pattern if pattern else _guess_weight(root, surface)
    template_type = classify_template_type(weight_form)
    slots = _build_slots(root, weight_form)
    tendency = _infer_tendency(weight_form, template_type)
    productivity = assess_productivity(weight_form)
    pos_aff = _pos_from_template(template_type)

    node = WeightNode(
        id=_next_weight_id(),
        weight_form=weight_form,
        template_type=template_type,
        slots=slots,
        semantic_tendency=tendency,
        recoverability_score=0.0,
        completeness_score=0.0,
        productivity_mode=productivity,
        pos_affinity=pos_aff,
    )
    # Compute derived scores
    rec = compute_recoverability(node, root)
    comp = compute_completeness(node)
    return WeightNode(
        id=node.id,
        weight_form=node.weight_form,
        template_type=node.template_type,
        slots=node.slots,
        semantic_tendency=node.semantic_tendency,
        recoverability_score=rec,
        completeness_score=comp,
        productivity_mode=node.productivity_mode,
        pos_affinity=node.pos_affinity,
    )


def classify_template_type(weight_form: str) -> WeightTemplateType:
    """Classify a weight form as nominal, verbal, or closed."""
    if weight_form in _VERBAL_PATTERNS:
        return WeightTemplateType.VERBAL
    if weight_form in _NOMINAL_PATTERNS:
        return WeightTemplateType.NOMINAL
    if weight_form in _CLOSED_FORMS:
        return WeightTemplateType.CLOSED
    # Heuristic: verbal forms typically start with يَ/تَ/أَ or contain فَعَل root
    if any(weight_form.startswith(p) for p in ("يَ", "تَ", "أَ", "نَ")):
        return WeightTemplateType.VERBAL
    return WeightTemplateType.NOMINAL


def compute_completeness(weight: WeightNode) -> float:
    """Score 0–1 against the 8 completeness criteria.

    Criteria: ثبوت, حد, امتداد, مقوم, علاقة بنائية, انتظام, وحدة, قابلية التعيين
    """
    score = 0.0
    # 1. ثبوت — the weight form exists and is non-empty
    if weight.weight_form:
        score += 0.125
    # 2. حد — distinguishes between different forms
    if weight.template_type is not None:
        score += 0.125
    # 3. امتداد — has distribution over slots
    if weight.slots and len(weight.slots) > 0:
        score += 0.125
    # 4. مقوم — the form constitutes the pattern, not just letters
    if weight.weight_form and len(weight.weight_form) >= 2:
        score += 0.125
    # 5. علاقة بنائية — connects root to augmentations
    if weight.slots and len(weight.slots) >= 2:
        score += 0.125
    # 6. انتظام — imposes non-arbitrary structure
    if weight.productivity_mode != ProductivityMode.HISTORICAL:
        score += 0.125
    # 7. وحدة — unifies material into one template
    if weight.weight_form and weight.template_type is not None:
        score += 0.125
    # 8. قابلية التعيين — can determine the type of the lexeme
    if weight.pos_affinity is not None and weight.pos_affinity != POS.UNKNOWN:
        score += 0.125
    return round(score, 4)


def compute_recoverability(weight: WeightNode, root: Tuple[str, ...]) -> float:
    """Score 0–1: can we recover the root from the weight?"""
    if not root or not weight.weight_form:
        return 0.0
    score = 0.0
    # Root exists → partial recovery possible
    if len(root) >= 2:
        score += 0.4
    if len(root) >= 3:
        score += 0.2
    # Slots provide recovery path
    if weight.slots and len(weight.slots) >= len(root):
        score += 0.2
    # Template type is known
    if weight.template_type != WeightTemplateType.CLOSED:
        score += 0.2
    return min(round(score, 4), 1.0)


def assess_productivity(weight_form: str) -> ProductivityMode:
    """Assess the productivity mode of a weight form."""
    if weight_form in _PRODUCTIVE_PATTERNS:
        return ProductivityMode.LIVING
    if weight_form in _HISTORICAL_PATTERNS:
        return ProductivityMode.HISTORICAL
    if weight_form in _CLOSED_FORMS:
        return ProductivityMode.CLOSED
    return ProductivityMode.LIVING


# ── Internal helpers ────────────────────────────────────────────────


def _guess_weight(root: Tuple[str, ...], surface: str) -> str:
    """Heuristic weight detection from root + surface."""
    if not root:
        return surface  # for closed forms
    n = len(root)
    if n == 3:
        # Very simplified: 3-letter root → guess pattern from surface length
        slen = len(surface.replace("\u064e", "").replace("\u064f", "")
                          .replace("\u0650", "").replace("\u0651", "")
                          .replace("\u0652", ""))
        if slen <= 3:
            return "فَعَلَ"
        if slen == 4:
            return "فَاعِل"
        if slen == 5:
            return "تَفْعِيل"
        return "اِسْتِفْعَال"
    return "فَعَلَ"


def _build_slots(root: Tuple[str, ...], weight_form: str) -> Tuple[str, ...]:
    """Build slot descriptors from root and weight form."""
    slots = []
    for i, r in enumerate(root):
        slots.append(f"C{i + 1}:{r}")
    # Add augmentation slots based on pattern length difference
    pattern_base = weight_form.replace("\u064e", "").replace("\u064f", "")
    pattern_base = pattern_base.replace("\u0650", "").replace("\u0651", "")
    pattern_base = pattern_base.replace("\u0652", "")
    extra = max(0, len(pattern_base) - len(root))
    for i in range(extra):
        slots.append(f"AUG{i + 1}")
    return tuple(slots)


def _infer_tendency(weight_form: str, template_type: WeightTemplateType) -> str:
    """Infer the semantic tendency of a weight form."""
    if template_type == WeightTemplateType.VERBAL:
        return "حدث"
    if template_type == WeightTemplateType.CLOSED:
        return "وظيفة"
    # Nominal patterns
    if "فَاعِل" in weight_form:
        return "وصف_فاعلية"
    if "مَفْعُول" in weight_form:
        return "وصف_مفعولية"
    if "فَعِيل" in weight_form:
        return "وصف_مبالغة"
    if "مَفْعَل" in weight_form or "مِفْعَل" in weight_form:
        return "مكان_أو_زمان"
    if "تَفْعِيل" in weight_form or "إِفْعَال" in weight_form:
        return "مصدر"
    return "ذات"


def _pos_from_template(template_type: WeightTemplateType) -> POS:
    """Map template type to POS affinity."""
    if template_type == WeightTemplateType.VERBAL:
        return POS.FI3L
    if template_type == WeightTemplateType.CLOSED:
        return POS.HARF
    return POS.ISM
