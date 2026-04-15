"""Layer 6 — طبقة التمثيل البرمجي (Programmatic Representation).

Converts the theoretical model into a codeable structure with full
traceability back through all layers.
"""

from __future__ import annotations

import hashlib

from arabic_engine.core.enums import StrictLayerID
from arabic_engine.core.types import (
    AuditoryMinimumRecord,
    GenerativeProfileRecord,
    JudgmentRecordL5,
    MentalFoundationRecord,
    RepresentationRecord,
    StructuralProfileRecord,
    TransformationProfileRecord,
)


def compute_feature_hash(
    generative: GenerativeProfileRecord,
    auditory: AuditoryMinimumRecord,
) -> str:
    """بصمة الخصائص — feature hash combining generative + auditory.

    Creates a deterministic hash from the key features of the element.
    """
    parts = [
        str(generative.voicedness),
        generative.place_class,
        generative.manner_class,
        f"{generative.closure_value:.2f}",
        f"{generative.sonority_level:.2f}",
        f"{auditory.audibility_score:.2f}",
        f"{auditory.unity_score:.2f}",
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def map_to_root_node(structural: StructuralProfileRecord) -> str:
    """تقابل جذري — root mapping description."""
    if structural.root_slot in ("fa", "ayn", "lam"):
        return f"root:{structural.root_slot}"
    if structural.augmentation_score > 0.5:
        return "augmented"
    if structural.attachment_score > 0.5:
        return "attached"
    return "non_root"


def compile_rule_set(
    transformation: TransformationProfileRecord,
) -> tuple[str, ...]:
    """مجموعة القواعد — compile applicable transformation rules."""
    rules: list[str] = []
    if transformation.substitution_confidence > 0.3:
        rules.append("ibdal")
    if transformation.deletion_confidence > 0.3:
        rules.append("hadhf")
    if transformation.illal_confidence > 0.3:
        rules.append("illal")
    if transformation.idgham_confidence > 0.3:
        rules.append("idgham")
    if transformation.inflection_stability_score > 0.7:
        rules.append("stable")
    return tuple(rules)


def validate_against_reality(
    judgment: JudgmentRecordL5,
    mental: MentalFoundationRecord,
) -> bool:
    """تحقق مطابقة الواقع — validate judgment against reality-match."""
    return (
        judgment.judgment_confidence >= 0.3
        and mental.reality_match_score >= 0.1
    )


def build_representation(
    element_id: str,
    mental: MentalFoundationRecord,
    generative: GenerativeProfileRecord,
    auditory: AuditoryMinimumRecord,
    structural: StructuralProfileRecord,
    transformation: TransformationProfileRecord,
    judgment: JudgmentRecordL5,
) -> RepresentationRecord:
    """بناء سجل التمثيل البرمجي — final programmatic representation."""
    feature_hash = compute_feature_hash(generative, auditory)
    root_mapping = map_to_root_node(structural)
    rule_set = compile_rule_set(transformation)
    valid = validate_against_reality(judgment, mental)

    # Build confidence chain from all layers
    confidence_chain = (
        mental.reality_match_score,
        generative.sonority_level,
        auditory.unity_score,
        structural.constitutiveness_score,
        transformation.recoverability_score,
        judgment.judgment_confidence,
    )

    # Determine graph target
    graph_target = "lexical"
    if judgment.deictic_score > 0.5:
        graph_target = "deictic"
    elif judgment.relational_score > 0.5:
        graph_target = "relational"

    layer_trace = (
        StrictLayerID.MENTAL_FOUNDATION,
        StrictLayerID.GENERATIVE,
        StrictLayerID.AUDITORY_MINIMUM,
        StrictLayerID.STRUCTURAL,
        StrictLayerID.TRANSFORMATION,
        StrictLayerID.HIGHER_FUNCTION,
        StrictLayerID.PROGRAMMATIC,
    )

    return RepresentationRecord(
        entity_id=element_id,
        layer_trace=layer_trace,
        feature_hash=feature_hash,
        root_mapping=root_mapping,
        rule_set=rule_set,
        validation_status=valid,
        confidence_chain=confidence_chain,
        graph_target=graph_target,
    )
