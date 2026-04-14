"""Tests for the D_min minimal complete Arabic phonological model."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    PhonCategory,
    PhonFeature,
    PhonGroup,
    PhonTransform,
)
from arabic_engine.core.types import DMin
from arabic_engine.signifier.dmin import (
    DMIN_REGISTRY,
    category_members,
    emphatic_consonants,
    encode,
    group_members,
    has_feature,
    has_transform,
    lookup,
    lookup_char,
    nasal_consonants,
    numeric_vector,
)

# ── Registry completeness ────────────────────────────────────────────

class TestRegistryCompleteness:
    """Verify the registry contains all 39 expected Unicode code-points."""

    # 28 consonants + semi-vowels (Table 1)
    CONSONANTS = [
        0x0621,  # ء
        0x0628,  # ب
        0x062A,  # ت
        0x062B,  # ث
        0x062C,  # ج
        0x062D,  # ح
        0x062E,  # خ
        0x062F,  # د
        0x0630,  # ذ
        0x0631,  # ر
        0x0632,  # ز
        0x0633,  # س
        0x0634,  # ش
        0x0635,  # ص
        0x0636,  # ض
        0x0637,  # ط
        0x0638,  # ظ
        0x0639,  # ع
        0x063A,  # غ
        0x0641,  # ف
        0x0642,  # ق
        0x0643,  # ك
        0x0644,  # ل
        0x0645,  # م
        0x0646,  # ن
        0x0647,  # ه
        0x0648,  # و
        0x064A,  # ي
    ]
    # 10 diacritics / marks (Table 2)
    MARKS = [
        0x064E,  # َ  فتحة
        0x064F,  # ُ  ضمة
        0x0650,  # ِ  كسرة
        0x0651,  # ّ  شدة
        0x0652,  # ْ  سكون
        0x064B,  # ً  تنوين فتح
        0x064C,  # ٌ  تنوين ضم
        0x064D,  # ٍ  تنوين كسر
        0x0653,  # ٓ  مدة
        0x0670,  # ٰ  ألف خنجرية
    ]
    # 1 long vowel letter (Table 3 — و ي already in Table 1)
    LONG_VOWELS = [0x0627]  # ا

    def test_all_consonants_present(self):
        for cp in self.CONSONANTS:
            assert cp in DMIN_REGISTRY, f"Missing consonant U+{cp:04X}"

    def test_all_marks_present(self):
        for cp in self.MARKS:
            assert cp in DMIN_REGISTRY, f"Missing mark U+{cp:04X}"

    def test_alef_long_vowel_present(self):
        assert 0x0627 in DMIN_REGISTRY

    def test_total_entry_count(self):
        expected = len(self.CONSONANTS) + len(self.MARKS) + len(self.LONG_VOWELS)
        assert len(DMIN_REGISTRY) == expected


# ── DMin dataclass contract ──────────────────────────────────────────

class TestDMinContract:
    """Every DMin entry must satisfy the D_min(x) = (u,c,g,f,t) contract."""

    def test_all_entries_have_unicode_matching_key(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.unicode == cp

    def test_all_entries_have_valid_category(self):
        for cp, d in DMIN_REGISTRY.items():
            assert isinstance(d.category, PhonCategory)

    def test_all_entries_have_valid_group(self):
        for cp, d in DMIN_REGISTRY.items():
            assert isinstance(d.group, PhonGroup)

    def test_all_entries_have_non_empty_features(self):
        for cp, d in DMIN_REGISTRY.items():
            assert len(d.features) >= 1, f"U+{cp:04X} has no features"

    def test_all_entries_have_non_empty_transforms(self):
        for cp, d in DMIN_REGISTRY.items():
            assert len(d.transforms) >= 1, f"U+{cp:04X} has no transforms"

    def test_all_entries_have_non_empty_code(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.code, f"U+{cp:04X} has empty code"

    def test_char_property(self):
        d = DMIN_REGISTRY[0x0628]  # ب
        assert d.char == "ب"

    def test_frozen(self):
        d = DMIN_REGISTRY[0x0628]
        with pytest.raises((AttributeError, TypeError)):
            d.code = "modified"  # type: ignore[misc]


# ── Numeric vector (D_min numeric encoding) ──────────────────────────

class TestNumericVector:
    """D_min(x) = (u, c, g, feature_mask, transform_mask) ∈ ℕ⁵."""

    def test_vector_is_5_tuple_of_ints(self):
        for cp, d in DMIN_REGISTRY.items():
            v = d.vector
            assert len(v) == 5
            assert all(isinstance(x, int) for x in v)

    def test_vector_first_element_is_codepoint(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.vector[0] == cp

    def test_vector_second_element_is_category_value(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.vector[1] == d.category.value

    def test_vector_third_element_is_group_value(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.vector[2] == d.group.value

    def test_feature_mask_non_zero(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.feature_mask > 0

    def test_transform_mask_non_zero(self):
        for cp, d in DMIN_REGISTRY.items():
            assert d.transform_mask > 0

    def test_feature_mask_bit_round_trip(self):
        d = DMIN_REGISTRY[0x0628]  # ب — features: SHADID, MAJHUR
        mask = d.feature_mask
        reconstructed = frozenset(
            f for f in PhonFeature if mask & (1 << (f.value - 1))
        )
        assert reconstructed == d.features

    def test_transform_mask_bit_round_trip(self):
        d = DMIN_REGISTRY[0x0644]  # ل — has TAAREF etc.
        mask = d.transform_mask
        reconstructed = frozenset(
            t for t in PhonTransform if mask & (1 << (t.value - 1))
        )
        assert reconstructed == d.transforms

    def test_all_vectors_unique(self):
        """Every phonological unit maps to a distinct numeric vector."""
        vectors = [d.vector for d in DMIN_REGISTRY.values()]
        assert len(vectors) == len(set(vectors))


# ── Specific phoneme correctness ─────────────────────────────────────

class TestSpecificPhonemes:
    """Spot-check selected phonemes against the reference tables."""

    def test_hamza_category_and_group(self):
        d = DMIN_REGISTRY[0x0621]  # ء
        assert d.category is PhonCategory.CONSONANT
        assert d.group is PhonGroup.HNJ_MZM

    def test_hamza_features(self):
        d = DMIN_REGISTRY[0x0621]
        assert PhonFeature.SHADID in d.features
        assert PhonFeature.MAHMOUS in d.features
        assert PhonFeature.HMZ in d.features

    def test_ba_shadid_majhur(self):
        d = DMIN_REGISTRY[0x0628]  # ب
        assert PhonFeature.SHADID in d.features
        assert PhonFeature.MAJHUR in d.features

    def test_sad_emphatic_sibilant(self):
        d = DMIN_REGISTRY[0x0635]  # ص
        assert PhonFeature.ITBAQ in d.features
        assert PhonFeature.SAFIR in d.features
        assert PhonFeature.MAHMOUS in d.features

    def test_dad_emphatic_prolonged(self):
        d = DMIN_REGISTRY[0x0636]  # ض
        assert PhonFeature.ITBAQ in d.features
        assert PhonFeature.ASTTALA in d.features
        assert PhonFeature.MAJHUR in d.features

    def test_ra_trill(self):
        d = DMIN_REGISTRY[0x0631]  # ر
        assert PhonFeature.TAKRIR in d.features
        assert PhonTransform.TAFKHIM in d.transforms
        assert PhonTransform.TARQIQ in d.transforms

    def test_lam_lateral_taaref(self):
        d = DMIN_REGISTRY[0x0644]  # ل
        assert PhonFeature.MUNHARIF in d.features
        assert PhonTransform.TAAREF in d.transforms
        assert PhonTransform.IDGHAM_SHAMSI in d.transforms

    def test_nun_nasal_full_transforms(self):
        d = DMIN_REGISTRY[0x0646]  # ن
        assert PhonFeature.ANFI in d.features
        assert PhonFeature.GHUNNA in d.features
        assert PhonTransform.IZHAR in d.transforms
        assert PhonTransform.IDGHAM in d.transforms
        assert PhonTransform.IKHFAA in d.transforms
        assert PhonTransform.IQLAB in d.transforms

    def test_waw_semi_vowel(self):
        d = DMIN_REGISTRY[0x0648]  # و
        assert d.category is PhonCategory.SEMI_VOWEL
        assert d.group is PhonGroup.SHF_LYN
        assert PhonFeature.ITLAL in d.features
        assert PhonFeature.TAWIL in d.features
        assert PhonTransform.MADD in d.transforms
        assert PhonTransform.ATAF in d.transforms

    def test_ya_semi_vowel(self):
        d = DMIN_REGISTRY[0x064A]  # ي
        assert d.category is PhonCategory.SEMI_VOWEL
        assert d.group is PhonGroup.HNK_LYN
        assert PhonTransform.NISBAH in d.transforms
        assert PhonTransform.MUTAKALLIM in d.transforms

    def test_fatha_short_vowel(self):
        d = DMIN_REGISTRY[0x064E]  # َ
        assert d.category is PhonCategory.SHORT_VOWEL
        assert d.group is PhonGroup.FTH
        assert PhonFeature.QASIR in d.features
        assert PhonFeature.NUWAWI in d.features
        assert PhonTransform.IIRAB in d.transforms

    def test_sukun_closure(self):
        d = DMIN_REGISTRY[0x0652]  # ْ
        assert d.category is PhonCategory.SUKUN
        assert PhonFeature.SIFR_HARAKA in d.features
        assert PhonFeature.QAFIL in d.features
        assert PhonTransform.JAZM in d.transforms

    def test_shadda_gemination(self):
        d = DMIN_REGISTRY[0x0651]  # ّ
        assert d.category is PhonCategory.SHADDA
        assert PhonFeature.TADFIF in d.features
        assert PhonTransform.IDGHAM in d.transforms
        assert PhonTransform.TADFIF_TR in d.transforms

    def test_tanwin_fath_indefinite(self):
        d = DMIN_REGISTRY[0x064B]  # ً
        assert d.category is PhonCategory.TANWIN
        assert d.group is PhonGroup.TAN_FTH
        assert PhonTransform.TANKIR in d.transforms

    def test_alef_long_vowel(self):
        d = DMIN_REGISTRY[0x0627]  # ا
        assert d.category is PhonCategory.LONG_VOWEL
        assert d.group is PhonGroup.ALF_LV
        assert PhonFeature.TAWIL in d.features
        assert PhonTransform.MADD in d.transforms


# ── Public API functions ─────────────────────────────────────────────

class TestPublicAPI:
    """Tests for the module-level query functions."""

    def test_lookup_returns_dmin(self):
        d = lookup(0x0628)
        assert isinstance(d, DMin)
        assert d.unicode == 0x0628

    def test_lookup_unknown_returns_none(self):
        assert lookup(0x0041) is None  # 'A' is not Arabic

    def test_lookup_char(self):
        d = lookup_char("ب")
        assert d is not None
        assert d.unicode == 0x0628

    def test_lookup_char_empty_returns_none(self):
        assert lookup_char("") is None

    def test_encode_ba(self):
        assert encode(0x0628) == "C:SHF:SHD:MJH"

    def test_encode_unknown(self):
        assert encode(0x0041) == ""

    def test_numeric_vector_ba(self):
        v = numeric_vector(0x0628)
        assert v is not None
        assert v[0] == 0x0628

    def test_numeric_vector_unknown_returns_none(self):
        assert numeric_vector(0x0041) is None

    def test_group_members_hlq(self):
        members = group_members(PhonGroup.HLQ)
        # ح U+062D, ع U+0639, غ U+063A
        assert 0x062D in members
        assert 0x0639 in members
        assert 0x063A in members

    def test_group_members_asli(self):
        members = group_members(PhonGroup.ASLI)
        assert 0x0632 in members  # ز
        assert 0x0633 in members  # س

    def test_category_members_semi_vowel(self):
        members = category_members(PhonCategory.SEMI_VOWEL)
        assert set(members) == {0x0648, 0x064A}

    def test_category_members_tanwin(self):
        members = category_members(PhonCategory.TANWIN)
        assert set(members) == {0x064B, 0x064C, 0x064D}

    def test_has_feature_itbaq(self):
        assert has_feature(0x0635, PhonFeature.ITBAQ)   # ص emphatic
        assert not has_feature(0x0628, PhonFeature.ITBAQ)  # ب not emphatic

    def test_has_transform_taaref(self):
        assert has_transform(0x0644, PhonTransform.TAAREF)   # ل has تعريف
        assert not has_transform(0x0628, PhonTransform.TAAREF)

    def test_emphatic_consonants_contains_four(self):
        emphatics = emphatic_consonants()
        # ص ض ط ظ are emphatic
        assert 0x0635 in emphatics  # ص
        assert 0x0636 in emphatics  # ض
        assert 0x0637 in emphatics  # ط
        assert 0x0638 in emphatics  # ظ

    def test_nasal_consonants_contains_mim_and_nun(self):
        nasals = nasal_consonants()
        assert 0x0645 in nasals  # م
        assert 0x0646 in nasals  # ن


# ── Phonological groupings from Table 4 ─────────────────────────────

class TestPhonGroups:
    """Verify the major consonant groupings match Table 4."""

    def test_pharyngeal_group(self):
        """حنجرية/مزمارية: ء ه"""
        hnj_mzm = set(group_members(PhonGroup.HNJ_MZM))
        hnj_hlq = set(group_members(PhonGroup.HNJ_HLQ))
        assert 0x0621 in hnj_mzm   # ء
        assert 0x0647 in hnj_hlq   # ه

    def test_faucal_group(self):
        """حلقية: ع ح غ خ"""
        hlq = set(group_members(PhonGroup.HLQ))
        hlq_lhw = set(group_members(PhonGroup.HLQ_LHW))
        assert {0x062D, 0x0639, 0x063A} == hlq   # ح ع غ
        assert 0x062E in hlq_lhw                  # خ

    def test_uvular_velar_group(self):
        """لهوية/طبقية: ق ك"""
        lhw = set(group_members(PhonGroup.LHW))
        tbq = set(group_members(PhonGroup.TBQ_LHW))
        assert 0x0642 in lhw   # ق
        assert 0x0643 in tbq   # ك

    def test_palatal_group(self):
        """شجرية/حنكية: ج ش"""
        shjr = set(group_members(PhonGroup.SHJR))
        assert 0x062C in shjr   # ج
        assert 0x0634 in shjr   # ش

    def test_labial_group(self):
        """شفوية: ب م"""
        shf = set(group_members(PhonGroup.SHF))
        assert 0x0628 in shf   # ب
        assert 0x0645 in shf   # م
