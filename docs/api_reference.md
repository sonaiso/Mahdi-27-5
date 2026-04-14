# API Reference — Arabic Engine

This document provides a quick reference to the public API of `arabic_engine`.
For full details, see the module docstrings.

---

## Top-Level Entry Points

### `arabic_engine.pipeline`

```python
from arabic_engine.pipeline import run, PipelineResult, verify_contracts
```

#### `run(text, *, world=None, inference_engine=None) → PipelineResult`

Execute the full 11-layer pipeline on raw Arabic *text*.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | — | Raw Arabic input (may include tashkīl) |
| `world` | `WorldModel \| None` | `None` | World model for confidence adjustment |
| `inference_engine` | `InferenceEngine \| None` | `None` | Rule engine for inference |

Returns a [`PipelineResult`](#pipelineresult) containing all layer outputs.

#### `PipelineResult`

| Field | Type | Description |
|-------|------|-------------|
| `raw` | `str` | Original unmodified input |
| `normalised` | `str` | Unicode-normalised text |
| `tokens` | `List[str]` | Whitespace-delimited tokens |
| `closures` | `List[LexicalClosure]` | Lexical closures (L2) |
| `syntax_nodes` | `List[SyntaxNode]` | I'rāb-annotated nodes (L3) |
| `concepts` | `List[Concept]` | Ontological concept nodes (L4) |
| `dalala_links` | `List[DalalaLink]` | Signification links (L5) |
| `proposition` | `Proposition` | Structured judgment (L6) |
| `time_space` | `TimeSpaceTag` | Temporal/spatial anchoring (L7) |
| `eval_result` | `EvalResult` | Truth/guidance/confidence (L8) |
| `inferences` | `List[InferenceResult]` | Derived propositions (L9) |
| `world_adjustment` | `float` | World-model confidence multiplier (L10) |

#### `verify_contracts() → bool`

Verify all layer-adjacency type contracts declared in `contracts.yaml`.
Raises `ValueError` on the first violation.

---

## Signifier Layer — `arabic_engine.signifier`

### `arabic_engine.signifier.unicode_norm`

```python
from arabic_engine.signifier.unicode_norm import normalize, tokenize, to_graphemes, normalize_hamza
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `normalize` | `(text, *, strip_tashkil=False) → str` | NFC + tatweel removal + whitespace collapse |
| `normalize_hamza` | `(text) → str` | Unify آ أ إ → ا |
| `tokenize` | `(text) → List[str]` | Normalise then split on whitespace |
| `to_graphemes` | `(token) → List[Grapheme]` | Decompose token into grapheme clusters |

### `arabic_engine.signifier.phonology`

```python
from arabic_engine.signifier.phonology import (
    is_consonant, is_vowel_mark, has_shadda, get_short_vowel, syllabify
)
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_consonant` | `(g: Grapheme) → bool` | True if grapheme is a consonant |
| `is_vowel_mark` | `(cp: int) → bool` | True if code-point is a short-vowel mark |
| `has_shadda` | `(g: Grapheme) → bool` | True if grapheme carries shaddah |
| `get_short_vowel` | `(g: Grapheme) → int \| None` | Short-vowel code-point on grapheme |
| `syllabify` | `(graphemes) → List[Syllable]` | CV-based syllabification |

### `arabic_engine.signifier.root_pattern`

```python
from arabic_engine.signifier.root_pattern import (
    extract_root_pattern, lexical_closure, batch_closure
)
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `extract_root_pattern` | `(token) → RootPattern \| None` | Root + pattern via lexicon |
| `lexical_closure` | `(token) → LexicalClosure` | Full morphological record for a token |
| `batch_closure` | `(tokens) → List[LexicalClosure]` | Batch lexical closure |

### `arabic_engine.signifier.dmin`

```python
from arabic_engine.signifier.dmin import (
    DMIN_REGISTRY,
    lookup, lookup_char, encode, numeric_vector,
    group_members, category_members, has_feature, has_transform,
    emphatic_consonants, nasal_consonants,
)
```

| Symbol | Type | Description |
|--------|------|-------------|
| `DMIN_REGISTRY` | `Dict[int, DMin]` | Complete registry: code-point → DMin |
| `lookup(cp)` | `DMin \| None` | Look up by integer code-point |
| `lookup_char(ch)` | `DMin \| None` | Look up by character string |
| `encode(cp)` | `str` | MinCode string (e.g. `'C:SHF:SHD:MJH'`) |
| `numeric_vector(cp)` | `tuple \| None` | 5-vector `(u, c, g, f_mask, t_mask)` |
| `group_members(g)` | `List[int]` | All code-points with a given PhonGroup |
| `category_members(c)` | `List[int]` | All code-points with a given PhonCategory |
| `has_feature(cp, f)` | `bool` | True if code-point has PhonFeature |
| `has_transform(cp, t)` | `bool` | True if code-point has PhonTransform |
| `emphatic_consonants()` | `List[int]` | All emphatic (مطبق) consonant code-points |
| `nasal_consonants()` | `List[int]` | All nasal (أنفي) consonant code-points |

---

## Signified Layer — `arabic_engine.signified`

```python
from arabic_engine.signified.ontology import map_concept, batch_map
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `map_concept` | `(closure) → Concept` | Map a single closure to a Concept |
| `batch_map` | `(closures) → List[Concept]` | Batch ontological mapping |

---

## Linkage Layer — `arabic_engine.linkage`

```python
from arabic_engine.linkage.dalala import validate_link, build_isnad_links, full_validation
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `validate_link` | `(closure, concept) → DalalaLink` | Compute signification mode + confidence |
| `build_isnad_links` | `(closures, concepts) → List[DalalaLink]` | Build predication links |
| `full_validation` | `(closures, concepts) → List[DalalaLink]` | validate_link + build_isnad_links |

---

## Syntax Layer — `arabic_engine.syntax`

```python
from arabic_engine.syntax.syntax import analyse
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `analyse` | `(closures) → List[SyntaxNode]` | I'rāb assignment + dependency linking |

---

## Cognition Layer — `arabic_engine.cognition`

### `arabic_engine.cognition.evaluation`

```python
from arabic_engine.cognition.evaluation import build_proposition, evaluate
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `build_proposition` | `(closures, concepts, links) → Proposition` | Compose judgment |
| `evaluate` | `(proposition, links) → EvalResult` | Truth/guidance/confidence |

### `arabic_engine.cognition.time_space`

```python
from arabic_engine.cognition.time_space import detect_time, detect_space, tag
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `detect_time` | `(closures) → (TimeRef, str)` | Infer temporal reference |
| `detect_space` | `(closures) → (SpaceRef, str)` | Infer spatial reference |
| `tag` | `(closures, proposition=None) → TimeSpaceTag` | Combined time+space tag |

### `arabic_engine.cognition.world_model`

```python
from arabic_engine.cognition.world_model import WorldModel
```

**`WorldModel` methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_fact` | `(subject, predicate, obj, truth_state, source) → WorldFact` | Insert fact |
| `lookup` | `(subject, predicate=None) → List[WorldFact]` | Query by subject |
| `matches` | `(proposition) → WorldFact \| None` | Find supporting fact |
| `confidence_adjustment` | `(proposition) → float` | Confidence multiplier |
| `all_facts` (property) | `List[WorldFact]` | All stored facts |

### `arabic_engine.cognition.inference_rules`

```python
from arabic_engine.cognition.inference_rules import InferenceEngine
```

**`InferenceEngine` methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `run` | `(propositions) → List[InferenceResult]` | Apply rules once |
| `run_until_fixed` | `(propositions, max_iterations=10) → List[InferenceResult]` | Fixed-point iteration |

### `arabic_engine.cognition.mafhum`

```python
from arabic_engine.cognition.mafhum import (
    analyse_mafhum, get_minimal_types, verify_irreducibility
)
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `analyse_mafhum` | `(closures, proposition, *, mantuq_closed=True) → List[MafhumResult]` | Detect all five Mafhūm types |
| `get_minimal_types` | `() → List[MafhumType]` | Return Fh_min* |
| `verify_irreducibility` | `() → dict[str, bool]` | Verify each type covers a unique domain |

---

## General Closure — `arabic_engine.closure`

```python
from arabic_engine.closure import verify_general_closure, format_closure_report
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `verify_general_closure` | `() → GeneralClosureResult` | Run full Ch. 19 closure check |
| `format_closure_report` | `(result) → str` | Human-readable Arabic/English report |

---

## Core Types — `arabic_engine.core`

### `arabic_engine.core.kernel` (Kernel-14)

```python
from arabic_engine.core.kernel import (
    KernelLabel, KernelRelation,
    KernelNode, KernelEdge, KernelGraph,
    KernelValidationResult, validate_kernel_graph,
    derive_utterance_from_carrier, derive_linguistic_profile,
    derive_knowledge_episode, derive_discourse_exchange, derive_reusable_model,
)
```

| Symbol | Description |
|--------|-------------|
| `KernelLabel` | Canonical 14 node labels only |
| `KernelRelation` | Minimal core kernel relationships |
| `KernelNode` / `KernelEdge` / `KernelGraph` | Minimal graph payload for kernel validation |
| `validate_kernel_graph(graph)` | Checks required fields + relation label compatibility |
| `derive_utterance_from_carrier` | Derives `Utterance` from `Carrier` |
| `derive_linguistic_profile` | Derives profile from `Method + Carrier + Concept` |
| `derive_knowledge_episode` | Derives episode from `Reality + Sense + PriorInfo + Link + Judgement` |
| `derive_discourse_exchange` | Derives exchange artifact from `Exchange + Carrier + Self + State` |
| `derive_reusable_model` | Derives reusable model from `Model + State + repeated validated patterns` |

### Enumerations (`arabic_engine.core.enums`)

| Enum | Values |
|------|--------|
| `POS` | ISM, FI3L, HARF, SIFA, ZARF, DAMIR, UNKNOWN |
| `SemanticType` | ENTITY, EVENT, ATTRIBUTE, RELATION, NORM |
| `DalalaType` | MUTABAQA, TADAMMUN, ILTIZAM, ISNAD, TAQYID, IDAFA, IHALA |
| `TruthState` | CERTAIN, PROBABLE, POSSIBLE, DOUBTFUL, FALSE, UNKNOWN |
| `GuidanceState` | OBLIGATORY, RECOMMENDED, PERMISSIBLE, DISLIKED, FORBIDDEN, NOT_APPLICABLE |
| `IrabCase` | RAF3, NASB, JARR, JAZM, SUKUN, UNKNOWN |
| `IrabRole` | FA3IL, MAF3UL_BIH, MUBTADA, KHABAR, FI3L, MUDAF, MUDAF_ILAYH, SIFA, HAL, TAMYIZ, ZARF, JARR_MAJRUR, UNKNOWN |
| `TimeRef` | PAST, PRESENT, FUTURE, ETERNAL, UNSPECIFIED |
| `SpaceRef` | HERE, THERE, NAMED, UNSPECIFIED |
| `ConstraintType` | SHART, GHAYA, ADAD, WASF, ISHARA |
| `MafhumType` | SHART, GHAYA, ADAD, WASF, ISHARA |
| `PhonCategory` | CONSONANT, SEMI_VOWEL, LONG_VOWEL, SHORT_VOWEL, SUKUN, SHADDA, TANWIN, SPECIAL_MARK |
| `PhonGroup` | HNJ_MZM, HNJ_HLQ, HLQ, HLQ_LHW, LHW, TBQ_LHW, SHJR, … (30+ groups) |
| `PhonFeature` | SHADID, RAKHW, MURAKKAB, MUTAWASSIT, TAKRIR, MUNHARIF, … (24 features) |
| `PhonTransform` | TAHQIQ, TASHIL, IBDAL, HADHF, IDGHAM, … (40+ transforms) |

### Dataclasses (`arabic_engine.core.types`)

| Class | Frozen | Key Fields |
|-------|--------|------------|
| `Grapheme` | ✓ | `base: int`, `marks: Tuple[int, ...]` |
| `Syllable` | ✓ | `onset`, `nucleus`, `coda`, `weight` |
| `RootPattern` | ✓ | `root`, `pattern`, `root_id`, `pattern_id` |
| `DMin` | ✓ | `unicode`, `category`, `group`, `features`, `transforms`, `code` |
| `LexicalClosure` | — | `surface`, `lemma`, `root`, `pattern`, `pos`, `case_mark`, `temporal`, … |
| `Concept` | — | `concept_id`, `label`, `semantic_type`, `properties` |
| `DalalaLink` | — | `source_lemma`, `target_concept_id`, `dalala_type`, `accepted`, `confidence` |
| `Proposition` | — | `subject`, `predicate`, `obj`, `time`, `space`, `polarity` |
| `EvalResult` | — | `proposition`, `truth_state`, `guidance_state`, `confidence` |
| `SyntaxNode` | — | `token`, `lemma`, `pos`, `case`, `role`, `governor`, `dependents` |
| `TimeSpaceTag` | — | `time_ref`, `space_ref`, `time_detail`, `space_detail` |
| `WorldFact` | — | `fact_id`, `subject`, `predicate`, `obj`, `truth_state`, `source` |
| `InferenceResult` | — | `rule_name`, `premises`, `conclusion`, `confidence`, `valid` |
| `MafhumPillar` | — | `closed_mantuq`, `constraint_type`, `mental_counterpart`, `transition_rule` |
| `MafhumResult` | — | `mafhum_type`, `constraint_type`, `pillars`, `source_text`, `valid`, `confidence` |

---

## Repository Integrity — `arabic_engine.core.integrity`

```python
from arabic_engine.core.integrity import (
    scan_repository_integrity,
    format_integrity_report,
)
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `scan_repository_integrity` | `(project_root, *, required_modules=..., scan_dirs=...) → IntegrityReport` | Validates critical architecture imports and duplicate-content policy |
| `format_integrity_report` | `(report) → str` | Formats a human-readable integrity summary |
