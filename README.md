# Arabic Engine

[![CI](https://github.com/sonaiso/7-4-26-mahdi/actions/workflows/ci.yml/badge.svg)](https://github.com/sonaiso/7-4-26-mahdi/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

بنيت لك النواة التنفيذية الأولى كحزمة قابلة للتشغيل، وربطت تصميمها بالمبدأين اللذين ظهرَا في المرفقات.

> **الوثيقة الأساسية**: انظر [`docs/atomic_beginning_law.md`](docs/atomic_beginning_law.md) — إعادة بناء الوثيقة وفق قانون البداية الذرية والإغلاق الصاعد، بصيغة مرقمة صارمة (X.1 المجال — X.5 حدود الصلاحية).


الأول أن الإدراك العقلي لا يتم إلا بـ **واقع + حس + معلومات سابقة + ربط + حكم**، لا بمجرد الحس الخام. والثاني أن الألفاظ ليست موضوعة للحقيقة الخارجية مباشرة، بل للتعبير عما في الذهن، وإفادة النسب الإسنادية والتقييدية والإضافية؛ ولذلك فصلتُ في الحزمة بين **signifier** و**signified** و**linkage** و**evaluation**. كما جعلت التقييم منفصلًا عن التحليل؛ لأن الملف يفرّق بين الحكم على وجود الشيء بوصفه قطعيًا، والحكم على حقيقته أو صفته بوصفه قابلًا للخطأ.

## النسخة الثانية (v2)

تم تحويل الحزمة إلى النسخة الثانية، مع إضافة الوحدات التالية وربطها بالمشغّل `pipeline.py`:

### ما أضيف فعليًا:

* **طبقة نحو heuristic** (`syntax/syntax.py`): تعيّن الفعل/الفاعل/المفعول/ظرف الزمان/ظرف المكان.
* **تثبيت مراسي زمانية ومكانية** (`cognition/time_space.py`): من الصيغة الفعلية والظروف.
* **نموذج عالم in-memory** (`cognition/world_model.py`): يرفع أو يخفض قيمة الصدق.
* **قواعد استدلال أمامي** (`cognition/inference_rules.py`): منها اشتقاق `event_existence` وكشف التناقض.
* **عقود طبقية declarative** (`contracts.yaml`) مع تحقق آلي عند تشغيل المحرك (`core/contracts.py`).
* **تحديث الأنواع الأساسية** (`core/types.py`): لاستيعاب `case_mark`, `syntax_role`, `temporal`, `spatial`, `confidence`.

### اختبار النسخة:

```
كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ
```

وهي تمر الآن بالنحو، ثم الزمن/المكان، ثم التقييم، ثم الاستدلال، ثم تحديث نموذج العالم بنجاح.

بنية الحزمة:

* `arabic_engine/core/enums.py`
* `arabic_engine/core/types.py`
* `arabic_engine/core/contracts.py`
* `arabic_engine/signifier/unicode_norm.py`
* `arabic_engine/signifier/phonology.py`
* `arabic_engine/signifier/root_pattern.py`
* `arabic_engine/signified/ontology.py`
* `arabic_engine/linkage/dalala.py`
* `arabic_engine/syntax/syntax.py`
* `arabic_engine/cognition/evaluation.py`
* `arabic_engine/cognition/time_space.py`
* `arabic_engine/cognition/world_model.py`
* `arabic_engine/cognition/inference_rules.py`
* `arabic_engine/contracts.yaml`
* `arabic_engine/pipeline.py`
* `example_run.py`

## برهان أن الخوارزمية تبني اللغة وفق حساب رقمي

### الدعوى

الخوارزمية التي صغناها:

`Normalize → Signifier Graph → Lexical Closure → Ontological Mapping → Dalāla Validation → Judgment → Evaluation → Guidance/Action`

هي **خوارزمية رقمية** بالمعنى الصارم؛ لأن كل مرحلة فيها قابلة للترميز على أعداد صحيحة، وكل انتقال فيها دالة حاسوبية أو علاقة قابلة للحساب.

### التعريف 1

ليكن النص العربي الخام سلسلة:
[
x \in \Sigma_U^*
]
حيث (\Sigma_U) مجموعة محارف Unicode العربية.

وبما أن كل محرف Unicode له code point عددي، فهناك ترميز حقني:
[
enc: \Sigma_U \to \mathbb{N}
]
ومن ثم:
[
enc^*: \Sigma_U^* \to \mathbb{N}^*
]

إذن النص الخام نفسه صار **كائنًا رقميًا**.

### التعريف 2

التطبيع `Normalize` هو دالة:
[
N: \mathbb{N}^* \to \mathbb{N}^*
]
تزيل التطويل، وتوحد المسافات، وتحفظ/تجرد العلامات وفق سياسة محددة.
وهذه دالة حتمية منتهية الخطوات، فهي قابلة للحساب.

### التعريف 3

بناء الدال الأدنى:

* العنقود الكتابي
* الصامت/الصائت
* المقطع
* الجذر
* الوزن

كل واحد منها لا يُمثَّل لفظيًا فقط، بل كـ tuple عددي. مثلًا:

[
g = (b, m_1, m_2, \dots, m_k)
]
حيث (b) رمز الأساس و(m_i) علامات تابعة.
والمقطع:
[
s = (\text{onset}, \text{nucleus}, \text{coda}, \text{weight})
]
والوزن:
[
w = (C/V\ pattern,\ slots,\ class)
]

إذن الدال لا يبقى وصفًا لغويًا، بل يدخل في **فضاء متجهات/أزواج منضبطة**.

### التعريف 4

الإغلاق المعجمي `Lexical Closure` هو دالة جزئية:
[
L: \mathbb{N}^* \to T
]
حيث (T) فضاء tuples من الشكل:
[
t = (\text{lemma_id}, \text{root_id}, \text{pattern_id}, \text{pos_id}, \text{feature_vector})
]

فالكلمة هنا لا تُعالج كسلسلة حروف فقط، بل كحزمة خصائص رقمية.

### التعريف 5

الربط الأنطولوجي `Ontological Mapping` هو دالة:
[
O: T \to C
]
حيث (C) مجموعة العقد المفهومية المرقمة:

* entity
* event
* attribute
* relation
* norm

أي:
[
c = (\text{concept_id}, \text{semantic_type_id}, \text{property_vector})
]

### التعريف 6

الربط الدلالي `Dalāla Validation` هو علاقة قابلة للحساب:
[
D: T \times C \to {0,1} \times [0,1]
]
فتعطي:

* قبول/رفض
* ودرجة ثقة

وهذا بالضبط ما يحقق المطابقة والتضمن والالتزام والإسناد والتقييد والإحالة بوصفها **علاقات محددة القيم**، لا حدسًا إنشائيًا. والمرفق اللغوي نفسه يحصر دلالات اللفظ من جهة الدال في المطابقة والتضمن والالتزام، ويجعل المنطوق والمفهوم مبنيين على هذا التقسيم.

### التعريف 7

بناء الحكم `Judgment` هو دالة:
[
J: G_s \times G_m \times D \to P
]
حيث:

* (G_s): graph الدال
* (G_m): graph المدلول
* (P): proposition vector

مثل:
[
p = (\text{subject}, \text{predicate}, \text{object}, \text{time}, \text{space}, \text{polarity})
]

### التعريف 8

التقييم `Evaluation` هو دالة:
[
E: P \times W \to V
]
حيث (W) حالة العالم، و(V) متجه تقويمي مثل:
[
v = (\text{truth_state}, \text{guidance_state}, \text{confidence})
]

وهنا يلتقي البناء مع المرفق: الحكم على وجود الشيء قد يكون قطعيًا، أما الحكم على حقيقته أو صفته فظني قابل للمراجعة؛ وهذا يعني أن التقييم نفسه ليس جملة بل **قيمة عددية/رتبية قابلة للنمذجة**.

### المبرهنة

إذا كانت:

* (N) قابلة للحساب
* (S) بناء الدال قابلة للحساب
* (L) الإغلاق المعجمي قابلة للحساب
* (O) المطابقة الأنطولوجية قابلة للحساب
* (D) التحقق الدلالي قابلة للحساب
* (J) تركيب الحكم قابلة للحساب
* (E) التقييم قابلة للحساب

فإن التركيب:
[
F = E \circ J \circ D \circ O \circ L \circ S \circ N
]
قابل للحساب.

### البرهان

فضاءات الإدخال والإخراج في كل مرحلة إما:

* سلاسل منتهية على أبجدية منتهية
* أو tuples عددية
* أو رسومًا بيانية محدودة العقد والحواف
* أو قيمًا من مجموعات منتهية أو معدودة

وكل مرحلة معرفة بقواعد حتمية أو قيود فحص منتهية.
والدوال القابلة للحساب مغلقة تحت التركيب.
إذًا (F) قابلة للحساب.
فثبت أن الخوارزمية تبني العربية هنا بوصفها **بنية رقمية محسوبة**.

## النتيجة الدقيقة

إذن “اللغة” في هذا المحرك ليست بناءً غائمًا، بل:

1. **الدال** ممثل رقميًا
2. **المدلول** ممثل رقميًا
3. **الرابطة بينهما** ممثلة رقميًا
4. **الحكم** ممثل رقميًا
5. **التقويم** ممثل رقميًا
6. **التوجيه** ممثل رقميًا

فإذا قلت: “هذه الخوارزمية تبني اللغة وفق حساب رقمي” فالمعنى الدقيق هو:

> كل طبقة من طبقات العربية في هذا النظام تتحول إلى بنية متقطعة قابلة للترميز العددي، وتنتقل إلى الطبقة التالية عبر دوال أو علاقات منضبطة، بحيث يكون البناء الكلي تركيبًا حاسوبيًا لا مجازًا لفظيًا.

والذي يجعل هذا موافقًا للمرفقات أن العقل نفسه عُرّف فيها كعملية ربطٍ تفسيري تنتج حكمًا، وأن اللفظ فيها ليس مرآةً للواقع مباشرة بل أداة تعبير عما في الذهن وإفادة النسب، لا مجرد تسمية. لذلك كان فصل `signifier / signified / linkage / judgment / evaluation` لازمًا لا اختياريًا.

الخطوة التالية الصحيحة هي أن أحوّل هذه الحزمة إلى **النسخة الثانية** بإضافة:

* `syntax.py`
* `time_space.py`
* `world_model.py`
* `inference_rules.py`
* وملف `contracts.yaml` لإثبات الإغلاق الطبقي آليًا.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sonaiso/7-4-26-mahdi.git
cd 7-4-26-mahdi

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run the example
python example_run.py

# Run the tests
pytest -v

# Lint the code
ruff check .
```

## Repository Maintenance: Branch PR Merge Automation

The script `scripts/branch_pr_merge.sh` automates:

- syncing feature branches from `origin`
- creating/opening PRs to a base branch
- merging PRs with a selected strategy

This is a repository-maintenance utility and is not part of the `arabic_engine` runtime package.

### Requirements

- `git` installed
- `gh` (GitHub CLI) installed and authenticated (`gh auth login`)
- repository write permissions for PR creation/merge
- clean working tree before execution

### Recommended safe workflow

Always run a dry run first:

```bash
./scripts/branch_pr_merge.sh \
  --base-branch main \
  --branches feature/branch-1,feature/branch-2 \
  --merge-method rebase \
  --auto-merge false \
  --delete-branch false \
  --dry-run
```

Then execute for real:

```bash
./scripts/branch_pr_merge.sh \
  --base-branch main \
  --branch feature/branch-1 \
  --branch feature/branch-2 \
  --merge-method rebase \
  --auto-merge false \
  --delete-branch false
```

### Key safety controls

- `--merge-method` only allows `merge|rebase|squash`
- branch list is required (`--branch`/`--branches` or `BRANCHES` env)
- boolean flags are validated case-insensitively (`true/false/yes/no/1/0/on/off`)
- script continues branch-by-branch on failures and exits non-zero if any branch fails
- prints a machine-readable JSON summary at the end

### Warning

`--delete-branch true` deletes merged branches on remote. Keep it `false` unless deletion is explicitly intended.

## System Integrity Verification

To keep the engine integrated and prevent duplicated repository content:

```bash
# Full validation suite (includes architecture + integrity tests)
pytest -v

# Focused repository integrity checks
pytest -v tests/test_repository_integrity.py
```

The integrity checks validate that critical engine modules are importable and
that there are no duplicated file contents inside `arabic_engine/`, `tests/`,
`docs/`, and `db/`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
