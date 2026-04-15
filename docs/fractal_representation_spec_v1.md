# Fractal Representation Spec v1
# مواصفة التمثيل الفراكتالي — الإصدار الأول

> **مواصفة مشتقة** — رمز الإصدار: `FRS-v1`
> هذه المواصفة مشتقة من الدستور الفراكتالي الأصلي `FCC-v1`.
> انظر: [`docs/fractal_core_constitution_v1.md`](fractal_core_constitution_v1.md)
>
> الوحدة البرمجية: `arabic_engine.representation.fractal_rep_spec`

---

## 1 — الأصل والغرض (Origin and Purpose)

**الأصل**: هذه المواصفة مشتقة مباشرة من الدستور الفراكتالي (FCC-v1 §7).
وجودها ضرورة حتمية لأن الدستور لا يتحول إلى تنفيذ حقيقي بدون مواصفة
تمثيل واضحة تربط المفهوم النظري بالكود القابل للتشغيل.

**الغرض**:
مواصفة التمثيل الفراكتالي هي المواصفة التنفيذية الأولى للدستور.
وظيفتها أن تحدد:

1. كيف يُرمَّز الأصل الفراكتالي `(E, K, F, C)` في Python.
2. كيف يُسجَّل أثر الطبقات `L0 → L9` بصورة قابلة للتتبع.
3. كيف ينتج المحرك مخرجاً نهائياً قابلاً للاختزال إلى أعداد صحيحة.

---

## 2 — الأصل الفراكتالي في التمثيل (Fractal Origin in Representation)

كل عنصر لغوي في المحرك يُمثَّل بواسطة tuple رباعية أصلية:

$$\text{FractalOrigin}(u) = (E,\, K,\, F,\, C) \in \mathbb{N} \times \Sigma^* \times \mathbb{N} \times \Sigma^*$$

| الحقل | الرمز | النوع | التعريف |
|-------|-------|-------|---------|
| `existence` | `E(u)` | `int ≥ 0` | نقطة Unicode للعنصر — إثبات وجوده |
| `prior_knowledge_key` | `K(u)` | `str ≠ ""` | مفتاح السجل السابق (DMIN_REGISTRY) |
| `function_mask` | `F(u)` | `int ≥ 0` | قناع بتي لسمات التحول الصوتي |
| `initial_class` | `C(u)` | `str ≠ ""` | التصنيف الأولي (مثل `"consonant"`) |

**مثال Python**:

```python
from arabic_engine.representation.fractal_rep_spec import FractalOrigin

origin = FractalOrigin(
    existence=0x0643,          # ك — U+0643
    prior_knowledge_key="U+0643",
    function_mask=0b10000001,  # CONSONANT | ROOT_RADICAL
    initial_class="consonant",
)
```

**شرط الصحة** (FCC-v1 §2):

```python
from arabic_engine.representation.fractal_rep_spec import validate_fractal_origin
result = validate_fractal_origin(origin)
assert result.valid
```

---

## 3 — أنماط التمثيل وصيَغه (Modes and Formats)

### 3.1 أنماط التمثيل (`RepresentationMode`)

| النمط | الرمز | الوصف |
|-------|-------|-------|
| `NUMERIC` | 1 | متجه عددي `∈ ℕⁿ` — النمط الافتراضي |
| `TEXT` | 2 | نص عربي قابل للقراءة |
| `GRAPH` | 3 | رسم عقدي متوافق مع الكيرنل-14 |
| `HYBRID` | 4 | نص + متجه عددي مدمجان |

### 3.2 صيغ التسلسل (`RepresentationFormat`)

| الصيغة | الرمز | الاستخدام |
|--------|-------|----------|
| `TUPLE` | 1 | Python tuple مجمّدة — الصيغة الافتراضية في الذاكرة |
| `JSON` | 2 | قاموس JSON للتبادل عبر الشبكة |
| `YAML` | 3 | YAML للملفات الإعدادية |
| `CYPHER` | 4 | Cypher لاستيراد Neo4j |

---

## 4 — سجل التمثيل الفراكتالي (Fractal Representation Record)

### 4.1 التعريف

`FractalRepresentation` هو الناتج الكامل والنهائي لمواصفة التمثيل.
إنه نوع بيانات Python مجمّد (`frozen=True`) يحتوي على:

| الحقل | النوع | الوصف |
|-------|-------|-------|
| `element_id` | `str` | معرّف فريد للعنصر (مثل `"U+0643"`) |
| `origin` | `FractalOrigin` | الأصل الفراكتالي `(E, K, F, C)` |
| `layer_trace` | `LayerTrace` | أثر الطبقات المكتملة |
| `mode` | `RepresentationMode` | نمط التمثيل |
| `format` | `RepresentationFormat` | صيغة التسلسل |
| `confidence_vector` | `tuple[float, ...]` | متجه الثقة لكل طبقة |
| `sha256` | `str` | بصمة SHA-256 حتمية للمحتوى |

### 4.2 تحويل إلى متجه عددي

كل `FractalRepresentation` قابل للاختزال إلى متجه عددي `∈ ℕ⁶`:

```
(existence, function_mask, mode_value, format_value, layer_count, sha256_prefix)
```

```python
rep.to_int_vector()
# → (0x0643, 129, 1, 1, 10, 3735928559)
```

هذا يحقق إعلان FCC-v1 §2: كل بنية في المحرك قابلة للاختزال إلى `ℕ`.

### 4.3 بصمة SHA-256

بصمة `sha256` تُحسب بصورة حتمية من `(origin, layer_trace)`:

```
sha256 = SHA256(
    str(existence) + ":" +
    prior_knowledge_key + ":" +
    str(function_mask) + ":" +
    initial_class + ":" +
    "|".join(layers) + ":" +
    final_layer + ":" +
    str(int(gate_passed))
)
```

وهي تضمن التفرّد وعدم التكرار وفق FCC-v1 §8 قيد 5.

---

## 5 — التحقق من الأصل (Origin Validation)

الدالة `validate_fractal_origin` تتحقق من الشروط الأربعة (FCC-v1 §2):

| الشرط | الخطأ عند الفشل |
|-------|----------------|
| `E(u) ∈ ℕ` | "E(u) must be a non-negative integer" |
| `K(u) ≠ ""` | "K(u) must be a non-empty string" |
| `F(u) ∈ ℕ` | "F(u) must be a non-negative integer" |
| `C(u) ≠ ""` | "C(u) must be a non-empty string" |

---

## 6 — الباني الرئيسي (Primary Builder)

```python
from arabic_engine.representation.fractal_rep_spec import (
    FractalOrigin,
    LayerTrace,
    RepresentationMode,
    RepresentationFormat,
    build_fractal_representation,
)

origin = FractalOrigin(
    existence=0x0643,
    prior_knowledge_key="U+0643",
    function_mask=0b10000001,
    initial_class="consonant",
)

trace = LayerTrace.from_sequence(
    ["SIGNAL", "MORPHOLOGY", "PHONOLOGY", "SYNTAX",
     "CONCEPT", "DALALA", "JUDGEMENT",
     "ANCHORING", "EVALUATION", "INFERENCE"],
    gate_passed=True,
)

rep = build_fractal_representation(
    element_id="U+0643",
    origin=origin,
    layer_trace=trace,
    mode=RepresentationMode.NUMERIC,
    format=RepresentationFormat.TUPLE,
    confidence_vector=(1.0, 0.95, 0.95, 0.90, 0.85, 0.80,
                       0.85, 0.90, 0.88, 0.88),
)

print(rep.to_int_vector())
print(rep.sha256)
```

---

## 7 — موقع المواصفة في المشروع (Project Position)

```
FCC-v1 (الدستور)
    │
    ├── FRS-v1 (هذه المواصفة)  ←─ arabic_engine.representation.fractal_rep_spec
    ├── KS-v1  (الكيرنل-14)    ←─ arabic_engine.core.kernel
    ├── ABL-v1 (قانون البداية) ←─ arabic_engine.core.laws
    ├── GCL-v1 (الإغلاق العام) ←─ arabic_engine.closure
    └── MFH-v1 (أنواع المفهوم) ←─ arabic_engine.cognition.mafhum
```

**القاعدة**: هذه المواصفة مشتقة من الدستور ولا ترتقي إليه.

---

## 8 — معايير القبول المحلية (Local Acceptance Criteria)

تُعدّ مواصفة التمثيل مستوفاة إذا تحقق ما يلي:

| المعيار | أسلوب التحقق |
|---------|-------------|
| `FractalOrigin` مجمّد وغير قابل للتغيير | `pytest.raises(AttributeError)` |
| `build_fractal_representation` يرفض أصلاً غير صحيح | `pytest.raises(ValueError)` |
| `to_int_vector` يُنتج tuple صحيحاً `∈ ℕ⁶` | `all(isinstance(x, int) and x >= 0 for x in rep.to_int_vector())` |
| `sha256` مختلف لعناصر مختلفة | بنائان منفصلان بأصول مختلفة |
| الوحدة قابلة للاستيراد | `import arabic_engine.representation.fractal_rep_spec` |
| اجتياز اختبارات النزاهة | `pytest -v tests/test_repository_integrity.py` |

---

## مراجع

- [`docs/fractal_core_constitution_v1.md`](fractal_core_constitution_v1.md) — الدستور الأصلي (FCC-v1)
- [`docs/kernel_schema.md`](kernel_schema.md) — مخطط الكيرنل-14
- [`docs/atomic_beginning_law.md`](atomic_beginning_law.md) — قانون البداية الذرية
- [`arabic_engine/representation/fractal_rep_spec.py`](../arabic_engine/representation/fractal_rep_spec.py) — التنفيذ البرمجي
- [`tests/test_fractal_constitution.py`](../tests/test_fractal_constitution.py) — الاختبارات
