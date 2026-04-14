# دستور الوزن الفراكتالي — Weight Fractal Constitution v1

**Identity**: WFC-v1 — Weight Fractal Constitution v1
**Depends on**: Semantic Direction Space Constitution v1 (SDS-v1), Masdar Fractal Constitution (MFC-v1)

---

## الباب الأول: الوزن شرط إمكان — Weight as Condition of Possibility (Art. 1–5)

### المادة 1 — Article 1: Weight Is Prior to the Word

The Arabic morphological weight (الوزن) is not a post-hoc description — it is the **condition of possibility** for the word to exist as a meaningful unit.

### المادة 2 — Article 2: Weight Classification

| Class              | Arabic          | Radical Count | Augmented |
|--------------------|-----------------|---------------|-----------|
| THULATHI_MUJARRAD  | ثلاثي مجرد     | 3             | No        |
| THULATHI_MAZEED    | ثلاثي مزيد     | 3             | Yes       |
| RUBA3I_MUJARRAD    | رباعي مجرد     | 4             | No        |
| RUBA3I_MAZEED      | رباعي مزيد     | 4             | Yes       |
| KHUMASI            | خماسي           | 5             | —         |

### المادة 3 — Article 3: Weight Profile

Each weight instance carries:
- Pattern string (e.g., `فَعْل`)
- Weight class
- Radical count
- Augmentation letters
- Semantic direction genus
- Carrying mode

### المادة 4 — Article 4: Pre-Compositional Nature

Weight determines the word's semantic capacity **before** syntactic composition. The word is already semantically directed at the morphological level.

### المادة 5 — Article 5: Relationship to D_min

The weight complements the D_min phonological minimum: D_min encodes *how* the word sounds, the weight encodes *what form* it takes.

---

## الباب الثاني: لماذا الوزن ليس اعتباطيًا — Why Weight Is Not Arbitrary (Art. 6–10)

### المادة 6 — Article 6: Non-Arbitrariness Theorem

**Theorem**: For every weight pattern `p` and derivational direction `d`, the mapping `p → d` is **systematic and rule-governed**, not arbitrary.

**Proof**: The weight-direction matrix shows that:
- `فَعْل` can carry MASDAR but not ISM_FA3IL
- `فاعِل` can carry ISM_FA3IL but not MASDAR
- `مَفعول` can carry ISM_MAF3UL but not ISM_FA3IL

These are not arbitrary — they follow from the **morphological structure** of the pattern.

### المادة 7 — Article 7: Carrying Mode

| Mode     | Arabic | Definition                              |
|----------|--------|-----------------------------------------|
| ASLI     | أصلي   | Weight carries direction directly       |
| TABI3I   | تابعي  | Weight carries via subsidiary derivation|
| MUSHTAQ  | مشتق   | Weight carries through re-projection    |
| MUMTANI3 | ممتنع  | Impossible for this weight              |

### المادة 8 — Article 8: Prohibition Proof

If a weight `p` is in the prohibited list of direction `d`, then no word with pattern `p` can carry direction `d`. This is a **structural impossibility**, not a convention.

### المادة 9–10: Examples and counter-examples.

---

## الباب الثالث: كيف يحمل الوزن جهة — Weight Carrying a Direction (Art. 11–15)

### المادة 11 — Article 11: Carrying Function

```
C : WeightProfile × SemanticDirection → WeightCarryingMode
```

### المادة 12 — Article 12: Carrying Matrix

The carrying matrix maps every (pattern, direction) pair to a carrying mode. See `weight_direction_matrix.json`.

### المادة 13 — Article 13: Weight Conditions

A direction specifies which weight patterns can carry it. The `validate_weight_carrying()` function checks this.

### المادة 14–15: Edge cases and weak-letter patterns.

---

## الباب الرابع: التوليد الفراكتالي — Fractal Derivation from Weight (Art. 16–20)

### المادة 16 — Article 16: Six-Phase Fractal Cycle

| Phase   | Arabic | Function                                |
|---------|--------|-----------------------------------------|
| TA3YIN  | تعيين  | Declare weight identity                 |
| TAMYIZ  | تمييز  | Distinguish from other weights          |
| TAHMIL  | تحميل  | Assign semantic direction to carry      |
| TAHQIQ  | تحقيق  | Prove weight↔direction non-arbitrary    |
| TAWLID  | توليد  | Generate derived fractal nodes          |
| RADD    | ردّ    | Trace back to root+weight origin        |

### المادة 17 — Article 17: Tree Structure

The fractal derivation produces a six-node chain, each node at one phase. The tree mirrors the Masdar Fractal Constitution's six-phase cycle.

### المادة 18 — Article 18: Parent-Child Links

Each node has at most one parent and at most one child, forming a strictly sequential chain.

### المادة 19–20: Closure condition — all six phases must be present.

---

## الباب الخامس: الوزن قبل التركيب — Weight as Pre-Compositional Condition (Art. 21–25)

### المادة 21 — Article 21

The weight determines the semantic capacity of the word **before** it enters syntactic composition. This is the key insight: meaning is not just compositional — it begins at the morphological level.

### المادة 22 — Article 22

The direction assignment from SDS-v1 combined with the weight carrying from WFC-v1 produces a **fully specified pre-compositional semantic profile** for every single word.

### المادة 23 — Article 23: Relationship to Masdar

The masdar (verbal noun) is the central bridge node. The weight fractal shows how other derivational directions branch from the masdar as fractal children.

### المادة 24–25: Integration with the pipeline.

---

## الباب السادس: الصياغة الرياضية — Mathematical Formulation (Art. 26–30)

### المادة 26 — Article 26

The weight fractal is a function:

```
W : P × R → D
```

Where:
- P = set of weight patterns
- R = set of roots
- D = set of derivational direction assignments

### المادة 27 — Article 27

The completeness score is:

```
completeness = (phase_coverage + direction_coverage) / 2
```

Where phase_coverage = |actual_phases ∩ expected_phases| / |expected_phases|.

### المادة 28 — Article 28: Closure Condition

A word is **weight-fractally closed** when:
- All 6 phases are present in the tree
- The direction map has at least one permitted direction
- The completeness score ≥ 0.75

### المادة 29–30: Total closure formula.

The total closure of a single word:

```
Ω(w) = R ∘ E ∘ D ∘ W ∘ S ∘ M ∘ P ∘ C ∘ N(w)
```

Ω(w).is_closed = True iff ALL components are non-None and valid.

---

## Implementation

- **Enums**: `arabic_engine/core/enums.py` — `WeightCarryingMode`, `WeightFractalPhase`, `WeightClass`
- **Types**: `arabic_engine/core/types.py` — `WeightProfile`, `WeightDirectionMapping`, `WeightFractalNode`, `WeightFractalResult`
- **Module**: `arabic_engine/signifier/weight_fractal.py`
- **Data**: `arabic_engine/data/weight_direction_matrix.json`
- **Tests**: `tests/test_weight_fractal.py`
- **Total Closure**: `arabic_engine/mufrad_closure.py` — `close_mufrad()`
- **Total Closure Type**: `arabic_engine/core/types.py` — `MufradClosureResult`
- **Total Closure Tests**: `tests/test_mufrad_closure.py`
