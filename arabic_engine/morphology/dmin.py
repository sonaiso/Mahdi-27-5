"""D_min — Minimal Complete Arabic Phonological Model.

Implements the numeric function::

    D_min(x) = (u, c, g, f, t)

for every Arabic consonant, short vowel, long vowel, tanwīn, sukūn,
shaddah, and special mark defined in the system tables.

The complete registry ``DMIN_REGISTRY`` maps Unicode code-points to
:class:`~arabic_engine.core.types.DMin` instances.  Every instance
exposes a ``.vector`` property returning a 5-tuple of integers::

    (unicode, category.value, group.value, feature_mask, transform_mask)

making each phonological unit a *computable numeric point* in ℕ⁵.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional

from arabic_engine.core.enums import (
    PhonCategory,
    PhonFeature,
    PhonGroup,
    PhonTransform,
)
from arabic_engine.core.types import DMin

# ── Shorthand aliases ────────────────────────────────────────────────
_C = PhonCategory
_G = PhonGroup
_F = PhonFeature
_T = PhonTransform

# ── Helper: build a frozen feature set ──────────────────────────────

def _f(*feats: PhonFeature) -> FrozenSet[PhonFeature]:
    """Return a frozen set of phonological features (shorthand helper)."""
    return frozenset(feats)


def _t(*transforms: PhonTransform) -> FrozenSet[PhonTransform]:
    """Return a frozen set of phonological transforms (shorthand helper)."""
    return frozenset(transforms)


# ── Complete D_min registry ──────────────────────────────────────────
# Keys are Unicode code-points (int).
# Entries follow the order: consonants → short vowels/marks → long vowels.

DMIN_REGISTRY: Dict[int, DMin] = {

    # ══════════════════════════════════════════════════════════════════
    # 1) CONSONANTS (صوامت)  —  Table 1
    # ══════════════════════════════════════════════════════════════════

    # ء  U+0621  حنجري/مزمَري
    0x0621: DMin(
        unicode=0x0621,
        category=_C.CONSONANT,
        group=_G.HNJ_MZM,
        features=_f(_F.SHADID, _F.MAHMOUS, _F.HMZ),
        transforms=_t(_T.TAHQIQ, _T.TASHIL, _T.IBDAL, _T.HADHF, _T.HAMLI_HAMZI),
        code="C:HNJ:SHD:MHM:HMZ",
    ),

    # ب  U+0628  شفوي
    0x0628: DMin(
        unicode=0x0628,
        category=_C.CONSONANT,
        group=_G.SHF,
        features=_f(_F.SHADID, _F.MAJHUR),
        transforms=_t(_T.ASAL_JADHARI, _T.IDGHAM, _T.IBDAL),
        code="C:SHF:SHD:MJH",
    ),

    # ت  U+062A  أسناني-لثوي
    0x062A: DMin(
        unicode=0x062A,
        category=_C.CONSONANT,
        group=_G.ASN_LTH,
        features=_f(_F.SHADID, _F.MAHMOUS),
        transforms=_t(_T.ASAL_JADHARI, _T.ZIYADA, _T.IDGHAM, _T.TAMATHUL),
        code="C:ASN-LTH:SHD:MHM",
    ),

    # ث  U+062B  بين-أسناني
    0x062B: DMin(
        unicode=0x062B,
        category=_C.CONSONANT,
        group=_G.BAYNASN,
        features=_f(_F.RAKHW, _F.MAHMOUS),
        transforms=_t(_T.ASAL_JADHARI, _T.IBDAL),
        code="C:BAYNASN:RKH:MHM",
    ),

    # ج  U+062C  شجري/حنكي
    0x062C: DMin(
        unicode=0x062C,
        category=_C.CONSONANT,
        group=_G.SHJR,
        features=_f(_F.MURAKKAB, _F.MAJHUR),
        transforms=_t(_T.ASAL_JADHARI, _T.BINA_ISHTIQAQI),
        code="C:SHJR:MRK:MJH",
    ),

    # ح  U+062D  حلقي
    0x062D: DMin(
        unicode=0x062D,
        category=_C.CONSONANT,
        group=_G.HLQ,
        features=_f(_F.RAKHW, _F.MAHMOUS),
        transforms=_t(_T.TAHQIQ),
        code="C:HLQ:RKH:MHM",
    ),

    # خ  U+062E  حلقي/لهوي
    0x062E: DMin(
        unicode=0x062E,
        category=_C.CONSONANT,
        group=_G.HLQ_LHW,
        features=_f(_F.RAKHW, _F.MAHMOUS),
        transforms=_t(_T.TAHQIQ),
        code="C:HLQ-LHW:RKH:MHM",
    ),

    # د  U+062F  أسناني-لثوي
    0x062F: DMin(
        unicode=0x062F,
        category=_C.CONSONANT,
        group=_G.ASN_LTH,
        features=_f(_F.SHADID, _F.MAJHUR),
        transforms=_t(_T.ASAL_JADHARI, _T.IDGHAM, _T.TAMATHUL),
        code="C:ASN-LTH:SHD:MJH",
    ),

    # ذ  U+0630  بين-أسناني
    0x0630: DMin(
        unicode=0x0630,
        category=_C.CONSONANT,
        group=_G.BAYNASN,
        features=_f(_F.RAKHW, _F.MAJHUR),
        transforms=_t(_T.ASAL_JADHARI, _T.IBDAL),
        code="C:BAYNASN:RKH:MJH",
    ),

    # ر  U+0631  لثوي
    0x0631: DMin(
        unicode=0x0631,
        category=_C.CONSONANT,
        group=_G.LTH,
        features=_f(_F.TAKRIR, _F.MAJHUR),
        transforms=_t(_T.TAFKHIM, _T.TARQIQ, _T.TAKRIR_TR, _T.ASAL_JADHARI),
        code="C:LTH:TKR:MJH",
    ),

    # ز  U+0632  أسلي/صفيري
    0x0632: DMin(
        unicode=0x0632,
        category=_C.CONSONANT,
        group=_G.ASLI,
        features=_f(_F.RAKHW, _F.MAJHUR, _F.SAFIR),
        transforms=_t(_T.ASAL_JADHARI),
        code="C:ASLI:SFYR:RKH:MJH",
    ),

    # س  U+0633  أسلي/صفيري
    0x0633: DMin(
        unicode=0x0633,
        category=_C.CONSONANT,
        group=_G.ASLI,
        features=_f(_F.RAKHW, _F.MAHMOUS, _F.SAFIR),
        transforms=_t(_T.ASAL_JADHARI, _T.BINA_SARFI),
        code="C:ASLI:SFYR:RKH:MHM",
    ),

    # ش  U+0634  شجري
    0x0634: DMin(
        unicode=0x0634,
        category=_C.CONSONANT,
        group=_G.SHJR,
        features=_f(_F.RAKHW, _F.MAHMOUS, _F.TAFSHI),
        transforms=_t(_T.ASAL_JADHARI, _T.TAFSHI_TR),
        code="C:SHJR:RKH:MHM:TFSH",
    ),

    # ص  U+0635  أسلي مستعلٍ مطبق
    0x0635: DMin(
        unicode=0x0635,
        category=_C.CONSONANT,
        group=_G.ASLI_MTPQ,
        features=_f(_F.RAKHW, _F.MAHMOUS, _F.SAFIR, _F.ITBAQ),
        transforms=_t(_T.TAFKHIM, _T.ASAL_JADHARI),
        code="C:ASLI:RKH:MHM:MTPQ",
    ),

    # ض  U+0636  لثوي مستعلٍ مطبق
    0x0636: DMin(
        unicode=0x0636,
        category=_C.CONSONANT,
        group=_G.LTH_MTPQ,
        features=_f(_F.MAJHUR, _F.ITBAQ, _F.ASTTALA),
        transforms=_t(_T.ASAL_JADHARI, _T.ASTTALA_TR),
        code="C:LTH:MJH:MTPQ:ASTT",
    ),

    # ط  U+0637  أسناني-لثوي مستعلٍ مطبق
    0x0637: DMin(
        unicode=0x0637,
        category=_C.CONSONANT,
        group=_G.ASN_LTH_MTPQ,
        features=_f(_F.SHADID, _F.MAHMOUS, _F.ITBAQ),
        transforms=_t(_T.TAFKHIM, _T.ASAL_JADHARI),
        code="C:ASN-LTH:SHD:MHM:MTPQ",
    ),

    # ظ  U+0638  بين-أسناني مستعلٍ مطبق
    0x0638: DMin(
        unicode=0x0638,
        category=_C.CONSONANT,
        group=_G.BAYNASN_MTPQ,
        features=_f(_F.RAKHW, _F.MAJHUR, _F.ITBAQ),
        transforms=_t(_T.TAFKHIM, _T.ASAL_JADHARI),
        code="C:BAYNASN:RKH:MJH:MTPQ",
    ),

    # ع  U+0639  حلقي
    0x0639: DMin(
        unicode=0x0639,
        category=_C.CONSONANT,
        group=_G.HLQ,
        features=_f(_F.MUTAWASSIT, _F.MAJHUR),
        transforms=_t(_T.TAHQIQ),
        code="C:HLQ:MTS-MJH",
    ),

    # غ  U+063A  حلقي
    0x063A: DMin(
        unicode=0x063A,
        category=_C.CONSONANT,
        group=_G.HLQ,
        features=_f(_F.RAKHW, _F.MAJHUR),
        transforms=_t(_T.TAHQIQ),
        code="C:HLQ:RKH:MJH",
    ),

    # ف  U+0641  شفوي-أسناني
    0x0641: DMin(
        unicode=0x0641,
        category=_C.CONSONANT,
        group=_G.SHF_ASN,
        features=_f(_F.RAKHW, _F.MAHMOUS),
        transforms=_t(_T.ASAL_JADHARI),
        code="C:SHF-ASN:RKH:MHM",
    ),

    # ق  U+0642  لهوي
    0x0642: DMin(
        unicode=0x0642,
        category=_C.CONSONANT,
        group=_G.LHW,
        features=_f(_F.SHADID, _F.MAHMOUS, _F.MSTALI),
        transforms=_t(_T.ASAL_JADHARI, _T.TAFKHIM),
        code="C:LHW:SHD:MHM:MSTAL",
    ),

    # ك  U+0643  طبقي/لهوي
    0x0643: DMin(
        unicode=0x0643,
        category=_C.CONSONANT,
        group=_G.TBQ_LHW,
        features=_f(_F.SHADID, _F.MAHMOUS),
        transforms=_t(_T.ASAL_JADHARI, _T.WAZIFA_SARFIYYA),
        code="C:TBQ-LHW:SHD:MHM",
    ),

    # ل  U+0644  لثوي
    0x0644: DMin(
        unicode=0x0644,
        category=_C.CONSONANT,
        group=_G.LTH,
        features=_f(_F.MUNHARIF, _F.MAJHUR),
        transforms=_t(_T.TAAREF, _T.IDGHAM_SHAMSI, _T.IZHAR_QAMARI, _T.ASAL_JADHARI),
        code="C:LTH:MNHRF:MJH",
    ),

    # م  U+0645  شفوي أنفي
    0x0645: DMin(
        unicode=0x0645,
        category=_C.CONSONANT,
        group=_G.SHF,
        features=_f(_F.MAJHUR, _F.ANFI, _F.GHUNNA),
        transforms=_t(_T.ASAL_JADHARI, _T.ZIYADA, _T.JAM, _T.IDGHAM),
        code="C:SHF:ANF:MJH:GHN",
    ),

    # ن  U+0646  لثوي أنفي
    0x0646: DMin(
        unicode=0x0646,
        category=_C.CONSONANT,
        group=_G.LTH,
        features=_f(_F.MAJHUR, _F.ANFI, _F.GHUNNA),
        transforms=_t(
            _T.ASAL_JADHARI,
            _T.TAWKID,
            _T.TANWIN_FUNC,
            _T.IZHAR,
            _T.IDGHAM,
            _T.IKHFAA,
            _T.IQLAB,
        ),
        code="C:LTH:ANF:MJH:GHN",
    ),

    # ه  U+0647  حنجري/حلقي
    0x0647: DMin(
        unicode=0x0647,
        category=_C.CONSONANT,
        group=_G.HNJ_HLQ,
        features=_f(_F.RAKHW, _F.MAHMOUS),
        transforms=_t(_T.DAMIR_FUNC, _T.HADHF, _T.ASAL_JADHARI),
        code="C:HNJ-HLQ:RKH:MHM",
    ),

    # و  U+0648  شبه صامت / صائت طويل ذو تحولات
    0x0648: DMin(
        unicode=0x0648,
        category=_C.SEMI_VOWEL,
        group=_G.SHF_LYN,
        features=_f(_F.MAJHUR, _F.LAYIN, _F.ITLAL, _F.TAWIL),
        transforms=_t(_T.ITLAL_TR, _T.MADD, _T.ATAF, _T.JAM),
        code="C/V:SHF:LYN:MJH:ETLAL",
    ),

    # ي  U+064A  شبه صامت / صائت طويل ذو تحولات
    0x064A: DMin(
        unicode=0x064A,
        category=_C.SEMI_VOWEL,
        group=_G.HNK_LYN,
        features=_f(_F.MAJHUR, _F.LAYIN, _F.ITLAL, _F.TAWIL),
        transforms=_t(_T.ITLAL_TR, _T.MADD, _T.NISBAH, _T.MUTAKALLIM),
        code="C/V:HNK:LYN:MJH:ETLAL",
    ),

    # ══════════════════════════════════════════════════════════════════
    # 2) SHORT VOWELS & STRUCTURAL MARKS (الحركات والعلامات)  —  Table 2
    # ══════════════════════════════════════════════════════════════════

    # َ  U+064E  فتحة
    0x064E: DMin(
        unicode=0x064E,
        category=_C.SHORT_VOWEL,
        group=_G.FTH,
        features=_f(_F.QASIR, _F.NUWAWI),
        transforms=_t(_T.WAZN, _T.IIRAB),
        code="V:FTH:QSR:NWY",
    ),

    # ُ  U+064F  ضمة
    0x064F: DMin(
        unicode=0x064F,
        category=_C.SHORT_VOWEL,
        group=_G.DMM,
        features=_f(_F.QASIR, _F.NUWAWI),
        transforms=_t(_T.WAZN, _T.IIRAB),
        code="V:DMM:QSR:NWY",
    ),

    # ِ  U+0650  كسرة
    0x0650: DMin(
        unicode=0x0650,
        category=_C.SHORT_VOWEL,
        group=_G.KSR,
        features=_f(_F.QASIR, _F.NUWAWI),
        transforms=_t(_T.WAZN, _T.IIRAB),
        code="V:KSR:QSR:NWY",
    ),

    # ّ  U+0651  شدة
    0x0651: DMin(
        unicode=0x0651,
        category=_C.SHADDA,
        group=_G.SHD_GRP,
        features=_f(_F.TADFIF),
        transforms=_t(_T.IDGHAM, _T.TADFIF_TR),
        code="M:SHD:TDF",
    ),

    # ْ  U+0652  سكون
    0x0652: DMin(
        unicode=0x0652,
        category=_C.SUKUN,
        group=_G.SKN_GRP,
        features=_f(_F.SIFR_HARAKA, _F.QAFIL),
        transforms=_t(_T.MAQTAA, _T.JAZM),
        code="S:SKN:QFL",
    ),

    # ً  U+064B  تنوين فتح
    0x064B: DMin(
        unicode=0x064B,
        category=_C.TANWIN,
        group=_G.TAN_FTH,
        features=_f(_F.QASIR, _F.NUWAWI),
        transforms=_t(_T.TANKIR, _T.BINA_SARFI),
        code="V:MURKB:TAN-FTH",
    ),

    # ٌ  U+064C  تنوين ضم
    0x064C: DMin(
        unicode=0x064C,
        category=_C.TANWIN,
        group=_G.TAN_DMM,
        features=_f(_F.QASIR, _F.NUWAWI),
        transforms=_t(_T.TANKIR, _T.BINA_SARFI),
        code="V:MURKB:TAN-DMM",
    ),

    # ٍ  U+064D  تنوين كسر
    0x064D: DMin(
        unicode=0x064D,
        category=_C.TANWIN,
        group=_G.TAN_KSR,
        features=_f(_F.QASIR, _F.NUWAWI),
        transforms=_t(_T.TANKIR, _T.BINA_SARFI),
        code="V:MURKB:TAN-KSR",
    ),

    # ٓ  U+0653  مدة
    0x0653: DMin(
        unicode=0x0653,
        category=_C.SPECIAL_MARK,
        group=_G.MDD_GRP,
        features=_f(_F.MD_KHAS),
        transforms=_t(_T.MADD, _T.HAMLI_HAMZI),
        code="M:MDD:MRKB",
    ),

    # ٰ  U+0670  ألف خنجرية
    0x0670: DMin(
        unicode=0x0670,
        category=_C.SPECIAL_MARK,
        group=_G.ALF_KHNJ,
        features=_f(_F.MD_KHAS),
        transforms=_t(_T.MADD, _T.HAMZA_CARRIER),
        code="V:ALF-KHNJ:MD-KHAS",
    ),

    # ══════════════════════════════════════════════════════════════════
    # 3) LONG VOWELS (الصوائت الطويلة)  —  Table 3
    # ══════════════════════════════════════════════════════════════════

    # ا  U+0627  ألف — صائت طويل / حامل كتابي
    0x0627: DMin(
        unicode=0x0627,
        category=_C.LONG_VOWEL,
        group=_G.ALF_LV,
        features=_f(_F.TAWIL, _F.NUWAWI),
        transforms=_t(_T.MADD, _T.HAMZA_CARRIER),
        code="V:ALF:TWL:NWY",
    ),
    # Note: و (0x0648) and ي (0x064A) also serve as long vowels;
    # their entries above (SEMI_VOWEL) capture both roles via the
    # TAWIL feature and the MADD transform.
}

# ── Public API ───────────────────────────────────────────────────────


def lookup(codepoint: int) -> Optional[DMin]:
    """Return the :class:`DMin` record for *codepoint*, or ``None``."""
    return DMIN_REGISTRY.get(codepoint)


def lookup_char(char: str) -> Optional[DMin]:
    """Return the :class:`DMin` record for the first character of *char*.

    Convenience wrapper around :func:`lookup` for string input.
    """
    if not char:
        return None
    return lookup(ord(char[0]))


def encode(codepoint: int) -> str:
    """Return the MinCode string for *codepoint* (e.g. ``'C:SHF:SHD:MJH'``).

    Returns an empty string when *codepoint* is not in the registry.
    """
    entry = DMIN_REGISTRY.get(codepoint)
    return entry.code if entry is not None else ""


def numeric_vector(codepoint: int) -> Optional[tuple]:
    """Return the numeric 5-vector ``(u, c, g, f_mask, t_mask)`` for *codepoint*.

    Returns ``None`` when *codepoint* is not in the registry.
    The vector is the core numeric encoding of ``D_min(x) ∈ ℕ⁵``.
    """
    entry = DMIN_REGISTRY.get(codepoint)
    return entry.vector if entry is not None else None


def group_members(group: PhonGroup) -> List[int]:
    """Return all code-points whose :attr:`~DMin.group` equals *group*."""
    return [cp for cp, d in DMIN_REGISTRY.items() if d.group is group]


def category_members(category: PhonCategory) -> List[int]:
    """Return all code-points whose :attr:`~DMin.category` equals *category*."""
    return [cp for cp, d in DMIN_REGISTRY.items() if d.category is category]


def has_feature(codepoint: int, feature: PhonFeature) -> bool:
    """Return ``True`` if *codepoint* has *feature* in its feature set."""
    entry = DMIN_REGISTRY.get(codepoint)
    return feature in entry.features if entry is not None else False


def has_transform(codepoint: int, transform: PhonTransform) -> bool:
    """Return ``True`` if *codepoint* has *transform* in its transform set."""
    entry = DMIN_REGISTRY.get(codepoint)
    return transform in entry.transforms if entry is not None else False


def emphatic_consonants() -> List[int]:
    """Return code-points of all emphatic (مطبق) consonants."""
    return [cp for cp in DMIN_REGISTRY if has_feature(cp, PhonFeature.ITBAQ)]


def nasal_consonants() -> List[int]:
    """Return code-points of all nasal (أنفي) consonants."""
    return [cp for cp in DMIN_REGISTRY if has_feature(cp, PhonFeature.ANFI)]
