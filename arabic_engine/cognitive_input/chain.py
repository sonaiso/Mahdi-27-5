"""Cognitive chain — سلسلة العقلنة الكاملة من اليونيكود إلى الحكم.

Implements the nine-layer cognitive re-rationalisation chain (Art. 9):

    U₀ (Unicode raw) → U₁ (atomized) → U₂ (differentiated) →
    U₃ (normalized) → U₄ (designated) → U₅ (initial conception) →
    U₆ (disciplined conception) → U₇ (semantic subject) →
    U₈ (judgement-ready)

Each transition uses the existing signal/signifier infrastructure
where applicable, and wraps it in the cognitive gate framework.
"""

from __future__ import annotations

from typing import List

from arabic_engine.cognitive_input.gate import (
    detect_jump_violations,
    evaluate_gate,
)
from arabic_engine.core.enums import CognitiveLayerID, LayerGateDecision, SignalType
from arabic_engine.core.types import (
    AtomizedInput,
    CognitiveChainResult,
    CognitiveGateRecord,
    CognitiveLayerResult,
    DesignatedUnit,
    DifferentiatedUnit,
    DisciplinedConceptionRecord,
    InitialConceptionRecord,
    JudgementReadyInput,
    NormalizedUnit,
    SemanticSubject,
)
from arabic_engine.signal.unicode_atoms import decompose

# ── Layer 0→1: Atomization (Art. 12–14) ─────────────────────────────


def _atomize(text: str) -> tuple[AtomizedInput, CognitiveLayerResult]:
    """U₀ → U₁: decompose Unicode into atoms."""
    atoms = decompose(text)

    valid = sum(1 for a in atoms if a.signal_type != SignalType.UNKNOWN)
    rejected = sum(1 for a in atoms if a.signal_type == SignalType.UNKNOWN)
    suspended = 0

    completeness = valid / len(atoms) if atoms else 0.0

    gate = evaluate_gate(
        from_layer=CognitiveLayerID.UNICODE_RAW,
        to_layer=CognitiveLayerID.ATOMIZED,
        membership=bool(text),
        completeness=completeness,
        has_blocker=len(atoms) == 0 and bool(text),
    )

    atomized = AtomizedInput(
        atoms=tuple(atoms),
        source_text=text,
        atom_count=len(atoms),
        valid_count=valid,
        suspended_count=suspended,
        rejected_count=rejected,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.ATOMIZED,
        gate=gate,
        membership=bool(text),
        completeness=completeness,
        blocker=gate.has_blocker,
    )

    return atomized, result


# ── Layer 1→2: Differentiation (Art. 15–17) ─────────────────────────


def _differentiate(
    atomized: AtomizedInput,
) -> tuple[list[DifferentiatedUnit], CognitiveLayerResult]:
    """U₁ → U₂: differentiate atoms from neighbours."""
    units: list[DifferentiatedUnit] = []
    atoms = atomized.atoms

    for i, atom in enumerate(atoms):
        prev_char = atoms[i - 1].char if i > 0 else ""
        next_char = atoms[i + 1].char if i < len(atoms) - 1 else ""
        distinct = atom.char != prev_char or atom.char != next_char

        units.append(DifferentiatedUnit(
            unit_id=f"DIFF_{atom.atom_id}",
            atom=atom,
            neighbour_distinct=distinct,
            assigned_type=atom.signal_type.name,
            initial_coherence=(
                "base" if atom.signal_type == SignalType.BASE_LETTER
                else "modifier" if atom.signal_type == SignalType.DIACRITIC
                else "separator" if atom.signal_type == SignalType.WHITESPACE
                else "other"
            ),
            combinable=atom.signal_type in (
                SignalType.BASE_LETTER, SignalType.DIACRITIC,
            ),
        ))

    completeness = 1.0 if units else 0.0
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.ATOMIZED,
        to_layer=CognitiveLayerID.DIFFERENTIATED,
        membership=bool(units),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.DIFFERENTIATED,
        gate=gate,
        membership=bool(units),
        completeness=completeness,
        blocker=False,
    )

    return units, result


# ── Layer 2→3: Normalization (Art. 18–20) ────────────────────────────


def _normalize(
    diff_units: list[DifferentiatedUnit],
    raw_text: str,
) -> tuple[list[NormalizedUnit], CognitiveLayerResult]:
    """U₂ → U₃: cluster and normalize."""
    from arabic_engine.signifier.unicode_norm import normalize

    normed_text = normalize(raw_text)
    tokens = normed_text.split() if normed_text.strip() else []

    units: list[NormalizedUnit] = []
    for idx, token in enumerate(tokens):
        units.append(NormalizedUnit(
            unit_id=f"NORM_{idx}",
            surface_text=token,
            normalized_text=token,
            raw_preserved=raw_text,
            cluster_count=len(token),
            normalization_policy="NFC+tatweel_removal+whitespace_collapse",
        ))

    completeness = 1.0 if units else 0.0
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.DIFFERENTIATED,
        to_layer=CognitiveLayerID.NORMALIZED,
        membership=bool(diff_units),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.NORMALIZED,
        gate=gate,
        membership=bool(diff_units),
        completeness=completeness,
        blocker=False,
    )

    return units, result


# ── Layer 3→4: Designation (Art. 21–25) ──────────────────────────────


def _designate(
    norm_units: list[NormalizedUnit],
) -> tuple[list[DesignatedUnit], CognitiveLayerResult]:
    """U₃ → U₄: establish presence, difference, designation."""
    units: list[DesignatedUnit] = []

    for idx, nu in enumerate(norm_units):
        units.append(DesignatedUnit(
            unit_id=f"DESG_{idx}",
            normalized_text=nu.normalized_text,
            is_present=True,
            is_distinct=True,
            initial_designation=nu.normalized_text,
            structural_position=f"token_{idx}",
            conception_ready=True,
        ))

    completeness = 1.0 if units else 0.0
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.NORMALIZED,
        to_layer=CognitiveLayerID.DESIGNATED,
        membership=bool(norm_units),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.DESIGNATED,
        gate=gate,
        membership=bool(norm_units),
        completeness=completeness,
        blocker=False,
    )

    return units, result


# ── Layer 4→5: Initial Conception (Art. 26, 28) ─────────────────────


def _initial_conception(
    designated: list[DesignatedUnit],
) -> tuple[list[InitialConceptionRecord], CognitiveLayerResult]:
    """U₄ → U₅: form initial conception for each designated unit."""
    conceptions: list[InitialConceptionRecord] = []

    for du in designated:
        if not du.conception_ready:
            continue
        conceptions.append(InitialConceptionRecord(
            conception_id=f"IC_{du.unit_id}",
            source_designation=du.initial_designation,
            initial_unity=du.normalized_text,
            initial_boundary=f"boundary_of_{du.normalized_text}",
            initial_direction=du.structural_position,
            recallable=True,
        ))

    completeness = (
        len(conceptions) / len(designated) if designated else 0.0
    )
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.DESIGNATED,
        to_layer=CognitiveLayerID.INITIAL_CONCEPTION,
        membership=bool(designated),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.INITIAL_CONCEPTION,
        gate=gate,
        membership=bool(designated),
        completeness=completeness,
        blocker=False,
    )

    return conceptions, result


# ── Layer 5→6: Disciplined Conception (Art. 27, 29) ─────────────────


def _discipline_conception(
    initials: list[InitialConceptionRecord],
) -> tuple[list[DisciplinedConceptionRecord], CognitiveLayerResult]:
    """U₅ → U₆: discipline conceptions with boundary/unity fixing."""
    disciplined: list[DisciplinedConceptionRecord] = []

    for ic in initials:
        disciplined.append(DisciplinedConceptionRecord(
            conception_id=f"DC_{ic.conception_id}",
            source_initial=ic.conception_id,
            boundary_fixed=True,
            unity_fixed=True,
            ambiguity_removed=True,
            encoding_ready=True,
        ))

    completeness = 1.0 if disciplined else 0.0
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.INITIAL_CONCEPTION,
        to_layer=CognitiveLayerID.DISCIPLINED_CONCEPTION,
        membership=bool(initials),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.DISCIPLINED_CONCEPTION,
        gate=gate,
        membership=bool(initials),
        completeness=completeness,
        blocker=False,
    )

    return disciplined, result


# ── Layer 6→7: Semantic Subject (Art. 31–33) ────────────────────────


def _build_semantic_subject(
    disciplined: list[DisciplinedConceptionRecord],
) -> tuple[list[SemanticSubject], CognitiveLayerResult]:
    """U₆ → U₇: conceptual encoding + semantic liberation."""
    subjects: list[SemanticSubject] = []

    for dc in disciplined:
        if not dc.encoding_ready:
            continue
        subjects.append(SemanticSubject(
            subject_id=f"SS_{dc.conception_id}",
            source_conception=dc.conception_id,
            conceptual_encoding=f"enc_{dc.conception_id}",
            semantic_determination="determined",
            dalala_ready=True,
        ))

    completeness = (
        len(subjects) / len(disciplined) if disciplined else 0.0
    )
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.DISCIPLINED_CONCEPTION,
        to_layer=CognitiveLayerID.SEMANTIC_SUBJECT,
        membership=bool(disciplined),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.SEMANTIC_SUBJECT,
        gate=gate,
        membership=bool(disciplined),
        completeness=completeness,
        blocker=False,
    )

    return subjects, result


# ── Layer 7→8: Judgement-Ready (Art. 41, terminal) ──────────────────


def _make_judgement_ready(
    subjects: list[SemanticSubject],
) -> tuple[list[JudgementReadyInput], CognitiveLayerResult]:
    """U₇ → U₈: liberate subject and assign judgement direction."""
    ready_inputs: list[JudgementReadyInput] = []

    for ss in subjects:
        if not ss.dalala_ready:
            continue
        ready_inputs.append(JudgementReadyInput(
            input_id=f"JR_{ss.subject_id}",
            source_subject=ss.subject_id,
            subject_liberated=True,
            judgement_direction="existential",
            ready=True,
        ))

    completeness = (
        len(ready_inputs) / len(subjects) if subjects else 0.0
    )
    gate = evaluate_gate(
        from_layer=CognitiveLayerID.SEMANTIC_SUBJECT,
        to_layer=CognitiveLayerID.JUDGEMENT_READY,
        membership=bool(subjects),
        completeness=completeness,
        has_blocker=False,
    )

    result = CognitiveLayerResult(
        layer=CognitiveLayerID.JUDGEMENT_READY,
        gate=gate,
        membership=bool(subjects),
        completeness=completeness,
        blocker=False,
    )

    return ready_inputs, result


# ── Full chain runner ───────────────────────────────────────────────


def run_cognitive_chain(text: str) -> CognitiveChainResult:
    """Run the full cognitive re-rationalisation chain on *text*.

    Processes the input through all nine layers (U₀–U₈), enforcing
    gate conditions at each transition and detecting any jump violations.

    Parameters
    ----------
    text : str
        Raw Unicode input text.

    Returns
    -------
    CognitiveChainResult
        Complete result including all layer results, gate records,
        and the final verdict.
    """
    layer_results: List[CognitiveLayerResult] = []
    gates: List[CognitiveGateRecord] = []
    jump_violations: list[str] = []
    final_layer = CognitiveLayerID.UNICODE_RAW

    # U₀ → U₁: Atomization
    atomized, r1 = _atomize(text)
    layer_results.append(r1)
    gates.append(r1.gate)
    if r1.gate.decision in (LayerGateDecision.REJECT,):
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=CognitiveLayerID.UNICODE_RAW,
            is_complete=False,
            reason=r1.gate.reason,
        )
    final_layer = CognitiveLayerID.ATOMIZED

    # U₁ → U₂: Differentiation
    diff_units, r2 = _differentiate(atomized)
    layer_results.append(r2)
    gates.append(r2.gate)
    if r2.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r2.gate.reason,
        )
    final_layer = CognitiveLayerID.DIFFERENTIATED

    # U₂ → U₃: Normalization
    norm_units, r3 = _normalize(diff_units, text)
    layer_results.append(r3)
    gates.append(r3.gate)
    if r3.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r3.gate.reason,
        )
    final_layer = CognitiveLayerID.NORMALIZED

    # U₃ → U₄: Designation
    designated, r4 = _designate(norm_units)
    layer_results.append(r4)
    gates.append(r4.gate)
    if r4.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r4.gate.reason,
        )
    final_layer = CognitiveLayerID.DESIGNATED

    # U₄ → U₅: Initial Conception
    initials, r5 = _initial_conception(designated)
    layer_results.append(r5)
    gates.append(r5.gate)
    if r5.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r5.gate.reason,
        )
    final_layer = CognitiveLayerID.INITIAL_CONCEPTION

    # U₅ → U₆: Disciplined Conception
    disciplined, r6 = _discipline_conception(initials)
    layer_results.append(r6)
    gates.append(r6.gate)
    if r6.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r6.gate.reason,
        )
    final_layer = CognitiveLayerID.DISCIPLINED_CONCEPTION

    # U₆ → U₇: Semantic Subject
    subjects, r7 = _build_semantic_subject(disciplined)
    layer_results.append(r7)
    gates.append(r7.gate)
    if r7.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r7.gate.reason,
        )
    final_layer = CognitiveLayerID.SEMANTIC_SUBJECT

    # U₇ → U₈: Judgement-Ready
    ready, r8 = _make_judgement_ready(subjects)
    layer_results.append(r8)
    gates.append(r8.gate)
    if r8.gate.decision == LayerGateDecision.REJECT:
        return CognitiveChainResult(
            source_text=text,
            layer_results=tuple(layer_results),
            gates=tuple(gates),
            final_layer=final_layer,
            is_complete=False,
            reason=r8.gate.reason,
        )
    final_layer = CognitiveLayerID.JUDGEMENT_READY

    # Check for any jump violations across the full chain
    layer_order = list(CognitiveLayerID)
    for i in range(len(layer_order) - 1):
        violations = detect_jump_violations(layer_order[i], layer_order[i + 1])
        jump_violations.extend(violations)

    is_complete = (
        final_layer == CognitiveLayerID.JUDGEMENT_READY
        and all(
            r.gate.decision in (LayerGateDecision.PASS, LayerGateDecision.COMPLETE)
            for r in layer_results
        )
    )

    return CognitiveChainResult(
        source_text=text,
        layer_results=tuple(layer_results),
        gates=tuple(gates),
        final_layer=final_layer,
        is_complete=is_complete,
        jump_violations=tuple(jump_violations),
        reason="Full cognitive chain completed" if is_complete else "Chain incomplete",
    )
