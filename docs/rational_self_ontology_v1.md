# Rational Self Ontology v1 — مع Lexeme Epistemic Core

## Overview

The Rational Self Ontology v1 introduces a two-level ontological foundation
into the Arabic engine:

1. **الذات العاقلة (Rational Self)** — the knowing agent as centre of
   perception, judgement, and intent.
2. **المفرد اللفظي (Lexeme as Epistemic Unit)** — the single word as the
   first tool of cognitive designation before composition.

### Core Thesis

> الوزن شرط إمكان معرفي للمفرد قبل التركيب
>
> The weight (الوزن) is an epistemic condition of possibility for the
> single word before composition — not because it alone suffices for all
> meaning, but because it is the structural minimum that makes the word
> amenable to designation, classification, and judgement.

---

## Architecture

### The Representational Chain (Non-Breakable)

```
Unicode
→ Grapheme
→ Phonological Unit
→ Haraka / Mark
→ Bare Material
→ Root / Root-Candidate
→ Weight / Closed Template
→ Lexeme
→ Conceptual Type
→ POS Finalisation (اسم / فعل / حرف)
→ Composition Readiness
```

### Module Structure

```
arabic_engine/lexeme/
├── __init__.py              # Public API exports
├── weight.py                # Weight extraction & scoring
├── lexeme_builder.py        # Lexeme construction
├── pos_finalization.py      # POS finalisation proofs
├── composition_gate.py      # Composition readiness gate
├── recovery.py              # Recovery rules RR-01…RR-06
├── validation.py            # Validation rules RS-01…RS-12
├── transitions.py           # Formal transition rules
└── rational_self.py         # Rational Self ↔ Lexeme bridge
```

---

## Node Types (§10.1)

| Node Type              | Arabic             | Description                       |
| ---------------------- | ------------------ | --------------------------------- |
| `UnicodeUnit`          | رمز Unicode        | Raw Unicode code point            |
| `GraphemeUnit`         | وحدة كتابية        | Written character or mark         |
| `PhonoUnit`            | وحدة صوتية         | Phonological/phonographic unit    |
| `HarakaUnit`           | حركة               | Vowelling or operational mark     |
| `BareLexicalMaterial`  | مادة لفظية عارية   | Pre-independence lexical material |
| `RootNode`             | جذر                | Root or root candidate            |
| `WeightNode`           | وزن                | Weight / structural template      |
| `ClosedTemplateNode`   | قالب مغلق          | Frozen template for particles     |
| `LexemeNode`           | مفرد مستقل         | Relatively independent lexeme     |
| `ConceptNode`          | نوع مفهومي         | Primary concept type              |
| `NounNode`             | اسم                | Noun                              |
| `VerbNode`             | فعل                | Verb                              |
| `ParticleNode`         | حرف                | Particle                          |
| `CompositionReadyNode` | جاهز للتركيب       | Pre-composition gate              |
| `RationalSelfRecord`   | الذات العاقلة      | Extended self model                |

---

## Edge Types (§10.2)

| Edge Type             | From → To                               | Meaning                     |
| --------------------- | ---------------------------------------- | --------------------------- |
| `ENCODES`             | UnicodeUnit → GraphemeUnit               | Code point encodes grapheme |
| `REALIZES`            | GraphemeUnit → PhonoUnit                 | Phonetic realisation        |
| `MODULATES`           | HarakaUnit → PhonoUnit / WeightNode     | Vowelling modulates         |
| `FORMS_MATERIAL`      | units → BareLexicalMaterial              | Material formation          |
| `INSTANTIATES_ROOT`   | BareLexicalMaterial → RootNode           | Root extraction             |
| `INSTANTIATES_WEIGHT` | BareLexicalMaterial → WeightNode         | Weight extraction           |
| `FILLS_TEMPLATE`      | RootNode → WeightNode                   | Root fills template         |
| `STABILIZES_AS`       | WeightNode → LexemeNode                 | Lexeme stabilisation        |
| `TYPED_AS`            | LexemeNode → ConceptNode                | Concept type assignment     |
| `FINALIZED_AS`        | LexemeNode → Noun/Verb/ParticleNode     | POS finalisation            |
| `DERIVED_FROM`        | DerivedNode → RootNode                  | Derivation link             |
| `REFERS_TO`           | NounNode → ReferentialNode              | Nominal reference           |
| `DENOTES_EVENT`       | VerbNode → ActionalityNode              | Event denotation            |
| `BINDS_RELATION`      | ParticleNode → RelationalNode           | Particle binding            |
| `PREPARES_FOR`        | LexemeNode → CompositionReadyNode       | Composition readiness       |
| `RECOVERS_TO`         | any → lower layer                        | Recovery link               |

---

## Required Fields

### WeightNode

| Field                  | Required | Type                 | Description                   |
| ---------------------- | -------- | -------------------- | ----------------------------- |
| `id`                   | Yes      | str                  | Unique identifier             |
| `weight_form`          | Yes      | str                  | e.g. "فاعل", "مفعول"         |
| `template_type`        | Yes      | WeightTemplateType   | NOMINAL / VERBAL / CLOSED     |
| `slots`                | Yes      | Tuple[str, ...]      | Root/augmentation positions   |
| `semantic_tendency`    | Yes      | str                  | General semantic direction    |
| `recoverability_score` | Yes      | float                | Recovery to root [0, 1]       |
| `completeness_score`   | Yes      | float                | Minimum completeness [0, 1]   |
| `productivity_mode`    | Yes      | ProductivityMode     | LIVING / CLOSED / HISTORICAL  |
| `pos_affinity`         | Yes      | POS                  | POS tendency                  |

### LexemeNode

| Field                 | Required    | Type              | Description                    |
| --------------------- | ----------- | ----------------- | ------------------------------ |
| `id`                  | Yes         | str               | Unique identifier              |
| `surface_form`        | Yes         | str               | Surface form                   |
| `normalized_form`     | Yes         | str               | Normalised form                |
| `root_ref`            | Conditional | Optional[str]     | Root reference                 |
| `weight_ref`          | Conditional | Optional[str]     | Weight reference               |
| `closed_template_ref` | Conditional | Optional[str]     | Closed template reference      |
| `independence_type`   | Yes         | IndependenceType  | Independence classification    |
| `concept_type`        | Yes         | str               | Concept type label             |
| `pos_final`           | Yes         | POS               | Final POS tag                  |
| `readiness_score`     | Yes         | float             | Composition readiness [0, 1]   |

---

## Validation Rules (RS-01 … RS-12)

| Rule  | Description                                                        |
| ----- | ------------------------------------------------------------------ |
| RS-01 | LexemeNode requires `surface_form`, `concept_type`, `pos_final`    |
| RS-02 | Must be independent by meaning or function                         |
| RS-03 | WeightNode `completeness_score` ≥ 0.65                             |
| RS-04 | WeightNode recoverable to slots + root/additions                   |
| RS-05 | Derived noun must link to root or derivation template              |
| RS-06 | Rigid noun must have referential/classificatory independence       |
| RS-07 | Verb must identify event/linking/copula power                      |
| RS-08 | Particle must identify relation/binding direction                  |
| RS-09 | No confusion between layers (layer ordering enforced)              |
| RS-10 | POS + concept must be set before composition                       |
| RS-11 | Matching mode must be specified                                    |
| RS-12 | Full chain Unicode→lexeme must be recoverable                      |

---

## Recovery Rules (RR-01 … RR-06)

| Rule  | From → To                              | Purpose                    |
| ----- | -------------------------------------- | -------------------------- |
| RR-01 | LexemeNode → WeightNode/RootNode       | Prove structure            |
| RR-02 | WeightNode → slots + positions         | Analyse template           |
| RR-03 | NounNode → ConceptNode + Referential   | Recover noun semantics     |
| RR-04 | VerbNode → Actional + tense/transit.   | Recover verb conditions    |
| RR-05 | ParticleNode → Relational + scope      | Recover particle relation  |
| RR-06 | CompositionReady → POS + concept + wt  | Ensure pre-composition     |

---

## Transition Rules (§12)

### From Material to Lexeme

| From                | Condition            | To                     |
| ------------------- | -------------------- | ---------------------- |
| Unicode / Grapheme  | Graphemic coherence   | BareLexicalMaterial    |
| BareLexicalMaterial | Sound/symbol pattern | Root/Weight Candidate  |
| Root + Weight       | Template satisfied   | LexemeNode             |
| Closed Template     | Fixed function       | Particle / Built Form  |
| LexemeNode          | Concept type set     | Noun / Verb / Particle |

### From Rigid/Derived

| Type            | Condition                    | Transition                  |
| --------------- | ---------------------------- | --------------------------- |
| Rigid (جامد)   | Existential/class reference | NounNode / ReferentialNode  |
| Derived nominal | Weight + event/description  | NounNode / DerivedNode      |
| Derived verbal  | Weight + event + tense      | VerbNode                    |
| Particle        | Closed template + function  | ParticleNode                |

---

## Kernel Extensions

Two new kernel relations added to `KernelRelation`:

- **`DESIGNATES`**: Self → Concept — the rational self designates (perceives/names) lexemes.
- **`INTENDS_COMPOSITION`**: Self → Concept — the rational self intends to compose.

---

## Pipeline Integration

The lexeme epistemic core is inserted between L2 (Lexical Closure) and L3 (Syntax):

```
L0  Normalise
L1  Tokenise
L2  Lexical Closure
L2w Weight Extraction       ← NEW
L2l Lexeme Construction     ← NEW
L2c Composition Gate        ← NEW
L3  Syntax
L4  Ontological Mapping
…
```

The runtime pipeline adds a **LEXEME** stage between UTTERANCE and CONCEPT.

---

## Usage Example

```python
from arabic_engine.lexeme.weight import extract_weight
from arabic_engine.lexeme.lexeme_builder import build_lexeme
from arabic_engine.lexeme.pos_finalization import auto_finalize
from arabic_engine.lexeme.composition_gate import check_composition_readiness
from arabic_engine.lexeme.validation import validate_all
from arabic_engine.core.types import LexicalClosure
from arabic_engine.core.enums import POS

# 1. Create a closure
closure = LexicalClosure(
    surface="كاتب", lemma="كاتب",
    root=("ك", "ت", "ب"), pattern="فَاعِل", pos=POS.ISM,
)

# 2. Extract weight
weight = extract_weight(closure.root, closure.surface, closure.pattern)

# 3. Build lexeme
lexeme = build_lexeme(closure, weight=weight)

# 4. Auto-finalise POS
pos_node = auto_finalize(lexeme)

# 5. Check composition readiness
comp = check_composition_readiness(lexeme)
assert comp.ready

# 6. Validate
results = validate_all(lexeme, weight=weight, pos_node=pos_node, composition_node=comp)
assert all(passed for _, passed in results)
```
