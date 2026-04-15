"""Unicode as Cognitive Input — إثبات اليونيكود كمعطى عقلي أولي.

Implements the formal proof that Unicode enters the system as primary
cognitive material (not a complete meaning), and is re-rationalised
layer by layer through the cognitive chain until it reaches the rank
of judgement-ready input — with no jumps permitted.

Modules
-------
chain
    The nine-layer cognitive processing chain (U₀–U₈).
gate
    Gate logic for each layer transition (Tᵢ: Uᵢ → Uᵢ₊₁).
proof
    Formal proof verification for the Unicode cognitive input thesis.
"""

from arabic_engine.cognitive_input.chain import (
    run_cognitive_chain as run_cognitive_chain,
)
from arabic_engine.cognitive_input.gate import (
    evaluate_gate as evaluate_gate,
)
from arabic_engine.cognitive_input.proof import (
    verify_unicode_cognitive_proof as verify_unicode_cognitive_proof,
)

__all__ = [
    "evaluate_gate",
    "run_cognitive_chain",
    "verify_unicode_cognitive_proof",
]
