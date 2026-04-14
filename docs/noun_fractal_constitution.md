# Noun Fractal Constitution v1 — دستور الاسم الفراكتالي

## Overview

The **Noun Fractal Constitution** establishes the Arabic noun (الاسم)
as the **primary epistemological vessel** for fixing existence,
differentiation, and classification of entities before composition.
It is implemented as a subsystem within the `arabic_engine` that
classifies every noun through **12 major facets (جهات)** and a
**6-stage fractal cycle**.

---

## Definition of the Noun (التعريف الجامع المانع)

> الاسم هو مفرد يدل على ذات، أو كلي، أو جزئي، أو نوع، أو جنس،
> أو فرد، أو صفة قائمة بمحل، أو مفهوم اسمي مجرّد، على وجه
> الاستقلال النسبي، من غير دلالة أصلية على حدث مقترن بزمن، ومن
> غير اقتصار على الربط النسبي المحض.

**The noun** is an independent linguistic unit that denotes a substance,
universal, particular, species, genus, individual, standing quality,
or abstract nominal concept — without an inherent indication of a
time-bound event, and without being reduced to pure relational binding.

---

## Proof: The Noun as Epistemological Precondition (شرط إمكان معرفي)

### Premise 1
Knowledge does not begin with events alone.  It begins by establishing
a *thing*, a *substance*, a *type*, an *individual*, or a *concept*.

### Premise 2
Without this establishment, it is impossible to:
- Judge
- Point
- Count
- Classify
- Refer
- Distinguish between existents

### Premise 3
The word class that fulfils these functions is the **noun** — not the
verb and not the particle.

### Conclusion
> The noun is a **primary epistemological precondition** for establishing
> the existent and distinguishing it before composition.

---

## The 12 Facets (الجهات الاثنتا عشرة)

### 1. Existence (جهة الموجود)
The noun is the first vessel for the existent: it establishes
designation, reference, counting, and differentiation capability.

**Module:** `arabic_engine.noun.existence`

### 2. Universal vs. Particular (جهة الكلي والجزئي)
- **Universal (كلي):** applicable to many (إنسان, شجر, مدينة)
- **Particular (جزئي):** restricted to one (زيد, عمّان, الأردن)

**Module:** `arabic_engine.noun.universality`

### 3. Genus / Species / Individual (جهة الجنس والنوع والفرد)
- **Genus (جنس):** broadest category (حيوان, نبات)
- **Species (نوع):** shares a closer reality (إنسان, شجرة)
- **Individual (فرد):** specific realised entity (زيد)

**Module:** `arabic_engine.noun.taxonomy`

### 4. Proper Noun Types (جهة العلم وأنواعه)
Nine sub-types: PERSONAL, PLACE, TIME, TRANSFERRED, COMPOUND,
NICKNAME, PATRONYMIC, COINED, BORROWED.

**Module:** `arabic_engine.noun.proper`

### 5. Adjectival Noun (جهة الصفة الاسمية)
Nouns that primarily describe a quality: الأبيض, الطويل, الكريم.
Detected via morphological patterns (فاعل, مفعول, فعيل, أفعل, …).

**Module:** `arabic_engine.noun.attribute`

### 6. Number (جهة الوحدة والكثرة)
Eight forms: SINGULAR, DUAL, SOUND_MASC_PLURAL, SOUND_FEM_PLURAL,
BROKEN_PLURAL, COLLECTIVE_NOUN, GENUS_NOUN, NUMERAL.

**Module:** `arabic_engine.noun.number`

### 7. Gender (جهة التذكير والتأنيث)
Three genders: MASCULINE, FEMININE, DUAL_GENDER.
Four bases: REAL, METAPHORICAL, LEXICAL, SEMANTIC.

**Module:** `arabic_engine.noun.gender`

### 8. Definiteness (جهة المعرفة والنكرة)
Eight types: DEFINITE_ARTICLE, DEFINITE_PROPER, DEFINITE_PRONOUN,
DEFINITE_DEMONSTRATIVE, DEFINITE_RELATIVE, DEFINITE_ANNEXATION,
DEFINITE_VOCATIVE, INDEFINITE.

**Module:** `arabic_engine.noun.definiteness`

### 9. Compound Noun (جهة المركب الاسمي)
Three types: ANNEXATION (عبد الله), BLEND (بعلبك), PREDICATIVE (تأبط شرًا).

**Module:** `arabic_engine.noun.compound`

### 10. Borrowed Noun (جهة المقترض)
Loanwords that have stabilised in Arabic use.  Source language is
identified where possible (English, Persian, Greek, Latin, …).

**Module:** `arabic_engine.noun.borrowed`

### 11. Rigid Pattern (جهة الوزن الجامد)
Non-derived nouns have a fixed phonological/morphological template
(e.g. فَعْل, فُعْل, فِعَالَة) that gives them stability.

**Module:** `arabic_engine.noun.rigid_pattern`

### 12. Signification (جهة المطابقة والتضمن والالتزام)
Three layers of meaning:
- **Mutābaqa (مطابقة):** exact denotation
- **Taḍammun (تضمن):** included parts and limits
- **Iltizām (التزام):** necessary entailments

**Module:** `arabic_engine.noun.signification`

---

## The 6-Stage Fractal Cycle (مراحل الفراكتال الاسمي)

```
تعيين → حفظ → ربط → حكم → انتقال → رد
```

| Stage | Arabic | Description |
|-------|--------|-------------|
| 1 | تعيين (Designation) | Designate the existent, attribute, universal/particular, proper, definite |
| 2 | حفظ (Preservation) | Preserve referential, typological, descriptive identity |
| 3 | ربط (Linkage) | Link signifier → signified, pattern → semantic direction |
| 4 | حكم (Judgment) | Judge: definite/indefinite, masc/fem, sg/du/pl, genus/species/individual |
| 5 | انتقال (Transition) | Prepare for composition: reference, description, predication, annexation |
| 6 | رد (Return) | Return to structure, type, direction, layer, pattern |

**Module:** `arabic_engine.noun.fractal`

---

## Minimum Complete Threshold (الحد الأدنى المكتمل)

A noun satisfies the minimum complete threshold when it has:

1. **Existence (الثبوت):** non-empty surface form
2. **Distinction (الحد):** distinguished from verb / particle
3. **Extension (الامتداد):** phonological, written, semantic, referential
4. **Constituent (المقوِّم):** material + pattern + semantic direction + independence
5. **Structural relations (العلاقة البنائية):** number, gender, definiteness
6. **Unity (الوحدة):** forms a single nominal unit
7. **Assignability (قابلية التعيين):** can be judged as proper/genus/species/…

**Function:** `arabic_engine.noun.constitution.validate_noun_completeness()`

---

## API Reference

### Entry Points

```python
from arabic_engine.noun import (
    classify_noun,              # Master classifier
    validate_noun_completeness, # Minimum threshold check
    run_noun_fractal,           # 6-stage fractal cycle
    build_noun_signification,   # Mutābaqa / taḍammun / iltizām
)
```

### `classify_noun(closure, concept=None, all_tokens=None, token_index=0) → NounNode`

Takes a `LexicalClosure` with `pos == POS.ISM` and produces a fully
classified `NounNode` by running all 12 facet resolvers.

### `validate_noun_completeness(node: NounNode) → bool`

Returns `True` if the noun satisfies the minimum complete threshold.

### `run_noun_fractal(closure, concept=None) → NounNode`

Executes the complete 6-stage fractal cycle, returning a `NounNode`
with `fractal_stage == RETURN`.

### `build_noun_signification(node, concept) → NounSignification`

Builds the three-layer signification record.

### Data Types

- **`NounNode`** — frozen dataclass with all 12 facets as fields
- **`NounSignification`** — frozen dataclass with mutābaqa, taḍammun, iltizām

### Enums

| Enum | Members | Description |
|------|---------|-------------|
| `Gender` | MASCULINE, FEMININE, DUAL_GENDER | Grammatical gender |
| `GenderBasis` | REAL, METAPHORICAL, LEXICAL, SEMANTIC | Gender basis |
| `NounNumber` | SINGULAR, DUAL, SOUND_MASC_PLURAL, … | Number |
| `Definiteness` | DEFINITE_ARTICLE, DEFINITE_PROPER, … | Definiteness |
| `NounKind` | ENTITY, ATTRIBUTE, PROPER, GENUS, … | Major categories |
| `UniversalParticular` | UNIVERSAL, PARTICULAR | Universal vs particular |
| `ProperNounType` | PERSONAL, PLACE, TIME, … | Proper noun types |
| `CompoundType` | ANNEXATION, BLEND, PREDICATIVE | Compound types |
| `DerivationStatus` | RIGID, DERIVED | Rigid vs derived |
| `NounFractalStage` | DESIGNATION, PRESERVATION, … | Fractal stages |

---

## Pipeline Integration

The noun classification step runs as **Layer 2c** between lexical
closure (Layer 2) and syntax (Layer 3):

```
L0 Normalise → L1 Tokenise → L2 Lexical Closure → L2c Noun Constitution → L3 Syntax → …
```

Every `LexicalClosure` with `pos == POS.ISM` gets a `noun_node`
field attached, which is then available to all downstream layers
(syntax, ontology, dalāla, evaluation, …).

---

## Examples

```python
from arabic_engine.pipeline import run

result = run("كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ")

for cl in result.closures:
    if cl.noun_node is not None:
        nn = cl.noun_node
        print(f"{nn.surface}: kind={nn.noun_kind.name}, "
              f"gender={nn.gender.name}, number={nn.number.name}, "
              f"definiteness={nn.definiteness.name}")
```

Output:
```
زَيْدٌ: kind=INDIVIDUAL, gender=MASCULINE, number=SINGULAR, definiteness=DEFINITE_PROPER
الرِّسَالَةَ: kind=ENTITY, gender=FEMININE, number=SINGULAR, definiteness=DEFINITE_ARTICLE
```
