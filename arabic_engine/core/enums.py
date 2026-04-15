"""Enumerations used across the Arabic engine.

Each enum encodes a discrete, finite category so that every linguistic
label in the system is a computable integer — not a free-form string.
"""

from __future__ import annotations

from enum import Enum, auto

# ── Part of Speech ──────────────────────────────────────────────────


class POS(Enum):
    """Arabic part-of-speech tags (اسم / فعل / حرف + sub-types)."""

    ISM = auto()  # اسم
    FI3L = auto()  # فعل
    HARF = auto()  # حرف
    SIFA = auto()  # صفة
    ZARF = auto()  # ظرف
    DAMIR = auto()  # ضمير
    MASDAR_SARIH = auto()  # مصدر صريح
    MASDAR_MUAWWAL = auto()  # مصدر مؤوّل
    UNKNOWN = auto()


# ── Semantic (ontological) type ─────────────────────────────────────


class SemanticType(Enum):
    """High-level concept categories (التعريف 5 — ontological mapping)."""

    ENTITY = auto()  # ذات
    EVENT = auto()  # حدث
    ATTRIBUTE = auto()  # صفة
    RELATION = auto()  # علاقة
    NORM = auto()  # حكم شرعي / قاعدة
    NOMINALIZED_EVENT = auto()  # حدث مصدري — nominalized event (masdar)
    EVENT_CONCEPT = auto()  # مفهوم حدثي مجرد — abstract event concept


# ── Dalāla (signification) type ─────────────────────────────────────


class DalalaType(Enum):
    """Kinds of signification linking signifier → signified."""

    MUTABAQA = auto()  # مطابقة – exact denotation
    TADAMMUN = auto()  # تضمن  – inclusion (part of meaning)
    ILTIZAM = auto()  # التزام – implication (necessary concomitant)
    ISNAD = auto()  # إسناد – predication
    TAQYID = auto()  # تقييد – restriction / qualification
    IDAFA = auto()  # إضافة – genitive construction
    IHALA = auto()  # إحالة – referential link
    MASDAR_BRIDGE = auto()  # جسر مصدري – masdar bridge (existential ↔ transformational)


# ── Truth state ─────────────────────────────────────────────────────


class TruthState(Enum):
    """Epistemic status of a proposition (التعريف 8)."""

    CERTAIN = auto()  # قطعي
    PROBABLE = auto()  # ظني راجح
    POSSIBLE = auto()  # ممكن
    DOUBTFUL = auto()  # مشكوك
    FALSE = auto()  # باطل
    UNKNOWN = auto()


# ── Guidance state ──────────────────────────────────────────────────


class GuidanceState(Enum):
    """Normative/actionable status derived from evaluation."""

    OBLIGATORY = auto()  # واجب
    RECOMMENDED = auto()  # مستحب
    PERMISSIBLE = auto()  # مباح
    DISLIKED = auto()  # مكروه
    FORBIDDEN = auto()  # حرام
    NOT_APPLICABLE = auto()


# ── I'rāb (syntactic inflection) ────────────────────────────────────


class IrabCase(Enum):
    """Grammatical case markers."""

    RAF3 = auto()  # رفع
    NASB = auto()  # نصب
    JARR = auto()  # جر
    JAZM = auto()  # جزم
    SUKUN = auto()  # سكون (مبني)
    UNKNOWN = auto()


class IrabRole(Enum):
    """Syntactic role in the sentence."""

    FA3IL = auto()  # فاعل
    MAF3UL_BIH = auto()  # مفعول به
    MUBTADA = auto()  # مبتدأ
    KHABAR = auto()  # خبر
    FI3L = auto()  # فعل
    MUDAF = auto()  # مضاف
    MUDAF_ILAYH = auto()  # مضاف إليه
    SIFA = auto()  # صفة
    HAL = auto()  # حال
    TAMYIZ = auto()  # تمييز
    ZARF = auto()  # ظرف
    JARR_MAJRUR = auto()  # جار ومجرور
    UNKNOWN = auto()


# ── Time / Space references (v2) ────────────────────────────────────


class TimeRef(Enum):
    """Temporal anchors for propositions."""

    PAST = auto()  # ماض
    PRESENT = auto()  # حاضر
    FUTURE = auto()  # مستقبل
    ETERNAL = auto()  # أزلي / دائم
    MASDAR_POTENTIAL = auto()  # إمكان زمني مصدري — masdar temporal potential
    UNSPECIFIED = auto()


class SpaceRef(Enum):
    """Spatial anchors for propositions."""

    HERE = auto()  # هنا
    THERE = auto()  # هناك
    NAMED = auto()  # مكان محدد بالاسم
    MASDAR_POTENTIAL = auto()  # إمكان مكاني مصدري — masdar spatial potential
    UNSPECIFIED = auto()


# ── Mafhūm types (Ch. 21) ───────────────────────────────────────────


class ConstraintType(Enum):
    """Structural constraint types in the Manṭūq (أنواع القيد البنيوي).

    Each constraint type generates a corresponding Mafhūm type when
    combined with a mental counterpart and a transition rule.
    """

    SHART = auto()  # شرط — condition (تعليق الحكم)
    GHAYA = auto()  # غاية — goal / endpoint (تحديد المنتهى)
    ADAD = auto()  # عدد — number (التحديد الكمي)
    WASF = auto()  # وصف — description (التقييد الوصفي)
    ISHARA = auto()  # إشارة — reference / deixis (التخصيص الإحالي)


class MafhumType(Enum):
    """Minimal types of Mafhūm (الأنواع الدنيا للمفهوم — Ch. 21).

    These are the five irreducible concept types that arise from the
    structure of the Manṭūq itself, each covering an independent domain:
      • SHART  — domain of suspension (تعليق)
      • GHAYA  — domain of limit / endpoint (حد ومنتهى)
      • ADAD   — domain of quantitative restriction (تحديد كمي)
      • WASF   — domain of qualitative restriction (تقييد نوعي)
      • ISHARA — domain of referential specification (تخصيص مرجعي)
    """

    SHART = auto()  # مفهوم الشرط
    GHAYA = auto()  # مفهوم الغاية
    ADAD = auto()  # مفهوم العدد
    WASF = auto()  # مفهوم الوصف
    ISHARA = auto()  # مفهوم الإشارة


# ── D_min Phonological layer ─────────────────────────────────────────
# Implements: D_min(x) = (u, c, g, f, t)
# where every field maps to a computable integer, making the full
# 5-tuple a numeric vector over ℕ⁵.


class PhonCategory(Enum):
    """Major phonological category — الفئة الكبرى (c in D_min)."""

    CONSONANT = auto()  # صامت
    SEMI_VOWEL = auto()  # شبه صامت / صائت ذو تحولات (و ي)
    LONG_VOWEL = auto()  # صائت طويل / حامل كتابي (ا)
    SHORT_VOWEL = auto()  # صائت قصير (فتحة ضمة كسرة)
    SUKUN = auto()  # علامة انعدام حركة (ْ)
    SHADDA = auto()  # علامة بنيوية / تضعيف (ّ)
    TANWIN = auto()  # حركة/علامة مركبة / تنوين (ً ٌ ٍ)
    SPECIAL_MARK = auto()  # علامة مدّ/همز خاصة (ٰ ٓ)


class PhonGroup(Enum):
    """Phonological/articulatory group — المجموعة الكبرى (g in D_min)."""

    # ── Consonant articulation groups (مجموعات الصوامت) ────────────
    HNJ_MZM = auto()  # حنجري/مزمَري — ء
    HNJ_HLQ = auto()  # حنجري/حلقي   — ه
    HLQ = auto()  # حلقي          — ح ع غ
    HLQ_LHW = auto()  # حلقي/لهوي     — خ
    LHW = auto()  # لهوي          — ق
    TBQ_LHW = auto()  # طبقي/لهوي     — ك
    SHJR = auto()  # شجري/حنكي     — ج ش
    ASN_LTH = auto()  # أسناني-لثوي   — ت د
    ASN_LTH_MTPQ = auto()  # أسناني-لثوي مطبق — ط
    BAYNASN = auto()  # بين-أسناني    — ث ذ
    BAYNASN_MTPQ = auto()  # بين-أسناني مطبق — ظ
    LTH = auto()  # لثوي          — ر ل ن (with feature distinctions)
    LTH_MTPQ = auto()  # لثوي مطبق     — ض
    ASLI = auto()  # أسلي/صفيري    — ز س
    ASLI_MTPQ = auto()  # أسلي مطبق     — ص
    SHF = auto()  # شفوي          — ب م (with feature distinctions)
    SHF_ASN = auto()  # شفوي-أسناني   — ف
    SHF_LYN = auto()  # شفوي لين      — و (semi-vowel)
    HNK_LYN = auto()  # حنكي لين      — ي (semi-vowel)
    # ── Long vowel (الصوائت الطويلة) ──────────────────────────────
    ALF_LV = auto()  # ألف           — ا
    # ── Short vowel / diacritic groups (الحركات والعلامات) ─────────
    FTH = auto()  # فتح           — َ (U+064E)
    DMM = auto()  # ضم            — ُ (U+064F)
    KSR = auto()  # كسر           — ِ (U+0650)
    SKN_GRP = auto()  # سكون          — ْ (U+0652)
    SHD_GRP = auto()  # شدة           — ّ (U+0651)
    TAN_FTH = auto()  # تنوين فتح     — ً (U+064B)
    TAN_DMM = auto()  # تنوين ضم      — ٌ (U+064C)
    TAN_KSR = auto()  # تنوين كسر     — ٍ (U+064D)
    ALF_KHNJ = auto()  # ألف خنجرية    — ٰ (U+0670)
    MDD_GRP = auto()  # مدة           — ٓ (U+0653)


class PhonFeature(Enum):
    """Minimal phonological features — السمات الدنيا (f in D_min).

    Each value is a unique power-of-two bit-position, enabling a compact
    integer bitmask: feature_mask = Σ 2^(f.value-1) for f in features.
    """

    # Manner of articulation (طريقة النطق)
    SHADID = auto()  # شديد   — stop / plosive
    RAKHW = auto()  # رخو    — fricative / continuant
    MURAKKAB = auto()  # مركب   — affricate
    MUTAWASSIT = auto()  # متوسط  — intermediate manner
    TAKRIR = auto()  # مكرر   — trill / vibrant
    MUNHARIF = auto()  # منحرف  — lateral
    TAFSHI = auto()  # تفشٍّ  — diffuse / spread
    # Voicing (الجهر والهمس)
    MAJHUR = auto()  # مجهور  — voiced
    MAHMOUS = auto()  # مهموس  — voiceless
    # Secondary articulation (الصفات الثانوية)
    ITBAQ = auto()  # مطبق   — pharyngealization / emphatic
    MSTALI = auto()  # مستعلٍ — dorsal elevation
    SAFIR = auto()  # صفيري  — sibilant / whistling
    ANFI = auto()  # أنفي   — nasal
    GHUNNA = auto()  # غنّي   — nasality / resonance
    LAYIN = auto()  # لين    — sonorant
    ASTTALA = auto()  # استطالة — prolongation (ض)
    HMZ = auto()  # همزي   — hamza-bearing
    # Vowel / nucleus features (الصوائت)
    NUWAWI = auto()  # نووي   — nuclear / syllabic
    QASIR = auto()  # قصير   — short vowel
    TAWIL = auto()  # طويل   — long vowel
    ITLAL = auto()  # اعتلال — defective / weak
    # Mark features (العلامات)
    SIFR_HARAKA = auto()  # صفر حركة — zero-vowel
    QAFIL = auto()  # قفل      — syllable closure
    TADFIF = auto()  # تضعيف   — gemination mark
    MD_KHAS = auto()  # مدّ خاص  — special extension mark


class PhonTransform(Enum):
    """Minimal transformations and functions — التحولات/الوظائف الدنيا (t in D_min).

    Each value is a unique power-of-two bit-position enabling a bitmask:
    transform_mask = Σ 2^(t.value-1) for t in transforms.
    """

    # Phonological processes (العمليات الصوتية)
    TAHQIQ = auto()  # تحقيق       — full realization
    TASHIL = auto()  # تسهيل       — facilitation / weakening
    IBDAL = auto()  # إبدال       — phonemic substitution
    HADHF = auto()  # حذف         — deletion / elision
    HAMLI_HAMZI = auto()  # حمل همزي    — hamza hosting
    IDGHAM = auto()  # إدغام       — assimilation / merging
    IDGHAM_SHAMSI = auto()  # إدغام شمسي  — solar (regressive) assimilation
    IZHAR_QAMARI = auto()  # إظهار قمري  — lunar clarity
    IZHAR = auto()  # إظهار       — clear articulation
    IKHFAA = auto()  # إخفاء       — nasalized concealment
    IQLAB = auto()  # إقلاب       — metamorphosis (ن → م before ب)
    TAFKHIM = auto()  # تفخيم       — velarization / emphasis
    TARQIQ = auto()  # ترقيق       — thinning / palatalization
    TAKRIR_TR = auto()  # تكرير       — trill articulation
    TAFSHI_TR = auto()  # تفشٍّ صوتي  — acoustic diffusion
    TAMATHUL = auto()  # تماثل       — progressive assimilation
    MADD = auto()  # مدّ         — vowel lengthening
    ITLAL_TR = auto()  # اعتلال      — weak-letter process
    ASTTALA_TR = auto()  # استطالة     — prolongation process
    # Morphological functions (الوظائف الصرفية)
    ASAL_JADHARI = auto()  # أصل جذري    — root-radical origin
    ZIYADA = auto()  # زيادة       — morphological augmentation
    BINA_SARFI = auto()  # بنية صرفية  — morphological structure
    BINA_ISHTIQAQI = auto()  # بناء اشتقاقي — derivational structure
    WAZIFA_SARFIYYA = auto()  # وظيفة صرفية — morphological function marker
    WAZN = auto()  # بناء وزني   — prosodic-pattern building
    # Syntactic / grammatical functions (الوظائف النحوية)
    TAAREF = auto()  # تعريف       — definiteness (لام التعريف)
    TAWKID = auto()  # توكيد       — emphasis marker
    TANWIN_FUNC = auto()  # تنوين       — nunation function
    JAZM = auto()  # جزم         — apocopation / jussive
    IIRAB = auto()  # إعراب       — grammatical case marking
    TANKIR = auto()  # تنكير       — indefiniteness
    JAM = auto()  # جمع         — pluralization marker
    ATAF = auto()  # عطف         — coordination marker
    NISBAH = auto()  # نسبة        — relational adjective marker
    MUTAKALLIM = auto()  # متكلم       — first-person marker
    DAMIR_FUNC = auto()  # هاء ضمير    — pronoun function
    TADFIF_TR = auto()  # تضعيف       — gemination function
    MAQTAA = auto()  # بناء مقطع مغلق — closed-syllable building
    HAMZA_CARRIER = auto()  # حامل كتابي  — orthographic hamza carrier


# ── Transition Engine — قانون الانتقال بين الخانات ──────────────────


class TransitionType(Enum):
    """الأنواع الكبرى للانتقال — the four major classes of cell transition."""

    FUNCTIONAL = auto()  # انتقال وظيفي    — same element, changed function
    RANK = auto()  # انتقال رتبي     — movement between phonetic tiers
    CONTEXTUAL = auto()  # انتقال تجاوري   — neighbour-driven transition
    MORPHO_STRUCTURAL = auto()  # انتقال بنيوي صرفي — pattern/template-driven


class TransitionLaw(Enum):
    """القوانين الجزئية للانتقال — the seven partial transition laws."""

    ITLAL = auto()  # اعتلال  — weak-letter transformation (ا و ي)
    IDGHAM = auto()  # إدغام   — gemination: C+C → Shadda
    IBDAL = auto()  # إبدال   — substitution within phonetic family
    HADHF = auto()  # حذف     — deletion from surface to deep structure
    WAQF = auto()  # وقف     — pause-final phonological reduction
    ZIYADA = auto()  # زيادة   — root element re-slotted as augment
    INZILAQ = auto()  # انزلاق  — glide ↔ long-vowel transition (و / ي)


class TransitionCondition(Enum):
    """شروط الانتقال — the five conditions required for a valid transition."""

    STRUCTURAL_VALIDITY = auto()  # بقاء داخل الأنماط المسموحة
    PHONETIC_BALANCE = auto()  # التخفيف دون الإفساد
    ROOT_PRESERVATION = auto()  # إمكان استرجاع الجذر بعد الانتقال
    FUNCTION_PRESERVATION = auto()  # وضوح الوظيفة بعد الانتقال
    NON_CONTRADICTION = auto()  # عدم الوقوع في صورة ممنوعة


class SyllablePosition(Enum):
    """موضع العنصر في المقطع — element's position inside the syllable."""

    ONSET = auto()  # بداية المقطع  — syllable onset (C)
    NUCLEUS = auto()  # نواة المقطع   — syllable nucleus (V)
    CODA = auto()  # نهاية المقطع  — syllable coda (C)
    INTER_WORD = auto()  # حدّ الكلمة    — word boundary


class FunctionRole(Enum):
    """الدور الوظيفي للعنصر — element's morpho-syntactic role in the word."""

    ROOT_RADICAL = auto()  # أصل جذري   — part of the tri-literal root
    AUGMENT = auto()  # زيادة      — morphological augment
    VOWEL_CARRIER = auto()  # حامل صائتي — vowel / nucleus carrier
    CASE_MARKER = auto()  # علامة إعراب — case / mood marker
    DEFINITENESS = auto()  # أداة تعريف  — definiteness particle
    PRONOUN = auto()  # ضمير       — pronominal clitic
    UNKNOWN = auto()  # غير محدد   — undetermined


# ── Functional Transition Schema — الانتقال الوظيفي المنضبط ──────────
# The following enums mirror the JSON Schema defined in
# arabic_engine/data/transition_record.schema.json and form the
# Python side of the formal functional-transition layer.


class CellType(Enum):
    """خانة الانتقال — cell identifier in the functional transition schema.

    Consonants (صوامت):
        C_ROOT_PLAIN       — plain root consonant (صامت جذري سهل)
        C_MULTI_FUNCTION   — multi-function / ambiguous consonant (صامت متعدد الوظائف)
        C_AUGMENTATIVE     — augmentative consonant (صامت زيادة)
        C_GLIDE_BACK       — back glide و (حرف لين خلفي)
        C_GLIDE_FRONT      — front glide ي (حرف لين أمامي)

    Long vowels (صوائت طويلة):
        V_LONG_A           — long /aː/ — ا
        V_LONG_W           — long /uː/ — و
        V_LONG_Y           — long /iː/ — ي

    Diacritics / short vowels (حركات):
        D_FATHA            — فتحة
        D_DAMMA            — ضمة
        D_KASRA            — كسرة
        D_SUKUN            — سكون
        D_SHADDA           — شدة
        D_TANWEEN_FATH     — تنوين فتح
        D_TANWEEN_DAMM     — تنوين ضم
        D_TANWEEN_KASR     — تنوين كسر

    Meta-cells (خانات بنيوية):
        CELL_ILLA                  — weak/defective letter structure (علّة)
        CELL_IMPLICIT              — deleted-but-recoverable element (ضمني)
        CELL_WAQF_COMPRESSED       — pause-compressed ending (وقف مضغوط)
        CELL_EXISTENTIAL           — pure existential state (وجود مطلق)
        CELL_EXISTENTIAL_TEMPORAL  — time-bound existential state (وجود زمني)
        CELL_EVENT_SOURCE          — abstract event / maṣdar source (حدث مصدري)
        CELL_EVENT_TEMPORAL        — temporalised event / verb form (حدث زمني)
        CELL_CAUSAL_INTERNAL       — self-contained causation (تسبب داخلي)
        CELL_CAUSAL_EXTERNAL       — external causation (تسبب خارجي)
    """

    # Consonants
    C_ROOT_PLAIN = auto()
    C_MULTI_FUNCTION = auto()
    C_AUGMENTATIVE = auto()
    C_GLIDE_BACK = auto()
    C_GLIDE_FRONT = auto()
    # Long vowels
    V_LONG_A = auto()
    V_LONG_W = auto()
    V_LONG_Y = auto()
    # Diacritics
    D_FATHA = auto()
    D_DAMMA = auto()
    D_KASRA = auto()
    D_SUKUN = auto()
    D_SHADDA = auto()
    D_TANWEEN_FATH = auto()
    D_TANWEEN_DAMM = auto()
    D_TANWEEN_KASR = auto()
    # Meta-cells
    CELL_ILLA = auto()
    CELL_IMPLICIT = auto()
    CELL_WAQF_COMPRESSED = auto()
    CELL_EXISTENTIAL = auto()
    CELL_EXISTENTIAL_TEMPORAL = auto()
    CELL_EVENT_SOURCE = auto()
    CELL_EVENT_TEMPORAL = auto()
    CELL_CAUSAL_INTERNAL = auto()
    CELL_CAUSAL_EXTERNAL = auto()
    # Masdar meta-cells (خانات مصدرية)
    CELL_MASDAR_EXPLICIT = auto()  # مصدر صريح — explicit verbal noun
    CELL_MASDAR_INTERPRETED = auto()  # مصدر مؤوّل — interpreted verbal noun
    CELL_MASDAR_BRIDGE = auto()  # جسر مصدري — masdar bridge node


class FuncTransitionClass(Enum):
    """صنف الانتقال الوظيفي — broad classification of a functional transition."""

    PHONOLOGICAL = auto()  # صوتي
    MORPHOLOGICAL = auto()  # صرفي
    ORTHOGRAPHIC = auto()  # إملائي / وقفي
    CAUSAL = auto()  # سببي
    TEMPORAL = auto()  # زمني
    EXISTENTIAL = auto()  # وجودي
    ABSTRACTIVE = auto()  # تجريدي


class EvidenceType(Enum):
    """نوع الدليل — the kind of evidence supporting a transition record."""

    LEXICAL = auto()  # معجمي
    PATTERN = auto()  # نمطي / وزني
    PHONOLOGICAL_CONTEXT = auto()  # سياق صوتي
    MORPH_CONTEXT = auto()  # سياق صرفي
    SURFACE_ONLY = auto()  # سطحي فقط
    DEEP_ANALYSIS = auto()  # تحليل عميق


class ReversibleValue(Enum):
    """قابلية الانتقال للعكس — whether a transition can be reversed."""

    YES = auto()  # قابل للعكس دائمًا
    NO = auto()  # غير قابل للعكس
    CONDITIONAL = auto()  # قابل للعكس بشرط


class ConditionToken(Enum):
    """رمز الشرط — atomic DSL token for preconditions and blocking conditions.

    Each value is a computable, snake_case label that can be evaluated
    against a context object.  The tokens cover:
      * phonological structure conditions (بنية صوتية)
      * morphological and lexical conditions (صرف ومعجم)
      * syllabic / positional conditions (مقطع وموضع)
      * causal / temporal / existential conditions (سبب / زمن / وجود)
    """

    # Glide / vowel structure
    GLIDE_LOSES_CONSONANTAL_LOAD = auto()
    SEGMENT_BECOMES_VOCALIC_NUCLEUS = auto()
    SYLLABLE_STRUCTURE_ALLOWS_LENGTHENING = auto()
    SEGMENT_REQUIRED_AS_EXPLICIT_ONSET = auto()
    SEGMENT_ENTERS_CONSONANTAL_POSITION = auto()
    SURFACE_REQUIRES_GLIDE_LINKING = auto()
    # Weak / implicit structure
    WEAK_SEGMENT_DELETED_ON_SURFACE = auto()
    DEEP_STRUCTURE_PRESERVED = auto()
    PATTERN_RECOVERS_MISSING_SLOT = auto()
    DELETION_CAUSES_ROOT_AMBIGUITY = auto()
    # Vowel extension
    FATHA_EXTENDED = auto()
    DAMMA_EXTENDED = auto()
    KASRA_EXTENDED = auto()
    SEGMENT_FORMS_INDEPENDENT_LONG_NUCLEUS = auto()
    # Gemination / compression
    TWO_IDENTICAL_CONSONANTS_IN_SEQUENCE = auto()
    COMPRESSION_ALLOWED = auto()
    IDENTITY_NOT_PROVEN = auto()
    AUGMENTATIVE_CONSONANT_CONTACTS_SIMILAR_OR_IDENTICAL_SEGMENT = auto()
    MORPH_PATTERN_ALLOWS_ASSIMILATION = auto()
    STRONG_SIMILARITY_OR_IDENTITY = auto()
    SURFACE_COMPRESSION_PERMITTED = auto()
    # Vowel drop / resyllabification
    MORPHOLOGICAL_CHANGE_DROPS_SHORT_VOWEL = auto()
    DROPPING_VOWEL_BREAKS_ALLOWED_SYLLABLE_PATTERN = auto()
    SEGMENT_REQUIRES_OPENING = auto()
    PATTERN_OR_LINKING_REQUIRES_MOVEMENT = auto()
    SEGMENT_REQUIRES_BACK_ROUNDING = auto()
    SEGMENT_REQUIRES_FRONTING = auto()
    # Root / augment classification
    SEGMENT_FUNCTIONS_AS_AUGMENTATIVE_MARKER = auto()
    ROOT_SLOTS_IDENTIFIED_INDEPENDENTLY = auto()
    LEXICON_CONFIRMS_SEGMENT_IS_ROOT_MEMBER = auto()
    CONTEXT_FAVORS_AUGMENTATIVE_READING = auto()
    PATTERN_REQUIRES_NON_ROOT_FUNCTION = auto()
    LEXICON_CONFIRMS_ROOT_STATUS = auto()
    SEGMENT_REQUIRED_FOR_ROOT_IDENTITY = auto()
    # Glide-as-augment
    WAAW_FUNCTIONS_AS_NON_ROOT_INCREMENT = auto()
    PATTERN_SUPPORTS_INCREMENTAL_ROLE = auto()
    ROOT_MEMBERSHIP_OF_WAAW_PROVEN = auto()
    YAA_FUNCTIONS_AS_NON_ROOT_INCREMENT = auto()
    ROOT_MEMBERSHIP_OF_YAA_PROVEN = auto()
    # Pause / waqf
    WORD_FINAL_POSITION = auto()
    PAUSE_MODE_ENABLED = auto()
    WEAK_FINAL_STRUCTURE_COMPRESSIBLE = auto()
    # Surface deletion
    SURFACE_DELETION_ALLOWED = auto()
    DEEP_RECOVERABILITY_PRESERVED = auto()
    ROOT_IDENTITY_COLLAPSES = auto()
    # Causal
    EXTERNAL_TRANSFORMER_APPEARS = auto()
    EFFECT_MOVES_BEYOND_ACTOR = auto()
    EXTERNAL_TRANSFORMER_REMOVED = auto()
    EFFECT_COLLAPSES_BACK_TO_SUBJECT = auto()
    # Temporal / existential
    ABSTRACT_EVENT_LINKED_TO_TIME_REFERENCE = auto()
    TIME_REFERENCE_REMOVED = auto()
    TEMPORAL_OPERATOR_APPLIED = auto()
    EXISTENTIAL_STATE_BOUND_TO_TIME = auto()
    TEMPORAL_OPERATOR_REMOVED = auto()
    # Masdar / verbal noun conditions
    ROOT_IDENTIFIED = auto()
    VERB_PATTERN_KNOWN = auto()
    BAB_ASSIGNED = auto()
    PARTICLE_AN_PRESENT = auto()
    VERB_FOLLOWS_PARTICLE = auto()
    MASDAR_IDENTIFIED = auto()
    DERIVATION_TARGET_FA3IL = auto()
    DERIVATION_TARGET_MAF3UL = auto()
    DERIVATION_TARGET_ZAMAN = auto()
    DERIVATION_TARGET_MAKAN = auto()
    DERIVATION_TARGET_HAY2A = auto()
    DERIVATION_TARGET_ALA = auto()


# ── AEU Periodic-Table enums ────────────────────────────────────────


class ElementClass(Enum):
    """تصنيف العنصر — structural class of an alphabetic encoding unit."""

    BASE_LETTER = auto()  # حرف أساسي
    VOWEL_MARKER = auto()  # علامة حركة
    STRUCTURAL_MARKER = auto()  # علامة بنيوية
    CARRIER_RELATED_UNIT = auto()  # وحدة مرتبطة بحامل
    COMPOSITE_DECISION_UNIT = auto()  # وحدة قرار مركبة


class ElementLayer(Enum):
    """طبقة العنصر — the architectural layer an AEU belongs to."""

    PHONOLOGICAL = auto()  # صوتية
    ORTHOGRAPHIC = auto()  # كتابية
    STRUCTURAL = auto()  # بنيوية
    MIXED = auto()  # مختلطة


class ElementFunction(Enum):
    """وظيفة العنصر — the functional role an AEU carries."""

    IDENTITY_BEARING = auto()  # حامل هوية
    MOTION_BEARING = auto()  # حامل حركة
    LENGTH_BEARING = auto()  # حامل طول
    CLOSURE_BEARING = auto()  # حامل إغلاق
    DUPLICATION_BEARING = auto()  # حامل تضعيف
    INDEFINITENESS_BEARING = auto()  # حامل تنكير
    ENCODING_BEARING = auto()  # حامل ترميز


class CombinationType(Enum):
    """نوع الاندماج — how an AEU combines with neighbours."""

    STANDALONE = auto()  # مستقل
    ATTACHES_TO_BASE = auto()  # يلتصق بالأساس
    CLUSTER_INTERNAL = auto()  # داخل عنقود
    CONTEXT_DEPENDENT = auto()  # معتمد على السياق


class UnicodeProfileType(Enum):
    """نوع الملف الموحد — Unicode rendering profile of an AEU."""

    SINGLE_CODE_POINT = auto()  # نقطة رمز واحدة
    COMBINING_MARK = auto()  # علامة تجميعية
    CONTEXTUAL_RENDERING = auto()  # عرض سياقي


class ProofStatus(Enum):
    """حالة الإثبات — proof/verification status of an AEU."""

    PROVEN = auto()  # مُثبَت
    PENDING = auto()  # قيد الإثبات
    ASSUMED = auto()  # مفترض — accepted without formal proof
    COMPOSITE = auto()  # مُركَّب


# ── Axiom-layer enums (الأصول الخمسة) ────────────────────────────────


class SlotState(Enum):
    """حالة الموضع — state of a structural slot (A1/A2)."""

    EMPTY = auto()  # فارغ قابل للامتلاء
    OCCUPIED = auto()  # مشغول بموجب أول
    BLOCKED = auto()  # محجوب بنيويًا


class OntologicalLayer(Enum):
    """الطبقة الوجودية — ontological rank for layer promotion (A4).

    Encodes the hierarchy: cell → transition → syllable → root → pattern.
    Each level requires the previous to be complete before promotion.
    """

    CELL = auto()  # خانة — atomic phonological cell
    TRANSITION = auto()  # انتقال — directed transition between cells
    SYLLABLE = auto()  # مقطع — syllable-level grouping
    ROOT = auto()  # جذر — root-level abstraction
    PATTERN = auto()  # وزن — morphological pattern


class OntologicalMode(Enum):
    """النمط الوجودي — the mode of existence of a linguistic element.

    Separates ontological kinds so that elements from different modes
    cannot be compared directly (Rank Law / قانون الرتبة).

    =========  ==========================================
    Mode        Description (Arabic / English)
    =========  ==========================================
    SLOT        موضع قابل للامتلاء — fillable structural position
    UNIT        وحدة قاعدية — atomic base unit (letter)
    MODIFIER    محمول تشغيلي — operational modifier (vowel mark)
    COMPOSITE   تركيب — composite construct (syllable, word)
    STRUCTURE   بنية — structural template (root, pattern)
    CONSTRAINT  قيد — constraint or condition
    =========  ==========================================
    """

    SLOT = auto()  # موضع — structural position (Structural Zero)
    UNIT = auto()  # وحدة — base unit (consonant / letter)
    MODIFIER = auto()  # محمول — modifier (short vowel, sukun, shadda)
    COMPOSITE = auto()  # تركيب — composite (syllable, morpheme)
    STRUCTURE = auto()  # بنية — structural template (root, pattern)
    CONSTRAINT = auto()  # قيد — condition / constraint


class TriadType(Enum):
    """نوع الثلاثية — the formal type of a triadic block.

    Every triad must declare its type before entering computation
    (قانون نوع المثلث).

    ==============  ==============================================
    Type             Description
    ==============  ==============================================
    DISTINCTIVE      مثلث تمييزي — previous / centre / next
    HIERARCHICAL     مثلث رتبي — apex / left-branch / right-branch
    GENERATIVE       مثلث توليدي — base / motion / constraint
    ==============  ==============================================
    """

    DISTINCTIVE = auto()  # تمييزي — سابق / مركز / لاحق
    HIERARCHICAL = auto()  # رتبي — قمة / ضلع / ضلع
    GENERATIVE = auto()  # توليدي — قاعدة / حركة / قيد


class RankType(Enum):
    """نوع الرتبة — the rank classification derived from limit/capacity balance.

    Implements Law 3 (قانون الحد والسعة):
      * L ≫ C → LIMITAL   (حدّي)
      * C ≫ L → CAPACITIVE (سعوي)
      * L ≈ C → TRANSITIONAL (انتقالي)
    """

    LIMITAL = auto()  # حدّي — limit-dominant
    CAPACITIVE = auto()  # سعوي — capacity-dominant
    TRANSITIONAL = auto()  # انتقالي — balanced / transitional


# ── Signified v2.0 — طبقة المدلول الموسّعة ──────────────────────────
# The twenty axes below extend the signified layer so that a Concept
# can encode not just its ontological *type* but also its epistemic
# standing, normative weight, affective charge, causal role, cultural
# scope, and every other dimension required to represent the full range
# of human conceptual knowledge.


class EpistemicStatus(Enum):
    """الوضع الإبستيمي — how knowledge of the concept is held (1/20).

    Complements :class:`TruthState` (which applies to propositions).
    ``EpistemicStatus`` applies to the *concept itself* and captures the
    epistemic grade at which the concept is known or postulated.
    """
    CERTAIN = auto()        # يقيني — known with certainty
    PROBABLE = auto()       # ظني    — probably true / held with high confidence
    DOUBTFUL = auto()       # مشكوك  — genuinely doubtful
    IMAGINED = auto()       # متخيَّل — constructed by imagination
    PRESUMED = auto()       # مفترض  — assumed without full proof
    NECESSARY = auto()      # ضروري  — necessarily true (cannot be otherwise)
    POSSIBLE = auto()       # ممكن   — possible but not certain
    IMPOSSIBLE = auto()     # ممتنع  — logically / ontologically impossible
    AXIOMATIC = auto()      # بديهي  — self-evident / axiomatic
    THEORETICAL = auto()    # نظري   — derived by theoretical reasoning


class NormativeCategory(Enum):
    """الجهة المعيارية المستقلة — normative / deontic category (2/20).

    Independent of :class:`GuidanceState` (which is a procedural
    evaluation output).  ``NormativeCategory`` encodes the *intrinsic*
    normative meaning carried by the concept.
    """
    OBLIGATORY = auto()     # واجب   — morally / legally required
    PERMISSIBLE = auto()    # مباح   — allowed without positive recommendation
    FORBIDDEN = auto()      # محظور  — prohibited
    RECOMMENDED = auto()    # مستحب  — recommended / praiseworthy
    DISAPPROVED = auto()    # مكروه  — disapproved / discouraged
    GOOD = auto()           # حسن    — ethically good
    BAD = auto()            # قبيح   — ethically bad
    JUST = auto()           # عادل   — just / fair
    UNJUST = auto()         # ظالم   — unjust / unfair
    NEUTRAL = auto()        # محايد  — normatively neutral


class AffectiveDimension(Enum):
    """البُعد الوجداني — the affective / emotional dimension (3/20).

    Concepts carry affective charge that shapes human understanding
    beyond purely rational classification.
    """
    LOVE = auto()           # محبة       — love / affection
    FEAR = auto()           # خوف        — fear / dread
    TRANQUILITY = auto()    # طمأنينة    — inner peace / tranquility
    ANXIETY = auto()        # قلق        — anxiety / worry
    AWE = auto()            # هيبة       — awe / reverence
    SHAME = auto()          # حياء/خجل   — shame / modesty
    HATE = auto()           # كراهية     — hatred / aversion
    INTIMACY = auto()       # أُنس       — intimacy / familiarity
    ALIENATION = auto()     # اغتراب     — alienation / estrangement
    JOY = auto()            # فرح        — joy / happiness
    GRIEF = auto()          # حزن        — grief / sorrow
    NEUTRAL = auto()        # محايد      — affectively neutral


class MentalIntentionalType(Enum):
    """نوع العقل القصدي الداخلي — intentional mental state type (4/20).

    Covers the inner mental life: concepts that are *about* other
    states (intentionality) rather than just representing external facts.
    """
    BELIEF = auto()         # اعتقاد   — propositional belief
    DESIRE = auto()         # رغبة     — desire / want
    INTENTION = auto()      # نية/قصد  — intention / purpose
    ATTENTION = auto()      # انتباه   — focal attention
    MEMORY = auto()         # تذكر     — memory / recollection
    EXPECTATION = auto()    # توقع     — expectation / anticipation
    DECISION = auto()       # قرار     — decision / resolution
    IMAGINATION = auto()    # تخيّل    — imagination / mental imagery
    PERCEPTION = auto()     # إدراك    — perceptual experience
    AWARENESS = auto()      # وعي      — consciousness / awareness


class ModalCategory(Enum):
    """الجهة المنطقية — alethic modal category (5/20).

    Encodes what is possible, necessary, impossible, or merely
    hypothetical — including counterfactual reasoning.
    """
    POSSIBLE = auto()           # ممكن           — possibly the case
    NECESSARY = auto()          # ضروري          — necessarily the case
    IMPOSSIBLE = auto()         # ممتنع          — impossible
    COUNTERFACTUAL = auto()     # مضاد للواقع    — contrary-to-fact
    HYPOTHETICAL = auto()       # افتراضي        — supposed for argument's sake
    ACTUAL = auto()             # واقعي          — actually obtaining


class FrameType(Enum):
    """نوع الإطار المفاهيمي — conceptual frame / scene type (6/20).

    Many concepts are only intelligible within a background frame
    (Charles Fillmore's frame semantics).  This enum names the most
    common encyclopaedic frames.
    """
    COMMERCIAL = auto()     # تجاري   — buying, selling, price, goods
    JOURNEY = auto()        # سفر     — traveller, path, destination, vehicle
    KINSHIP = auto()        # قرابة   — parent, child, sibling, lineage
    CONFLICT = auto()       # صراع   — adversary, battle, victory, defeat
    TEACHING = auto()       # تعليم   — teacher, student, lesson, assessment
    GOVERNANCE = auto()     # حكم    — ruler, law, authority, subject
    RELIGIOUS = auto()      # ديني   — worship, ritual, sacred, obligation
    MEDICAL = auto()        # طبي    — patient, symptom, diagnosis, treatment
    DOMESTIC = auto()       # منزلي  — household, family, dwelling, routine
    NONE = auto()           # لا إطار — no particular frame


class ScriptPhase(Enum):
    """مرحلة السيناريو الإجرائي — phase within a cognitive script (7/20).

    Schank & Abelson-style scripts: stereotyped event sequences.
    A concept may be located at a particular phase in such a sequence.
    """
    PRECONDITION = auto()   # شرط سابق    — must hold before script begins
    INITIATION = auto()     # بدء         — script-opening action
    DEVELOPMENT = auto()    # تطور        — main body of the script
    CLIMAX = auto()         # ذروة        — peak / pivotal moment
    RESOLUTION = auto()     # حلّ         — outcome / resolution
    POSTCONDITION = auto()  # نتيجة لاحقة — state that holds after script
    NONE = auto()           # لا سيناريو  — not script-bound


class CausalRole(Enum):
    """الدور السببي-التفسيري — causal / explanatory role (8/20).

    Human knowledge is built on causal models.  This enum labels
    the role a concept plays inside a causal-explanatory chain.
    """
    CAUSE = auto()      # سبب       — direct cause
    CONDITION = auto()  # شرط       — necessary / sufficient condition
    ENABLER = auto()    # مُمكِّن   — enables without directly causing
    BLOCKER = auto()    # مانع      — prevents / blocks an effect
    MECHANISM = auto()  # آلية      — the *how* of causation
    MEDIATOR = auto()   # وسيط      — intermediary in a causal chain
    EFFECT = auto()     # أثر/نتيجة — downstream effect
    GOAL = auto()       # غاية      — final cause / telos
    LAW = auto()        # قانون     — governing regularity / nomic law
    NONE = auto()       # لا دور    — no causal role assigned


class InstitutionalCategory(Enum):
    """التصنيف المؤسسي الاجتماعي — social / institutional category (9/20).

    Searle-style institutional facts: realities that exist only through
    collective acceptance (X counts as Y in context C).
    """
    STATE = auto()          # دولة     — state / sovereign entity
    LAW = auto()            # قانون    — legal rule or statute
    PROPERTY = auto()       # ملكية    — ownership right
    CONTRACT = auto()       # عقد      — binding agreement
    POSITION = auto()       # منصب     — social role / office
    INSTITUTION = auto()    # مؤسسة   — established organisation
    CURRENCY = auto()       # عملة     — medium of exchange
    NORM = auto()           # معيار    — social / conventional norm
    RITUAL = auto()         # طقس      — ceremonial practice
    NONE = auto()           # لا تصنيف — not an institutional fact


class CategorizationMode(Enum):
    """نمط التصنيف المفاهيمي — how the concept belongs to its category (10/20).

    Classical categories have crisp boundaries; prototype-based and
    fuzzy categories admit degrees of membership (Rosch, Zadeh).
    """
    CLASSICAL = auto()              # كلاسيكي        — necessary & sufficient conditions
    PROTOTYPE_BASED = auto()        # نموذجي         — graded membership around prototype
    FUZZY_BOUNDED = auto()          # ضبابي الحدود   — membership by degree (fuzzy sets)
    GRADIENT_MEMBERSHIP = auto()    # عضوية متدرجة   — continuous membership scale
    RADIAL = auto()                 # شعاعي          — radial network of related senses


class CulturalScope(Enum):
    """النطاق الثقافي الحضاري — cultural / civilisational scope (11/20).

    Marks whether a concept is universal or specific to a particular
    cultural, religious, or domain tradition.
    """
    UNIVERSAL = auto()          # كوني         — applies across all cultures
    CULTURE_SPECIFIC = auto()   # ثقافي خاص    — specific to one culture
    CIVILIZATIONAL = auto()     # حضاري        — shared within a civilisation
    DOMAIN_SPECIFIC = auto()    # تخصصي        — confined to a specialised domain
    RELIGIOUS_SPECIFIC = auto() # ديني خاص     — specific to a religious tradition


class DiachronicStatus(Enum):
    """الوضع التاريخي الدلالي — diachronic / historical semantic status (12/20).

    Tracks whether a concept has drifted, narrowed, broadened, or
    specialised relative to its original meaning.
    """
    ORIGINAL = auto()       # أصلي        — meaning as originally used
    SHIFTED = auto()        # منتقل       — meaning has shifted
    NARROWED = auto()       # ضيّق        — meaning has narrowed
    BROADENED = auto()      # موسَّع      — meaning has broadened
    SPECIALIZED = auto()    # تخصّص       — moved to technical domain
    GENERALIZED = auto()    # عمّ         — moved from technical to general use
    OBSOLETE = auto()       # متقادم      — no longer in active use


class ConceptFormationMode(Enum):
    """طريقة تكوين المفهوم — how the concept was formed (13/20).

    Distinguishes primitive atomic concepts from derived, composed,
    blended, or metaphorically extended ones.
    """
    PRIMITIVE = auto()              # أصلي بسيط       — irreducible primitive
    DERIVED = auto()                # مشتق            — derived from another concept
    COMPOSED = auto()               # مركّب           — composed from parts
    BLENDED = auto()                # ممزوج           — conceptual blend (Fauconnier)
    ANALOGICALLY_EXTENDED = auto()  # تمديد قياسي     — extended by analogy
    METAPHORICAL = auto()           # مجازي           — grounded in metaphor


class MetaConceptualLevel(Enum):
    """المستوى فوق المفاهيمي — meta-conceptual order (14/20).

    First-order concepts are *about* the world; second-order concepts
    are about first-order concepts; third-order are about the system
    of concepts itself.
    """
    FIRST_ORDER = auto()    # مستوى أول  — concepts about entities / events
    SECOND_ORDER = auto()   # مستوى ثان  — concepts about first-order concepts
    THIRD_ORDER = auto()    # مستوى ثالث — concepts about the conceptual system


class InterpretiveStability(Enum):
    """استقرار التفسير — interpretive stability / polysemy status (15/20).

    Some concepts have a single stable reading; others are ambiguous,
    polysemous, or actively contested.
    """
    STABLE = auto()             # ثابت           — single, stable interpretation
    AMBIGUOUS = auto()          # ملتبس          — genuinely ambiguous
    POLYSEMOUS = auto()         # متعدد المعاني  — multiple related senses
    CONTEXT_RESOLVED = auto()   # محدَّد بالسياق — disambiguation requires context
    CONTESTED = auto()          # متنازع عليه    — meaning is socially contested


class SalienceLevel(Enum):
    """مستوى البروز الإدراكي — cognitive salience / prominence level (16/20).

    In human cognition not all features / concepts are equally salient.
    This enum captures the prominence profile of a concept.
    """
    CENTRAL = auto()        # مركزي    — highly salient, prototype-like
    PERIPHERAL = auto()     # هامشي    — low salience, atypical
    FOREGROUNDED = auto()   # بارز     — brought to focal attention
    BACKGROUNDED = auto()   # خلفي     — presupposed, not in focus
    UNEXPECTED = auto()     # مفاجئ    — surprises the interpreter
    EXPECTED = auto()       # متوقع    — predicted by context


class EmbodiedDomain(Enum):
    """المجال الإدراكي المتجسد — embodied / perceptual domain (17/20).

    Lakoff & Johnson: many abstract concepts are grounded in
    embodied sensorimotor experience.  This enum names the source
    domain of that grounding.
    """
    VISUAL = auto()         # بصري       — sight / visual experience
    AUDITORY = auto()       # سمعي       — hearing / sound
    TACTILE = auto()        # لمسي       — touch / texture
    BALANCE = auto()        # توازن      — bodily balance / equilibrium
    MOTION = auto()         # حركة       — kinesthetic / movement
    FORCE = auto()          # قوة/جهد    — force / effort / resistance
    CONTAINMENT = auto()    # احتواء     — in/out container schema
    PROXIMITY = auto()      # قرب/بُعد   — near/far spatial experience
    VERTICAL_AXIS = auto()  # محور عمودي — up/down orientation
    NONE = auto()           # لا تجسيد   — not grounded in embodied experience


class SelfModelAspect(Enum):
    """جانب النموذج الذاتي — aspect of the self-model (18/20).

    Concepts involved in self-awareness, personal identity, and
    first-person perspective.
    """
    EGO = auto()                    # الأنا              — the ego / subjective centre
    SELF_IMAGE = auto()             # صورة الذات        — self-conception / self-image
    SELF_AWARENESS = auto()         # وعي الذات         — reflective self-awareness
    OTHER_DISTINCTION = auto()      # تمييز الذات من الغير — self vs. other
    PERSONAL_CONTINUITY = auto()    # الاستمرار الشخصي  — identity over time
    FIRST_PERSON = auto()           # منظور أول         — first-person perspective
    NONE = auto()                   # لا جانب ذاتي      — not self-related


class OperationalCapacity(Enum):
    """القدرة الإجرائية — operational / performative capacity (19/20).

    Some concepts not only *mean* something but also *do* something:
    they enable actions, issue commands, create obligations, etc.
    (Austin / Searle speech-act inspired).
    """
    ENABLES = auto()    # يُمكِّن   — grants ability or access
    COMMANDS = auto()   # يأمر     — directive / command
    PROMISES = auto()   # يَعِد    — commissive / promise
    PERMITS = auto()    # يأذن     — declarative permission
    RESTRICTS = auto()  # يُقيِّد  — restricts / prohibits
    ACTIVATES = auto()  # يُنشِّط  — triggers a process or state
    NONE = auto()       # لا قدرة  — no operational capacity


class ConceptRelationType(Enum):
    """نوع العلاقة بين المفاهيم — inter-concept relation type (20/20).

    The top-level relation vocabulary for building a concept network.
    These relations are used in :class:`~arabic_engine.core.types.ConceptRelation`
    to wire concept nodes together into a full knowledge graph.
    """
    IS_A = auto()           # هو نوع من       — taxonomic (hyponymy)
    PART_OF = auto()        # جزء من          — meronymy / part–whole
    CAUSES = auto()         # يُسبِّب         — causal relation
    ENABLES = auto()        # يُمكِّن         — enabling (weaker than causes)
    OPPOSES = auto()        # يُعارض          — opposition / antonymy
    PRESUPPOSES = auto()    # يفترض مسبقًا    — logical presupposition
    SYMBOLIZES = auto()     # يرمز إلى        — symbolic / iconic link
    INSTANTIATES = auto()   # يُمثِّل نموذجًا — instance-of
    REALIZES = auto()       # يُجسِّد         — realisation / implementation
    REGULATES = auto()      # يَضبط           — regulatory / governance link



# ── Dalāla kind ──────────────────────────────────────────────────────


class DalaalaKind(Enum):
    """نوع الدلالة — kind of signification (extended dalāla vocabulary)."""

    MUTABAQA = auto()   # مطابقة — exact denotation
    TADHAMMUN = auto()  # تضمن   — inclusion / containment
    ILTIZAM = auto()    # التزام — necessary implication
    ISHARA = auto()     # إشارة  — indicative / symbolic reference


# ── Judgement / method / proof ──────────────────────────────────────


class JudgementType(Enum):
    """نوع الحكم — type of logical or normative judgement."""

    EXISTENCE = auto()              # وجودي         — existence judgement
    ESSENCE = auto()                # ماهوي         — essence / quiddity
    ATTRIBUTE = auto()              # وصفي          — attribute judgement
    RELATION = auto()               # علائقي        — relational judgement
    INTERPRETIVE = auto()           # تأويلي        — interpretive judgement
    FORMAL_CONTRADICTION = auto()   # تناقض صوري   — formal contradiction
    NORMATIVE = auto()              # معياري        — normative judgement
    PURE_LINGUISTIC = auto()        # لغوي بحت     — purely linguistic
    METAPHYSICAL = auto()           # ميتافيزيقي   — metaphysical
    CAUSAL = auto()                 # سببي          — causal judgement
    FORMAL = auto()                 # صوري          — formal / logical


class MethodFamily(Enum):
    """عائلة المنهج — family of inference or derivation method."""

    RATIONAL = auto()       # عقلي       — rational / deductive
    SCIENTIFIC = auto()     # تجريبي     — empirical / scientific
    LINGUISTIC = auto()     # لغوي       — linguistic analysis
    MATHEMATICAL = auto()   # رياضي      — mathematical / formal
    PHYSICAL = auto()       # طبيعي      — physical / natural-science


class LinkKind(Enum):
    """نوع الرابط — kind of inter-node link."""

    CAUSAL = auto()                 # سببي               — causal link
    TEMPORAL = auto()               # زمني               — temporal link
    LOGICAL = auto()                # منطقي              — logical link
    SEMANTIC = auto()               # دلالي              — semantic link
    STRUCTURAL = auto()             # بنيوي              — structural link
    CONTEXTUAL = auto()             # سياقي              — contextual link
    TEXTUAL_INFERENCE = auto()      # استنتاج نصي        — textual inference link


class ProofPathKind(Enum):
    """نوع مسار الإثبات — kind of proof path."""

    DIRECT_PROOF = auto()   # إثبات مباشر    — direct proof
    INDIRECT = auto()       # غير مباشر      — indirect / reductio
    CONSTRUCTIVE = auto()   # بنائي          — constructive proof
    REFUTATION = auto()     # بالتناقض       — proof by refutation


# ── Path kind (proof / evidence path) ───────────────────────────────


class PathKind(Enum):
    """نوع المسار — kind of proof or evidence path in a knowledge episode."""

    HISSI = auto()          # حسّي      — sensory / empirical path
    AQLI = auto()           # عقلي      — rational / deductive path
    LINGUISTIC = auto()     # لغوي      — linguistic / textual path
    FORMAL = auto()         # صوري      — formal / logical path


# ── Signification classes (signifier / signified / uttered form) ────


class SignifierClass(Enum):
    """صنف الدال — broad class of the signifier form."""

    LEXICAL = auto()        # معجمي      — lexical signifier
    SYNTACTIC = auto()      # نحوي       — syntactic / grammatical
    PHONOLOGICAL = auto()   # صوتي       — phonological form
    ORTHOGRAPHIC = auto()   # كتابي      — orthographic form
    UTTERED_FORM = auto()   # صيغة ملفوظة — uttered surface form
    RHETORICAL = auto()     # بلاغي      — rhetorical / figurative
    MORPHOLOGICAL = auto()  # صرفي       — morphological form
    PROSODIC = auto()       # إيقاعي     — prosodic / metrical


class SignifiedClass(Enum):
    """صنف المدلول — broad class of the signified concept."""

    CONCEPTUAL = auto()         # مفاهيمي        — conceptual signified
    REFERENTIAL = auto()        # إحالي          — referential (names/entities)
    RELATIONAL = auto()         # علائقي         — relational signified
    NORMATIVE = auto()          # معياري         — normative / legal concept
    ABSTRACT = auto()           # تجريدي         — abstract concept
    ONTOLOGICAL = auto()        # وجودي          — ontological category
    META_CONCEPTUAL = auto()    # ما فوق مفاهيمي — meta-conceptual
    PROPOSITIONAL = auto()      # قضوي           — propositional content
    PREDICATIVE = auto()        # إسنادي         — predicative signified
    EXISTENTIAL = auto()        # وجودي تحقق     — existential content
    ATTRIBUTIVE = auto()        # وصفي           — attributive / descriptive
    CAUSAL = auto()             # سببي           — causal content
    TELEOLOGICAL = auto()       # غائي           — teleological / purposive
    DEONTIC = auto()            # إلزامي         — deontic / obligatory
    TEMPORAL = auto()           # زمني           — temporal content
    SPATIAL = auto()            # مكاني          — spatial content
    MODAL = auto()              # نمطي           — modal content
    INTENSIONAL = auto()        # مضموني         — intensional meaning
    EXTENSIONAL = auto()        # خارجي          — extensional reference
    EPISTEMIC = auto()          # معرفي          — epistemic content
    EVALUATIVE = auto()         # تقييمي         — evaluative content
    INFERENTIAL = auto()        # استدلالي       — inferential content


class ConceptualSignifiedClass(Enum):
    """صنف المدلول المفاهيمي — finer class of the conceptual signified."""

    ENTITY_CONCEPT = auto()     # مفهوم ذات       — entity / substance concept
    EVENT_CONCEPT = auto()      # مفهوم حدث       — event / process concept
    PROPERTY_CONCEPT = auto()   # مفهوم خاصية     — property / attribute concept
    UNIVERSAL = auto()          # كلي              — universal concept
    PARTICULAR = auto()         # جزئي             — particular concept
    META_CONCEPT = auto()       # ما فوق مفهوم    — meta-concept / concept of concept
    RELATIONAL = auto()         # علائقي           — relational concept
    CONCRETE = auto()           # ملموس            — concrete / material concept


class UtteredFormClass(Enum):
    """صنف الصيغة الملفوظة — class of the uttered surface form."""

    WORD_UTTERANCE = auto()         # لفظ مفرد         — single word utterance
    MARKED_UTTERANCE = auto()       # لفظ معلَّم       — morphologically marked
    PHRASE = auto()                 # عبارة             — phrase
    CLAUSE = auto()                 # جملة فرعية       — clause
    SENTENCE_UTTERANCE = auto()     # جملة ملفوظة      — full sentence utterance


class OntologicalConstraintType(Enum):
    """نوع القيد الوجودي — ontological constraint kind."""

    STRUCTURAL = auto()                 # بنيوي          — structural constraint
    LEXICAL_CONSTRAINT = auto()         # معجمي          — lexical constraint
    CONTEXTUAL_CONSTRAINT = auto()      # سياقي          — contextual constraint
    INTERPRETIVE_CONSTRAINT = auto()    # تأويلي         — interpretive constraint
    RHETORICAL_CONSTRAINT = auto()      # بلاغي          — rhetorical constraint
    REFERENTIAL_CONSTRAINT = auto()     # إحالي          — referential constraint
    LOGICAL_CONSTRAINT = auto()         # منطقي          — logical constraint
    SEMANTIC_CONSTRAINT = auto()        # دلالي          — semantic constraint
    PRAGMATIC_CONSTRAINT = auto()       # تداولي         — pragmatic constraint
    SYNTACTIC_CONSTRAINT = auto()       # نحوي           — syntactic constraint
    PHONOLOGICAL_CONSTRAINT = auto()    # صوتي           — phonological constraint
    MORPHOLOGICAL_CONSTRAINT = auto()   # صرفي           — morphological constraint
    EPISTEMIC_CONSTRAINT = auto()       # معرفي          — epistemic constraint


class UtteranceToConceptConstraint(Enum):
    """قيد ربط الملفوظ بالمفهوم — constraint on utterance→concept mapping."""

    SURFACE_VALIDITY = auto()           # صحة سطحية         — surface-level validity
    LEXICAL_ACCESS = auto()             # وصول معجمي        — lexical access
    CONTEXT_RESOLUTION = auto()         # حل السياق         — context resolution
    CONCEPT_SELECTION = auto()          # اختيار المفهوم    — concept selection
    FIGURATIVE_DISAMBIGUATION = auto()  # توضيح مجازي       — figurative disambiguation
    REFERENTIAL_RESOLUTION = auto()     # حل الإحالة        — referential resolution
    LOGICAL_COHERENCE = auto()          # تماسك منطقي       — logical coherence


# ── Coupling relation type ───────────────────────────────────────────


class CouplingRelationType(Enum):
    """نوع علاقة التزاوج — relation type between signifier and signified."""

    DIRECT = auto()                 # مباشر      — direct denotation
    INFERENTIAL = auto()            # استدلالي   — inferential / implied
    COMPOSITIONAL = auto()          # تركيبي     — compositional
    HIERARCHICAL = auto()           # هرمي       — hierarchical (restriction)
    REFERENTIAL_COUPLING = auto()   # إحالي      — referential coupling
    FIGURATIVE = auto()             # مجازي      — figurative / metaphorical
    ANALOGICAL = auto()             # قياسي      — analogical coupling
    SYNTAGMATIC = auto()            # تضامني     — syntagmatic (paradigmatic axis)
    PARADIGMATIC = auto()           # استبدالي   — paradigmatic (selection axis)
    CONNOTATIVE = auto()            # إيحائي     — connotative / associated


# ── Sense / trace / trust ───────────────────────────────────────────


class SenseModality(Enum):
    """طريقة الحس — sensory modality for perception concepts."""

    VISUAL = auto()         # بصري           — sight / visual
    AUDITORY = auto()       # سمعي           — hearing / auditory
    TACTILE = auto()        # لمسي           — touch / tactile
    OLFACTORY = auto()      # شمي            — smell
    GUSTATORY = auto()      # ذوقي           — taste
    PROPRIOCEPTIVE = auto() # استشعار ذاتي   — proprioceptive
    VISION = VISUAL         # backward-compat alias for VISUAL
    HEARING = AUDITORY      # backward-compat alias for AUDITORY
    TOUCH = TACTILE         # backward-compat alias for TACTILE
    SMELL = OLFACTORY       # backward-compat alias for OLFACTORY
    TASTE = GUSTATORY       # backward-compat alias for GUSTATORY


class TraceMode(Enum):
    """نمط التتبع — mode of epistemic / inference trace."""

    DIRECT = auto()                 # مباشر          — direct trace
    MEDIATED = auto()               # وسيط           — mediated trace
    BIDIRECTIONAL = auto()          # ثنائي الاتجاه  — bidirectional
    DIRECT_PERCEPTION = DIRECT      # backward-compat alias for DIRECT


class TraceQuality(Enum):
    """جودة التتبع — quality / reliability grade of a trace."""

    STRONG = auto()     # قوي        — high-quality trace
    MEDIUM = auto()     # متوسط      — medium quality
    WEAK = auto()       # ضعيف       — weak trace
    UNVERIFIED = auto() # غير مُتحقَّق منه — unverified


class TrustBasis(Enum):
    """أساس الثقة — basis on which trust is grounded."""

    EXPERTISE = auto()          # خبرة               — expertise
    AUTHORITY = auto()          # سلطة               — authority
    FAMILIARITY = auto()        # ألفة               — familiarity / acquaintance
    TESTIMONY_CHAIN = auto()    # سلسلة شهادات       — chain of testimony
    NONE = auto()               # لا أساس            — no trust basis


class TrustLevel(Enum):
    """مستوى الثقة — degree of trust assigned to a source."""

    LOW = auto()        # منخفض      — low trust
    MEDIUM = auto()     # متوسط      — medium trust
    HIGH = auto()       # عالي       — high trust


# ── Utterance / sender / style ──────────────────────────────────────


class UtteranceMode(Enum):
    """نمط الملفوظ — mode of utterance production."""

    STATEMENT = auto()      # خبر        — statement / declarative utterance
    QUESTION = auto()       # سؤال       — interrogative utterance
    COMMAND = auto()        # أمر        — imperative utterance
    REPORT = auto()         # تقرير      — report utterance
    EXPLANATION = auto()    # تفسير      — explanatory utterance
    DIALOGUE_TURN = auto()  # دور حوار  — turn in dialogue


class SenderRoleType(Enum):
    """نوع دور المُرسِل — role played by the sender in a discourse."""

    SOURCE = auto()         # مصدر       — source / narrator role
    EXPLAINER = auto()      # مُفسِّر   — explaining role
    WITNESS = auto()        # شاهد       — witness role
    TEACHER = auto()        # معلِّم     — teaching role
    COMMANDER = auto()      # آمر        — commanding role
    QUESTIONER = auto()     # مُستفسِر  — questioning role
    INTERPRETER = auto()    # مُفسِّر   — interpreting role


class StyleKind(Enum):
    """نوع الأسلوب — discourse / rhetorical style kind."""

    KHABAR = auto()         # خبر        — declarative / informative
    INSHA = auto()          # إنشاء      — performative / creative
    QUESTION = auto()       # استفهام    — interrogative style
    ANSWER = auto()         # جواب       — answer style
    COMMAND = auto()        # أمر        — directive / command
    PROHIBITION = auto()    # نهي        — prohibitive
    EXPLANATION = auto()    # تفسير      — explanatory style
    ARGUMENT = auto()       # جدل        — argumentative style
    TESTIMONY = auto()      # شهادة      — testimony style
    SYMBOLIC = auto()       # رمزي       — symbolic / figurative


# ── Validation outcome / state ──────────────────────────────────────


class ValidationOutcome(Enum):
    """نتيجة التحقق — outcome of a validation check."""

    VALID = auto()                      # صحيح           — valid result
    INVALID = auto()                    # غير صحيح       — invalid result
    PENDING = auto()                    # معلَّق         — pending / deferred
    REJECTED_METHODOLOGICALLY = auto()  # مرفوض منهجيًّا — rejected on method grounds


class ValidationState(Enum):
    """حالة التحقق — current state of a validation process."""

    PENDING = auto()        # معلَّق         — not yet validated
    VALID = auto()          # صحيح           — validated and valid
    INVALID = auto()        # غير صحيح       — validated and invalid


# ── Discourse-exchange enums ─────────────────────────────────────────


class AuthorityLevel(Enum):
    """مستوى السلطة — authority level of a discourse participant."""

    LOW = auto()        # منخفض      — low authority
    MEDIUM = auto()     # متوسط      — medium authority
    HIGH = auto()       # عالي       — high authority


class CarrierClass(Enum):
    """صنف الحامل الخطابي — class of the discourse carrier."""

    UTTERANCE = auto()  # ملفوظ      — utterance carrier
    CONCEPT = auto()    # مفهوم      — conceptual carrier
    BOTH = auto()       # كلاهما     — utterance + concept


class ExchangeType(Enum):
    """نوع التبادل الخطابي — discourse exchange type."""

    REPORT = auto()         # تقرير      — reporting exchange
    TEACHING = auto()       # تعليم      — teaching exchange
    QUESTION = auto()       # سؤال       — question exchange
    ANSWER = auto()         # جواب       — answer exchange
    COMMAND = auto()        # أمر        — command exchange
    WARNING = auto()        # تحذير      — warning exchange
    PERSUASION = auto()     # إقناع      — persuasion exchange
    NEGOTIATION = auto()    # تفاوض      — negotiation exchange
    TESTIMONY = auto()      # شهادة      — testimony exchange
    EXPLANATION = auto()    # تفسير      — explanatory exchange


class ExchangePurposeType(Enum):
    """نوع غرض التبادل — purpose type of a discourse exchange."""

    INFORM = auto()                 # إخبار          — informing
    TEACH = auto()                  # تعليم          — teaching
    VERIFY = auto()                 # تحقق           — verification
    GUIDE = auto()                  # توجيه          — guidance
    BIND = auto()                   # إلزام          — binding / obligating
    PERSUADE = auto()               # إقناع          — persuasion
    WARN = auto()                   # تحذير          — warning
    REQUEST = auto()                # طلب            — request
    TEST = auto()                   # اختبار         — testing
    PRESERVE_KNOWLEDGE = auto()     # حفظ المعرفة   — knowledge preservation


class ExchangeStyleType(Enum):
    """نوع أسلوب التبادل — stylistic type of a discourse exchange."""

    KHABARI = auto()        # خبري       — informative / declarative
    INSHAI = auto()         # إنشائي     — performative / creative
    EXPLANATORY = auto()    # تفسيري     — explanatory
    ARGUMENTATIVE = auto()  # جدلي       — argumentative
    DIRECTIVE = auto()      # توجيهي     — directive
    INTERROGATIVE = auto()  # استفهامي   — interrogative
    PEDAGOGICAL = auto()    # تعليمي     — pedagogical
    TESTIMONIAL = auto()    # شهادي      — testimonial


class ExchangeStatus(Enum):
    """حالة التبادل — status of a discourse exchange."""

    DRAFTED = auto()        # مسودة      — draft / not yet transmitted
    TRANSMITTED = auto()    # مُرسَل     — transmitted
    RECEIVED = auto()       # مُستقبَل   — received
    INTERPRETED = auto()    # مُفسَّر    — interpreted
    ACCEPTED = auto()       # مقبول      — accepted
    REJECTED = auto()       # مرفوض      — rejected
    SUSPENDED = auto()      # معلَّق     — suspended


class PurposeType(Enum):
    """نوع الغرض — communicative purpose type."""

    INFORM = auto()             # إخبار          — informing
    INSTRUCT = auto()           # توجيه          — instructing
    PERSUADE = auto()           # إقناع          — persuasion
    TEST = auto()               # اختبار         — testing
    QUERY = auto()              # استفسار        — querying
    PRESERVE = auto()           # حفظ            — preservation
    REFUTE = auto()             # دحض            — refutation
    WARN = auto()               # تحذير          — warning
    REQUEST_ACTION = auto()     # طلب فعل        — request for action
    CLARIFY = auto()            # توضيح          — clarification


class ExplicitnessLevel(Enum):
    """مستوى الصراحة — explicitness level of an utterance or style."""

    DIRECT = auto()         # صريح       — direct / explicit
    SEMI_DIRECT = auto()    # شبه صريح   — semi-direct
    IMPLICIT = auto()       # ضمني       — implicit / indirect


class ReceptionStateType(Enum):
    """نوع حالة الاستقبال — type of reception state."""

    RECEIVED = auto()               # مُستقبَل           — received
    UNDERSTOOD = auto()             # مفهوم              — understood
    MISUNDERSTOOD = auto()          # مُساء فهمه         — misunderstood
    ACCEPTED = auto()               # مقبول              — accepted
    REJECTED = auto()               # مرفوض              — rejected
    SUSPENDED = auto()              # معلَّق             — suspended
    PARTIALLY_UNDERSTOOD = auto()   # مفهوم جزئيًّا     — partially understood


class InterpretiveOutcomeType(Enum):
    """نوع نتيجة التأويل — type of interpretive outcome."""

    ALIGNED = auto()        # متوافق     — aligned with intent
    NARROWED = auto()       # مُضيَّق    — narrowed interpretation
    EXPANDED = auto()       # مُوسَّع   — expanded interpretation
    DISTORTED = auto()      # مشوَّه     — distorted interpretation
    CONFLICTING = auto()    # متعارض     — conflicting interpretation
    UNRESOLVED = auto()     # غير محلول  — unresolved interpretation


class GapSeverity(Enum):
    """خطورة الفجوة — severity of a discourse or epistemic gap."""

    MODERATE = auto()   # متوسط      — moderate gap
    CRITICAL = auto()   # حرج        — critical gap
    FATAL = auto()      # قاتل       — fatal / blocking gap
    MINOR = auto()      # بسيط       — minor gap
    HIGH = CRITICAL     # backward-compat alias for CRITICAL
    MEDIUM = MODERATE   # backward-compat alias for MODERATE


class DiscourseGapType(Enum):
    """نوع الفجوة الخطابية — type of discourse gap."""

    MISSING_SENDER = auto()                 # مُرسِل مفقود
    MISSING_RECEIVER = auto()               # مُستقبِل مفقود
    MISSING_PURPOSE = auto()                # غرض مفقود
    MISSING_STYLE = auto()                  # أسلوب مفقود
    MISSING_CARRIER = auto()                # حامل مفقود
    INVALID_CARRIER = auto()                # حامل غير صالح
    MISSING_RECEPTION = auto()              # استقبال مفقود
    MISSING_RECEPTION_STATE = auto()        # حالة استقبال مفقودة
    MISSING_TRUST_PROFILE = auto()          # ملف ثقة مفقود
    MISSING_TRANSFERRED_KNOWLEDGE = auto()  # معرفة منقولة مفقودة
    INVALID_TRANSFERRED_KNOWLEDGE = auto()  # معرفة منقولة غير صالحة
    INVALID_STYLE_PURPOSE_FIT = auto()      # أسلوب لا يناسب الغرض
    SENDER_PURPOSE_MISMATCH = auto()        # تعارض المُرسِل والغرض
    RECEPTION_INCONSISTENCY = auto()        # تناقض الاستقبال


class DiscourseValidationOutcome(Enum):
    """نتيجة التحقق الخطابي — validation outcome for a discourse exchange."""

    VALID = auto()      # صحيح       — discourse is valid
    INVALID = auto()    # غير صحيح   — discourse is invalid
    INCOMPLETE = auto() # غير مكتمل  — discourse is incomplete


# ── Epistemic-engine enums ───────────────────────────────────────────


class EpistemicRank(Enum):
    """الرتبة المعرفية — epistemic / certainty rank of a knowledge episode."""

    CERTAIN = auto()             # قطعي           — fully certain
    TRUE_NON_CERTAIN = auto()    # صحيح ظني       — true but non-certain
    PROBABILISTIC_DOUBT = auto() # شك احتمالي    — probabilistic doubt
    IMPOSSIBLE = auto()          # مستحيل         — logically impossible


class InsertionPolicy(Enum):
    """سياسة الإدخال — policy for inserting knowledge into the graph."""

    FOUNDATIONAL = auto()   # أساسي      — foundational (certain) knowledge
    ADMISSIBLE = auto()     # مقبول      — admissible (non-certain) knowledge
    GUARDED = auto()        # محروس      — guarded (doubtful) knowledge
    BLOCKED = auto()        # محجوب      — blocked (invalid/impossible)


class ContaminationLevel(Enum):
    """مستوى التلوث — opinion-contamination level of an epistemic operation."""

    NONE = auto()       # لا تلوث    — no contamination
    LOW = auto()        # منخفض      — low contamination
    MEDIUM = auto()     # متوسط      — medium contamination
    HIGH = auto()       # عالي       — high contamination


class RealityKind(Enum):
    """نوع الواقع — kind of reality anchor for a knowledge episode."""

    MATERIAL = auto()       # مادي           — material / physical reality
    ABSTRACT = auto()       # تجريدي         — abstract / conceptual reality
    RATIONAL = auto()       # عقلي           — rational / logical reality
    SOCIAL = auto()         # اجتماعي        — social / institutional reality
    HISTORICAL = auto()     # تاريخي         — historical reality
    PHYSICAL_OBJECT = auto() # جسم مادي      — concrete physical object
    EVENT = auto()          # حدث            — event / occurrence
    TEXT_OBJECT = auto()    # نص             — textual object


class CarrierType(Enum):
    """نوع الحامل اللغوي — type of linguistic carrier in epistemic context."""

    UTTERANCE = auto()  # ملفوظ      — utterance carrier
    CONCEPT = auto()    # مفهوم      — conceptual carrier
    BOTH = auto()       # كلاهما     — both utterance and concept


class DecisionCode(Enum):
    """رمز القرار — decision / error code from the epistemic validator."""

    EPI001_MISSING_REALITY = auto()             # واقع مفقود
    EPI002_MISSING_SENSE = auto()               # حس مفقود
    EPI003_MISSING_PRIOR_INFO = auto()          # معلومة سابقة مفقودة
    EPI004_OPINION_CONTAMINATION = auto()       # تلوث رأي
    EPI005_MISSING_LINKING = auto()             # ربط مفقود
    EPI006_MISSING_JUDGEMENT = auto()           # حكم مفقود
    EPI007_MISSING_METHOD = auto()              # منهج مفقود
    EPI008_METHOD_FIT_FAILURE = auto()          # فشل ملاءمة المنهج
    EPI009_CARRIER_INVALID = auto()             # حامل غير صالح
    EPI010_MISSING_PROOF_PATH = auto()          # مسار إثبات مفقود
    EPI011_MISSING_CONFLICT_RULE = auto()       # قاعدة تعارض مفقودة
    EPI012_CARRIER_BOTH_MISSING = auto()        # كلا الحاملين مفقودان
    EPI013_PROOF_METHOD_MISMATCH = auto()       # تعارض المنهج ومسار الإثبات
    EPI014_UTTERANCE_CONCEPT_CONFLICT = auto()  # تعارض الملفوظ والمفهوم


# ── Info kind ───────────────────────────────────────────────────────


class InfoKind(Enum):
    """نوع المعلومة السابقة — kind of prior information in a knowledge episode."""

    LEXICAL = auto()        # معجمي          — lexical information
    ENCYCLOPEDIC = auto()   # موسوعي         — encyclopedic / world knowledge
    CAUSAL = auto()         # سببي           — causal background
    CONTEXTUAL = auto()     # سياقي          — contextual background
    TESTIMONIAL = auto()    # شهادي          — testimonial prior info
    FORMAL = auto()         # صوري           — formal / logical prior


# ── Rational-self / receiver / reception ────────────────────────────


class RationalSelfKind(Enum):
    """نوع الذات العاقلة — kind of rational self participating in discourse."""

    INDIVIDUAL = auto()     # فردي           — individual rational agent
    COLLECTIVE = auto()     # جماعي          — collective / group agent
    INSTITUTIONAL = auto()  # مؤسسي          — institutional agent
    MODELED_AGENT = auto()  # عامل نموذجي    — modeled / virtual agent


class ReceiverRoleType(Enum):
    """نوع دور المُستقبِل — role played by the receiver in a discourse."""

    LISTENER = auto()       # مستمع          — passive listener
    LEARNER = auto()        # متعلِّم        — active learner
    EXAMINER = auto()       # فاحص           — examiner / evaluator
    ADDRESSEE = auto()      # مُخاطَب        — direct addressee
    RESPONDENT = auto()     # مُجيب          — respondent / answerer
    EVALUATOR = auto()      # مُقيِّم        — evaluator / assessor


class ReceiverExpectedAction(Enum):
    """الفعل المتوقع من المستقبِل — expected action from the receiver."""

    UNDERSTAND = auto()     # يفهم       — expected to understand
    VERIFY = auto()         # يتحقق      — expected to verify
    ACT = auto()            # يتصرف      — expected to act
    ANSWER = auto()         # يجيب       — expected to answer
    PRESERVE = auto()       # يحفظ       — expected to preserve
    RELAY = auto()          # يُوصِّل   — expected to relay / transmit


class ReceptionMode(Enum):
    """نمط الاستقبال — mode of receiving a discourse."""

    HEARD = auto()          # سمعي       — heard / auditory reception
    READ = auto()           # مقروء      — read / written reception
    OBSERVED = auto()       # مرئي       — observed / visual reception
    INFERRED = auto()       # مستنتَج    — inferred reception
    RECALLED = auto()       # متذكَّر    — recalled from memory


class ReceiverState(Enum):
    """حالة المستقبِل — cognitive/attentional state of the receiver."""

    OPEN = auto()           # منفتح      — open and receptive
    RESISTANT = auto()      # مقاوم      — resistant / closed
    BIASED = auto()         # متحيِّز    — biased
    UNCERTAIN = auto()      # متردِّد    — uncertain / hesitant
    ATTENTIVE = auto()      # منتبه      — actively attentive


# ── Fractal Kernel enums ─────────────────────────────────────────────


class ActivationStage(Enum):
    """مرحلة التنشيط — activation stage in the fractal kernel."""

    SIGNAL = auto()
    MORPHOLOGY = auto()
    CONCEPT = auto()
    AXIS = auto()
    RELATION = auto()
    ROLE = auto()
    FACTOR = auto()
    CASE = auto()
    JUDGEMENT = auto()


class HypothesisStatus(Enum):
    """حالة الفرضية — status of a hypothesis node."""

    ACTIVE = auto()
    PRUNED = auto()
    STABILIZED = auto()
    SUSPENDED = auto()
    REVISED = auto()


class ConstraintStrength(Enum):
    """قوة القيد — strength of a constraint in the kernel."""

    ABSOLUTE = auto()
    STRONG = auto()
    MODERATE = auto()
    TENTATIVE = auto()
    WEAK = auto()


class ConflictState(Enum):
    """حالة التعارض — conflict state between kernel nodes."""

    NONE = auto()
    SOFT = auto()
    HARD = auto()
    UNRESOLVED = auto()


class RevisionType(Enum):
    """نوع المراجعة — type of belief revision."""

    CONFLICT_RESOLUTION = auto()
    EXTERNAL_EVIDENCE = auto()
    EXPANSION = auto()
    CONTRACTION = auto()
    REVISION = auto()


class SignalType(Enum):
    """نوع الإشارة — type of signal in the kernel."""

    BASE_LETTER = auto()
    DIACRITIC = auto()
    NUMERAL = auto()
    WHITESPACE = auto()
    PUNCTUATION = auto()
    UNKNOWN = auto()


# ── Strict 7-Layer System enums ──────────────────────────────────────


class StrictLayerID(Enum):
    """معرّف الطبقة الصارمة — layer identifier in the strict 7-layer system."""

    MENTAL_FOUNDATION = auto()
    GENERATIVE = auto()
    AUDITORY_MINIMUM = auto()
    STRUCTURAL = auto()
    TRANSFORMATION = auto()
    HIGHER_FUNCTION = auto()
    PROGRAMMATIC = auto()


class AuditoryNode(Enum):
    """عقدة الطبقة السمعية — node type in the auditory/phonological layer."""

    PHONEME = auto()
    SYLLABLE = auto()
    WORD_FORM = auto()
    PROSODIC = auto()
    ONSET = auto()
    NUCLEUS = auto()
    CODA = auto()


class StructuralNode(Enum):
    """عقدة بنيوية — structural node type."""

    ROOT = auto()
    PATTERN = auto()
    MORPHEME = auto()
    WORD = auto()
    AFFIX = auto()
    PREFIX = auto()
    SUFFIX = auto()
    CLITIC = auto()
    STEM = auto()


class TransformationNode(Enum):
    """عقدة التحول — transformation node type."""

    INPUT = auto()
    RULE = auto()
    OUTPUT = auto()
    TRIGGER = auto()
    CONTEXT = auto()
    RESULT = auto()
    INTERMEDIATE = auto()
    EXCEPTION = auto()


class MentalPrimitive(Enum):
    """البدائي الذهني — mental primitive type."""

    CONCEPT = auto()
    RELATION = auto()
    SCHEMA = auto()
    SCRIPT = auto()
    EVENT = auto()
    PROPERTY = auto()
    INDIVIDUAL = auto()
    PROCESS = auto()
    FRAME = auto()


class MentalEdgeType(Enum):
    """نوع الحافة الذهنية — mental graph edge type."""

    ASSOCIATION = auto()
    CAUSAL = auto()
    HIERARCHICAL = auto()
    TEMPORAL = auto()
    SPATIAL = auto()
    INSTRUMENTAL = auto()
    CONDITIONAL = auto()


class LayerEdgeType(Enum):
    """نوع الحافة بين الطبقات — edge type between system layers."""

    PROJECTION = auto()
    REALIZATION = auto()
    CONSTRAINT = auto()
    FEEDBACK = auto()
    ACTIVATION = auto()
    INHIBITION = auto()
    SUPPORT = auto()
    CONFLICT = auto()
    INHERITANCE = auto()
    COMPOSITION = auto()
    DEPENDENCY = auto()
    ENTAILMENT = auto()
    ANALOGY = auto()
    REVISION = auto()
    ENDORSEMENT = auto()
    CONTRADICTION = auto()
    ELABORATION = auto()
    SPECIFICATION = auto()
    GENERALIZATION = auto()
    INSTANCE = auto()
    PART_OF = auto()
    CAUSE = auto()
    EFFECT = auto()
    CONDITION = auto()
    CONCESSION = auto()
    CONTRAST = auto()
    PARALLEL = auto()
    TEMPORAL = auto()
    SPATIAL = auto()


class JudgmentCategory(Enum):
    """فئة الحكم — judgment category in layer 5."""

    ORIGINAL = auto()
    AUGMENTED = auto()
    SUBSTITUTED = auto()
    DELETED = auto()
    WEAKENED_TRANSFORMED = auto()
    ASSIMILATED = auto()
    ATTACHED_MARKER = auto()
    DEICTIC_BUILDER = auto()
    RELATIONAL_CONNECTOR = auto()


class GenerativeNode(Enum):
    """عقدة توليدية — generative node type."""

    BASE = auto()
    DERIVED = auto()
    COMPOUND = auto()
    PATTERN = auto()
    BROKEN_PLURAL = auto()
    VERBAL_NOUN = auto()
    PARTICIPLE = auto()
    DIMINUTIVE = auto()


class RepresentationNode(Enum):
    """عقدة تمثيلية — representation node type."""

    LEXICAL = auto()
    MORPHOLOGICAL = auto()
    SYNTACTIC = auto()
    SEMANTIC = auto()
    PRAGMATIC = auto()
    PHONOLOGICAL = auto()
    GRAPHEMIC = auto()
    DIACRITIC = auto()
    PROSODIC = auto()
    DISCOURSE = auto()


class TransitionGateStatus(Enum):
    """حالة بوابة الانتقال — status of a transition gate."""

    PASSED = auto()
    BLOCKED = auto()
    INSUFFICIENT_DATA = auto()


# ── Masdar (verbal noun) enums ──────────────────────────────────────


class MasdarType(Enum):
    """نوع المصدر — classification of the verbal noun.

    ORIGINAL   — المصدر الأصلي  (e.g. كِتابة، خُروج)
    MIMI       — المصدر الميمي  (e.g. مَكْتَب → مَوْعِد)
    INDUSTRIAL — المصدر الصناعي (e.g. إنسانية، حرية)
    MARRAH     — مصدر المرة     (e.g. ضَرْبة واحدة)
    HAY2A      — مصدر الهيئة    (e.g. جِلْسة، مِشْية)
    MUAWWAL    — المصدر المؤوّل  (أن + فعل)
    """

    ORIGINAL = auto()
    MIMI = auto()
    INDUSTRIAL = auto()
    MARRAH = auto()
    HAY2A = auto()
    MUAWWAL = auto()


class MasdarBab(Enum):
    """باب المصدر — morphological masdar pattern (verb form → masdar weight).

    Tri-literal base forms (الثلاثي المجرد):
        FA3L, FI3ALA, FU3UL, FA3AL, FA3IL, FU3AL

    Augmented forms (الثلاثي المزيد):
        IF3AL, TAF3IL, MUFA3ALA, INFI3AL, IFTI3AL,
        TAFA33UL, TAFA3UL, IF3I3AL, ISTIF3AL
    """

    # Tri-literal base (أبواب الثلاثي المجرد)
    FA3L = auto()       # فَعْل   (e.g. ضَرْب، فَتْح)
    FI3ALA = auto()     # فِعالة  (e.g. كِتابة، صِناعة)
    FU3UL = auto()      # فُعول   (e.g. خُروج، دُخول)
    FA3AL = auto()      # فَعَل   (e.g. طَلَب، عَمَل)
    FA3IL = auto()      # فَعِيل  (e.g. رَحيل، صَهيل)
    FU3AL = auto()      # فُعال   (e.g. سُعال، دُعاء)
    # Augmented forms (أبواب المزيد)
    IF3AL = auto()      # إفعال   (e.g. إكرام، إسلام)
    TAF3IL = auto()     # تفعيل   (e.g. تعليم، تكريم)
    MUFA3ALA = auto()   # مُفاعلة (e.g. مُقاتلة، مُكاتبة)
    INFI3AL = auto()    # انفعال  (e.g. انكسار، انفتاح)
    IFTI3AL = auto()    # افتعال  (e.g. اجتماع، اقتراح)
    TAFA33UL = auto()   # تَفَعُّل (e.g. تَعَلُّم، تَقَدُّم)
    TAFA3UL = auto()    # تَفاعُل (e.g. تَعاوُن، تَبادُل)
    IF3I3AL = auto()    # افعِلال (e.g. احمرار، اصفرار)
    ISTIF3AL = auto()   # استفعال (e.g. استغفار، استخراج)


class DerivationTarget(Enum):
    """هدف الاشتقاق — what can be derived from a masdar.

    Each target corresponds to a derivational output type that branches
    from the masdar as a fractal node.
    """

    FI3L = auto()             # فعل        — verb
    ISM_FA3IL = auto()        # اسم فاعل   — active participle
    ISM_MAF3UL = auto()       # اسم مفعول  — passive participle
    ISM_ZAMAN = auto()        # اسم زمان   — noun of time
    ISM_MAKAN = auto()        # اسم مكان   — noun of place
    ISM_HAY2A = auto()        # اسم هيئة   — noun of manner
    ISM_ALA = auto()          # اسم آلة    — noun of instrument
    SIFA_MUSHABBAHA = auto()  # صفة مشبهة  — resembling adjective
    ISM_TAFDIL = auto()       # اسم تفضيل  — elative / comparative


class KawnType(Enum):
    """نوع الكينونة — ontological being-mode.

    WUJUDI        — كينونة وجودية  (existential being — static nouns)
    TAHAWWULI     — كينونة تحولية  (transformational being — verbs/events)
    MASDAR_BRIDGE — عقدة الربط المصدرية (bridge node linking both)
    """

    WUJUDI = auto()
    TAHAWWULI = auto()
    MASDAR_BRIDGE = auto()


# ── Epistemic Reception Constitution v1 ─────────────────────────────


class SubjectGenre(Enum):
    """أجناس الموضوع الوارد — supreme genres of incoming subject matter (Art. 5).

    WUJUD  — وجود  : what establishes the thing, self, referent, or entity
    SIFA   — صفة   : what establishes the quality, state, or description
    HADATH — حدث   : what establishes occurrence, change, becoming, or actuality
    NISBA  — نسبة  : what establishes linkage, direction, or connection
    """

    WUJUD = auto()   # وجود — existence
    SIFA = auto()    # صفة — attribute
    HADATH = auto()  # حدث — event
    NISBA = auto()   # نسبة — relation


class ReceptionRank(Enum):
    """رتب التلقي — ordered ranks of reception and processing (Art. 13).

    HISS    — حس     : first input via direct or quasi-direct effect
    SHUUUR  — شعور   : living internal effect (acceptance, aversion, etc.)
    FIKR    — فكر    : binding perceived subject with prior info for meaning
    NIYYA   — نية    : determining direction of purpose after disclosure
    KHIYAR  — خيار   : opening possible alternatives after determination
    IRADA   — إرادة  : enacting one of the chosen alternatives with resolve
    """

    HISS = auto()    # حس — sense
    SHUUUR = auto()  # شعور — feeling
    FIKR = auto()    # فكر — thought
    NIYYA = auto()   # نية — intention
    KHIYAR = auto()  # خيار — choice
    IRADA = auto()   # إرادة — will


class ReceptionLayer(Enum):
    """الطبقات الكبرى داخل محور التلقي — major layers (Art. 14).

    ISTIQBAL          — استقبال          : reception (sense, feeling)
    MUALAJA_MARIFIYYA — معالجة معرفية    : cognitive processing (thought)
    TAWJIH            — توجيه            : pre-judgment direction (intention, choice, will)
    """

    ISTIQBAL = auto()           # استقبال — reception
    MUALAJA_MARIFIYYA = auto()  # معالجة معرفية — cognitive processing
    TAWJIH = auto()             # توجيه — pre-judgment direction


class CarryingMode(Enum):
    """معيار الحمل — whether a reception rank carries a subject genre (Arts. 36–38).

    ASIL    — أصيل   : the rank carries the genre directly and primarily
    TABI    — تبعي   : the rank carries it via another or partially
    MUMTANI — ممتنع  : invalid to attribute this genre to this rank
    """

    ASIL = auto()     # أصيل — original
    TABI = auto()     # تبعي — subsidiary
    MUMTANI = auto()  # ممتنع — prohibited


class ReceptionDecisionCode(Enum):
    """رموز قرار الاستقبال المعرفي — decision codes for reception validation."""

    REC001_SUBJECT_GENRE_UNRESOLVED = auto()  # جنس الموضوع غير محدد
    REC002_AXIS_CONFUSION = auto()            # خلط بين المحورين
    REC003_SENSE_OVERREACH = auto()           # إفراط في نسبة الإغلاق للحس
    REC004_FEELING_AS_JUDGMENT = auto()       # معاملة الشعور كحكم
    REC005_INTENTION_AS_RECEPTION = auto()    # معاملة النية كاستقبال أولي
    REC006_WILL_AS_DETERMINATION = auto()     # معاملة الإرادة كتعيين أصلي
    REC007_CARRYING_VIOLATION = auto()        # حمل ممتنع
    REC008_RANK_ORDER_VIOLATION = auto()      # خلل في ترتيب الرتب


class ReceptionValidationOutcome(Enum):
    """نتيجة التحقق من الاستقبال المعرفي — reception validation outcome."""

    ACCEPTED = auto()                  # مقبول — passes all constitutional checks
    REJECTED_CONSTITUTIONALLY = auto()  # مرفوض دستوريًا — violates articles
    INCOMPLETE = auto()                # غير مكتمل — subject not fully classified


# ── Semantic Direction Space Constitution v1 ────────────────────────


class SemanticDirectionGenus(Enum):
    """الأجناس العليا للجهات — supreme genera of semantic directions (Art. 1–5).

    These classify the *intrinsic semantic bearing* of a word before any
    reception or judgment.  Logically distinct from :class:`SubjectGenre`
    which classifies what arrives to the rational self.

    WUJUD  — وجود  : existence — what establishes being
    SIFA   — صفة   : attribute — what describes quality or state
    HADATH — حدث   : event — what establishes occurrence or change
    NISBA  — نسبة  : relation — what establishes linkage or direction
    """

    WUJUD = auto()   # وجود — existence
    SIFA = auto()    # صفة — attribute
    HADATH = auto()  # حدث — event
    NISBA = auto()   # نسبة — relation


class DerivationalDirection(Enum):
    """الجهات الاشتقاقية المركزية — core derivational directions (Art. 6–12).

    Each value represents a direction that a root can project into via
    morphological derivation.  Extends :class:`DerivationTarget` with
    direction-aware classification.

    ISM_FA3IL       — اسم فاعل   : active participle
    ISM_MAF3UL      — اسم مفعول  : passive participle
    ISM_ZAMAN       — اسم زمان   : noun of time
    ISM_MAKAN       — اسم مكان   : noun of place
    ISM_ALA         — اسم آلة    : noun of instrument
    ISM_HAY2A       — اسم هيئة   : noun of manner
    ISM_TAFDIL      — اسم تفضيل  : elative / comparative
    SIFA_MUSHABBAHA — صفة مشبهة  : resembling adjective
    MASDAR          — مصدر       : verbal noun
    FI3L_MADI       — فعل ماضٍ   : past-tense verb
    FI3L_MUDARI3    — فعل مضارع  : present-tense verb
    FI3L_AMR        — فعل أمر    : imperative verb
    ISM_JAMID       — اسم جامد   : non-derived (rigid) noun
    """

    ISM_FA3IL = auto()        # اسم فاعل — active participle
    ISM_MAF3UL = auto()       # اسم مفعول — passive participle
    ISM_ZAMAN = auto()        # اسم زمان — noun of time
    ISM_MAKAN = auto()        # اسم مكان — noun of place
    ISM_ALA = auto()          # اسم آلة — noun of instrument
    ISM_HAY2A = auto()        # اسم هيئة — noun of manner
    ISM_TAFDIL = auto()       # اسم تفضيل — elative / comparative
    SIFA_MUSHABBAHA = auto()  # صفة مشبهة — resembling adjective
    MASDAR = auto()           # مصدر — verbal noun
    FI3L_MADI = auto()        # فعل ماضٍ — past-tense verb
    FI3L_MUDARI3 = auto()     # فعل مضارع — present-tense verb
    FI3L_AMR = auto()         # فعل أمر — imperative verb
    ISM_JAMID = auto()        # اسم جامد — rigid noun


class DirectionRelation(Enum):
    """العلاقات بين الجهات — permitted relations between directions (Art. 34–40).

    WIRATHA       — الوراثة         : direction inherits from a parent
    TAWAFUQ       — التوافق         : two directions may co-occur
    MAN3          — المنع           : two directions are mutually exclusive
    TAHAWWUL      — التحول          : one transforms into another
    ISHTIRAT      — الاشتراط        : one requires another as precondition
    ISQAT_TARKIBI — الإسقاط التركيبي : projects into syntactic structure
    RADD          — الردّ            : rejects or reverses another
    """

    WIRATHA = auto()        # الوراثة — inheritance
    TAWAFUQ = auto()        # التوافق — compatibility
    MAN3 = auto()           # المنع — prohibition
    TAHAWWUL = auto()       # التحول — transformation
    ISHTIRAT = auto()       # الاشتراط — conditioning
    ISQAT_TARKIBI = auto()  # الإسقاط التركيبي — syntactic projection
    RADD = auto()           # الردّ — return / rejection


class DirectionBoundary(Enum):
    """الفواصل الحدّية — boundary types between directions (Art. 13–19).

    HADD_FASIL     — حد فاصل    : absolute boundary — no overlap
    HADD_INTIQALI  — حد انتقالي : transitional boundary — gradual shift
    HADD_MUSHTARAK — حد مشترك   : shared boundary — partial overlap
    """

    HADD_FASIL = auto()      # حد فاصل — absolute boundary
    HADD_INTIQALI = auto()   # حد انتقالي — transitional boundary
    HADD_MUSHTARAK = auto()  # حد مشترك — shared boundary


# ── Weight Fractal Constitution v1 ──────────────────────────────────


class WeightCarryingMode(Enum):
    """معيار حمل الوزن — how a weight carries a semantic direction (Art. 11–15).

    ASLI     — أصلي    : weight carries the direction originally and directly
    TABI3I   — تابعي   : weight carries it via subsidiary derivation
    MUSHTAQ  — مشتق    : weight carries it through derived re-projection
    MUMTANI3 — ممتنع   : impossible for this weight to carry this direction
    """

    ASLI = auto()      # أصلي — original / direct carrying
    TABI3I = auto()    # تابعي — subsidiary carrying
    MUSHTAQ = auto()   # مشتق — derived carrying
    MUMTANI3 = auto()  # ممتنع — impossible carrying


class WeightFractalPhase(Enum):
    """أطوار الدورة الفراكتالية للوزن — phases of weight fractal cycle (Art. 16–20).

    TA3YIN  — تعيين  : assignment — declaring the weight identity
    TAMYIZ  — تمييز  : distinction — distinguishing from other weights
    TAHMIL  — تحميل  : loading — assigning a semantic direction to carry
    TAHQIQ  — تحقيق  : verification — proving weight↔direction non-arbitrary
    TAWLID  — توليد  : generation — producing derived fractal nodes
    RADD    — ردّ    : return to source — tracing back to root+weight origin
    """

    TA3YIN = auto()  # تعيين — assignment
    TAMYIZ = auto()  # تمييز — distinction
    TAHMIL = auto()  # تحميل — loading
    TAHQIQ = auto()  # تحقيق — verification
    TAWLID = auto()  # توليد — generation
    RADD = auto()    # ردّ — return to source


class WeightClass(Enum):
    """تصنيف الوزن الصرفي — morphological weight classification (Art. 1–5).

    THULATHI_MUJARRAD — ثلاثي مجرد  : base tri-literal
    THULATHI_MAZEED  — ثلاثي مزيد   : augmented tri-literal
    RUBA3I_MUJARRAD  — رباعي مجرد   : base quadri-literal
    RUBA3I_MAZEED    — رباعي مزيد   : augmented quadri-literal
    KHUMASI          — خماسي        : quinqui-literal
    """

    THULATHI_MUJARRAD = auto()  # ثلاثي مجرد — base tri-literal
    THULATHI_MAZEED = auto()    # ثلاثي مزيد — augmented tri-literal
    RUBA3I_MUJARRAD = auto()    # رباعي مجرد — base quadri-literal
    RUBA3I_MAZEED = auto()      # رباعي مزيد — augmented quadri-literal
    KHUMASI = auto()            # خماسي — quinqui-literal


class WeightKind(Enum):
    """نوع الوزن — distinguishes productive weights from closed templates (Art. 4–8).

    PRODUCTIVE      — منتج        : active derivational weight
    CLOSED_TEMPLATE — قالب مغلق   : non-generative fixed template
    MEASURE_ONLY    — قياسي فقط   : measurable but non-productive
    """

    PRODUCTIVE = auto()       # منتج — active derivational weight
    CLOSED_TEMPLATE = auto()  # قالب مغلق — non-generative fixed template
    MEASURE_ONLY = auto()     # قياسي فقط — measurable but non-productive


class WeightPossibilityDimension(Enum):
    """أبعاد شرط الإمكان للوزن — 6 dimensions of weight possibility (Art. 9–17).

    BINYAWI  — بنيوي   : structural possibility
    MAQTA3I  — مقطعي   : syllabic possibility
    SARFI    — صرفي    : morphological possibility
    DALALI   — دلالي   : semantic possibility
    TAWLIDI  — توليدي  : generative possibility
    RADDI    — ردّي    : return / trace-back possibility
    """

    BINYAWI = auto()   # بنيوي — structural
    MAQTA3I = auto()   # مقطعي — syllabic
    SARFI = auto()     # صرفي — morphological
    DALALI = auto()    # دلالي — semantic
    TAWLIDI = auto()   # توليدي — generative
    RADDI = auto()     # ردّي — return / trace-back


class ThulathiBab(Enum):
    """أبواب الثلاثي المجرد — trilateral base verb doors (Art. 43–46).

    FA3ALA_YAF3ULU — فَعَلَ يَفْعُلُ
    FA3ALA_YAF3ILU — فَعَلَ يَفْعِلُ
    FA3ALA_YAF3ALU — فَعَلَ يَفْعَلُ
    FA3ILA_YAF3ALU — فَعِلَ يَفْعَلُ
    FA3ULA_YAF3ULU — فَعُلَ يَفْعُلُ
    """

    FA3ALA_YAF3ULU = auto()  # فَعَلَ يَفْعُلُ
    FA3ALA_YAF3ILU = auto()  # فَعَلَ يَفْعِلُ
    FA3ALA_YAF3ALU = auto()  # فَعَلَ يَفْعَلُ
    FA3ILA_YAF3ALU = auto()  # فَعِلَ يَفْعَلُ
    FA3ULA_YAF3ULU = auto()  # فَعُلَ يَفْعُلُ


class AugmentedSemanticLayer(Enum):
    """الطبقة الدلالية للمزيد — semantic layer of augmented weights (Art. 47–50).

    SABABIYYA  — سببية   : causation
    MUSHARAKA  — مشاركة  : reciprocity / participation
    MUTAWA3A   — مطاوعة  : compliance / reflexivity
    TADARRUJ   — تدرّج   : gradation
    TALAB      — طلب     : seeking / requesting
    TAKALLUF   — تكلّف   : affectation / effort
    TAHAWWUL   — تحوّل   : transformation
    """

    SABABIYYA = auto()   # سببية — causation
    MUSHARAKA = auto()   # مشاركة — reciprocity
    MUTAWA3A = auto()    # مطاوعة — compliance / reflexivity
    TADARRUJ = auto()    # تدرّج — gradation
    TALAB = auto()       # طلب — seeking
    TAKALLUF = auto()    # تكلّف — affectation
    TAHAWWUL = auto()    # تحوّل — transformation


class NasikhCategory(Enum):
    """تصنيف النواسخ — copula/nasikh verb categories (Art. 55–58).

    KANA_WA_AKHAWAT  — كان وأخواتها  : existential / temporal copulae
    KADA_WA_AKHAWAT   — كاد وأخواتها  : near-action copulae
    ZANNA_WA_AKHAWAT  — ظنّ وأخواتها  : cognitive / epistemic copulae
    """

    KANA_WA_AKHAWAT = auto()   # كان وأخواتها
    KADA_WA_AKHAWAT = auto()   # كاد وأخواتها
    ZANNA_WA_AKHAWAT = auto()  # ظنّ وأخواتها


class WeightValidationStatus(Enum):
    """حالة قبول الوزن — weight acceptance/rejection status (Art. 63–64).

    ACCEPTED  — مقبول  : weight passes all criteria
    REJECTED  — مرفوض  : weight fails mandatory criteria
    DEFICIENT — ناقص   : weight partially meets criteria
    """

    ACCEPTED = auto()   # مقبول — passes all criteria
    REJECTED = auto()   # مرفوض — fails mandatory criteria
    DEFICIENT = auto()  # ناقص — partially meets criteria


# ── Unicode Cognitive Input Proof enums ─────────────────────────────


class CognitiveLayerID(Enum):
    """معرّف الطبقة العقلية — cognitive re-rationalisation layer (Art. 41).

    Represents the nine stages U₀–U₈ through which a Unicode input is
    re-rationalised from raw encoding to judgement-ready material.

    U₀  UNICODE_RAW          المدخل اليونيكودي الخام
    U₁  ATOMIZED             المُعطى المُعيَّن ذريًا
    U₂  DIFFERENTIATED       الذرّات المتميزة المتشاكلة
    U₃  NORMALIZED           المُعطى المُطبَّع
    U₄  DESIGNATED           المُعطى الحاضر المفروق المُعيَّن
    U₅  INITIAL_CONCEPTION   التصور الأولي
    U₆  DISCIPLINED_CONCEPTION  التصور المنضبط
    U₇  SEMANTIC_SUBJECT     الموضوع الدلالي المحرر
    U₈  JUDGEMENT_READY       المُعطى الصالح للحكم
    """

    UNICODE_RAW = auto()             # U₀ — المدخل اليونيكودي الخام
    ATOMIZED = auto()                # U₁ — التعيين الذري
    DIFFERENTIATED = auto()          # U₂ — التمييز والتشاكل
    NORMALIZED = auto()              # U₃ — التجميع والتطبيع
    DESIGNATED = auto()              # U₄ — الحضور والفرق والتعيين
    INITIAL_CONCEPTION = auto()      # U₅ — التصور الأولي
    DISCIPLINED_CONCEPTION = auto()  # U₆ — التصور المنضبط
    SEMANTIC_SUBJECT = auto()        # U₇ — الموضوع الدلالي المحرر
    JUDGEMENT_READY = auto()         # U₈ — الصالح للحكم


class LayerGateDecision(Enum):
    """قرار بوابة العبور — gate decision at a cognitive layer boundary.

    PASS     — عبور   : minimum completeness met, proceed to next layer
    REJECT   — رد     : blocking condition found, cannot proceed
    SUSPEND  — تعليق  : incomplete but no blocker, awaiting more data
    COMPLETE — اكتمال : layer fully satisfied with no residual
    """

    PASS = auto()      # عبور — الحد الأدنى مستوفى
    REJECT = auto()    # رد — مانع قاطع
    SUSPEND = auto()   # تعليق — ناقص بلا مانع
    COMPLETE = auto()  # اكتمال — الطبقة كاملة تمامًا
