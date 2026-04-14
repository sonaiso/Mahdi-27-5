"""Relation hypotheses — فرضيات علاقية.

Generates relation hypothesis nodes from concept hypotheses.
Each adjacent pair of concepts produces a candidate relation.

Supported relation types:
- إسناد (predication) — verb–subject / topic–comment
- ظرفية (adverbial/locative) — preposition-governed
- تقييد (restriction/modification) — default adjective/qualifier
- عطف (conjunction) — conjunctive particles و ف ثم أو
- إضافة (annexation/iḍāfa) — possessive construct
- حال (adverbial/ḥāl) — circumstantial relation
- بدل (apposition/substitution) — same-referent replacement
- توكيد (emphasis/corroboration) — emphatic repetition
- نعت (adjectival qualification) — adjective modifying noun
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode

_PREP_TOKENS = frozenset({
    "إلى", "من", "في", "على", "عن", "ب", "ل", "ك",
    "حتى", "منذ", "مذ", "خلا", "عدا", "حاشا",
})

_CONJUNCTION_PARTICLES = frozenset({
    "و", "ف", "ثم", "أو", "أم", "بل", "لا", "لكن", "حتى",
})

# Temporal/spatial adverbs that signal ظرفية
_TEMPORAL_ADVERBS = frozenset({
    "اليوم", "غدًا", "غداً", "أمس", "حين", "إذ", "إذا",
    "متى", "لما", "بعد", "قبل", "عند",
    "دائمًا", "أبدًا", "أحيانًا", "صباحًا", "مساءً",
    "ليلًا", "نهارًا",
})

_SPATIAL_ADVERBS = frozenset({
    "هنا", "هناك", "فوق", "تحت", "أمام", "خلف",
    "يمين", "يسار", "بين", "وسط", "حول",
    "شمال", "جنوب", "شرق", "غرب",
})

# Emphasis/corroboration tokens
_EMPHASIS_TOKENS = frozenset({
    "نفس", "عين", "كل", "جميع", "كلا", "كلتا",
    "أجمع", "أجمعين",
})


def generate(concept_hypotheses: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate relation hypotheses for adjacent concept pairs.

    Parameters
    ----------
    concept_hypotheses : list[HypothesisNode]
        Concept hypotheses in sentence order.

    Returns
    -------
    list[HypothesisNode]
        Relation hypotheses, one or more per adjacent pair.
    """
    hypotheses: List[HypothesisNode] = []
    for i in range(len(concept_hypotheses) - 1):
        src = concept_hypotheses[i]
        tgt = concept_hypotheses[i + 1]
        src_type = str(src.get("semantic_type", ""))
        tgt_type = str(tgt.get("semantic_type", ""))
        src_label = str(src.get("label", ""))
        tgt_label = str(tgt.get("label", ""))
        src_det = str(src.get("determination", ""))
        tgt_det = str(tgt.get("determination", ""))

        rels = _infer_relations(
            src_type, tgt_type, src_label, tgt_label,
            src_det, tgt_det,
        )

        for rel_idx, (rel, conf_factor) in enumerate(rels):
            node_id = f"REL_{src.node_id}_{tgt.node_id}"
            if rel_idx > 0:
                node_id = f"REL_{src.node_id}_{tgt.node_id}_ALT{rel_idx}"

            hypotheses.append(
                HypothesisNode(
                    node_id=node_id,
                    hypothesis_type="relation",
                    stage=ActivationStage.RELATION,
                    source_refs=(src.node_id, tgt.node_id),
                    payload=(
                        ("relation_type", rel),
                        ("source_label", src_label),
                        ("target_label", tgt_label),
                    ),
                    confidence=min(src.confidence, tgt.confidence) * conf_factor,
                    status=HypothesisStatus.ACTIVE,
                )
            )
    return hypotheses


def _infer_relations(
    src_type: str,
    tgt_type: str,
    src_label: str,
    tgt_label: str,
    src_det: str,
    tgt_det: str,
) -> list[tuple[str, float]]:
    """Infer relation type(s) for an adjacent concept pair.

    Returns a list of (relation_type, confidence_factor) tuples.
    Multiple entries indicate ambiguity — competing hypotheses.
    """
    # 1. Conjunction particles → عطف
    if tgt_label in _CONJUNCTION_PARTICLES:
        return [("عطف", 0.95)]
    if src_label in _CONJUNCTION_PARTICLES:
        return [("عطف", 0.95)]

    # 2. Preposition tokens → ظرفية
    if src_label in _PREP_TOKENS:
        return [("ظرفية", 0.95)]

    # 3. Temporal / spatial adverbs → ظرفية
    if src_label in _TEMPORAL_ADVERBS or src_label in _SPATIAL_ADVERBS:
        return [("ظرفية", 0.9)]

    # 4. Emphasis tokens → توكيد
    if tgt_label in _EMPHASIS_TOKENS:
        return [("توكيد", 0.85)]

    # 5. EVENT → ENTITY = إسناد (predication)
    if src_type == "EVENT" and tgt_type == "ENTITY":
        return [("إسناد", 1.0)]

    # 6. ENTITY + ENTITY: multiple possible relations
    if src_type == "ENTITY" and tgt_type == "ENTITY":
        return _entity_entity_relations(
            src_label, tgt_label, src_det, tgt_det,
        )

    # 7. EVENT + EVENT → عطف or subordination
    if src_type == "EVENT" and tgt_type == "EVENT":
        return [("عطف", 0.7), ("تقييد", 0.3)]

    # 8. Default → تقييد
    return [("تقييد", 1.0)]


def _entity_entity_relations(
    src_label: str,
    tgt_label: str,
    src_det: str,
    tgt_det: str,
) -> list[tuple[str, float]]:
    """Determine relation between two adjacent entities.

    This is the most ambiguous case in Arabic syntax.
    Possible relations: إضافة, نعت, بدل, توكيد, حال, تقييد.
    """
    results: list[tuple[str, float]] = []

    # إضافة (annexation): definite + indefinite-becoming-definite
    # e.g. كتاب الطالب (book of the student)
    if src_det == "indefinite" and tgt_det == "definite":
        results.append(("إضافة", 0.8))
    elif src_det == "definite" and tgt_det == "definite":
        # Could be نعت (adjective) or بدل (apposition) or توكيد
        results.append(("نعت", 0.5))
        results.append(("بدل", 0.3))
        if tgt_label in _EMPHASIS_TOKENS:
            results.append(("توكيد", 0.7))
    elif src_det == "indefinite" and tgt_det == "indefinite":
        # Likely نعت (adjective modifying indefinite noun)
        results.append(("نعت", 0.7))
        results.append(("حال", 0.3))

    # If no specific pattern matched, default to تقييد
    if not results:
        results.append(("تقييد", 1.0))

    return results
