# Final Kernel-14 Schema (Canonical)

هذا المستند هو المرجع الرسمي للنواة المعرفية-التفسيرية في المشروع.
أي بنية خارج هذه النواة تُعامل كمشتقة وليست أصلًا.

## 1) Canonical labels (14 only)

1. `Self`
2. `Reality`
3. `Sense`
4. `PriorInfo`
5. `Link`
6. `Concept`
7. `Judgement`
8. `Method`
9. `Proof`
10. `Carrier`
11. `Exchange`
12. `Model`
13. `Constraint`
14. `State`

> Rule: no additional primary labels are allowed in kernel scope.

## 2) Core relationships (minimal)

- `(:Self)-[:KNOWS]->(:Concept)`
- `(:Self)-[:EMITS]->(:Carrier)`
- `(:Self)-[:RECEIVES]->(:Carrier)`
- `(:Reality)-[:IS_SENSED_AS]->(:Sense)`
- `(:Sense)-[:IS_INTERPRETED_WITH]->(:PriorInfo)`
- `(:PriorInfo)-[:ARE_BOUND_BY]->(:Link)`
- `(:Link)-[:YIELDS]->(:Concept)`
- `(:Concept)-[:IS_JUDGED_AS]->(:Judgement)`
- `(:Judgement)-[:IS_EVALUATED_BY]->(:Method)`
- `(:Judgement)-[:IS_JUSTIFIED_BY]->(:Proof)`
- `(:Judgement)-[:IS_LIMITED_BY]->(:Constraint)`
- `(:Judgement)-[:HAS_STATE]->(:State)`
- `(:Concept)-[:ARE_CARRIED_BY]->(:Carrier)`
- `(:Carrier)-[:PARTICIPATES_IN]->(:Exchange)`
- `(:Exchange)-[:INVOLVES]->(:Self)`
- `(:Exchange)-[:FORMS]->(:Model)`
- `(:Model)-[:HAS_STATE]->(:State)`

## 3) Required minimum fields

Only minimum fields are required; anything else is optional metadata.

- `Self`: `self_id`, `name`
- `Reality`: `reality_id`, `kind`
- `Sense`: `sense_id`, `modality`
- `PriorInfo`: `prior_info_id`, `source`
- `Link`: `link_id`, `link_kind`
- `Concept`: `concept_id`, `label`
- `Judgement`: `judgement_id`, `judgement_type`
- `Method`: `method_id`, `family`
- `Proof`: `proof_id`, `proof_kind`
- `Carrier`: `carrier_id`, `carrier_type`
- `Exchange`: `exchange_id`, `exchange_type`
- `Model`: `model_id`, `name`
- `Constraint`: `constraint_id`, `constraint_type`
- `State`: `state_id`, `state_type`

## 4) Derivation rules (base vs derived)

### 4.1 Base (أصل)

العناصر الأصلية هي العقد الأربع عشرة السابقة فقط مع العلاقات الأساسية.

### 4.2 Derived (مشتق)

أي كيان أعلى من النواة يعد مشتقًا، ويجب أن يوضح أصل اشتقاقه من عقد النواة:

- **Utterance** ← derived from `Carrier`
- **LinguisticProfile** ← derived from `Method + Carrier + Concept`
- **KnowledgeEpisode** ← derived from `Reality + Sense + PriorInfo + Link + Judgement`
- **DiscourseExchange** ← derived from `Exchange + Carrier + Self + State`
- **ReusableModel** ← derived from `Model + State + repeated validated patterns`

### 4.3 Representation (تمثيل)

- Python is the logic source (validation, derivation, lifecycle rules).
- Neo4j is graph representation for storage/querying.
- Derived entities must not be promoted to new primary labels in kernel scope.

## 5) Alignment with existing layers

- `signifier`, `syntax`, `signified`, `linkage`, `cognition` remain usable as
  operational layers.
- They are interpreted as **derived/application layers** over the kernel, not
  additional ontological roots.

## 6) Rational Self Ontology v1 Extensions

### New Kernel Relations

Two new relations extend the Self node's capabilities:

- `(:Self)-[:DESIGNATES]->(:Concept)` — The rational self designates
  (perceives/names) lexemes as concept instances.
- `(:Self)-[:INTENDS_COMPOSITION]->(:Concept)` — The rational self intends
  to compose lexemes into larger structures.

### Self Node Extended Fields

The `Self` node in Neo4j now supports:

- `perception_mode` (NOT NULL) — The self's perception mode (بصري/سمعي/…)
- `judgment_capacity` (NOT NULL) — The self's judgement capacity [0, 1]

### Relationship to Lexeme Epistemic Core

The `RationalSelfRecord` dataclass bridges the Self kernel node to the
Lexeme Epistemic Core module. It provides the epistemic agent model that
drives the chain:

```
perception → designation → classification → judgement → composition
```

See `docs/rational_self_ontology_v1.md` for the complete specification.
