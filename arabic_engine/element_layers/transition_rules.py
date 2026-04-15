"""Transition rules — قواعد الانتقال بين الطبقات.

Central module that collects all gate-check functions and provides
a unified validation interface for the full layer trace.
"""

from __future__ import annotations

from arabic_engine.core.enums import TransitionGateStatus
from arabic_engine.core.types import (
    AuditoryMinimumRecord,
    GenerativeProfileRecord,
    JudgmentRecordL5,
    LayerTraceRecord,
    MentalFoundationRecord,
    StructuralProfileRecord,
    TransformationProfileRecord,
    TransitionGate,
)
from arabic_engine.element_layers.layer0_mental import check_gate_0_to_1
from arabic_engine.element_layers.layer1_generative import check_gate_1_to_2
from arabic_engine.element_layers.layer2_auditory import check_gate_2_to_3
from arabic_engine.element_layers.layer3_structural import check_gate_3_to_4
from arabic_engine.element_layers.layer4_transformation import check_gate_4_to_5
from arabic_engine.element_layers.layer5_judgment import check_gate_5_to_6


def gate_0_to_1(mental: MentalFoundationRecord) -> TransitionGate:
    """بوابة 0→1: الأساس العقلي → القوام التوليدي."""
    return check_gate_0_to_1(mental)


def gate_1_to_2(generative: GenerativeProfileRecord) -> TransitionGate:
    """بوابة 1→2: القوام التوليدي → القوام السمعي."""
    return check_gate_1_to_2(generative)


def gate_2_to_3(auditory: AuditoryMinimumRecord) -> TransitionGate:
    """بوابة 2→3: القوام السمعي → القوام البنيوي."""
    return check_gate_2_to_3(auditory)


def gate_3_to_4(structural: StructuralProfileRecord) -> TransitionGate:
    """بوابة 3→4: القوام البنيوي → التحول."""
    return check_gate_3_to_4(structural)


def gate_4_to_5(transformation: TransformationProfileRecord) -> TransitionGate:
    """بوابة 4→5: التحول → الوظيفة العليا."""
    return check_gate_4_to_5(transformation)


def gate_5_to_6(
    judgment: JudgmentRecordL5,
    mental: MentalFoundationRecord,
) -> TransitionGate:
    """بوابة 5→6: الوظيفة العليا → التمثيل البرمجي."""
    return check_gate_5_to_6(judgment, mental)


def validate_full_trace(trace: LayerTraceRecord) -> bool:
    """تحقق من مسار طبقي كامل — all gates must be PASSED."""
    if trace.final_gate_status != TransitionGateStatus.PASSED:
        return False
    for gate in trace.gates:
        if gate.gate_status != TransitionGateStatus.PASSED:
            return False
    return True
