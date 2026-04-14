#!/usr/bin/env python3
"""Example run — demonstrates the full v2 pipeline on a sample sentence.

Sentence: كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ
Expected output includes lexical closures, syntax nodes, concepts,
dalāla links, judgment, time/space tags, evaluation, and inference.
"""

from __future__ import annotations

from arabic_engine.closure import format_closure_report, verify_general_closure
from arabic_engine.cognition.inference_rules import InferenceEngine
from arabic_engine.cognition.world_model import WorldModel
from arabic_engine.core.enums import TruthState
from arabic_engine.pipeline import run, verify_contracts


def main() -> None:
    # ── Verify layer contracts ──────────────────────────────────
    print("=" * 60)
    print("Layer contract verification …")
    try:
        verify_contracts()
        print("  ✓ All contracts satisfied.")
    except ValueError as exc:
        print(f"  ✗ Contract violation: {exc}")
    print()

    # ── Set up world model (v2) ─────────────────────────────────
    world = WorldModel()
    world.add_fact(
        subject="زَيْد",
        predicate="كَتَبَ",
        obj="رِسَالَة",
        truth_state=TruthState.CERTAIN,
        source="witness",
    )

    # ── Set up inference engine (v2) ────────────────────────────
    engine = InferenceEngine()

    # ── Run pipeline ────────────────────────────────────────────
    sentence = "كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ"
    print("=" * 60)
    print(f"Input: {sentence}")
    print("=" * 60)

    result = run(sentence, world=world, inference_engine=engine)

    # ── Display results ─────────────────────────────────────────
    print("\n── Normalised ──")
    print(f"  {result.normalised}")

    print("\n── Tokens ──")
    for t in result.tokens:
        print(f"  • {t}")

    print("\n── Lexical Closures ──")
    for cl in result.closures:
        print(
            f"  {cl.surface:>20}  →  lemma={cl.lemma}, "
            f"root={cl.root}, pattern={cl.pattern}, pos={cl.pos.name}"
        )

    print("\n── Syntax (i'rāb) ──")
    for sn in result.syntax_nodes:
        print(
            f"  {sn.token:>20}  →  case={sn.case.name}, "
            f"role={sn.role.name}, governor={sn.governor}"
        )

    print("\n── Concepts ──")
    for co in result.concepts:
        print(
            f"  [{co.concept_id}] {co.label}  "
            f"type={co.semantic_type.name}  props={co.properties}"
        )

    print("\n── Dalāla Links ──")
    for lk in result.dalala_links:
        print(
            f"  {lk.source_lemma} → concept {lk.target_concept_id}  "
            f"type={lk.dalala_type.name}  "
            f"accepted={lk.accepted}  conf={lk.confidence}"
        )

    print("\n── Proposition (judgment) ──")
    p = result.proposition
    print(
        f"  subject={p.subject}, predicate={p.predicate}, "
        f"object={p.obj}, time={p.time.name}, polarity={p.polarity}"
    )

    print("\n── Time / Space ──")
    ts = result.time_space
    print(f"  time={ts.time_ref.name}, space={ts.space_ref.name}")

    print("\n── Evaluation ──")
    ev = result.eval_result
    print(
        f"  truth={ev.truth_state.name}, "
        f"guidance={ev.guidance_state.name}, "
        f"confidence={ev.confidence}"
    )

    print("\n── World-Model Adjustment ──")
    print(f"  factor={result.world_adjustment}")

    if result.inferences:
        print("\n── Inferences ──")
        for inf in result.inferences:
            print(
                f"  rule={inf.rule_name}, valid={inf.valid}, "
                f"conf={inf.confidence}"
            )
    else:
        print("\n── Inferences ──")
        print("  (none derived)")

    print("\n" + "=" * 60)
    print("Pipeline complete.")

    # ── General Closure Verification (Ch. 19) ───────────────
    print()
    closure_result = verify_general_closure()
    print(format_closure_report(closure_result))


if __name__ == "__main__":
    main()
