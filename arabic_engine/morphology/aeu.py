"""AEU — Alphabetic Encoding Unit Registry (وحدة الترميز الأبجدي).

Master Minimal Alphabetic Encoding Architecture
================================================

Every Arabic orthographic element is represented as a fully proven
:class:`~arabic_engine.core.types.AEU` instance satisfying the
Minimal Complete form::

    AMU = (R, B, N, G, E)

    R — Referent       الدلالة الوظيفية
    B — Boundary       الحد الفاصل
    N — Necessity      الضرورة
    G — Governing Role الدور الحاكم
    E — Encoding ID    هوية الترميز

Extended to the full 16-field periodic-table record::

    AEU = {ID, Name, Class, Function, Referent, Boundary, Necessity,
           Governing_Role, Layer, Combination_Type, Math_Form,
           Unicode_Codepoint, Unicode_Profile, Depends_On, Unlocks,
           Proof_Status}

The ``math_form`` is an 8-position binary vector in ``{0,1}⁸``::

    Position  Meaning
    ────────  ───────────────────────────────────────────────────────
    0         base_letter     — consonant / semi-vowel / long vowel
    1         vowel_marker    — short vowel diacritic
    2         short           — QASIR feature present
    3         long            — TAWIL / length feature present
    4         closure         — QAFIL / syllable-closure present
    5         gemination      — TADFIF / doubling present
    6         indefiniteness  — TANKIR transform present
    7         special_mark    — SPECIAL_MARK / SUKUN / SHADDA / TANWIN

The registry ``AEU_REGISTRY`` maps ``element_id`` strings to :class:`AEU`
instances.  The secondary index ``AEU_BY_UNICODE`` maps Unicode code-points
to the same records.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from arabic_engine.core.enums import (
    CombinationType,
    ElementClass,
    ElementFunction,
    ElementLayer,
    ProofStatus,
    UnicodeProfileType,
)
from arabic_engine.core.types import AEU

# ── Shorthand aliases ────────────────────────────────────────────────
_CL = ElementClass
_LA = ElementLayer
_EF = ElementFunction
_CB = CombinationType
_UP = UnicodeProfileType
_PS = ProofStatus


def _mf(
    base: int,
    vowel: int,
    short: int,
    long_: int,
    closure: int,
    gemination: int,
    indef: int,
    special: int,
) -> Tuple[int, ...]:
    """Build an 8-position math_form binary vector."""
    return (base, vowel, short, long_, closure, gemination, indef, special)


# ── Complete AEU registry ────────────────────────────────────────────
# Keys are element_id strings (e.g. "AE_001").
# Entries follow the order: consonants (Table 1) → marks (Table 2) → long vowel.

AEU_REGISTRY: Dict[str, AEU] = {

    # ══════════════════════════════════════════════════════════════════
    # Table 1 — Consonants and Semi-Vowels (الصوامت وأشباه الصوامت)
    # ══════════════════════════════════════════════════════════════════

    # ء  U+0621  الهمزة — Composite Decision Unit
    "AE_001": AEU(
        element_id="AE_001",
        element_name="Hamza",
        element_class=_CL.COMPOSITE_DECISION_UNIT,
        element_function=_EF.ENCODING_BEARING,
        referent="الهمزة: صامت حنجري مستقل عن كرسيه الكتابي",
        boundary="ليست مساوية للألف ولا الواو ولا الياء الحاملة لها",
        necessity="لا يفسَّر القرار الكتابي الهمزي دون فصلها عن الكرسي",
        governing_role="context-sensitive orthographic decision unit",
        layer=_LA.MIXED,
        combination_type=_CB.CONTEXT_DEPENDENT,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0621,
        unicode_profile=_UP.CONTEXTUAL_RENDERING,
        depends_on=("PR_010",),
        unlocks=("hamza_orthography", "seat_selection"),
        proof_status=_PS.PENDING,
    ),

    # ب  U+0628  الباء
    "AE_002": AEU(
        element_id="AE_002",
        element_name="Ba",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الباء: صامت شفوي شديد مجهور",
        boundary="ليست الميم ولا الواو ولا أي صامت آخر",
        necessity="لا تكتمل صياغة عدد كبير من الجذور العربية دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0628,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ت  U+062A  التاء
    "AE_003": AEU(
        element_id="AE_003",
        element_name="Ta",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="التاء: صامت أسناني-لثوي شديد مهموس",
        boundary="ليست الطاء ولا الدال ولا الثاء",
        necessity="لا يُمثَّل الصوت الأسناني الشديد المهموس في الكتابة دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x062A,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ث  U+062B  الثاء
    "AE_004": AEU(
        element_id="AE_004",
        element_name="Tha",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الثاء: صامت بين-أسناني رخو مهموس",
        boundary="ليست التاء ولا الذال ولا السين",
        necessity="لا يُمثَّل الصوت البين-أسناني المهموس في الكتابة دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x062B,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ج  U+062C  الجيم
    "AE_005": AEU(
        element_id="AE_005",
        element_name="Jim",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الجيم: صامت شجري مركب مجهور",
        boundary="ليست الشين ولا أي صامت حنكي آخر",
        necessity="لا يُمثَّل الصوت الشجري المركب دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x062C,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ح  U+062D  الحاء
    "AE_006": AEU(
        element_id="AE_006",
        element_name="Ha_Haa",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الحاء: صامت حلقي رخو مهموس",
        boundary="ليست الهاء ولا العين ولا الخاء",
        necessity="لا يُمثَّل الصامت الحلقي المهموس الرخو دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x062D,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # خ  U+062E  الخاء
    "AE_007": AEU(
        element_id="AE_007",
        element_name="Kha",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الخاء: صامت حلقي-لهوي رخو مهموس",
        boundary="ليست الحاء ولا الغين ولا القاف",
        necessity="لا يُمثَّل الصامت الحلقي-اللهوي المهموس دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x062E,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # د  U+062F  الدال
    "AE_008": AEU(
        element_id="AE_008",
        element_name="Dal",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الدال: صامت أسناني-لثوي شديد مجهور",
        boundary="ليست التاء ولا الطاء ولا الذال",
        necessity="لا يُمثَّل الصامت الأسناني الشديد المجهور دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x062F,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ذ  U+0630  الذال
    "AE_009": AEU(
        element_id="AE_009",
        element_name="Dhal",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الذال: صامت بين-أسناني رخو مجهور",
        boundary="ليست الدال ولا الثاء ولا الظاء",
        necessity="لا يُمثَّل الصامت البين-أسناني المجهور الرخو دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0630,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ر  U+0631  الراء
    "AE_010": AEU(
        element_id="AE_010",
        element_name="Ra",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الراء: صامت لثوي مكرَّر مجهور",
        boundary="ليست اللام ولا النون ولا أي صامت لثوي آخر",
        necessity="لا يُمثَّل الصامت التكريري دون الراء",
        governing_role="identity-bearing consonant with trill feature",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0631,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ز  U+0632  الزاي
    "AE_011": AEU(
        element_id="AE_011",
        element_name="Zay",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الزاي: صامت أسلي-صفيري رخو مجهور",
        boundary="ليست السين ولا الصاد ولا أي صامت صفيري آخر",
        necessity="لا يُمثَّل الصامت الصفيري المجهور الرخو دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0632,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # س  U+0633  السين
    "AE_012": AEU(
        element_id="AE_012",
        element_name="Sin",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="السين: صامت أسلي-صفيري رخو مهموس",
        boundary="ليست الزاي ولا الصاد ولا أي صامت صفيري آخر",
        necessity="لا يُمثَّل الصامت الصفيري المهموس الرخو دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0633,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ش  U+0634  الشين
    "AE_013": AEU(
        element_id="AE_013",
        element_name="Shin",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الشين: صامت شجري رخو مهموس بسمة التفشي",
        boundary="ليست الجيم ولا السين ولا أي صامت حنكي-شجري آخر",
        necessity="لا يُمثَّل الصامت الشجري المهموس التفشي دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0634,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ص  U+0635  الصاد
    "AE_014": AEU(
        element_id="AE_014",
        element_name="Sad",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الصاد: صامت أسلي مطبق مهموس صفيري",
        boundary="ليست السين ولا الطاء ولا الضاد",
        necessity="لا يُمثَّل الصامت الأسلي المطبق الصفيري المهموس دونها",
        governing_role="identity-bearing emphatic consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0635,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ض  U+0636  الضاد
    "AE_015": AEU(
        element_id="AE_015",
        element_name="Dad",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الضاد: صامت لثوي مطبق مجهور باستطالة",
        boundary="ليست الطاء ولا الظاء ولا الدال",
        necessity="لا يُمثَّل الصامت اللثوي المطبق المستطال المجهور دونها",
        governing_role="identity-bearing emphatic consonant with prolongation",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0636,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ط  U+0637  الطاء
    "AE_016": AEU(
        element_id="AE_016",
        element_name="Ta_Emphatic",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الطاء: صامت أسناني-لثوي مطبق شديد مهموس",
        boundary="ليست التاء ولا الدال ولا الضاد",
        necessity="لا يُمثَّل الصامت الأسناني الشديد المطبق المهموس دونها",
        governing_role="identity-bearing emphatic consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0637,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ظ  U+0638  الظاء
    "AE_017": AEU(
        element_id="AE_017",
        element_name="Dha_Emphatic",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الظاء: صامت بين-أسناني مطبق رخو مجهور",
        boundary="ليست الذال ولا الطاء ولا الضاد",
        necessity="لا يُمثَّل الصامت البين-أسناني المطبق المجهور دونها",
        governing_role="identity-bearing emphatic consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0638,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ع  U+0639  العين
    "AE_018": AEU(
        element_id="AE_018",
        element_name="Ain",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="العين: صامت حلقي متوسط مجهور",
        boundary="ليست الهمزة ولا الحاء ولا الغين",
        necessity="لا يُمثَّل الصامت الحلقي المتوسط المجهور دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0639,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # غ  U+063A  الغين
    "AE_019": AEU(
        element_id="AE_019",
        element_name="Ghain",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الغين: صامت حلقي رخو مجهور",
        boundary="ليست العين ولا الخاء ولا القاف",
        necessity="لا يُمثَّل الصامت الحلقي الرخو المجهور دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x063A,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ف  U+0641  الفاء
    "AE_020": AEU(
        element_id="AE_020",
        element_name="Fa",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الفاء: صامت شفوي-أسناني رخو مهموس",
        boundary="ليست الباء ولا الواو ولا الميم",
        necessity="لا يُمثَّل الصامت الشفوي-الأسناني المهموس دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0641,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ق  U+0642  القاف
    "AE_021": AEU(
        element_id="AE_021",
        element_name="Qaf",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="القاف: صامت لهوي شديد مهموس مستعلٍ",
        boundary="ليست الكاف ولا الغين ولا الخاء",
        necessity="لا يُمثَّل الصامت اللهوي الشديد المستعلي المهموس دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0642,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ك  U+0643  الكاف
    "AE_022": AEU(
        element_id="AE_022",
        element_name="Kaf",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الكاف: صامت طبقي-لهوي شديد مهموس",
        boundary="ليست القاف ولا الغين ولا أي طبقي آخر",
        necessity="لا يُمثَّل الصامت الطبقي الشديد المهموس دونها",
        governing_role="identity-bearing consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0643,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ل  U+0644  اللام
    "AE_023": AEU(
        element_id="AE_023",
        element_name="Lam",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="اللام: صامت لثوي منحرف مجهور",
        boundary="ليست الراء ولا النون ولا أي لثوي آخر",
        necessity="لا يُمثَّل الصامت اللثوي المنحرف ولا لام التعريف دونها",
        governing_role="identity-bearing lateral consonant / definiteness marker",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0644,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation", "definiteness_marking"),
        proof_status=_PS.PROVEN,
    ),

    # م  U+0645  الميم
    "AE_024": AEU(
        element_id="AE_024",
        element_name="Mim",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الميم: صامت شفوي أنفي مجهور",
        boundary="ليست الباء ولا النون ولا الواو",
        necessity="لا يُمثَّل الصامت الشفوي الأنفي المجهور دونها",
        governing_role="identity-bearing nasal consonant",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0645,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ن  U+0646  النون
    "AE_025": AEU(
        element_id="AE_025",
        element_name="Nun",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="النون: صامت لثوي أنفي مجهور ذو غنة",
        boundary="ليست الميم ولا اللام ولا التنوين",
        necessity="لا تكتمل أحكام النون وقوانين التجويد دونها",
        governing_role="identity-bearing nasal consonant (nunation anchor)",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0646,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation", "tajweed_rules"),
        proof_status=_PS.PROVEN,
    ),

    # ه  U+0647  الهاء
    "AE_026": AEU(
        element_id="AE_026",
        element_name="Ha_Low",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.IDENTITY_BEARING,
        referent="الهاء: صامت حنجري-حلقي رخو مهموس",
        boundary="ليست الحمزة ولا الحاء ولا العين",
        necessity="لا يُمثَّل الصامت الحنجري-الحلقي المهموس الرخو دونها",
        governing_role="identity-bearing consonant / pronoun suffix anchor",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0647,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # و  U+0648  الواو — شبه صامت / صائت طويل
    "AE_027": AEU(
        element_id="AE_027",
        element_name="Waw",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.LENGTH_BEARING,
        referent="الواو: شبه صامت شفوي-ليّن يؤدي دور الصائت الطويل",
        boundary="ليست الباء ولا الألف ولا الياء",
        necessity="لا يُمثَّل الصائت الطويل /uː/ ولا شبه الصامت الشفوي دونها",
        governing_role="semi-vowel / long vowel carrier",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 1, 0, 0, 0, 0),
        unicode_codepoint=0x0648,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("long_vowel_u", "syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ي  U+064A  الياء — شبه صامت / صائت طويل
    "AE_028": AEU(
        element_id="AE_028",
        element_name="Ya",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.LENGTH_BEARING,
        referent="الياء: شبه صامت حنكي-ليّن يؤدي دور الصائت الطويل",
        boundary="ليست الألف ولا الواو ولا الكاف",
        necessity="لا يُمثَّل الصائت الطويل /iː/ ولا شبه الصامت الحنكي دونها",
        governing_role="semi-vowel / long vowel carrier",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 1, 0, 0, 0, 0),
        unicode_codepoint=0x064A,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("long_vowel_i", "syllable_formation", "root_derivation"),
        proof_status=_PS.PROVEN,
    ),

    # ══════════════════════════════════════════════════════════════════
    # Table 2 — Short Vowels and Structural Marks (الحركات والعلامات)
    # ══════════════════════════════════════════════════════════════════

    # َ  U+064E  الفتحة
    "AE_029": AEU(
        element_id="AE_029",
        element_name="Fatha",
        element_class=_CL.VOWEL_MARKER,
        element_function=_EF.MOTION_BEARING,
        referent="الفتحة: حركة قصيرة أمامية-علوية ضمن النظام العربي",
        boundary="ليست ضمةً ولا كسرةً ولا سكونًا ولا مدًّا",
        necessity="لا يكتمل تمثيل الحركة القصيرة المفتوحة في الإخراج المشكول دونها",
        governing_role="marker of vocalic motion (front-open)",
        layer=_LA.ORTHOGRAPHIC,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 1, 1, 0, 0, 0, 0, 0),
        unicode_codepoint=0x064E,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_008",),
        unlocks=("vocalized_output", "cluster_formation"),
        proof_status=_PS.PROVEN,
    ),

    # ُ  U+064F  الضمة
    "AE_030": AEU(
        element_id="AE_030",
        element_name="Damma",
        element_class=_CL.VOWEL_MARKER,
        element_function=_EF.MOTION_BEARING,
        referent="الضمة: حركة قصيرة خلفية-مستديرة ضمن النظام العربي",
        boundary="ليست فتحةً ولا كسرةً ولا سكونًا ولا مدًّا",
        necessity="لا يكتمل تمثيل الحركة القصيرة المضمومة في الإخراج المشكول دونها",
        governing_role="marker of vocalic motion (back-round)",
        layer=_LA.ORTHOGRAPHIC,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 1, 1, 0, 0, 0, 0, 0),
        unicode_codepoint=0x064F,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_008",),
        unlocks=("vocalized_output", "cluster_formation"),
        proof_status=_PS.PROVEN,
    ),

    # ِ  U+0650  الكسرة
    "AE_031": AEU(
        element_id="AE_031",
        element_name="Kasra",
        element_class=_CL.VOWEL_MARKER,
        element_function=_EF.MOTION_BEARING,
        referent="الكسرة: حركة قصيرة أمامية-مغلقة ضمن النظام العربي",
        boundary="ليست فتحةً ولا ضمةً ولا سكونًا ولا مدًّا",
        necessity="لا يكتمل تمثيل الحركة القصيرة المكسورة في الإخراج المشكول دونها",
        governing_role="marker of vocalic motion (front-close)",
        layer=_LA.ORTHOGRAPHIC,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 1, 1, 0, 0, 0, 0, 0),
        unicode_codepoint=0x0650,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_008",),
        unlocks=("vocalized_output", "cluster_formation"),
        proof_status=_PS.PROVEN,
    ),

    # ّ  U+0651  الشدة
    "AE_032": AEU(
        element_id="AE_032",
        element_name="Shadda",
        element_class=_CL.STRUCTURAL_MARKER,
        element_function=_EF.DUPLICATION_BEARING,
        referent="الشدة: علامة بنيوية تقرِّر التضعيف أو الضغط البنيوي",
        boundary="ليست حركةً ولا حرفًا أساسيًا ولا سكونًا ولا مدًّا",
        necessity="لا يمكن تمثيل التضعيف البنيوي الصحيح دونها",
        governing_role="duplication-bearing structural marker",
        layer=_LA.STRUCTURAL,
        combination_type=_CB.CLUSTER_INTERNAL,
        math_form=_mf(0, 0, 0, 0, 0, 1, 0, 1),
        unicode_codepoint=0x0651,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_009",),
        unlocks=("gemination", "cluster_ordering"),
        proof_status=_PS.PROVEN,
    ),

    # ْ  U+0652  السكون
    "AE_033": AEU(
        element_id="AE_033",
        element_name="Sukun",
        element_class=_CL.STRUCTURAL_MARKER,
        element_function=_EF.CLOSURE_BEARING,
        referent="السكون: علامة تقرِّر انعدام الحركة وإغلاق المقطع",
        boundary="ليست حركةً ولا حرفًا أساسيًا ولا شدةً ولا مدًّا",
        necessity="لا يكتمل تمثيل إغلاق المقطع والتوقف الصرفي دونه",
        governing_role="closure-bearing zero-vowel marker",
        layer=_LA.STRUCTURAL,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 0, 0, 0, 1, 0, 0, 1),
        unicode_codepoint=0x0652,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_007",),
        unlocks=("syllable_closure", "waqf_form"),
        proof_status=_PS.PROVEN,
    ),

    # ً  U+064B  تنوين الفتح
    "AE_034": AEU(
        element_id="AE_034",
        element_name="Tanwin_Fath",
        element_class=_CL.STRUCTURAL_MARKER,
        element_function=_EF.INDEFINITENESS_BEARING,
        referent="تنوين الفتح: حركة مركبة تقرِّر التنكير في حالة النصب",
        boundary="ليست فتحةً مفردةً ولا تنوين ضم ولا تنوين كسر",
        necessity="لا يُمثَّل التنكير في حالة النصب المنوَّن دونه",
        governing_role="indefiniteness-bearing nunation (open / nasb)",
        layer=_LA.STRUCTURAL,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 1, 1, 0, 0, 0, 1, 0),
        unicode_codepoint=0x064B,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_011",),
        unlocks=("indefiniteness_marking", "nunation"),
        proof_status=_PS.PENDING,
    ),

    # ٌ  U+064C  تنوين الضم
    "AE_035": AEU(
        element_id="AE_035",
        element_name="Tanwin_Damm",
        element_class=_CL.STRUCTURAL_MARKER,
        element_function=_EF.INDEFINITENESS_BEARING,
        referent="تنوين الضم: حركة مركبة تقرِّر التنكير في حالة الرفع",
        boundary="ليست ضمةً مفردةً ولا تنوين فتح ولا تنوين كسر",
        necessity="لا يُمثَّل التنكير في حالة الرفع المنوَّن دونه",
        governing_role="indefiniteness-bearing nunation (round / rafa)",
        layer=_LA.STRUCTURAL,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 1, 1, 0, 0, 0, 1, 0),
        unicode_codepoint=0x064C,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_011",),
        unlocks=("indefiniteness_marking", "nunation"),
        proof_status=_PS.PENDING,
    ),

    # ٍ  U+064D  تنوين الكسر
    "AE_036": AEU(
        element_id="AE_036",
        element_name="Tanwin_Kasr",
        element_class=_CL.STRUCTURAL_MARKER,
        element_function=_EF.INDEFINITENESS_BEARING,
        referent="تنوين الكسر: حركة مركبة تقرِّر التنكير في حالة الجر",
        boundary="ليست كسرةً مفردةً ولا تنوين فتح ولا تنوين ضم",
        necessity="لا يُمثَّل التنكير في حالة الجر المنوَّن دونه",
        governing_role="indefiniteness-bearing nunation (close / jarr)",
        layer=_LA.STRUCTURAL,
        combination_type=_CB.ATTACHES_TO_BASE,
        math_form=_mf(0, 1, 1, 0, 0, 0, 1, 0),
        unicode_codepoint=0x064D,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_011",),
        unlocks=("indefiniteness_marking", "nunation"),
        proof_status=_PS.PENDING,
    ),

    # ٓ  U+0653  المدة
    "AE_037": AEU(
        element_id="AE_037",
        element_name="Madda",
        element_class=_CL.STRUCTURAL_MARKER,
        element_function=_EF.ENCODING_BEARING,
        referent="المدة: علامة مركبة تجمع بين الهمزة فوق الألف وإطالة الصوت",
        boundary="ليست مدًّا مستقلًا ولا همزةً عارية ولا ألفًا عاديةً",
        necessity="لا يُمثَّل تركيب الهمزة المطوَّلة فوق الألف دونها",
        governing_role="hamza-over-alef composite length mark",
        layer=_LA.STRUCTURAL,
        combination_type=_CB.CLUSTER_INTERNAL,
        math_form=_mf(0, 0, 0, 0, 0, 0, 0, 1),
        unicode_codepoint=0x0653,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_010", "PR_012"),
        unlocks=("alef_madda", "hamza_above_alef"),
        proof_status=_PS.COMPOSITE,
    ),

    # ٰ  U+0670  الألف الخنجرية
    "AE_038": AEU(
        element_id="AE_038",
        element_name="Superscript_Alef",
        element_class=_CL.CARRIER_RELATED_UNIT,
        element_function=_EF.LENGTH_BEARING,
        referent="الألف الخنجرية: علامة مدٍّ صغيرة فوق الحرف في الرسم القرآني",
        boundary="ليست ألفًا عاديةً ولا مدةً ولا أي علامة مد كاملة",
        necessity="لا يُمثَّل المد الصغير في المواضع القرآنية دونها",
        governing_role="dagger alef length marker (Quranic orthography)",
        layer=_LA.MIXED,
        combination_type=_CB.CLUSTER_INTERNAL,
        math_form=_mf(0, 0, 0, 0, 0, 0, 0, 1),
        unicode_codepoint=0x0670,
        unicode_profile=_UP.COMBINING_MARK,
        depends_on=("PR_012",),
        unlocks=("dagger_alef", "quran_orthography"),
        proof_status=_PS.PENDING,
    ),

    # ══════════════════════════════════════════════════════════════════
    # Table 3 — Long Vowel Letter (الصائت الطويل)
    # ══════════════════════════════════════════════════════════════════

    # ا  U+0627  الألف — صائت طويل / حامل كتابي
    "AE_039": AEU(
        element_id="AE_039",
        element_name="Alef",
        element_class=_CL.BASE_LETTER,
        element_function=_EF.LENGTH_BEARING,
        referent="الألف: صائت طويل وحامل كتابي لكرسي الهمزة",
        boundary="ليست الواو ولا الياء ولا الألف الخنجرية ولا همزة مستقلة",
        necessity="لا يُمثَّل الصائت الطويل /aː/ ولا يُشيَّد كرسي الهمزة الأولى دونها",
        governing_role="long vowel carrier / primary hamza seat",
        layer=_LA.PHONOLOGICAL,
        combination_type=_CB.STANDALONE,
        math_form=_mf(1, 0, 0, 1, 0, 0, 0, 0),
        unicode_codepoint=0x0627,
        unicode_profile=_UP.SINGLE_CODE_POINT,
        depends_on=("PR_001", "PR_002"),
        unlocks=("long_vowel_a", "hamza_seat_alef"),
        proof_status=_PS.PROVEN,
    ),
}

# ── Secondary index: Unicode code-point → AEU ────────────────────────
AEU_BY_UNICODE: Dict[int, AEU] = {
    a.unicode_codepoint: a for a in AEU_REGISTRY.values()
}


# ── Public API ───────────────────────────────────────────────────────


def lookup(element_id: str) -> Optional[AEU]:
    """Return the :class:`AEU` record for *element_id*, or ``None``."""
    return AEU_REGISTRY.get(element_id)


def lookup_unicode(codepoint: int) -> Optional[AEU]:
    """Return the :class:`AEU` record for Unicode *codepoint*, or ``None``."""
    return AEU_BY_UNICODE.get(codepoint)


def lookup_char(char: str) -> Optional[AEU]:
    """Return the :class:`AEU` record for the first character of *char*.

    Convenience wrapper around :func:`lookup_unicode` for string input.
    """
    if not char:
        return None
    return lookup_unicode(ord(char[0]))


def elements_by_class(cls: ElementClass) -> List[AEU]:
    """Return all :class:`AEU` records whose :attr:`~AEU.element_class` equals *cls*."""
    return [a for a in AEU_REGISTRY.values() if a.element_class is cls]


def elements_by_layer(layer: ElementLayer) -> List[AEU]:
    """Return all :class:`AEU` records whose :attr:`~AEU.layer` equals *layer*."""
    return [a for a in AEU_REGISTRY.values() if a.layer is layer]


def elements_by_function(func: ElementFunction) -> List[AEU]:
    """Return all :class:`AEU` records whose :attr:`~AEU.element_function` equals *func*."""
    return [a for a in AEU_REGISTRY.values() if a.element_function is func]


def elements_by_proof_status(status: ProofStatus) -> List[AEU]:
    """Return all :class:`AEU` records whose :attr:`~AEU.proof_status` equals *status*."""
    return [a for a in AEU_REGISTRY.values() if a.proof_status is status]


def elements_by_combination_type(ctype: CombinationType) -> List[AEU]:
    """Return all :class:`AEU` records whose :attr:`~AEU.combination_type` equals *ctype*."""
    return [a for a in AEU_REGISTRY.values() if a.combination_type is ctype]


def proven_elements() -> List[AEU]:
    """Return all :class:`AEU` records with :attr:`ProofStatus.PROVEN` status."""
    return elements_by_proof_status(ProofStatus.PROVEN)


def periodic_table() -> List[dict]:
    """Return the full Alphabetic Periodic Table as a list of row dicts.

    Each row contains the 16 canonical columns::

        Element_ID, Name, Class, Function, Referent, Boundary,
        Necessity, Governing_Role, Layer, Combination_Type,
        Math_Form, Unicode_Codepoint, Unicode_Profile,
        Depends_On, Unlocks, Proof_Status

    Rows are ordered by :attr:`~AEU.element_id`.
    """
    return [a.to_row() for a in sorted(AEU_REGISTRY.values(), key=lambda a: a.element_id)]
