# دستور فضاء الجهات الدلالية — Semantic Direction Space Constitution v1

**Identity**: SDS-v1 — Semantic Direction Space Constitution v1
**Depends on**: Epistemic Reception Constitution v1 (ERC-v1), Masdar Fractal Constitution (MFC-v1)

---

## الباب الأول: الأجناس العليا — Supreme Genera (Art. 1–5)

### المادة 1 — Article 1: Definition of the Genus Axis

The Semantic Direction Space classifies the intrinsic semantic bearing of a word **before any reception or judgment**. The genus axis is logically prior to the reception subject axis of ERC-v1.

### المادة 2 — Article 2: The Four Supreme Genera

| Genus     | Arabic  | Definition                                            |
|-----------|---------|-------------------------------------------------------|
| WUJUD     | الوجود  | What establishes being — existence, entity, substance |
| SIFA      | الصفة   | What describes quality, state, or capacity            |
| HADATH    | الحدث   | What establishes occurrence, change, or becoming      |
| NISBA     | النسبة  | What establishes linkage, direction, or connection    |

### المادة 3 — Article 3: Exhaustiveness

Every Arabic word belongs to exactly one supreme genus. No word can remain unclassified.

### المادة 4 — Article 4: Mutual Exclusion

The four genera are mutually exclusive at the word level — a word cannot simultaneously be WUJUD and HADATH.

### المادة 5 — Article 5: Genus vs. Subject Genre

`SemanticDirectionGenus` classifies the *intrinsic bearing* of the word itself.
`SubjectGenre` (ERC-v1) classifies *what arrives to the rational self*.
The former is prior to the latter.

---

## الباب الثاني: الجهات الاشتقاقية — Derivational Directions (Art. 6–12)

### المادة 6 — Article 6: Definition

A derivational direction is a morphological projection that a root can take. Each direction specifies a semantic function (agent, patient, time, place, instrument, etc.).

### المادة 7 — Article 7: The 13 Core Directions

| Direction         | Arabic      | Genus  | Function               |
|-------------------|-------------|--------|------------------------|
| ISM_FA3IL         | اسم فاعل   | SIFA   | Active participle      |
| ISM_MAF3UL        | اسم مفعول  | SIFA   | Passive participle     |
| ISM_ZAMAN         | اسم زمان   | NISBA  | Noun of time           |
| ISM_MAKAN         | اسم مكان   | NISBA  | Noun of place          |
| ISM_ALA           | اسم آلة    | WUJUD  | Noun of instrument     |
| ISM_HAY2A         | اسم هيئة   | SIFA   | Noun of manner         |
| ISM_TAFDIL        | اسم تفضيل  | SIFA   | Elative / comparative  |
| SIFA_MUSHABBAHA   | صفة مشبهة  | SIFA   | Resembling adjective   |
| MASDAR            | مصدر       | HADATH | Verbal noun            |
| FI3L_MADI         | فعل ماضٍ   | HADATH | Past-tense verb        |
| FI3L_MUDARI3      | فعل مضارع  | HADATH | Present-tense verb     |
| FI3L_AMR          | فعل أمر    | HADATH | Imperative verb        |
| ISM_JAMID         | اسم جامد   | WUJUD  | Non-derived noun       |

### المادة 8–12: Each direction is formally specified with weight conditions and root conditions (see `direction_space_seed.json`).

---

## الباب الثالث: الفواصل الحدّية — Boundary Conditions (Art. 13–19)

### المادة 13 — Article 13: Three Boundary Types

| Boundary        | Arabic      | Definition                         |
|-----------------|-------------|------------------------------------|
| HADD_FASIL      | حد فاصل    | Absolute — no overlap possible     |
| HADD_INTIQALI   | حد انتقالي | Transitional — gradual shift       |
| HADD_MUSHTARAK  | حد مشترك   | Shared — partial overlap exists    |

### المادة 14–19: Boundary rules between specific direction pairs are encoded in the seed data.

---

## الباب الرابع: شروط حمل الوزن — Weight Carrying Conditions (Art. 20–26)

### المادة 20 — Article 20

A weight pattern can carry a direction only if it appears in the direction's weight condition list.

### المادة 21 — Article 21

If no weight conditions are specified, the direction is unconstrained.

### المادة 22–26: Specific weight↔direction carrying rules are in `weight_direction_matrix.json`.

---

## الباب الخامس: شروط حمل الجذر — Root Carrying Conditions (Art. 27–33)

### المادة 27 — Article 27

Root type is inferred from radical count: 3 → triliteral, 4 → quadriliteral.

### المادة 28 — Article 28

A root can carry a direction only if its type appears in the direction's root condition list.

### المادة 29–33: Specific root↔direction rules.

---

## الباب السادس: العلاقات المسموح بها — Permitted Relations (Art. 34–40)

### المادة 34 — Article 34: Seven Relation Types

| Relation       | Arabic            | Definition                                    |
|----------------|-------------------|-----------------------------------------------|
| WIRATHA        | الوراثة           | Direction inherits properties from a parent    |
| TAWAFUQ        | التوافق           | Two directions may co-occur                   |
| MAN3           | المنع             | Two directions are mutually exclusive          |
| TAHAWWUL       | التحول            | One direction transforms into another          |
| ISHTIRAT       | الاشتراط          | One requires another as precondition           |
| ISQAT_TARKIBI  | الإسقاط التركيبي  | Direction projects into syntactic structure    |
| RADD           | الردّ              | Direction rejects or reverses another          |

### المادة 35–40: Each relation is conditional — conditions are stored in the seed data.

---

## الباب السابع: الحد الأدنى المكتمل — Completeness Conditions (Art. 41–45)

### المادة 41 — Article 41

The direction space is *complete* when:
1. Every genus has at least one direction.
2. At least one relation of each type exists.
3. All boundary types are represented.

### المادة 42–45: Formal completeness verification.

---

## الباب الثامن: الصياغة الرياضية — Mathematical Formulation (Art. 46–50)

### المادة 46 — Article 46

The direction space is a labelled directed graph:

```
S = (D, R, G, B)
```

Where:
- D = set of directions
- R ⊆ D × D × RelationType = set of relations
- G : D → {WUJUD, SIFA, HADATH, NISBA} = genus function
- B : D → {FASIL, INTIQALI, MUSHTARAK} = boundary function

### المادة 47 — Article 47

Direction assignment is a function:

```
A : LexicalClosure → D
```

Such that A(w).genus = G(A(w)).

### المادة 48–50: Formal proofs of completeness and consistency.

---

## Implementation

- **Enums**: `arabic_engine/core/enums.py` — `SemanticDirectionGenus`, `DerivationalDirection`, `DirectionRelation`, `DirectionBoundary`
- **Types**: `arabic_engine/core/types.py` — `SemanticDirection`, `DirectionRelationRecord`, `SemanticDirectionSpace`, `DirectionAssignment`
- **Module**: `arabic_engine/signified/semantic_direction.py`
- **Data**: `arabic_engine/data/direction_space_seed.json`
- **Tests**: `tests/test_semantic_direction.py`
