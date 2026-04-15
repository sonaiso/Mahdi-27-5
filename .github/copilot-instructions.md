# Copilot Instructions — Arabic Engine

## Project Overview

**Arabic Engine** (`arabic_engine`) is a computational Arabic language analysis pipeline written in Python 3.10+. It processes raw Arabic text through a chain of discrete, numerically-encoded transformations based on two foundational principles:

1. **Atomic Beginning Law** (قانون البداية الذرية) — every linguistic structure is built from discrete, numerically representable atomic units.
2. **Ascending Closure** (الإغلاق الصاعد) — each layer must be completely closed before the next layer may begin.

The engine is **not** a statistical NLP toolkit. It is a formal, rule-based system where every layer is a computable function and every type boundary is verified by contracts.

## Quick Reference — Common Commands

```bash
# Install (editable, with dev dependencies)
pip install -e ".[dev]"

# Lint (must pass before any PR)
ruff check .

# Auto-fix lint issues
ruff check --fix .

# Run all tests (completes in a few seconds)
pytest -v

# Run a specific test file
pytest -v tests/test_pipeline.py

# Smoke-test the pipeline
python example_run.py
```

## Repository Layout

```
arabic_engine/               # Main package — all production code
├── __init__.py              # Package metadata, exports __version__
├── pipeline.py              # PRIMARY entry-point: run() orchestrates all layers (L0–L10)
├── runtime_pipeline.py      # Secondary 8-stage operational pipeline (Utterance→Judgement)
├── closure.py               # General Closure verification (Ch. 19 proof)
├── contracts.yaml           # Declarative layer-adjacency type contracts
│
├── core/                    # Shared types and enums
│   ├── enums.py             # ALL enumerations (POS, DalalaType, TruthState, etc.)
│   ├── types.py             # ALL dataclasses (LexicalClosure, Concept, Proposition, etc.)
│   ├── contracts.py         # Runtime contract verification (loads contracts.yaml)
│   ├── calculus.py          # Core calculus operations
│   ├── integrity.py         # Repository integrity checks
│   ├── kernel.py            # Kernel-14 epistemic kernel
│   ├── laws.py              # Formal law definitions
│   ├── masdar_fractal.py    # Masdar fractal constitution
│   └── trace.py             # Trace records
│
├── signifier/               # الدال — Signifier layer (L0–L2)
│   ├── unicode_norm.py      # L0: Unicode normalisation, L1: tokenisation
│   ├── phonology.py         # Phonological analysis / syllabification
│   ├── root_pattern.py      # L2: Root & morphological pattern extraction
│   ├── dmin.py              # D_min — minimal phonological model (ℕ⁵)
│   ├── aeu.py               # Arabic Expression Unit
│   ├── masdar.py            # Masdar extraction & derivation (L7c)
│   ├── functional_transition.py
│   └── transition.py        # Phonological transitions
│
├── signified/               # المدلول — Signified layer (L4)
│   ├── ontology.py          # L4: Ontological mapping
│   ├── ontology_v1.py       # Extended ontology
│   └── signified_v2.py      # V2 signified model
│
├── linkage/                 # الرابطة — Linkage layer (L5, L7b)
│   ├── dalala.py            # L5: Dalāla validation (mutābaqa/taḍammun/iltizām/isnād)
│   ├── semantic_roles.py    # L7b: Semantic role assignment
│   └── masdar_bridge.py     # Masdar bridge: existential ↔ transformational
│
├── syntax/                  # النحو — Syntax layer (L3)
│   └── syntax.py            # L3: I'rāb case/role assignment
│
├── cognition/               # الإدراك — Cognition layer (L6–L10)
│   ├── evaluation.py        # L6: Judgment, L8: Truth-guidance evaluation
│   ├── time_space.py        # L7: Temporal/spatial anchoring
│   ├── inference_rules.py   # L9: Forward-chaining rule engine
│   ├── world_model.py       # L10: In-memory world model
│   ├── mafhum.py            # Mafhūm (implied meaning) — Ch. 21
│   ├── explanation.py       # Explanation builder
│   ├── epistemic_v1.py      # Epistemic validation
│   ├── discourse_exchange.py
│   ├── episode_validator.py
│   ├── knowledge_graph.py
│   └── seed_data.py
│
├── constraints/             # Constraint engine (propagation, pruning, scoring)
├── hypothesis/              # Hypothesis layer (axes, cases, concepts, etc.)
├── layers/                  # 7-layer element analysis (L0–L6 mental→representation)
├── metrics/                 # Metrics/dashboards (ambiguity, stub tracking, etc.)
├── runtime/                 # Runtime adapters & orchestrator
├── signal/                  # Signal layer (normalisation, segmentation, atoms)
└── data/                    # Static data files (JSON, YAML, SQL, Cypher schemas)

tests/                       # All tests (many test files, runs in seconds)
docs/                        # Documentation (architecture, proofs, API reference)
db/                          # Cypher graph database schemas & seeds
scripts/                     # Maintenance scripts (branch_pr_merge.sh)
```

## Pipeline Architecture

The main pipeline (`arabic_engine.pipeline.run()`) composes 11 layers:

| Layer | Name | Module | Input → Output |
|-------|------|--------|----------------|
| L0 | Normalise | `signifier.unicode_norm.normalize` | `str → str` |
| L1 | Tokenize | `signifier.unicode_norm.tokenize` | `str → List[str]` |
| L2 | Lexical Closure | `signifier.root_pattern.batch_closure` | `List[str] → List[LexicalClosure]` |
| L3 | Syntax | `syntax.syntax.analyse` | `List[LexicalClosure] → List[SyntaxNode]` |
| L4 | Ontology | `signified.ontology.batch_map` | `List[LexicalClosure] → List[Concept]` |
| L5 | Dalāla | `linkage.dalala.full_validation` | `(closures, concepts) → List[DalalaLink]` |
| L6 | Judgment | `cognition.evaluation.build_proposition` | `(closures, concepts, links) → Proposition` |
| L7 | Time/Space | `cognition.time_space.tag` | `(closures, proposition) → TimeSpaceTag` |
| L7b | Semantic Roles | `linkage.semantic_roles.derive_semantic_roles` | `(closures, syntax_nodes) → Dict` |
| L8 | Evaluation | `cognition.evaluation.evaluate` | `(proposition, links) → EvalResult` |
| L9 | Inference | `cognition.inference_rules.InferenceEngine.run` | `List[Proposition] → List[InferenceResult]` |
| L10 | World Model | `cognition.world_model.WorldModel` | `Proposition → float` |

There is also a **runtime pipeline** (`runtime_pipeline.py`) with 8 stages: Utterance → Concept → Axis → Relation → Role → Factor → Case → Judgement.

## Key Types and Enums

All types live in `arabic_engine/core/types.py` and all enums in `arabic_engine/core/enums.py`. These two files are very large. Key types:

- **`LexicalClosure`** — morphological record for a token (surface, lemma, root, pattern, POS, confidence)
- **`Concept`** — ontological concept node (concept_id, label, semantic_type, properties)
- **`DalalaLink`** — signification link between signifier and signified
- **`SyntaxNode`** — token in the i'rāb dependency tree
- **`Proposition`** — structured judgment (subject, predicate, object, time, space, polarity)
- **`EvalResult`** — evaluation vector (truth_state, guidance_state, confidence)
- **`TimeSpaceTag`** — temporal/spatial anchoring

Key enums: `POS` (ISM/FI3L/HARF), `DalalaType` (MUTABAQA/TADAMMUN/ILTIZAM/ISNAD), `TruthState`, `GuidanceState`, `IrabCase`, `IrabRole`, `SemanticType`, `TimeRef`, `SpaceRef`.

## Contracts and Closure Verification

- **`contracts.yaml`** defines type-boundary contracts for every pipeline layer. The function `arabic_engine.core.contracts.verify_contracts()` loads this YAML and checks that each layer module/function exists and is importable.
- **`arabic_engine.closure.verify_general_closure()`** verifies 11 conditions for the formal General Closure of the system (Ch. 19).
- If you add a new layer or modify an existing one, update `contracts.yaml` accordingly.

## Coding Conventions

- **Python 3.10+** — use `from __future__ import annotations` in every module.
- **Type hints** on all function signatures.
- **PEP 8** with `ruff` as the linter/formatter (line length: 100, rules: E, F, W, I).
- **Dataclasses** (`@dataclass` or `@dataclass(frozen=True)`) for all structured types. Many are frozen for immutability.
- **Docstrings** often include Arabic text alongside English translations. This is intentional — the project is bilingual.
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- The `saleh/` directory exists but is currently empty — it can be ignored.

## Testing

- Test files are in `tests/` and follow the pattern `test_<module>.py`.
- Tests use `pytest` (no fixtures or conftest.py — tests are self-contained).
- **`tests/test_repository_integrity.py`** checks that all critical modules are importable and no duplicate file contents exist across `arabic_engine/`, `tests/`, `docs/`, `db/`.
- **`tests/test_architecture_guard.py`** guards the architectural module structure.
- When adding a new module, add a corresponding test file in `tests/`.
- All tests should pass quickly (a few seconds).

## CI Workflow

The CI (`.github/workflows/ci.yml`) runs on pushes/PRs to `main`:

1. **Lint job**: `ruff check .` on Python 3.12.
2. **Test job**: `pip install -e ".[dev]"` then `pytest -v` on Python 3.10, 3.11, and 3.12.

Both jobs must pass for a PR to be merged.

## Dependencies

- **Runtime**: `pyyaml>=6.0` (only external dependency)
- **Dev**: `pytest>=7.0`, `ruff>=0.4.0`
- Build system: `setuptools>=68.0` + `wheel`

The project is deliberately minimal in dependencies. Do not add heavy dependencies without strong justification.

## Common Pitfalls and Workarounds

1. **Large type files**: `core/types.py` and `core/enums.py` are very large files. Use `grep` or targeted `view_range` rather than reading them entirely. Search for specific class/enum names.

2. **Arabic text in code**: The codebase contains extensive Arabic text in strings, comments, and docstrings. This is domain-correct — do not remove or transliterate it.

3. **Two pipelines**: There are two separate pipeline systems:
   - `pipeline.py` — the main v3 pipeline (`run()`) used in production and tests
   - `runtime_pipeline.py` — the runtime operational bridge (`run_pipeline()`)
   
   Most tests and the example script use `pipeline.run()`.

4. **Contract verification**: If you add a new layer module, you must:
   - Add it to `contracts.yaml`
   - Ensure `verify_contracts()` still passes
   - Ensure `verify_general_closure()` still passes

5. **Data files**: Static data lives in `arabic_engine/data/` (JSON, YAML, SQL, Cypher). These are loaded at runtime by various modules. The `db/` directory contains graph database schemas.

6. **Import structure**: All public types are centralised in `core/types.py` and `core/enums.py`. Pipeline modules import from these central files. Follow this pattern when adding new types.

## How to Add a New Layer/Module

1. Create the module under the appropriate sub-package (`signifier/`, `signified/`, `linkage/`, `syntax/`, `cognition/`).
2. Define any new types in `core/types.py` and enums in `core/enums.py`.
3. Add the layer entry to `contracts.yaml` with its input/output types and invariants.
4. Wire it into `pipeline.py` (import + call in `run()`).
5. Add tests in `tests/test_<module>.py`.
6. Run `ruff check .` and `pytest -v` to verify.
7. Update `docs/architecture.md` if the layer stack changes.

## Key Documentation

- `docs/architecture.md` — full architecture overview, layer stack, type tables
- `docs/atomic_beginning_law.md` — formal proof of the Atomic Beginning Law
- `docs/chapter_19_general_closure.md` — Ch. 19 General Closure proof
- `docs/chapter_21_mafhum_types.md` — Ch. 21 Mafhūm types proof
- `docs/kernel_schema.md` — Kernel-14 epistemic kernel schema
- `docs/api_reference.md` — public API quick reference
- `docs/masdar_fractal_constitution.md` — Masdar Fractal Constitution
- `CONTRIBUTING.md` — contribution guidelines
- `CHANGELOG.md` — version history
