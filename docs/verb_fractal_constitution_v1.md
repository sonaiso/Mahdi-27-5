# Verb Fractal Constitution v1 — دستور الفعل الفراكتالي

> الفعل بوصفه لفظًا مفردًا ليس مجرد حامل لحدث، بل هو شرط إمكان معرفي
> وفراكتالي، لأن العالم لا يدرك بالذوات وحدها بل بما يقع ويتحول ويؤثر
> ويتسبب وينفعل.

---

## §1  Definition of the Verb — تعريف الفعل

The verb is not merely a "word denoting action".  It is:

> **A singular lexical unit denoting occurrence, becoming, or
> predicative attribution, bound to a temporal or modal direction,
> and prepared to carry predication toward an agent or its stand-in.**

Every verb thus contains, at its structural minimum:

| Pillar | Arabic | English |
|--------|--------|---------|
| Event | الحدث | The occurrence or process |
| Time / Modality | الزمن أو الجهة | Temporal or modal orientation |
| Predication (potential) | الإسناد بالقوة | Readiness to receive a subject |
| Agent-linkage | التهيؤ للربط بالفاعل | Slot for the doer or experiencer |

### Implementation

```python
from arabic_engine.core.types import VerbProfile
```

`VerbProfile` encodes root, bāb, tense, transitivity, completeness,
voice, person, number, gender, and nāsikh status.

---

## §2  Proof: Verb as Epistemic Condition — الفعل شرط إمكان معرفي

### Premise 1

The world is not grasped by entities alone.  It is also grasped
through what **occurs, transforms, originates, transitions,
affects, and produces change**.

### Premise 2

The noun alone — even a concrete or descriptive noun — cannot
represent: occurrence, transformation, origination, cessation,
gradation, causation, or passivity.

### Premise 3

If the event cannot be represented, then we cannot know:
*who* did it, *when* it happened, whether it was transitive or
intransitive, whether it is causal or derivative.

### Conclusion

> **The verb is a condition of epistemic possibility for
> representing the dynamic world, not merely a school-grammar
> category.**

---

## §3  Proof: Verb as Fractal Structure — الفعل بنية فراكتالية

The verb is not established all at once; it passes through the
same six-stage cycle that governs the entire project:

```
تعيين → حفظ → ربط → حكم → انتقال → رد
```

| Stage | Arabic | Question |
|-------|--------|----------|
| Designation | تعيين | What verb is this?  Trilateral / augmented?  Transitive / intransitive? |
| Preservation | حفظ | Does it preserve its root, pattern, event direction, and predicative capacity? |
| Linkage | ربط | Does it link event ↔ time, event ↔ agent, event ↔ patient, morphology ↔ semantics? |
| Judgment | حكم | Can it be classified as sound / defective, causal / non-causal, copular / non-copular? |
| Transition | انتقال | Can it transition to maṣdar, participles, time/place nouns, propositions? |
| Return | ردّ | Can it be traced back to its root, bāb, pattern, original semantic capacity? |

### Implementation

```python
from arabic_engine.core.enums import VerbFractalStage
from arabic_engine.verb import build_fractal_node

node = build_fractal_node("كَتَبَ", pattern="فَعَلَ")
assert node.fractal_stage == VerbFractalStage.RADD  # fully resolved
```

---

## §4  Minimum Complete Threshold — الحد الأدنى المكتمل

A word does not qualify as a verb unless it satisfies **all eight
conditions**:

| # | Arabic | Condition | Description |
|---|--------|-----------|-------------|
| 1 | ثبوت | Thubūt | Has a realised phonological form (past / present / imperative) |
| 2 | حد | Ḥadd | Distinctly identifiable as a verb (not noun, particle, maṣdar) |
| 3 | امتداد | Imtidād | Has phonological, pattern, temporal, and predicative extension |
| 4 | مقوِّم | Muqawwim | Has root + pattern + temporal direction + event capacity |
| 5 | علاقة بنائية | ʿAlāqa Bināʾiyya | Root → Pattern → Event → Time → Predication chain intact |
| 6 | انتظام | Intiẓām | Follows a known bāb and morphological system |
| 7 | وحدة | Waḥda | Functions as a single verbal unit |
| 8 | قابلية تعيين | Qābiliyyat Taʿyīn | Classifiable (base/augmented, transitive, tense…) |

### Implementation

```python
from arabic_engine.verb import validate_threshold
from arabic_engine.core.types import VerbMinimalThreshold

threshold = validate_threshold(...)
assert threshold.is_complete  # all eight pillars hold
```

---

## §5  Trilateral Bābs as Minimum Gates — أبواب الثلاثي كحد أدنى مكتمل

The six trilateral gates are not arbitrary phonetic variations;
they are the **minimum structural bridges** connecting a bare
root to the morphological, temporal, and semantic systems.

| # | Gate | Past | Present | Semantic tendency |
|---|------|------|---------|-------------------|
| 1 | باب نَصَرَ | فَعَلَ | يَفْعُلُ | Transitive action |
| 2 | باب ضَرَبَ | فَعَلَ | يَفْعِلُ | Transitive action |
| 3 | باب فَتَحَ | فَعَلَ | يَفْعَلُ | Transitive action |
| 4 | باب عَلِمَ | فَعِلَ | يَفْعَلُ | State / affect |
| 5 | باب كَرُمَ | فَعُلَ | يَفْعُلُ | Inherent quality |
| 6 | باب حَسِبَ | فَعِلَ | يَفْعِلُ | State / affect |

### Proof

1. The trilateral root alone is insufficient — it specifies
   neither bāb, nor vowelling, nor morphological behaviour.
2. When a conjugation gate is added, the root acquires the
   capacity for actual realisation, present-tense formation,
   semantic orientation, and derivation.
3. Differences between gates are not arbitrary: they produce
   morphological, behavioural, and sometimes semantic distinctions.

> **The trilateral bāb is the minimum-completeness gate for the
> bare verb, because it binds the root to the temporal, morphological,
> and semantic system.**

### Implementation

```python
from arabic_engine.verb import get_thulathi_bab, all_thulathi_babs
from arabic_engine.core.enums import ThulathiBab

bab = get_thulathi_bab(ThulathiBab.FA3ALA_YAF3ULU)
assert bab.past_pattern == "فَعَلَ"
```

---

## §6  Augmented Patterns as Epistemic Conditions — المزيد شرط إمكان

Augmented patterns are not derivational luxuries.  The world
cannot be known through simple events alone — it also requires:

| Pattern | Arabic | Semantic layer |
|---------|--------|----------------|
| أَفْعَلَ | إفعال | Causation / transitivity |
| فَعَّلَ | تفعيل | Intensification / transitivity |
| فَاعَلَ | مفاعلة | Reciprocity / partnership |
| تَفَعَّلَ | تفعّل | Affectation / reflexivity |
| تَفَاعَلَ | تفاعل | Mutual action / pretence |
| اِنْفَعَلَ | انفعال | Passivity / compliance |
| اِفْتَعَلَ | افتعال | Reflexivity / adoption |
| اِفْعَلَّ | افعلال | Colour or defect |
| اِسْتَفْعَلَ | استفعال | Request / becoming |

> **Each augmented pattern is a condition of epistemic possibility
> for representing higher-order event distinctions.**

---

## §7  Maṣdar — المصدر شرط إمكان

The maṣdar is not an incidental noun.  It is a foundational pillar.

The verb carries the event bound to time and predication.  But the
mind also needs the **event abstracted from its time and partial
predication** so that it can:
- classify it
- abstract it
- make it the subject of a judgment
- derive from it

Without the maṣdar, "writing" cannot be abstracted from "he wrote",
nor "exit" from "he exited", nor "beneficence" from "he did good".

> **The maṣdar is a condition of epistemic possibility for
> abstracting the event from time and partial predication.**

---

## §8  Derivatives — المشتقات شروط إمكان

Each derivative closes a facet of event-knowledge:

| Derivative | Arabic | Epistemic function |
|------------|--------|-------------------|
| Active participle | اسم الفاعل | Knowing the source / agent of the event |
| Passive participle | اسم المفعول | Knowing the patient / affected entity |
| Noun of time | اسم الزمان | Knowing when the event occurs |
| Noun of place | اسم المكان | Knowing where the event occurs |
| Noun of manner | اسم الهيئة | Knowing the manner of occurrence |
| Noun of instrument | اسم الآلة | Knowing the mediating tool |

> **Verbal derivatives are conditions of epistemic possibility
> for detailing the event-world — not decorative branches.**

### Implementation

```python
from arabic_engine.verb import build_derivatives, get_thulathi_bab
from arabic_engine.core.enums import ThulathiBab

bab = get_thulathi_bab(ThulathiBab.FA3ALA_YAF3ULU)
chain = build_derivatives(("ك", "ت", "ب"), bab)
assert chain.masdar != ""
assert chain.ism_fa3il != ""
```

---

## §9  Tense as Structural Pillar — الزمن ركن بنيوي

Tense in the verb is not an external adornment; it is structural.

If the event is stripped of all temporal orientation:
- We cannot know whether it occurred, is occurring, or is requested.
- We cannot distinguish factual from potential.
- We cannot anchor the event in the speaker's timeline.

Tense provides:

1. **Designation direction** — past / present-future / imperative
2. **Existential direction** — did it happen?  is it happening?
3. **Relation to speaker and reference time** — now, before now,
   after now

> **Tense is a condition of possibility for the verb *qua* verb,
> not merely an external temporal marker.**

---

## §10  Coherence and Derivational Network — التشاكل والارتباط

A complete verb is not a point; it is the **centre of a coherent
derivational network**.  Taking كَتَبَ:

```
كَتَبَ → يَكْتُبُ → اُكْتُبْ → كِتَابَة → كَاتِب → مَكْتُوب → مَكْتَب
```

Every node in this network is structurally derivable from the
root + bāb, and every node is traceable back to them.

---

## §11  Nāsikh Verbs — الأفعال الناسخة

Nāsikh verbs are not school-grammar exceptions.  They are
**epistemic-possibility gates** for predication binding,
approximation, inception, and belief.

### كان وأخواتها — Temporal/predicative binding

Condition of possibility for: persistence, transformation,
temporal restriction, predication transfer.

Members: كان, أصبح, أمسى, أضحى, ظل, بات, صار, ليس,
ما زال, ما فتئ, ما برح, ما انفك, ما دام

### كاد وأخواتها — Approximation / inception

Condition of possibility for: nearness, inception, hope,
near-possibility, incomplete occurrence.

Members: كاد, أوشك, عسى, شرع, بدأ, أخذ, جعل, طفق, أنشأ, هبّ

### ظنّ وأخواتها — Belief / epistemic judgment

Condition of possibility for: belief, estimation, supposition,
epistemic transfer.

Members: ظنّ, حسب, خال, زعم, رأى, علم, وجد, درى, تعلّم,
اتّخذ, ردّ, ترك, صيّر

### Implementation

```python
from arabic_engine.verb import classify_nasikh, is_nasikh

profile = classify_nasikh("كان")
assert profile.category == NasikhCategory.KANA_WA_AKHAWAT
assert is_nasikh("كاد")
```

---

## §12  Person as Epistemic Linkage — الشخص الخطابي شرط إمكان

The verb in Arabic does not merely denote an event; through its
morphological form it also indicates the **discourse person**:

- أَكْتُبُ — first person (speaker)
- تَكْتُبُ — second person (addressee)
- يَكْتُبُ — third person (absent)

These are not purely inflectional ornaments; they are the
**binding between event and rational agent from the standpoint
of discourse position**, prior to full syntactic composition.

> **The personal form of the verb is a condition of epistemic
> possibility for representing the agent's discourse position.**

---

## §13  Composition Readiness — الجاهزية للتركيب

The verb becomes ready for syntactic composition only when all
of the following are assembled:

1. Root (الجذر)
2. Bāb or pattern (الباب أو الوزن)
3. Tense (الزمن)
4. Transitivity (اللزوم/التعدي)
5. Agent/patient potential (الفاعلية/المفعولية بالقوة)
6. Causality when needed (السببية/المسببية)
7. Dependent derivatives (المشتقات التابعة)
8. Discourse person (الشخص الخطابي)
9. Verb type: complete / copular / approximative / epistemic

When all are present, the verb becomes:

> **An epistemic derivational centre, ready for composition
> according to the axioms of reason and the constitution.**

---

## §14  Final Consolidated Statement — الصياغة المحكمة النهائية

> The verb, as a singular lexical unit, is not merely an event
> carrier but a fractal epistemic condition, because the world
> cannot be grasped by entities alone — it must also be grasped
> through what occurs, transforms, affects, causes, and is
> affected.  Therefore the verb is not established unless it
> satisfies the minimum complete threshold: realisation,
> distinctness, extension, constituents, structural relation,
> regularity, unity, and classifiability.  The minimum gates
> of this completeness in the trilateral are the conjugation
> bābs (فَعَلَ يَفْعُلُ, فَعَلَ يَفْعِلُ, فَعَلَ يَفْعَلُ, …)
> because they are not disconnected phonetic forms but systems
> that bind the root to vowelling, gate, semantic direction,
> and the present tense, making the bare verb fit for
> conjugation and derivation.  The same fractal operates in
> augmented patterns, because each augmented pattern opens
> necessary semantic layers such as causation, compliance,
> partnership, affectation, and request — not formal additions
> but epistemic conditions for what lies above the event's origin.
> The maṣdar is a condition for abstracting the event from time
> and predication; verbal derivatives are conditions for
> detailing the facets of agency, passivity, time, place, manner,
> and instrument.  Tense is not an incidental adverb but a
> structural pillar that determines the direction of occurrence;
> the personal form binds the verb to the rational agent as
> speaker, addressee, or absent.  Nāsikh verbs enter this proof
> because كان and its sisters are conditions for temporal and
> predicative binding, كاد and its sisters for approximation and
> inception, and ظنّ and its sisters for belief and estimation.
> Thus the entire verb is organised into a coherent, traceable
> derivational network, and becomes ready for composition
> according to the axioms of reason and the constitution — not as
> random tradition but as a complete fractal structure.
