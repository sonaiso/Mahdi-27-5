# Duplicate Logic Audit — تدقيق المنطق المكرر

> **Scope**: All `validate_*` / `verify_*` functions in `arabic_engine/`.
> **Status**: Documentation-only audit. **No refactoring was performed.**

---

## 1. Executive Summary — الملخص التنفيذي

The Arabic Engine contains **16 validator / verifier functions** spread across
8 modules in 5 sub-packages. They fall into four broad categories:

| Category | Count | Modules |
|----------|-------|---------|
| Signifier-layer validators (diacritics, syllables) | 4 | `diacritics/validator.py`, `syllables/validator.py` |
| Epistemic / episode validators | 7 | `cognition/epistemic_v1.py`, `cognition/episode_validator.py`, `cognition/epistemic_reception.py` |
| Linkage validators | 1 | `linkage/dalala.py` |
| Structural / contract verifiers | 4 | `core/contracts.py`, `closure.py` |

A recurring return-type pattern is `Tuple[bool, List[str]]` ("is_valid,
violations"). This pattern appears in 4 functions across 2 modules. It is a
*convention*, not duplication — each function operates on a distinct domain
type.

---

## 2. Audit Table — جدول التدقيق

| # | Module | Function | Purpose | Return Type | Domain |
|---|--------|----------|---------|-------------|--------|
| 1 | `diacritics/validator.py` | `validate(token)` | Check diacritical mark conflicts/redundancy on a raw token | `Tuple[bool, List[str]]` | Signifier — diacritics |
| 2 | `diacritics/validator.py` | `validate_analysis(analysis)` | Same checks on a pre-computed `DiacriticAnalysis` | `Tuple[bool, List[str]]` | Signifier — diacritics |
| 3 | `syllables/validator.py` | `validate_syllable(syllable, is_final)` | Phonotactic legality of a single `SyllableUnit` | `Tuple[bool, List[str]]` | Signifier — syllables |
| 4 | `syllables/validator.py` | `validate_analysis(analysis)` | Aggregate syllable validation over a `SyllableAnalysis` | `Tuple[bool, List[str]]` | Signifier — syllables |
| 5 | `cognition/epistemic_v1.py` | `validate_linguistic_carrier(carrier)` | Validate a `LinguisticCarrierRecord` (dataclass) against carrier-type rules (UTTERANCE/CONCEPT/BOTH) | `Tuple[bool, List[DecisionCode], List[GapRecord]]` | Epistemic — standalone function |
| 6 | `cognition/epistemic_v1.py` | `validate_episode(inp)` | 12-condition validation of a `KnowledgeEpisodeInput` (dataclass) — the central rational-method check | `ValidationResult` | Epistemic — standalone function |
| 7 | `cognition/epistemic_v1.py` | `validate_batch(inputs)` | Batch wrapper — applies `validate_episode` to a sequence | `Tuple[ValidationResult, ...]` | Epistemic — standalone function |
| 8 | `cognition/episode_validator.py` | `validate_episode(self, episode_id)` | 10-condition validation of an episode by graph ID — reads from `KnowledgeGraph` | `EpisodeValidationResult` | Epistemic — graph-backed method |
| 9 | `cognition/episode_validator.py` | `validate_linguistic_carrier(self, episode_id)` | Validate carrier by traversing graph edges (CARRIED_BY / REALIZED_AS) | `dict` | Epistemic — graph-backed method |
| 10 | `cognition/episode_validator.py` | `validate_all(self)` | Batch wrapper — validates every episode in the graph | `List[EpisodeValidationResult]` | Epistemic — graph-backed method |
| 11 | `cognition/epistemic_reception.py` | `validate_carrying_claim(claimed)` | Check a `CarryingAssignment` against the constitutional matrix | `Tuple[bool, List[ReceptionDecisionCode]]` | Epistemic reception |
| 12 | `cognition/epistemic_reception.py` | `validate_reception(inp)` | Full 9-step constitutional validation of an `EpistemicReceptionInput` | `EpistemicReceptionResult` | Epistemic reception |
| 13 | `cognition/epistemic_reception.py` | `validate_reception_batch(...)` | Batch wrapper for reception validation | (batch result) | Epistemic reception |
| 14 | `linkage/dalala.py` | `validate_link(closure, concept)` | Compute dalāla link type (mutābaqa / taḍammun / iltizām) between signifier and signified | `DalalaLink` | Linkage — dalāla |
| 15 | `core/contracts.py` | `verify_contracts(...)` | Check that every pipeline layer's module/function exists and return types match `contracts.yaml` | `bool` (raises on failure) | Infrastructure — contracts |
| 16 | `core/contracts.py` | `verify_adjacency(...)` | Check type compatibility between adjacent layers; returns mismatch list | `List[Dict[str, str]]` | Infrastructure — contracts |
| 17 | `closure.py` | `verify_general_closure(...)` | Verify the 11 conditions of the General Closure (Ch. 19 proof) | (closure result) | Infrastructure — closure |

---

## 3. Potential Duplications — الازدواجيات المحتملة

### 3.1 `validate_linguistic_carrier` — `epistemic_v1.py` vs `episode_validator.py`

| Aspect | `epistemic_v1.py` (line 97) | `episode_validator.py` (line 264) |
|--------|---------------------------|----------------------------------|
| **Signature** | `validate_linguistic_carrier(carrier: LinguisticCarrierRecord) -> Tuple[bool, List[DecisionCode], List[GapRecord]]` | `validate_linguistic_carrier(self, episode_id: str) -> dict` |
| **Input** | A `LinguisticCarrierRecord` dataclass (standalone, no graph) | An `episode_id` string; retrieves carrier from `KnowledgeGraph` |
| **What it checks** | Carrier-type rules on a flat record: UTTERANCE → `utterance` not None; CONCEPT → `concept` not None; BOTH → both not None | Graph-backed: traverses `CARRIED_BY` edge, counts `REALIZED_AS` neighbours, checks `CarrierClass` against actual node counts |
| **Return type** | `Tuple[bool, List[DecisionCode], List[GapRecord]]` | `dict` with status string |
| **Data model** | `LinguisticCarrierRecord` (dataclass with `carrier_type: CarrierType`) | `LinguisticCarrierNode` (graph node with `carrier_class: CarrierClass`) |
| **Error model** | Uses `DecisionCode` / `GapRecord` enums | Returns a plain dict with `"invalid"` / `"ok"` strings |

**Analysis**: The two functions encode the *same conceptual rule* (a carrier of
type X must have the corresponding sub-components present) but operate at
**different architectural layers**:

- `epistemic_v1.validate_linguistic_carrier` is a **pure function** that
  validates a flat data record. It is called inside `validate_episode` as step 9
  of 12.
- `EpisodeValidator.validate_linguistic_carrier` is a **graph method** that
  fetches data from a `KnowledgeGraph` and returns a diagnostic dict.

The rule logic overlaps, but the data access patterns, input types, return
types, and error models are fundamentally different.

**Verdict**: **Domain-specific separation — candidate for shared helper (low
priority).** A shared predicate like `_carrier_fields_present(type, has_utt,
has_con) -> bool` could eliminate the duplicated condition checks, but the
refactoring gain is small relative to the coupling it would introduce between
the two modules.

---

### 3.2 `validate_analysis` — `diacritics/validator.py` vs `syllables/validator.py`

| Aspect | `diacritics/validator.py` (line 49) | `syllables/validator.py` (line 62) |
|--------|-------------------------------------|-------------------------------------|
| **Input type** | `DiacriticAnalysis` | `SyllableAnalysis` |
| **What it checks** | Conflicting / redundant diacritical marks on bindings | Phonotactic legality of syllable types (CV, CVC, etc.) |
| **Return type** | `Tuple[bool, List[str]]` | `Tuple[bool, List[str]]` |
| **Iteration target** | `analysis.bindings` (list of `DiacriticBinding`) | `analysis.pattern.syllables` (list of `SyllableUnit`) |

**Analysis**: The function names are identical but they operate on **completely
different domain types**. The shared name `validate_analysis` is a natural
naming convention for "validate the analysis result produced by this module's
analyser." The return-type pattern `Tuple[bool, List[str]]` is a lightweight
convention — no shared base class or protocol is needed.

**Verdict**: **Common pattern — justified, no refactoring needed.** The name
collision is scoped by module and is idiomatic Python. The identical return
type is a convention, not duplication.

---

### 3.3 `validate_episode` — `epistemic_v1.py` vs `episode_validator.py`

| Aspect | `epistemic_v1.py` (line 333) | `episode_validator.py` (line 132) |
|--------|-------------------------------|----------------------------------|
| **Signature** | `validate_episode(inp: KnowledgeEpisodeInput) -> ValidationResult` | `validate_episode(self, episode_id: str) -> EpisodeValidationResult` |
| **Input** | `KnowledgeEpisodeInput` dataclass (all fields provided inline) | `episode_id` string; all data fetched from `KnowledgeGraph` |
| **Condition count** | **12** conditions (reality anchor, sense trace, prior info, opinion contamination, linking trace, judgement, method, method-fit, carrier, proof path, conflict rule, carrier-both conflict) | **10** conditions (schema section 5 — reality anchor, sense trace, prior info, method, linking trace, judgement, carrier, proof path, conflict rule, reality anchor type) |
| **Return type** | `ValidationResult` (contains `outcome`, `rank`, `insertion_policy`, `gaps`, `messages`) | `EpisodeValidationResult` (contains `validation_state`, `epistemic_rank`, `errors`, `gaps`) |
| **Side effects** | None (pure function) | Writes `validation_state`, `epistemic_rank`, and `GapNode` objects back into the graph |
| **Batch wrapper** | `validate_batch(inputs)` — sequential tuple | `validate_all()` — sorted list from graph traversal |

**Analysis**: Both functions implement a multi-condition validation sequence
for knowledge episodes, but they serve **different integration surfaces**:

- `epistemic_v1.validate_episode` is the **stateless, dataclass-first** entry
  point. It validates 12 conditions from a flat input and returns a pure result.
  It is designed for pipeline integration and unit testing.
- `EpisodeValidator.validate_episode` is the **graph-backed, stateful** entry
  point. It validates 10 conditions by querying a `KnowledgeGraph` and writes
  results back. It is designed for the graph-database workflow.

The condition sets partially overlap (both check reality anchor, sense trace,
prior info, carrier, etc.) but differ in count, ordering, severity model, and
error representation.

**Verdict**: **Domain-specific separation — candidate for shared helper
(medium priority).** The overlapping condition checks (reality anchor present,
sense trace present, prior info present, etc.) could be extracted into a
shared condition-checker that both implementations call. However, the different
data-access patterns (dataclass fields vs graph traversals) and different error
models (`GapRecord` vs plain strings) make a clean extraction non-trivial.

---

### 3.4 Return-type pattern: `Tuple[bool, List[str]]`

The following functions share this return type:

1. `diacritics/validator.py::validate`
2. `diacritics/validator.py::validate_analysis`
3. `syllables/validator.py::validate_syllable`
4. `syllables/validator.py::validate_analysis`

**Verdict**: **Common pattern — justified, no refactoring needed.** Each
function operates on a distinct domain type (`DiacriticAnalysis` vs
`SyllableUnit` / `SyllableAnalysis`). The shared `(bool, list[str])` return
convention is a lightweight validation idiom. Introducing a shared base class or
generic protocol would add complexity without meaningful benefit.

---

## 4. Summary of Verdicts — ملخص الأحكام

| # | Duplication Candidate | Verdict | Priority |
|---|----------------------|---------|----------|
| 3.1 | `validate_linguistic_carrier` (epistemic_v1 vs episode_validator) | Domain-specific separation — candidate for shared helper | Low |
| 3.2 | `validate_analysis` (diacritics vs syllables) | Common pattern — justified, no refactoring needed | None |
| 3.3 | `validate_episode` (epistemic_v1 vs episode_validator) | Domain-specific separation — candidate for shared helper | Medium |
| 3.4 | `Tuple[bool, List[str]]` return pattern | Common pattern — justified, no refactoring needed | None |

---

## 5. Conclusion — الخاتمة

The Arabic Engine contains **no harmful duplication** in its validation layer.
The apparent overlaps fall into two categories:

1. **Same-name functions on different domain types** (e.g. `validate_analysis`
   for diacritics vs syllables). These are justified naming conventions scoped
   by module. No refactoring is needed.

2. **Same-concept validation at different architectural layers** (e.g.
   `validate_episode` as a pure function vs a graph method). These encode the
   same business rules against different data-access patterns. A shared helper
   *could* reduce the condition-checking overlap, but the coupling cost
   outweighs the benefit at the current codebase scale.

**Recommendation**: No immediate refactoring is required. If the condition
lists in `epistemic_v1.validate_episode` and
`EpisodeValidator.validate_episode` diverge further, consider extracting a
shared condition registry to keep them aligned.

> **Note**: This audit is documentation only. No code was modified, moved,
> or refactored as part of this review.
