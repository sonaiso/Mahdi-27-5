"""Factor hypotheses — فرضيات العامل النحوي.

Determines the grammatical governor (عامل) for each role hypothesis.

Handles:
- Explicit verb factors (فعل ظاهر)
- Defective verb factors (فعل ناقص — كان وأخواتها)
- Particle factors (حرف — إنّ وأخواتها، حروف الجر)
- Semantic factors (عامل معنوي — الابتداء)
- Implicit/estimated factors (عامل مقدّر — e.g. elided verb)
- Elided factors (عامل محذوف — deleted governing element)
- Vocative factors (أداة النداء)
- Negation/interrogation tools (أدوات)
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode

# ── Particle lists for factor identification ────────────────────────

_INNA_PARTICLES = frozenset({
    "إنّ", "أنّ", "لكنّ", "كأنّ", "ليت", "لعل",
    "إن", "أن", "لكن", "كأن",
})

_KANA_VERBS = frozenset({
    "كان", "أصبح", "أمسى", "أضحى", "ظل", "بات",
    "صار", "ليس", "ما_زال", "ما_فتئ",
})

_PREP_TOKENS = frozenset({
    "إلى", "من", "في", "على", "عن", "ب", "ل", "ك",
    "حتى", "منذ", "مذ",
})


def generate(
    role_hypotheses: List[HypothesisNode],
    concept_hypotheses: List[HypothesisNode],
) -> List[HypothesisNode]:
    """Generate factor hypotheses for each role hypothesis.

    Parameters
    ----------
    role_hypotheses : list[HypothesisNode]
        Role hypotheses in sentence order.
    concept_hypotheses : list[HypothesisNode]
        Concept hypotheses (for verb/particle lookup).

    Returns
    -------
    list[HypothesisNode]
        Factor hypotheses, one per role.
    """
    # Find verb and particle concept labels
    verb_label: Optional[str] = None
    prep_label: Optional[str] = None
    inna_label: Optional[str] = None
    kana_label: Optional[str] = None

    for c in concept_hypotheses:
        label = str(c.get("label", ""))
        stype = str(c.get("semantic_type", ""))
        if stype == "EVENT" and verb_label is None:
            verb_label = label
        if label in _PREP_TOKENS and prep_label is None:
            prep_label = label
        if label in _INNA_PARTICLES and inna_label is None:
            inna_label = label
        if label in _KANA_VERBS and kana_label is None:
            kana_label = label

    hypotheses: List[HypothesisNode] = []
    for role_h in role_hypotheses:
        role = str(role_h.get("role", ""))
        factor, factor_type = _infer_factor(
            role, verb_label, prep_label, inna_label, kana_label,
        )

        hypotheses.append(
            HypothesisNode(
                node_id=f"FACT_{role_h.node_id}",
                hypothesis_type="factor",
                stage=ActivationStage.FACTOR,
                source_refs=(role_h.node_id,),
                payload=(
                    ("factor", factor),
                    ("factor_type", factor_type),
                    ("governed_role", role),
                ),
                confidence=role_h.confidence,
                status=HypothesisStatus.ACTIVE,
            )
        )
    return hypotheses


def _infer_factor(
    role: str,
    verb_label: Optional[str],
    prep_label: Optional[str],
    inna_label: Optional[str],
    kana_label: Optional[str],
) -> tuple[str, str]:
    """Determine factor and factor type from role and context.

    Expanded to handle:
    - عامل مقدّر (implicit factor when no verb is visible)
    - عامل محذوف (elided factor for vocative, exclamatory)
    - Specific particle identification for إنّ/كان factors
    """
    # Self-governing elements (verbs, particles, tools)
    if role == "فعل":
        return ("ذاتي", "فعل")
    if role == "فعل_ناقص":
        return ("ذاتي", "فعل_ناقص")

    # Verb-governed roles
    if role == "فاعل":
        if verb_label:
            return (verb_label, "فعل")
        # No visible verb → implicit factor (عامل مقدّر)
        return ("مقدّر", "عامل_مقدّر")

    if role == "مفعول":
        if verb_label:
            return (verb_label, "فعل")
        return ("مقدّر", "عامل_مقدّر")

    # Nominal sentence: semantic factor (الابتداء)
    if role == "مبتدأ":
        return ("ابتداء", "عامل_معنوي")
    if role == "خبر":
        return ("ابتداء", "عامل_معنوي")

    # إنّ وأخواتها governed roles
    if role == "اسم_إن":
        return (inna_label or "إنّ", "حرف_مشبه_بالفعل")
    if role == "خبر_إن":
        return (inna_label or "إنّ", "حرف_مشبه_بالفعل")

    # كان وأخواتها governed roles
    if role == "اسم_كان":
        return (kana_label or "كان", "فعل_ناقص")
    if role == "خبر_كان":
        return (kana_label or "كان", "فعل_ناقص")

    # Preposition-governed
    if role == "حرف_جر":
        return ("ذاتي", "حرف_جر")
    if role == "مجرور":
        return (prep_label or "حرف_جر", "حرف_جر")
    if role == "مضاف_إليه":
        return ("إضافة", "مضاف")

    # Vocative: governed by elided verb (أنادي/أدعو)
    if role == "منادى":
        return ("محذوف_أنادي", "عامل_محذوف")

    # Adverbial (حال): governed by the verb
    if role == "حال":
        if verb_label:
            return (verb_label, "فعل")
        return ("مقدّر", "عامل_مقدّر")

    # Tamyiz (تمييز): governed by verb or quantity
    if role == "تمييز":
        if verb_label:
            return (verb_label, "فعل")
        return ("مقدّر", "عامل_مقدّر")

    # Tools and particles — self-governing
    if role in ("أداة_نداء", "أداة_استفهام", "أداة_نفي", "أداة"):
        return ("ذاتي", "أداة")

    # Catch-all: implicit factor
    return ("مقدّر", "عامل_مقدّر")
