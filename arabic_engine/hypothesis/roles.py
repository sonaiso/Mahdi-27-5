"""Role hypotheses — فرضيات الأدوار النحوية.

Generates grammatical role hypotheses from concept hypotheses.
Handles Arabic-specific grammatical constructs:
- إنّ وأخواتها (inna and sisters)
- كان وأخواتها (kana and sisters)
- أدوات النداء (vocative particles)
- التقديم والتأخير (fronting/inversion)
- حروف الجر (prepositions)
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus, ParticleType
from arabic_engine.core.types import HypothesisNode
from arabic_engine.particle.registry import forms_by_type, is_particle

_PREP_TOKENS = forms_by_type(ParticleType.JARR)

_INNA_PARTICLES = forms_by_type(ParticleType.MASHABBAH)

_KANA_VERBS = frozenset({
    "كان", "أصبح", "أمسى", "أضحى", "ظل", "بات",
    "صار", "ليس", "ما_زال", "ما_فتئ",
})

_VOCATIVE_PARTICLES = forms_by_type(ParticleType.NIDA)

# Interrogative particles from the registry + interrogative pronouns/adverbs
# that function as question words but are grammatically nouns (أسماء الاستفهام),
# not pure particles. They are included here for role detection purposes.
_INTERROGATIVE_PARTICLES = forms_by_type(ParticleType.ISTIFHAM) | frozenset({
    "ما", "من", "أين", "كيف", "متى", "لماذا",
    "أي", "أنّى", "كم", "أيّ", "ماذا",
})

_NEGATION_PARTICLES = forms_by_type(ParticleType.NAFY)


def generate(concept_hypotheses: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate role hypotheses for each concept hypothesis.

    Parameters
    ----------
    concept_hypotheses : list[HypothesisNode]
        Concept hypotheses in sentence order.

    Returns
    -------
    list[HypothesisNode]
        Role hypotheses, one or more per concept.
    """
    hypotheses: List[HypothesisNode] = []
    verb_seen = False
    subject_seen = False
    inna_active = False
    kana_active = False
    vocative_active = False
    prep_active = False
    last_was_prep = False

    for i, concept in enumerate(concept_hypotheses):
        stype = str(concept.get("semantic_type", ""))
        label = str(concept.get("label", ""))

        roles = _infer_role(
            stype, label, i, verb_seen, subject_seen,
            inna_active, kana_active, vocative_active,
            prep_active, last_was_prep,
        )

        # Update state tracking
        if stype == "EVENT":
            verb_seen = True
            if label in _KANA_VERBS:
                kana_active = True
        elif stype == "ENTITY" and verb_seen and not subject_seen:
            subject_seen = True

        if label in _INNA_PARTICLES:
            inna_active = True
        elif label in _VOCATIVE_PARTICLES:
            vocative_active = True
        elif label in _PREP_TOKENS:
            prep_active = True

        last_was_prep = label in _PREP_TOKENS

        # Emit hypotheses — if multiple roles, emit competing hypotheses
        for role_idx, (role, conf) in enumerate(roles):
            node_id = f"ROLE_{concept.node_id}"
            if role_idx > 0:
                node_id = f"ROLE_{concept.node_id}_ALT{role_idx}"
            hypotheses.append(
                HypothesisNode(
                    node_id=node_id,
                    hypothesis_type="role",
                    stage=ActivationStage.ROLE,
                    source_refs=(concept.node_id,),
                    payload=(
                        ("role", role),
                        ("token_label", label),
                    ),
                    confidence=concept.confidence * conf,
                    status=HypothesisStatus.ACTIVE,
                )
            )

        # Reset single-use state
        if label not in _PREP_TOKENS:
            prep_active = False

    return hypotheses


def _infer_role(
    stype: str,
    label: str,
    position: int,
    verb_seen: bool,
    subject_seen: bool,
    inna_active: bool,
    kana_active: bool,
    vocative_active: bool,
    prep_active: bool,
    last_was_prep: bool,
) -> list[tuple[str, float]]:
    """Infer role(s) and confidence(s).

    Returns a list of (role, confidence) tuples. Multiple entries
    indicate ambiguity — competing hypotheses.
    """
    # Particles and tools
    if label in _INNA_PARTICLES:
        return [("أداة", 0.95)]
    if label in _KANA_VERBS and stype == "EVENT":
        return [("فعل_ناقص", 0.95)]
    if label in _VOCATIVE_PARTICLES:
        return [("أداة_نداء", 0.95)]
    if label in _INTERROGATIVE_PARTICLES:
        return [("أداة_استفهام", 0.95)]
    if label in _NEGATION_PARTICLES:
        return [("أداة_نفي", 0.9)]
    if label in _PREP_TOKENS:
        return [("حرف_جر", 0.95)]

    # After vocative particle → منادى
    if vocative_active and stype == "ENTITY":
        return [("منادى", 0.9)]

    # After preposition → مجرور
    if last_was_prep and stype == "ENTITY":
        return [("مجرور", 0.9)]

    # After إنّ — first entity is اسم إنّ, next is خبر إنّ
    if inna_active and stype == "ENTITY" and not verb_seen:
        if not subject_seen:
            return [("اسم_إن", 0.9)]
        return [("خبر_إن", 0.85)]

    # After كان — first entity is اسم كان, next is خبر كان
    if kana_active and stype == "ENTITY":
        if not subject_seen:
            return [("اسم_كان", 0.9)]
        return [("خبر_كان", 0.85)]

    # Standard verb-argument structure
    if stype == "EVENT":
        return [("فعل", 0.95)]

    if stype == "ENTITY" and verb_seen and not subject_seen:
        return [("فاعل", 0.9)]

    if stype == "ENTITY" and verb_seen and subject_seen:
        return [("مفعول", 0.85)]

    # Nominal sentence
    if stype == "ENTITY" and not verb_seen and position == 0:
        return [("مبتدأ", 0.85)]

    if stype == "ENTITY" and not verb_seen:
        return [("خبر", 0.8)]

    return [("غير_محدد", 0.5)]
