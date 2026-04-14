# دستور الوزن الفراكتالي — Weight Fractal Constitution v1

**Identity**: WFC-v1 — Weight Fractal Constitution v1
**Depends on**: Semantic Direction Space Constitution v1 (SDS-v1), Masdar Fractal Constitution (MFC-v1), Epistemic Reception Constitution v1 (ERC-v1)

---

## تمهيد سيادي — Sovereign Preamble

The weight (الوزن) is not a mere morphological label or a rote-learned template.
It is:

> **A fractal mathematical node, an epistemic condition of possibility for the word before composition, a structure carrying semantic direction, and an organising medium between root and word.**

The weight is:
- A carrying law
- A measurement structure
- A transition condition
- A linking mechanism between root, semantic direction, and final word

This document follows the Epistemic Reception Constitution v1 and the Semantic Direction Space Constitution v1,
and precedes the Fractal Derivation Function Spec v1 and Lexeme Fractal Constitution v2.

---

## الباب الأول: موضوع الوثيقة — Subject of the Document (Art. 1–3)

### المادة 1 — Article 1: Subject

Establishing the weight as a mathematical-fractal structure that carries semantic direction and transforms root material into a valid word before composition.

### المادة 2 — Article 2: Function

- Define weight foundationally
- Distinguish weight from root, form, and closed template
- Define condition of possibility
- Define minimum complete threshold
- Define direction carrying
- Define acceptance and rejection criteria
- Define mathematical formulation
- Prepare for derivation function integration

### المادة 3 — Article 3: Purpose

Prove that weights are:
- Systematic (not arbitrary)
- Classifiable
- Reducible
- Computationally implementable as fractal structures

---

## الباب الثاني: تعريف الوزن — Weight Definition (Art. 4–8)

### المادة 4 — Article 4: Definition

The weight is a **controlled template structure** that organises root positions, vowels, augmentations, and syllables, binding them to a general semantic direction.

### المادة 5 — Article 5: What Is Not a Weight

The weight is NOT:
- The root
- The final surface form
- Mere vowel patterns
- Mere letter count
- Pure convention without law

### المادة 6 — Article 6: Weight vs. Root

The root is the original semantic nucleus; the weight is the organisational law for that nucleus in a productive template.

### المادة 7 — Article 7: Weight vs. Form

The weight is a general template; the form (الصيغة) is a specific realisation of that template in a particular word.

### المادة 8 — Article 8: Weight vs. Closed Template

The weight is productive or measurable; the closed template (القالب المغلق) is non-generative but may function as a weight for certain particles and built-in nominals.

| Kind              | Arabic       | Description                              |
|-------------------|-------------|------------------------------------------|
| PRODUCTIVE        | منتج         | Active derivational weight               |
| CLOSED_TEMPLATE   | قالب مغلق    | Non-generative fixed template            |
| MEASURE_ONLY      | قياسي فقط   | Measurable but non-productive            |

---

## الباب الثالث: شرط الإمكان للوزن — Condition of Possibility (Art. 9–17)

### المادة 9 — Article 9: Definition

The condition of possibility is the set of conditions without which a structure cannot be a productive weight.

### المادة 10 — Article 10

Not every letter-vowel ordering is a weight. It is only a weight if it can:
- Organise root positions
- Carry a semantic direction
- Open a path to a valid word

### المادة 11 — Article 11: Six Levels

| Level     | Arabic  | Description                              |
|-----------|---------|------------------------------------------|
| BINYAWI   | بنيوي   | Clear positional structure               |
| MAQTA3I   | مقطعي   | Realisable syllable structure            |
| SARFI     | صرفي    | Known morphological slot                 |
| DALALI    | دلالي   | Bindable to a semantic direction         |
| TAWLIDI   | توليدي  | Can produce valid lexemes                |
| RADDI     | ردّي    | Derivatives traceable to root            |

### المادة 12–17

Each level is scored 0.0–1.0; the aggregate is their mean.
Implemented by `validate_weight_possibility()`.

---

## الباب الرابع: الحد الأدنى المكتمل — Minimum Complete Threshold (Art. 18–26)

### المادة 18 — Article 18: Eight Dimensions

A weight is not accepted until it satisfies:

| Dimension             | Arabic            | Symbol |
|-----------------------|-------------------|--------|
| Stability             | الثبوت            | Th     |
| Boundary              | الحد              | Hd     |
| Extension             | الامتداد          | Ex     |
| Constituent           | المقوِّم          | Muq    |
| Structural Relation   | العلاقة البنائية  | Rel    |
| Regularity            | الانتظام          | Ord    |
| Unity                 | الوحدة            | Uni    |
| Assignability         | قابلية التعيين    | Det    |

### المادة 19–26

```
MWC(W) = (Th + Hd + Ex + Muq + Rel + Ord + Uni + Det) / 8
```

The weight is accepted only if `MWC(W) >= θ₁` (default 0.625).
Implemented by `compute_mwc()`.

---

## الباب الخامس: الوزن والقانون الفراكتالي — Fractal Law (Art. 27–34)

### المادة 27 — Article 27: General Law

```
تعيين → حفظ → ربط → حكم → انتقال → رد
```

### المادة 28–33

| Phase          | Arabic  | Function                                    |
|----------------|---------|---------------------------------------------|
| Identification | تعيين   | Assign template + positions                 |
| Preservation   | حفظ     | Preserve identity + root order              |
| Linkage        | ربط     | Link root↔weight, weight↔direction          |
| Judgement      | حكم     | Judge validity/productivity                 |
| Transition     | انتقال  | Transition to mufrad/derivative             |
| Return         | ردّ     | Trace form → template → root               |

### المادة 34 — Article 34: Fractal Proof

The weight is fractal because the same law recurs:
- In the phonetic levels beneath it
- In the forms realised from it
- In the derivational family produced by it

```
FW(W) = (Id + Pr + Rb + Jd + Tr + Rc) / 6
```

Accepted only if `FW(W) >= θ₂` (default 0.667).
Implemented by `compute_fractal_score()`.

---

## الباب السادس: حمل الوزن للجهات الدلالية — Direction Carrying (Art. 35–42)

### المادة 35–36

The weight carries a **general semantic direction**, not just a form.
Not every weight carries every direction.

### المادة 37 — Article 37: Four Suitability Conditions

| Condition                  | Arabic               | Symbol |
|----------------------------|---------------------|--------|
| Structural Suitability     | الملاءمة البنيوية    | W1     |
| Syllabic Suitability       | الملاءمة المقطعية    | W2     |
| Morphological Suitability  | الملاءمة الصرفية     | W3     |
| Semantic Suitability       | الملاءمة الدلالية    | W4     |

### المادة 38–42

```
Carrier(W, s_i) = 1  iff  f(W1, W2, W3, W4) >= θ_w
```

Default `θ_w = 0.75`.
Implemented by `evaluate_direction_suitability()`.

| Carrying Mode | Arabic | Definition                              |
|---------------|--------|-----------------------------------------|
| ASLI          | أصلي   | Weight carries direction directly       |
| TABI3I        | تابعي  | Weight carries via subsidiary derivation|
| MUSHTAQ       | مشتق   | Weight carries through re-projection    |
| MUMTANI3      | ممتنع  | Impossible for this weight              |

---

## الباب السابع: وزن الثلاثي المجرد — Trilateral Base (Art. 43–46)

### المادة 43–44

The trilateral base verb doors are the minimum complete gateways for verbs:

| Door                 | Past     | Present     |
|----------------------|----------|-------------|
| FA3ALA_YAF3ULU       | فَعَلَ   | يَفْعُلُ    |
| FA3ALA_YAF3ILU       | فَعَلَ   | يَفْعِلُ    |
| FA3ALA_YAF3ALU       | فَعَلَ   | يَفْعَلُ    |
| FA3ILA_YAF3ALU       | فَعِلَ   | يَفْعَلُ    |
| FA3ULA_YAF3ULU       | فَعُلَ   | يَفْعُلُ    |

### المادة 45–46

These doors are not arbitrary; they preserve root positions, link past to present,
open derivation, and carry structural distinctions.
Implemented by `classify_verb_door()`.

---

## الباب الثامن: وزن المزيد — Augmented Weight (Art. 47–50)

### المادة 47–48

The augmented weight carries a higher semantic layer:

| Layer       | Arabic  | Example Pattern |
|-------------|---------|-----------------|
| SABABIYYA   | سببية   | أَفْعَلَ         |
| MUSHARAKA   | مشاركة  | فَاعَلَ          |
| MUTAWA3A    | مطاوعة  | انْفَعَلَ        |
| TADARRUJ    | تدرّج   | تَفَعَّلَ        |
| TALAB       | طلب     | اسْتَفْعَلَ      |
| TAKALLUF    | تكلّف   | تَفَاعَلَ        |
| TAHAWWUL    | تحوّل   | افْعَلَّ         |

### المادة 49–50

Implemented by `validate_augmented_weight()`.

---

## الباب التاسع: الجامد والمصدر والمشتقات — Nouns, Masdar, Derivatives (Art. 51–54)

### المادة 51 — Article 51: Frozen Nouns

Frozen nouns (الاسم الجامد) are not outside the system; they establish existential independence through a fixed weight.

### المادة 52 — Article 52: Masdar

The masdar is a linking node between existential and transformational being, requiring a weight that fixes the event abstracted from time and person.

### المادة 53 — Article 53: Nominal & Verbal Derivatives

Derivative weights carry directions: فاعلية, مفعولية, ظرفية زمانية, ظرفية مكانية, آلية, هيئة.

### المادة 54 — Article 54

These are not appendages but conditions of possibility for detailing the event, descriptive, and nominal worlds.

---

## الباب العاشر: الزمن والشخص والناسخ — Tense, Person, Copula (Art. 55–58)

### المادة 55 — Article 55: Tense in Verbal Weight

The verbal weight carries a temporal direction; tense is a structural element, not a mere external adverb.

### المادة 56 — Article 56: Person

The verbal weight accepts binding to speaker (متكلم), addressee (مخاطب), or absent (غائب).

### المادة 57 — Article 57: Copula Verbs (النواسخ)

| Category            | Arabic           | Examples               |
|---------------------|-----------------|------------------------|
| KANA_WA_AKHAWAT     | كان وأخواتها    | كان، صار، أصبح، ظل    |
| KADA_WA_AKHAWAT     | كاد وأخواتها    | كاد، أوشك، عسى        |
| ZANNA_WA_AKHAWAT    | ظنّ وأخواتها    | ظنّ، حسب، علم، رأى    |

### المادة 58 — Article 58

These are conditions of possibility for temporal, judgemental, or epistemic binding that cannot be fulfilled by the full eventive verb alone.

---

## الباب الحادي عشر: الصياغة الرياضية — Mathematical Formulation (Art. 59–62)

### المادة 59 — Article 59: Formal Weight Tuple

```
W = (R, V, A, S, D, P)
```

Where:
- **R**: Root positional structure
- **V**: Vowel pattern structure
- **A**: Augmentation positions
- **S**: Syllabic structure
- **D**: General semantic direction
- **P**: Carrying capacity for lexeme/derivative type

Implemented by `build_formal_tuple()`.

### المادة 60 — Article 60: MWC Formula

```
MWC(W) = (Th + Hd + Ex + Muq + Rel + Ord + Uni + Det) / 8
```

Accepted only if `MWC(W) >= θ₁`.

### المادة 61 — Article 61: Fractal Score

```
FW(W) = (Id + Pr + Rb + Jd + Tr + Rc) / 6
```

Accepted only if `FW(W) >= θ₂`.

### المادة 62 — Article 62: Direction Carrying

```
Carrier(W, s_i) = 1  iff  f(W1, W2, W3, W4) >= θ_w
```

---

## الباب الثاني عشر: معايير القبول والرفض — Acceptance/Rejection (Art. 63–64)

### المادة 63 — Article 63: Acceptance Criteria

1. Representable as template
2. Distinguished from others by boundary
3. MWC >= θ₁
4. Carries a semantic direction
5. Can transition to mufrad/derivative
6. Derivatives can be traced back

### المادة 64 — Article 64: Rejection Criteria

1. Mere movement ordering without law
2. No general semantic direction
3. No generative or analytic path
4. Cannot trace forms back to it
5. Confuses weight with root or final form

Implemented by `validate_weight_acceptance()`.

---

## الباب الثالث عشر: الصيغة المختصرة المعتمدة — Summary Formula (Art. 65–66)

### المادة 65

> The weight is a fractal mathematical node and an epistemic condition of possibility for the word before composition.
> Not every ordering is a weight; it is only accepted if it satisfies the minimum complete threshold,
> then fulfils the fractal law: identification, preservation, linkage, judgement, transition, return.
> The weight carries the general semantic direction, links root to word, prevents arbitrariness in derivation,
> and opens the door to generation, return, and measurement.

### المادة 66 — Article 66: Next Phase

Directly derived from this document:
- **Fractal Derivation Function Spec v1**
- **Lexeme Fractal Constitution v2**

---

## Implementation

- **Enums**: `arabic_engine/core/enums.py` — `WeightCarryingMode`, `WeightFractalPhase`, `WeightClass`, `WeightKind`, `WeightPossibilityDimension`, `WeightValidationStatus`, `ThulathiBab`, `AugmentedSemanticLayer`, `NasikhCategory`
- **Types**: `arabic_engine/core/types.py` — `WeightProfile`, `WeightDirectionMapping`, `WeightFractalNode`, `WeightFractalResult`, `WeightFormalTuple`, `VerbDoor`, `WeightPossibilityResult`, `WeightMWCScore`, `WeightFractalScore`, `WeightDirectionSuitability`, `WeightValidationResult`
- **Module**: `arabic_engine/signifier/weight_fractal.py`
- **Data**: `arabic_engine/data/weight_direction_matrix.json`, `arabic_engine/data/verb_doors_seed.json`, `arabic_engine/data/augmented_weights_seed.json`
- **Tests**: `tests/test_weight_fractal.py`
- **Total Closure**: `arabic_engine/mufrad_closure.py` — `close_mufrad()`
- **Total Closure Type**: `arabic_engine/core/types.py` — `MufradClosureResult`

### Thresholds

| Symbol | Purpose                        | Default |
|--------|--------------------------------|---------|
| θ₁     | MWC minimum acceptance         | 0.625   |
| θ₂     | Fractal score minimum          | 0.667   |
| θ_w    | Direction suitability minimum  | 0.75    |

### Total Closure Formula

```
Ω(w) = R ∘ E ∘ D ∘ W ∘ S ∘ M ∘ P ∘ C ∘ N(w)
```

Ω(w).is_closed = True iff ALL components are non-None and valid.
