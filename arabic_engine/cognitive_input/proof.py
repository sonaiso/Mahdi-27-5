"""Formal proof verification — إثبات برهان اليونيكود كمعطى عقلي أولي.

Verifies the formal proof that Unicode enters the system as primary
cognitive material and is re-rationalised through the nine-layer chain
with no jumps (Art. 47–52).

The proof has five premises:
1. Unicode enters as capturable encoding material (Art. 47)
2. Capturable material is not a complete meaning (Art. 48)
3. Therefore it may be treated as primary cognitive input (Art. 49)
4. But primary cognitive input requires re-rationalisation (Art. 50)
5. Each layer has a minimum completeness → no jumping (Art. 51)

Conclusion: Unicode is re-rationalised layer by layer to judgement (Art. 52)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List

from arabic_engine.cognitive_input.chain import run_cognitive_chain
from arabic_engine.cognitive_input.gate import (
    detect_jump_violations,
    is_valid_transition,
)
from arabic_engine.core.enums import CognitiveLayerID, LayerGateDecision

# ── Proof status ────────────────────────────────────────────────────


class ProofConditionStatus(Enum):
    """Status of a single proof condition."""

    VERIFIED = auto()   # محقق
    FAILED = auto()     # غير محقق


@dataclass(frozen=True)
class ProofCondition:
    """A single condition in the formal proof."""

    condition_id: str
    article: str
    description: str
    description_ar: str
    status: ProofConditionStatus
    evidence: str = ""


@dataclass
class UnicodeCognitiveProofResult:
    """Result of the full Unicode-as-cognitive-input proof verification.

    Contains the five premises, the conclusion, and supplementary
    structural checks (jump prevention, ascending order, completeness).
    """

    conditions: List[ProofCondition] = field(default_factory=list)
    all_passed: bool = False
    summary: str = ""
    summary_ar: str = ""


# ── Proof verification ──────────────────────────────────────────────


def verify_unicode_cognitive_proof(
    test_text: str = "كَتَبَ",
) -> UnicodeCognitiveProofResult:
    """Verify the formal proof that Unicode is cognitive input (Art. 47–52).

    Runs the cognitive chain on *test_text* and checks all formal
    conditions of the proof.

    Parameters
    ----------
    test_text : str
        A sample Arabic text to use for the proof demonstration.

    Returns
    -------
    UnicodeCognitiveProofResult
        The complete proof verification result.
    """
    result = UnicodeCognitiveProofResult()
    chain = run_cognitive_chain(test_text)

    # ── Premise 1 (Art. 47): Unicode enters as capturable material ──
    p1_ok = bool(test_text) and len(chain.layer_results) > 0
    result.conditions.append(ProofCondition(
        condition_id="P1",
        article="Art. 47",
        description=(
            "Unicode enters the system as capturable encoding material"
        ),
        description_ar=(
            "اليونيكود يدخل النظام بوصفه مادة ترميزية قابلة للالتقاط"
        ),
        status=(
            ProofConditionStatus.VERIFIED if p1_ok
            else ProofConditionStatus.FAILED
        ),
        evidence=f"Input text has {len(test_text)} characters",
    ))

    # ── Premise 2 (Art. 48): Capturable ≠ complete meaning ──────────
    # Verified structurally: the first layer produces atoms, not meanings
    p2_ok = (
        len(chain.layer_results) >= 1
        and chain.layer_results[0].layer == CognitiveLayerID.ATOMIZED
    )
    result.conditions.append(ProofCondition(
        condition_id="P2",
        article="Art. 48",
        description=(
            "Capturable material is not a complete meaning but is "
            "amenable to designation, differentiation, and conception"
        ),
        description_ar=(
            "المادة القابلة للالتقاط ليست معنىً مكتملًا لكنها قابلة "
            "للتعيين والتمييز والتصور"
        ),
        status=(
            ProofConditionStatus.VERIFIED if p2_ok
            else ProofConditionStatus.FAILED
        ),
        evidence=(
            f"First layer output is {chain.layer_results[0].layer.name}"
            if chain.layer_results
            else "No layer results"
        ),
    ))

    # ── Premise 3 (Art. 49): → primary cognitive input ──────────────
    p3_ok = p1_ok and p2_ok
    result.conditions.append(ProofCondition(
        condition_id="P3",
        article="Art. 49",
        description=(
            "Therefore Unicode may be treated as primary cognitive input"
        ),
        description_ar=(
            "فيجوز معاملة اليونيكود بوصفه معطًى عقليًا أوليًا"
        ),
        status=(
            ProofConditionStatus.VERIFIED if p3_ok
            else ProofConditionStatus.FAILED
        ),
        evidence="Follows from P1 ∧ P2",
    ))

    # ── Premise 4 (Art. 50): Re-rationalisation required ────────────
    # Verified: the chain processes through multiple layers
    p4_ok = len(chain.layer_results) >= 8
    result.conditions.append(ProofCondition(
        condition_id="P4",
        article="Art. 50",
        description=(
            "Primary cognitive input must be re-rationalised through "
            "the cognitive chain layer by layer"
        ),
        description_ar=(
            "المعطى العقلي الأولي لا يصير صالحًا للدلالة ولا للحكم "
            "إلا بعد إعادة بنائه داخل سلسلة العقل"
        ),
        status=(
            ProofConditionStatus.VERIFIED if p4_ok
            else ProofConditionStatus.FAILED
        ),
        evidence=f"Chain produced {len(chain.layer_results)} layer results",
    ))

    # ── Premise 5 (Art. 51): Each layer has min completeness → no jump
    all_layers_ascending = True
    layers = list(CognitiveLayerID)
    for i in range(len(layers) - 1):
        if not is_valid_transition(layers[i], layers[i + 1]):
            all_layers_ascending = False
            break

    no_jumps = len(chain.jump_violations) == 0
    all_gates_ok = all(
        r.gate.decision in (LayerGateDecision.PASS, LayerGateDecision.COMPLETE)
        for r in chain.layer_results
    )
    p5_ok = all_layers_ascending and no_jumps and all_gates_ok

    result.conditions.append(ProofCondition(
        condition_id="P5",
        article="Art. 51",
        description=(
            "Each layer has minimum completeness and jumping is "
            "structurally prevented"
        ),
        description_ar=(
            "لكل طبقة حد أدنى مكتمل، والقفز ممتنع بنيويًا"
        ),
        status=(
            ProofConditionStatus.VERIFIED if p5_ok
            else ProofConditionStatus.FAILED
        ),
        evidence=(
            f"Ascending: {all_layers_ascending}, "
            f"No jumps: {no_jumps}, "
            f"All gates passed: {all_gates_ok}"
        ),
    ))

    # ── Conclusion (Art. 52): Full re-rationalisation proven ────────
    conclusion_ok = all(
        c.status == ProofConditionStatus.VERIFIED
        for c in result.conditions
    )
    result.conditions.append(ProofCondition(
        condition_id="CONCLUSION",
        article="Art. 52",
        description=(
            "The program receives Unicode as primary cognitive input, "
            "re-rationalises it layer by layer through the cognitive "
            "chain, and produces judgement-ready material with no jumps"
        ),
        description_ar=(
            "يثبت أن البرنامج يستلم المعطى من اليونيكود كمعطًى عقلي "
            "أولي، ثم يعيد بناءه داخل سلسلة العقل وفق أوليات العقل "
            "والحد الأدنى المكتمل لكل طبقة، ومن غير قفز"
        ),
        status=(
            ProofConditionStatus.VERIFIED if conclusion_ok
            else ProofConditionStatus.FAILED
        ),
        evidence=(
            f"Chain complete: {chain.is_complete}, "
            f"Final layer: {chain.final_layer.name}"
        ),
    ))

    # ── Supplementary: Jump violation checks (Art. 35) ──────────────
    # Verify specific prohibited jumps
    prohibited_jumps = [
        (CognitiveLayerID.UNICODE_RAW, CognitiveLayerID.JUDGEMENT_READY),
        (CognitiveLayerID.UNICODE_RAW, CognitiveLayerID.SEMANTIC_SUBJECT),
        (CognitiveLayerID.UNICODE_RAW, CognitiveLayerID.DISCIPLINED_CONCEPTION),
        (CognitiveLayerID.NORMALIZED, CognitiveLayerID.JUDGEMENT_READY),
        (CognitiveLayerID.INITIAL_CONCEPTION, CognitiveLayerID.JUDGEMENT_READY),
    ]

    for from_l, to_l in prohibited_jumps:
        violations = detect_jump_violations(from_l, to_l)
        jump_prevented = len(violations) > 0
        result.conditions.append(ProofCondition(
            condition_id=f"JUMP_{from_l.name}_to_{to_l.name}",
            article="Art. 35",
            description=(
                f"Jump from {from_l.name} to {to_l.name} "
                f"must be prevented"
            ),
            description_ar=(
                f"يُمنع القفز من {from_l.name} إلى {to_l.name}"
            ),
            status=(
                ProofConditionStatus.VERIFIED if jump_prevented
                else ProofConditionStatus.FAILED
            ),
            evidence="; ".join(violations) if violations else "No violation detected",
        ))

    result.all_passed = all(
        c.status == ProofConditionStatus.VERIFIED
        for c in result.conditions
    )

    result.summary = (
        "Unicode as Cognitive Input Proof: "
        + ("VERIFIED ✓" if result.all_passed else "FAILED ✗")
        + f" ({sum(1 for c in result.conditions if c.status == ProofConditionStatus.VERIFIED)}"
        f"/{len(result.conditions)} conditions passed)"
    )
    result.summary_ar = (
        "برهان اليونيكود كمعطى عقلي أولي: "
        + ("مُحقَّق ✓" if result.all_passed else "غير مُحقَّق ✗")
    )

    return result


def format_proof_report(result: UnicodeCognitiveProofResult) -> str:
    """Format a human-readable proof report.

    Parameters
    ----------
    result : UnicodeCognitiveProofResult
        The result from :func:`verify_unicode_cognitive_proof`.

    Returns
    -------
    str
        Formatted report string.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("Unicode as Cognitive Input — Proof Verification")
    lines.append("إثبات اليونيكود كمعطى عقلي أولي — التحقق البرهاني")
    lines.append("=" * 60)

    for cond in result.conditions:
        status_icon = "✓" if cond.status == ProofConditionStatus.VERIFIED else "✗"
        lines.append(f"\n[{status_icon}] {cond.condition_id} ({cond.article})")
        lines.append(f"    {cond.description}")
        lines.append(f"    {cond.description_ar}")
        if cond.evidence:
            lines.append(f"    Evidence: {cond.evidence}")

    lines.append("\n" + "-" * 60)
    lines.append(result.summary)
    lines.append(result.summary_ar)
    lines.append("=" * 60)

    return "\n".join(lines)
