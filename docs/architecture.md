# Architecture — Arabic Engine

## Overview

The Arabic Engine is a computational Arabic language analysis pipeline based on two
foundational principles:

1. **Atomic Beginning Law** (قانون البداية الذرية) — every linguistic structure is
   built from discrete, numerically representable atomic units.
2. **Ascending Closure** (الإغلاق الصاعد) — each layer of the pipeline is
   completely closed before the next layer may begin.

The full pipeline is a computable function composition:

```
F = E ∘ I ∘ W ∘ T ∘ J ∘ D ∘ O ∘ L ∘ S ∘ N
```

where every intermediate type is a finite, numerically-encoded structure, making
`F` a total computable function over ℕ.

---

## Canonical Kernel-14 (Final)

The project now defines a canonical epistemic kernel of exactly 14 primary
labels:

`Self, Reality, Sense, PriorInfo, Link, Concept, Judgement, Method, Proof, Carrier, Exchange, Model, Constraint, State`

This kernel is the only ontological root. Higher structures are treated as
derived/application structures:

- `Utterance` ← derived from `Carrier`
- `LinguisticProfile` ← derived from `Method + Carrier + Concept`
- `KnowledgeEpisode` ← derived from `Reality + Sense + PriorInfo + Link + Judgement`
- `DiscourseExchange` ← derived from `Exchange + Carrier + Self + State`
- `ReusableModel` ← derived from `Model + State + repeated validated patterns`

See [`docs/kernel_schema.md`](kernel_schema.md) for the formal schema.

---

## Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│  L0   Unicode Normalisation         arabic_engine.signal.unicode_norm       │
│  L1   Tokenisation                  arabic_engine.signal.unicode_norm       │
│  L2   Lexical Closure (root/pattern)arabic_engine.morphology.root_pattern   │
│  L3   Syntax / I'rāb               arabic_engine.syntax.syntax             │
│  L4   Ontological Mapping           arabic_engine.semantics.ontology        │
│  L5   Dalāla Validation             arabic_engine.semantics.dalala          │
│  L6   Judgment / Proposition        arabic_engine.cognition.evaluation      │
│  L7   Time / Space Anchoring        arabic_engine.cognition.time_space      │
│  L7b  Semantic Roles                arabic_engine.semantics.semantic_roles  │
│  L7c  Masdar Analysis               arabic_engine.morphology.masdar         │
│  L8   Truth-Guidance Evaluation     arabic_engine.cognition.evaluation      │
│  L9   Inference                     arabic_engine.cognition.inference_rules │
│  L10  World-Model Adjustment        arabic_engine.cognition.world_model     │
└─────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
arabic_engine/
├── __init__.py                  Package root (version, public API)
│
├── core/                        Core types and kernel
│   ├── enums.py                 All enumeration types (POS, DalalaType, …)
│   ├── types.py                 All dataclass types (LexicalClosure, DMin, …)
│   ├── kernel.py                Kernel-14 label enum and helpers
│   └── trace.py                 Runtime state and tracing dataclasses
│
├── formal/                      Axiomatic foundations (split from core/)
│   ├── calculus.py              Five primitive calculus operations
│   ├── laws.py                  Foundational formal laws
│   ├── fractal_constitution.py  Fractal Core Constitution v1
│   └── masdar_fractal.py        Masdar fractal derivation law
│
├── validation/                  Contract & integrity checks (split from core/)
│   ├── contracts.py             Layer-adjacency contract verification
│   └── integrity.py             Repository-level integrity scanner
│
├── signal/                      Unicode atom → normalisation → segmentation
│   ├── unicode_atoms.py         Unicode atom decomposition
│   ├── unicode_norm.py          Unicode normalisation & tokenisation (L0–L1)
│   ├── normalization.py         Atom-level normalisation with trace
│   └── segmentation.py          Clitic-split segmentation hypotheses
│
├── morphology/                  الصرف — Root/pattern, phonology, D_min
│   ├── root_pattern.py          Root & morphological pattern extraction (L2)
│   ├── phonology.py             Phonological analysis / syllabification
│   ├── dmin.py                  D_min — minimal complete phonological model
│   ├── masdar.py                Masdar extraction & derivation engine (L7c)
│   ├── aeu.py                   Atomic Epistemic Unit builder
│   ├── transition.py            Cell-transition engine
│   └── functional_transition.py Functional transition loader & DSL
│
├── semantics/                   المدلول والرابطة — Ontology, dalāla, roles
│   ├── ontology.py              Ontological mapping (L4)
│   ├── ontology_v1.py           v1 ontology with 20 semantic axes
│   ├── signified_v2.py          v2 signified layer
│   ├── dalala.py                Dalāla validation (L5)
│   ├── semantic_roles.py        Semantic role assignment (L7b)
│   └── masdar_bridge.py         Masdar bridge — existential ↔ transformational
│
├── syntax/                      النحو — Syntax layer
│   └── syntax.py                I'rāb assignment & dependency linking (L3)
│
├── cognition/                   الإدراك — Cognition layer
│   ├── evaluation.py            Judgment & evaluation (L6, L8)
│   ├── time_space.py            Temporal/spatial anchoring (L7)
│   ├── world_model.py           In-memory world knowledge base (L10)
│   ├── inference_rules.py       Forward-chaining rule engine (L9)
│   ├── knowledge_graph.py       In-memory epistemic knowledge graph
│   ├── episode_validator.py     Epistemic episode validator
│   ├── epistemic_reception.py   Epistemic reception constitution
│   ├── discourse_exchange.py    Deliberative discourse exchange
│   ├── explanation.py           Pipeline explanation payloads
│   └── mafhum.py                Mafhūm (implied meaning) analysis (Ch. 21)
│
├── pipeline/                    Unified pipeline machinery
│   ├── __init__.py              Re-exports main pipeline run/verify
│   ├── orchestrator.py          Fractal Kernel orchestrator
│   ├── adapters.py              Legacy RuntimeState adapters
│   ├── hypothesis/              Staged hypothesis generation
│   ├── constraints/             Scoring, pruning, propagation, revision
│   └── element_layers/          7-layer phonological element analysis
│
├── metrics/                     Quality metrics and dashboards
├── representation/              Fractal representation spec
├── data/                        Static data files (JSON patterns, etc.)
│
├── main_pipeline.py             Top-level v3 pipeline (delegates to pipeline/)
├── closure.py                   General Closure verification (Ch. 19)
├── runtime_pipeline.py          Legacy 8-stage pipeline (deprecated)
└── contracts.yaml               Declarative layer-adjacency contracts
```

### Backward Compatibility

Old import paths (``signifier/``, ``signified/``, ``linkage/``, ``layers/``,
``hypothesis/``, ``constraints/``, ``runtime/``, ``element_layers/``) are
preserved as thin shim modules that redirect to the canonical locations.
These shims will be removed in a future release.

---

## Core Data Types

### Signifier Layer Types

| Type | Description |
|------|-------------|
| `Grapheme` | Single grapheme cluster: base code-point + diacritic marks |
| `Syllable` | Phonological syllable: onset, nucleus, coda, weight |
| `RootPattern` | Extracted tri-literal root + morphological pattern |
| `DMin` | Minimal Complete Representation `D_min(x) = (u, c, g, f, t) ∈ ℕ⁵` |

### Signified / Linkage Types

| Type | Description |
|------|-------------|
| `LexicalClosure` | Full morphological + lexical record for a token (التعريف 4) |
| `Concept` | Ontological concept node (التعريف 5) |
| `DalalaLink` | Validated signification link: signifier → signified (التعريف 6) |

### Cognition Types

| Type | Description |
|------|-------------|
| `SyntaxNode` | Token in the i'rāb dependency tree |
| `Proposition` | Structured judgment `(subject, predicate, object, time, space)` (التعريف 7) |
| `EvalResult` | Evaluation vector `(truth, guidance, confidence)` (التعريف 8) |
| `TimeSpaceTag` | Temporal/spatial anchoring for a proposition |
| `WorldFact` | A fact held in the world-model knowledge base |
| `InferenceResult` | Result of applying a forward-chaining rule |
| `MafhumResult` | Result of Mafhūm (implied meaning) analysis (Ch. 21) |

### Masdar (Verbal Noun) Types

| Type | Description |
|------|-------------|
| `MasdarRecord` | Full masdar record: surface, root, pattern, bab, event core |
| `MasdarDerivation` | Single derivation from masdar to target form |
| `FractalMasdarNode` | Fractal node linking existential ↔ transformational being |

See [`docs/masdar_fractal_constitution.md`](masdar_fractal_constitution.md) for the
formal Masdar Fractal Constitution.

---

## D_min Phonological Model

`D_min(x)` is the core phonological encoding:

```
D_min(x) = (u, c, g, f, t)  ∈ ℕ⁵
```

| Component | Type | Description |
|-----------|------|-------------|
| `u` | `int` | Unicode code-point |
| `c` | `PhonCategory` | Major phonological category (consonant, short vowel, …) |
| `g` | `PhonGroup` | Articulatory group (pharyngeal, labial, …) |
| `f` | `FrozenSet[PhonFeature]` | Feature bitmask |
| `t` | `FrozenSet[PhonTransform]` | Transform bitmask |

The registry `DMIN_REGISTRY` covers all 39 Arabic Unicode phonological
units: 28 consonants/semi-vowels (Table 1), 10 diacritics/marks (Table 2),
and 1 long-vowel letter (Table 3).

---

## Dalāla (Signification) Modes

| Mode | Arabic | Confidence | Description |
|------|--------|-----------|-------------|
| MUTABAQA | مطابقة | 1.0 | Exact denotation (lemma = concept label) |
| TADAMMUN | تضمن | 0.75 | Partial inclusion (root radical in concept) |
| ILTIZAM | التزام | 0.5 | Necessary concomitant (fallback) |
| ISNAD | إسناد | 0.95 | Predication (verb ↔ noun argument) |

---

## Evaluation Thresholds

| Average Confidence | TruthState |
|-------------------|------------|
| ≥ 0.9 | CERTAIN (قطعي) |
| 0.7 – 0.9 | PROBABLE (ظني راجح) |
| 0.4 – 0.7 | POSSIBLE (ممكن) |
| < 0.4 | DOUBTFUL (مشكوك) |

---

## General Closure (Ch. 19)

The `arabic_engine.closure` module implements the proof of General Closure
of the Manṭūq (`Closed_Mantūq(L*)`).  It verifies:

1. Every layer module/function exists and is importable.
2. POS ternary classification `{ISM, FI3L, HARF}` is present.
3. I'rāb cases and roles cover the minimal set.
4. Dalāla types cover `{MUTABAQA, TADAMMUN, ILTIZAM}`.
5. Propositional truth/guidance states cover the required range.
6. Time/space reference enums are complete.
7. Inference engine has ≥ 2 rules.
8. Layer order is ascending (no jumps).
9. No contradiction between layers.
10. All structures are decomposable to Unicode atoms.
11. The Manṭūq/Mafhūm boundary is clear.

---

## Mafhūm Analysis (Ch. 21)

The five minimal Mafhūm types (`Fh_min*`) are:

| Type | Arabic | Constraint Domain |
|------|--------|-------------------|
| SHART | مفهوم الشرط | Suspension of judgment on a condition |
| GHAYA | مفهوم الغاية | Endpoint / limit of judgment |
| ADAD | مفهوم العدد | Quantitative restriction |
| WASF | مفهوم الوصف | Qualitative restriction |
| ISHARA | مفهوم الإشارة | Referential / deictic specification |

A Mafhūm is valid only when all four pillars (أركان) hold:
1. Closed Manṭūq (منطوق مغلق)
2. Structural constraint (قيد بنيوي)
3. Mental counterpart (مقابل ذهني)
4. Transition rule (قاعدة انتقال)

---

## Further Reading

* [`docs/atomic_beginning_law.md`](atomic_beginning_law.md) — formal proof document
* [`docs/chapter_19_general_closure.md`](chapter_19_general_closure.md) — Ch. 19 proof
* [`docs/chapter_21_mafhum_types.md`](chapter_21_mafhum_types.md) — Ch. 21 proof
* [`docs/api_reference.md`](api_reference.md) — public API quick reference

---

## Operational Integrity Guard

Repository-level integrity is enforced by tests in
`tests/test_repository_integrity.py` using `arabic_engine.core.integrity`.

It validates:

1. Critical architecture modules remain importable.
2. Duplicate file contents are not introduced across:
   * `arabic_engine/`
   * `tests/`
   * `docs/`
   * `db/`
