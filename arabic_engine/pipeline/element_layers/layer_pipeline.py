"""Layer pipeline — أنبوب التنفيذ الطبقي الكامل.

Orchestrates the full Layer 0 → Layer 6 analysis for individual
phonological elements (code-points) and for whole words.
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import TransitionGateStatus
from arabic_engine.core.types import (
    LayerTraceRecord,
    RootPattern,
    Syllable,
    TransitionGate,
)
from arabic_engine.pipeline.element_layers.layer0_mental import build_mental_foundation
from arabic_engine.pipeline.element_layers.layer1_generative import build_generative_profile
from arabic_engine.pipeline.element_layers.layer2_auditory import build_auditory_minimum
from arabic_engine.pipeline.element_layers.layer3_structural import build_structural_profile
from arabic_engine.pipeline.element_layers.layer4_transformation import build_transformation_record
from arabic_engine.pipeline.element_layers.layer5_judgment import build_judgment
from arabic_engine.pipeline.element_layers.layer6_representation import build_representation
from arabic_engine.pipeline.element_layers.transition_rules import (
    gate_0_to_1,
    gate_1_to_2,
    gate_2_to_3,
    gate_3_to_4,
    gate_4_to_5,
    gate_5_to_6,
)
from arabic_engine.morphology.dmin import DMIN_REGISTRY


def analyze_element(
    codepoint: int,
    *,
    char: str = "",
    syllable: Optional[Syllable] = None,
    root_pattern: Optional[RootPattern] = None,
    surface_form: Optional[str] = None,
    underlying_form: Optional[str] = None,
    surface_present: bool = True,
    underlying_present: bool = True,
) -> LayerTraceRecord:
    """تحليل عنصر واحد عبر جميع الطبقات.

    Runs each layer in sequence; if any gate blocks, the analysis
    stops and returns a partial trace.
    """
    if not char and codepoint in DMIN_REGISTRY:
        char = chr(codepoint)

    element_id = f"U+{codepoint:04X}"
    gates: list[TransitionGate] = []

    # ── Layer 0: Mental Foundation ──────────────────────────────────
    mental = build_mental_foundation(codepoint)
    g0 = gate_0_to_1(mental)
    gates.append(g0)
    if g0.gate_status != TransitionGateStatus.PASSED:
        return LayerTraceRecord(
            element_id=element_id,
            layer_0=mental,
            gates=tuple(gates),
            final_gate_status=TransitionGateStatus.BLOCKED,
        )

    # ── Layer 1: Generative Profile ─────────────────────────────────
    generative = build_generative_profile(codepoint)
    g1 = gate_1_to_2(generative)
    gates.append(g1)
    if g1.gate_status != TransitionGateStatus.PASSED:
        return LayerTraceRecord(
            element_id=element_id,
            layer_0=mental,
            layer_1=generative,
            gates=tuple(gates),
            final_gate_status=TransitionGateStatus.BLOCKED,
        )

    # ── Layer 2: Auditory Minimum ───────────────────────────────────
    auditory = build_auditory_minimum(generative, syllable)
    g2 = gate_2_to_3(auditory)
    gates.append(g2)
    if g2.gate_status != TransitionGateStatus.PASSED:
        return LayerTraceRecord(
            element_id=element_id,
            layer_0=mental,
            layer_1=generative,
            layer_2=auditory,
            gates=tuple(gates),
            final_gate_status=TransitionGateStatus.BLOCKED,
        )

    # ── Layer 3: Structural Profile ─────────────────────────────────
    structural = build_structural_profile(
        codepoint, char, syllable, root_pattern,
    )
    g3 = gate_3_to_4(structural)
    gates.append(g3)
    if g3.gate_status != TransitionGateStatus.PASSED:
        return LayerTraceRecord(
            element_id=element_id,
            layer_0=mental,
            layer_1=generative,
            layer_2=auditory,
            layer_3=structural,
            gates=tuple(gates),
            final_gate_status=TransitionGateStatus.BLOCKED,
        )

    # ── Layer 4: Transformation ─────────────────────────────────────
    transformation = build_transformation_record(
        codepoint,
        structural,
        surface_form,
        underlying_form,
        surface_present,
        underlying_present,
    )
    g4 = gate_4_to_5(transformation)
    gates.append(g4)
    if g4.gate_status != TransitionGateStatus.PASSED:
        return LayerTraceRecord(
            element_id=element_id,
            layer_0=mental,
            layer_1=generative,
            layer_2=auditory,
            layer_3=structural,
            layer_4=transformation,
            gates=tuple(gates),
            final_gate_status=TransitionGateStatus.BLOCKED,
        )

    # ── Layer 5: Judgment ───────────────────────────────────────────
    judgment = build_judgment(structural, transformation)
    g5 = gate_5_to_6(judgment, mental)
    gates.append(g5)
    if g5.gate_status != TransitionGateStatus.PASSED:
        return LayerTraceRecord(
            element_id=element_id,
            layer_0=mental,
            layer_1=generative,
            layer_2=auditory,
            layer_3=structural,
            layer_4=transformation,
            layer_5=judgment,
            gates=tuple(gates),
            final_gate_status=TransitionGateStatus.BLOCKED,
        )

    # ── Layer 6: Representation ─────────────────────────────────────
    representation = build_representation(
        element_id, mental, generative, auditory,
        structural, transformation, judgment,
    )

    return LayerTraceRecord(
        element_id=element_id,
        layer_0=mental,
        layer_1=generative,
        layer_2=auditory,
        layer_3=structural,
        layer_4=transformation,
        layer_5=judgment,
        layer_6=representation,
        gates=tuple(gates),
        final_gate_status=TransitionGateStatus.PASSED,
    )


def analyze_word(
    word: str,
    *,
    root_pattern: Optional[RootPattern] = None,
) -> List[LayerTraceRecord]:
    """تحليل كلمة كاملة — analyse every element in a word.

    Splits the word into individual characters and runs the full
    layer pipeline on each one.
    """
    results: List[LayerTraceRecord] = []
    for char in word:
        cp = ord(char)
        # Skip combining marks (handled as part of the base character)
        if cp in DMIN_REGISTRY or (0x0621 <= cp <= 0x064A):
            trace = analyze_element(
                cp,
                char=char,
                root_pattern=root_pattern,
            )
            results.append(trace)
    return results
