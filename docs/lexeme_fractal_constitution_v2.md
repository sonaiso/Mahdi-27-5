# Lexeme Fractal Constitution v2 — دستور المفرد الفراكتالي

## Overview

This constitution establishes the single lexeme (المفرد) as a **complete
fractal unit** — the final rank of self-sufficiency and the first rank
of compositional society.  It sits after the Weight Fractal, Semantic
Direction, and Epistemic Reception constitutions in the pipeline and
directly precedes Noun, Verb, Particle, and Syntax constitutions.

## Position in the Pipeline

```
Unicode → Grapheme → Bare Material → Root → Weight → Direction
→ Derivation → **Lexeme** → POS Finalization → Composition Readiness
```

The lexeme is the closure point of the single-word analysis chain.

## The Six Pillars (Art. 20–26)

| # | Pillar (Arabic) | Pillar (English) | Enum |
|---|----------------|------------------|------|
| 1 | المادة | Material | `LexemePillar.MADDA` |
| 2 | القالب/الوزن | Template / Weight | `LexemePillar.QALIB_WAZN` |
| 3 | الجهة الدلالية | Semantic Direction | `LexemePillar.JIHA` |
| 4 | النوع المفهومي | Conceptual Type | `LexemePillar.NAW3` |
| 5 | القسم النهائي | Final POS | `LexemePillar.QISM` |
| 6 | الجاهزية للتركيب | Composition Readiness | `LexemePillar.JAHIZIYYA` |

## Mathematical Formalization (Art. 57–59)

```
L = (M, W/T, S, T, P, R)

LexValid(L) = 1  iff  q(M, W/T, S, T, P, R) ≥ θ_L

Ready(L) = (Mat + Struct + Dir + Type + POS + Recover) / 6
```

Threshold `θ_R = 0.75` (matching existing `is_closed` convention).

## The Fractal Law Cycle (Art. 46–52)

```
تعيين → حفظ → ربط → حكم → انتقال → ردّ
TA3YIN → HIFZ → RABT → HUKM → INTIQAL → RADD
```

| Phase | Arabic | Function | What it does |
|-------|--------|----------|-------------|
| 1 | تعيين | Assignment | Assign material, direction, type, category |
| 2 | حفظ | Preservation | Preserve root, weight, direction, identity |
| 3 | ربط | Linking | Link material→structure→direction→POS→composition |
| 4 | حكم | Judgment | Judge validity, POS, direction, readiness |
| 5 | انتقال | Transition | Transition to compositional roles |
| 6 | ردّ | Return | Return to root, weight, direction, derivation |

## Signification Triad (Art. 42–45)

| Mode | Arabic | Description |
|------|--------|-------------|
| Mutabaqa | مطابقة | What the lexeme denotes |
| Tadammun | تضمن | What enters its definition |
| Iltizam | التزام | What follows necessarily |

These vary by POS (noun, verb, particle).

## Acceptance / Rejection Criteria (Art. 60–61)

**Acceptance (7 criteria):**
1. Material established (`MADDA_THABITA`)
2. Weight established (`WAZN_THABIT`)
3. Direction established (`JIHA_THABITA`)
4. Type established (`NAW3_THABIT`)
5. POS established (`QISM_THABIT`)
6. Return possible (`RADD_MUMKIN`)
7. Ready for composition (`JAHIZ_LIL_TARKIB`)

**Rejection (5 criteria):**
1. Unclosed material (`MADDA_MAFTUHA`)
2. Direction undetermined (`JIHA_MUTA3ADHIRA`)
3. POS not established (`QISM_GHAYR_THABIT`)
4. Return impossible (`RADD_MUTA3ADHIR`)
5. Not ready (`GHAYR_JAHIZ`)

## Implementation Mapping

| Article | Module | Function / Type |
|---------|--------|----------------|
| Art. 20–26 | `core/enums.py` | `LexemePillar` |
| Art. 24 | `core/enums.py` | `ConceptualType` |
| Art. 42–44 | `core/enums.py` | `SignificationMode` |
| Art. 46 | `core/enums.py` | `LexemeFractalPhase` |
| Art. 57 | `core/types.py` | `Lexeme` |
| Art. 46–52 | `core/types.py` | `LexemeFractalNode` |
| Art. 53–59 | `core/types.py` | `CompositionReadiness` |
| Art. 42–45 | `core/types.py` | `SignificationTriad` |
| Art. 46–61 | `core/types.py` | `LexemeFractalResult` |
| Art. 60–61 | `core/enums.py` | `LexemeAcceptanceCode` |
| Art. 24 | `signifier/lexeme_fractal.py` | `classify_conceptual_type()` |
| Art. 53–59 | `signifier/lexeme_fractal.py` | `compute_readiness()` |
| Art. 58, 60–61 | `signifier/lexeme_fractal.py` | `validate_lexeme()` |
| Art. 42–45 | `signifier/lexeme_fractal.py` | `build_signification_triad()` |
| Art. 46–52 | `signifier/lexeme_fractal.py` | `run_lexeme_fractal()` |

## Relation to Prior Constitutions

| Constitution | Relationship |
|-------------|-------------|
| Epistemic Reception v1 | Validates how the mind receives the lexeme |
| Semantic Direction Space v1 | Supplies the genus axis for the lexeme |
| Weight Fractal v1 | Supplies the structural axis for the lexeme |
| Fractal Derivation Function v1 | Supplies derivation/stabilization paths |
| **Lexeme Fractal v2** | **Closes the single word; enables composition** |

## Next Constitutions

- Noun Fractal Constitution v1
- Verb Fractal Constitution v1
- Particle Fractal Constitution v1
- Composition / Syntax Constitution v1
