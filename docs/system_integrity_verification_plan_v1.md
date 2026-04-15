# خطة التحقق من سلامة النظام — الإصدار الأول

# System Integrity Verification Plan v1

> **وثيقة تشغيلية** — مشتقة من دستور أهداف المشروع ومقاصده البرهانية
> ([`PGPO-v1`](project_goals_and_proof_objectives_constitution_v1.md))
> ومن الدستور الفراكتالي الأصلي ([`FCC-v1`](fractal_core_constitution_v1.md)).
>
> هذه الوثيقة تحوّل المبادئ الدستورية إلى معايير قبول قابلة للتنفيذ والاختبار.
> أي تعارض بينها وبين الدستور الأعلى يُحسم لصالح الدستور.

**الرقم المرجعي**: `SIVP-v1`

**المرحلة**: Verification Phase — لا Feature Phase

---

## فهرس المحتويات

1. [المبدأ التوجيهي](#المبدأ-التوجيهي)
2. [الأولويات الثلاث العليا](#الأولويات-الثلاث-العليا)
3. [الحزمة A: منع القفز والتحقق من الحدود](#الحزمة-a-منع-القفز-والتحقق-من-الحدود)
4. [الحزمة B: سلامة الأثر وإعادة التتبع](#الحزمة-b-سلامة-الأثر-وإعادة-التتبع)
5. [الحزمة C: اتساق التعريفات والتصنيفات](#الحزمة-c-اتساق-التعريفات-والتصنيفات)
6. [المستويات اللاحقة](#المستويات-اللاحقة)
7. [الربط بالوحدات البرمجية القائمة](#الربط-بالوحدات-البرمجية-القائمة)
8. [نموذج القبول النهائي للمرحلة](#نموذج-القبول-النهائي-للمرحلة)
9. [قائمة التحقق التشغيلية](#قائمة-التحقق-التشغيلية)

---

## المبدأ التوجيهي

المرحلة الحالية ليست مرحلة إضافة مزايا، بل مرحلة **تحقق صارم من صحة السلسلة
كلها**، حتى لا يتحول المشروع إلى وحدات ناجحة محليًا لكنها مفككة كليًا.

قيمة الاختبار مشروطة بموضعه داخل السلسلة (المادة 20–24 من `PGPO-v1`).
النجاح المحلي لا يكفي إذا لم يثبت موضعه ضمن الهيكلة الفراكتالية المترابطة
(المادة 15 من `PGPO-v1`).

---

## الأولويات الثلاث العليا

| الرتبة | الأولوية | ما يحفظ | المرجع الدستوري |
|--------|----------|---------|-----------------|
| 1 | منع القفز والتحقق من الحدود | **السلسلة** | المواد 16–19 |
| 2 | سلامة الأثر وإعادة التتبع | **البرهان** | المواد 25–27 |
| 3 | اتساق التعريفات والتصنيفات | **وحدة العقل الدلالي** | المواد 12–15 |

**لماذا هذه الثلاثة أولًا؟**

لأنها حراس البنية الفراكتالية كلها. بدونها يكون عندنا كود يعمل، واختبارات تمر،
وAPI تستجيب — لكن لا يوجد مشروع واحد متماسك. كل تحسين لاحق (نظافة برمجية،
جاهزية إنتاجية، أمان، أداء) يبقى هشًا ما لم تثبت هذه الثلاثة أولًا.

---

## الحزمة A: منع القفز والتحقق من الحدود

### Boundary & Gate Enforcement

**المرجع الدستوري**: الباب الخامس — قانون السلسلة والانتقال (المواد 16–19)

### النطاق

| البند | الوصف |
|-------|-------|
| Contract enforcement | فرض عقود الطبقات داخل التنفيذ الفعلي |
| منع القفز برمجيًا | كل قفز بين طبقات غير متجاورة يفشل برمجيًا |
| Boundary gate suites | اختبارات حدود بين كل طبقتين متجاورتين |
| Unified state model | توحيد حالات القرار في كل الطبقات |

### الأصول البرمجية القائمة

| المكوّن | الملف | الحالة |
|---------|-------|--------|
| `evaluate_gate()` | `cognitive_input/gate.py` | ✅ مطبّق ومختبر |
| `is_valid_transition()` | `cognitive_input/gate.py` | ✅ مطبّق ومختبر |
| `detect_jump_violations()` | `cognitive_input/gate.py` | ✅ مطبّق ومختبر |
| `CognitiveGateRecord` | `core/types.py` | ✅ معرّف |
| `LayerGateDecision` | `core/enums.py` | ✅ `PASS/REJECT/SUSPEND/COMPLETE` |
| `TransitionGateStatus` | `core/enums.py` | ✅ `PASSED/BLOCKED/INSUFFICIENT_DATA` |
| `contracts.yaml` | الجذر | ✅ 25 عقد طبقي |
| `verify_contracts()` | `core/contracts.py` | ⚠️ يتحقق من الاستيراد فقط |
| اختبارات البوابات | `tests/test_cognitive_input.py` | ✅ 57 اختبار |

### الفجوات المحددة

1. **`pipeline.py` لا يستخدم البوابات**: السلسلة الرئيسية `run()` تستدعي الطبقات
   تتابعيًا دون فحص بوابة عند كل حد.
2. **عقود الأنواع لا تُفرض وقت التنفيذ**: `contracts.yaml` يصرّح بالأنواع لكن
   `verify_contracts()` لا يتحقق من مطابقة الأنواع الفعلية.
3. **حالات القرار غير موحّدة بين الأنابيب**: `pipeline.py` يعيد `PipelineResult`
   بدون حالة `SUCCESS/SUSPEND/FAILURE`؛ بينما `cognitive_input/chain.py` يستخدم
   `LayerGateDecision`.

### معايير القبول

- [ ] **A1**: لا انتقال بين طبقتين في `pipeline.run()` إلا عبر gate صريح
- [ ] **A2**: كل طبقة ترجع واحدة من: `SUCCESS / SUSPEND / FAILURE`
- [ ] **A3**: كل boundary test يثبت: input contract, output contract,
  completeness threshold, blocker behavior
- [ ] **A4**: أي jump يفشل **برمجيًا** لا توثيقيًا فقط
- [ ] **A5**: `verify_contracts()` يتحقق من مطابقة الأنواع الفعلية لعقود الطبقات
- [ ] **A6**: `PipelineResult` يتضمن حالة موحدة وسجل بوابات

---

## الحزمة B: سلامة الأثر وإعادة التتبع

### Trace & Replay Integrity

**المرجع الدستوري**: الباب السابع — حفظ الأثر (المواد 25–27)

### النطاق

| البند | الوصف |
|-------|-------|
| Trace integrity | سلامة سجل الأثر لكل طبقة |
| Replayability | إعادة تشغيل جلسة من سجلها فقط |
| Reproducibility | المدخل نفسه → المخرج نفسه |
| Suspend/failure reasoning | تفسير معلل لكل تعليق أو فشل |

### الأصول البرمجية القائمة

| المكوّن | الملف | الحالة |
|---------|-------|--------|
| `LayerTraceRecord` | `core/types.py` | ✅ سجل 7 طبقات + بوابات |
| `TraceEntry` | `runtime_pipeline.py` | ✅ سجل المرحلة |
| `PerceptTrace` | `core/types.py` | ✅ أثر الإدراك |
| `KnowledgeEpisode` | `core/types.py` | ✅ الحلقة المعرفية الكاملة |
| `CognitiveChainResult` | `cognitive_input/chain.py` | ✅ نتيجة السلسلة المعرفية |
| `SignalState/HypothesisState/DecisionState` | `core/trace.py` | ✅ حالات ثلاثية |
| اختبارات الأثر | `tests/test_trace.py` | ✅ موجودة |

### الفجوات المحددة

1. **أنظمة أثر متعددة غير موحّدة**: يوجد `LayerTraceRecord` و`TraceEntry`
   و`PerceptTrace` و`KnowledgeEpisode` — ولا يوجد نموذج أثر موحّد يجمعها.
2. **لا توجد آلية إعادة تشغيل**: لا يمكن إعادة تنفيذ جلسة من سجل الأثر وحده.
3. **لا يوجد hash للمدخلات**: سجلات الأثر لا تحفظ hash للمدخل لأغراض التحقق
   من إعادة الإنتاج.
4. **التفسير المعلل جزئي**: `explanation` موجود لكنه لا يغطي كل حالات التعليق
   والفشل بنحو منتظم.

### معايير القبول

- [ ] **B1**: كل طبقة تسجل: input hash, output summary, rules applied,
  confidence/completeness, state, timestamp
- [ ] **B2**: يمكن إعادة تشغيل session واحدة من trace فقط
- [ ] **B3**: يمكن ردّ أي حكم إلى طبقاته الأدنى عبر سلسلة أثر متصلة
- [ ] **B4**: لا توجد نتيجة نهائية بلا trace chain كاملة
- [ ] **B5**: كل تعليق أو فشل مصحوب بتفسير معلل (reason + evidence)
- [ ] **B6**: `PipelineResult` يتضمن سلسلة أثر موحّدة

---

## الحزمة C: اتساق التعريفات والتصنيفات

### Domain Consistency Audit

**المرجع الدستوري**: الباب الرابع — البنية الفراكتالية (المواد 12–15)

### النطاق

| البند | الوصف |
|-------|-------|
| Domain taxonomy consistency | اتساق التصنيفات المجالية |
| Knowledge/schema integrity | سلامة المخططات والمعرفة |
| Duplicate logic detection | كشف المنطق المكرر |
| Package structure integrity | سلامة بنية الحزم |

### الأصول البرمجية القائمة

| المكوّن | الملف | الحالة |
|---------|-------|--------|
| `verify_general_closure()` | `closure.py` | ✅ 14 حكم إغلاق |
| اختبارات البنية | `tests/test_architecture_guard.py` | ✅ حراسة المعمارية |
| اختبارات السلامة | `tests/test_repository_integrity.py` | ✅ استيراد + تكرار |
| `core/enums.py` | الأنواع المركزية | ✅ تعدادات موحدة |
| `core/types.py` | الأنواع المركزية | ✅ أنواع بيانات موحدة |
| `contracts.yaml` | عقود الطبقات | ✅ 25 عقد |

### الفجوات المحددة

1. **حالات قرار متعددة**: `LayerGateDecision` (4 حالات)، `TransitionGateStatus`
   (3 حالات)، `ValidationState` (3 حالات) — تؤدي وظائف متقاطعة.
2. **أنظمة أنابيب متوازية**: `pipeline.py` (11 طبقة)، `runtime_pipeline.py`
   (8 مراحل)، `cognitive_input/chain.py` (9 طبقات) — ثلاث سلاسل بمصطلحات
   مختلفة.
3. **`verify_general_closure()` لا يُستدعى تلقائيًا**: الإغلاق العام يُفحص في
   الاختبارات فقط، لا عند التشغيل.
4. **عدم ربط contracts.yaml بالاختبارات الحدّية**: العقود مصرّحة لكن لا يوجد
   اختبار يتحقق من كل invariant مصرّح.

### معايير القبول

- [ ] **C1**: كل مفهوم domain له تعريف واحد معتمد في `core/enums.py`
  أو `core/types.py`
- [ ] **C2**: كل enum/type/schema مرتبط بمرجع واحد لا بعدة نماذج متنافسة
- [ ] **C3**: لا منطق مكرر في أكثر من package بلا تبرير موثّق
- [ ] **C4**: لا يوجد اسم واحد بمعنيين مختلفين في الكود
- [ ] **C5**: لا يوجد معنًى واحد ممثلًا بنماذج متنافرة
- [ ] **C6**: كل invariant مصرّح في `contracts.yaml` مغطّى باختبار حدّي

---

## المستويات اللاحقة

تُنفّذ بعد إتمام الحزم الثلاث الأولى:

### المستوى الرابع: التحقق من الحالات المعلّقة

| البند | المعيار |
|-------|---------|
| Suspend/ambiguous-state validation | كل حالة تعليق موثّقة ومبررة |
| Unified state model refinement | نموذج حالة واحد يغطي كل الأنابيب |
| Reproducibility checks | المدخل نفسه → المخرج نفسه دائمًا |

### المستوى الخامس: الصيانة ونظافة الكود

| البند | المعيار |
|-------|---------|
| Maintainability audits | مؤشرات التعقيد والقراءة |
| Duplicate logic removal | إزالة أو تبرير كل تكرار |
| Package structure refinement | تحسين بنية الحزم |

### المستوى السادس: الأمان والمتانة

| البند | المعيار |
|-------|---------|
| Security checks | لا ثغرات في المدخلات والمخرجات |
| Robustness checks | معالجة الحالات الحدية والأخطاء |
| Production readiness | جاهزية التشغيل الإنتاجي |

### المستوى السابع: اتساق التوثيق

| البند | المعيار |
|-------|---------|
| Docs-to-code consistency | كل وثيقة لها أثر في الكود |
| Knowledge/schema expansion | توسعة المعرفة والمخططات |

---

## الربط بالوحدات البرمجية القائمة

| المعيار | الوحدة البرمجية المسؤولة | الاختبار |
|---------|-------------------------|----------|
| A1: Gate في pipeline | `pipeline.py` + `cognitive_input/gate.py` | `test_pipeline` |
| A2: حالة موحدة | `core/enums.py` (`LayerGateDecision`) | `test_cognitive_input` |
| A3: اختبارات حدود | `contracts.yaml` | `test_contracts` + جديد |
| A4: منع القفز | `cognitive_input/gate.py` | `test_cognitive_input` |
| A5: فرض العقود | `core/contracts.py` | `test_contracts` |
| A6: PipelineResult + gates | `pipeline.py` | `test_pipeline` |
| B1: أثر مفصّل | `core/types.py` (`LayerTraceRecord`) | `test_trace` |
| B2: إعادة التشغيل | جديد | جديد |
| B3: ردّ الحكم | `pipeline.py` + trace | `test_pipeline` |
| B4: trace chain | `pipeline.py` | `test_pipeline` |
| B5: تفسير معلل | `cognition/explanation.py` | `test_evaluation` |
| B6: أثر موحّد | `pipeline.py` | `test_pipeline` |
| C1: تعريف واحد | `core/enums.py` + `core/types.py` | `test_core` |
| C2: مرجع واحد | `core/` | `test_repository_integrity` |
| C3: لا تكرار | كل الحزم | `test_repository_integrity` |
| C4: لا تضارب أسماء | كل الحزم | `test_architecture_guard` |
| C5: لا نماذج متنافرة | `core/enums.py` | `test_core` |
| C6: invariants مغطاة | `contracts.yaml` | `test_contracts` + جديد |

---

## نموذج القبول النهائي للمرحلة

**لا تُعتبر المرحلة الحالية ناجحة إلا إذا تحقق ما يلي:**

### الحزمة A — الحدود والبوابات

- [ ] كل طبقة لا تعمل خارج boundary contract
- [ ] كل انتقال يمر عبر gate قابل للاختبار
- [ ] كل gate يُرجع `SUCCESS / SUSPEND / FAILURE` بنحو موحّد
- [ ] أي قفز طبقي يفشل برمجيًا ويُسجّل في الأثر

### الحزمة B — الأثر وإعادة التتبع

- [ ] كل مخرج له trace كامل من المدخل إلى الناتج
- [ ] كل trace قابل لإعادة التشغيل
- [ ] كل تعليق أو فشل مصحوب بتفسير معلل
- [ ] لا نتيجة نهائية بلا سلسلة أثر متصلة

### الحزمة C — اتساق المجال

- [ ] كل تعريف domainي له مرجع واحد
- [ ] كل تكرار منطقي إما أُزيل أو بُرر
- [ ] كل وثيقة عليا لها أثر فعلي في الكود والاختبارات
- [ ] كل state موحّد عبر كل الأنابيب

---

## قائمة التحقق التشغيلية

### الأولوية 1 — منع القفز والتحقق من الحدود

- [ ] ربط `evaluate_gate()` بسلسلة `pipeline.run()` عند كل حد طبقي
- [ ] إضافة فحص `is_valid_transition()` قبل كل استدعاء طبقة في `pipeline.run()`
- [ ] توحيد حالات القرار بين `pipeline.py` و`runtime_pipeline.py`
  و`cognitive_input/chain.py`
- [ ] إضافة اختبارات حدّية (boundary tests) لكل زوج طبقات متجاور في
  `contracts.yaml`
- [ ] تفعيل فحص الأنواع الفعلية في `verify_contracts()` بدلًا من فحص الاستيراد
  فقط
- [ ] إضافة حقل `gate_records` إلى `PipelineResult`

### الأولوية 2 — سلامة الأثر وإعادة التتبع

- [ ] إضافة `input_hash` و`timestamp` إلى `LayerTraceRecord` أو نموذج أثر موحّد
- [ ] توحيد `LayerTraceRecord` و`TraceEntry` و`PerceptTrace` في نموذج أثر واحد
  أو ربطها بواجهة مشتركة
- [ ] بناء دالة `replay_from_trace()` تعيد تنفيذ جلسة من سجلها
- [ ] التأكد من أن كل `SUSPEND` و`FAILURE` يحمل `reason` و`evidence`
- [ ] إضافة اختبار تحقق من إعادة الإنتاج (reproducibility): نفس المدخل →
  نفس المخرج → نفس الأثر

### الأولوية 3 — اتساق التعريفات والتصنيفات

- [ ] إجراء مسح للتعدادات المتقاطعة (`LayerGateDecision` vs
  `TransitionGateStatus` vs `ValidationState`) وتوحيدها أو توثيق الفرق
- [ ] توثيق العلاقة بين الأنابيب الثلاث (`pipeline.py`, `runtime_pipeline.py`,
  `cognitive_input/chain.py`) وتحديد أيها المرجعي
- [ ] إضافة اختبار يتحقق من أن كل invariant في `contracts.yaml` مُغطّى باختبار
- [ ] تفعيل `verify_general_closure()` كجزء من CI أو كاختبار إلزامي

---

## الوثائق ذات الصلة

| الوثيقة | المرجع |
|---------|--------|
| دستور أهداف المشروع | [`PGPO-v1`](project_goals_and_proof_objectives_constitution_v1.md) |
| الدستور الفراكتالي | [`FCC-v1`](fractal_core_constitution_v1.md) |
| إثبات اليونيكود | [`Proof v1`](unicode_cognitive_input_proof_v1.md) |
| الإغلاق العام | [`Ch. 19`](chapter_19_general_closure.md) |
| المعمارية | [`architecture`](architecture.md) |
| عقود الطبقات | `contracts.yaml` |

---

*نهاية الوثيقة — `SIVP-v1`*
