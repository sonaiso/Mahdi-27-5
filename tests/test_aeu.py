"""Tests for the AEU (Alphabetic Encoding Unit) periodic table.

Verifies that the Master Minimal Alphabetic Encoding Architecture
satisfies all structural and proof-theoretic invariants:

    AMU = (R, B, N, G, E)
    AEU = {ID, Name, Class, Function, Referent, Boundary, Necessity,
           Governing_Role, Layer, Combination_Type, Math_Form,
           Unicode_Codepoint, Unicode_Profile, Depends_On, Unlocks,
           Proof_Status}
"""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import (
    CombinationType,
    ElementClass,
    ElementFunction,
    ElementLayer,
    ProofStatus,
    UnicodeProfileType,
)
from arabic_engine.core.types import AEU
from arabic_engine.signifier.aeu import (
    AEU_BY_UNICODE,
    AEU_REGISTRY,
    elements_by_class,
    elements_by_combination_type,
    elements_by_function,
    elements_by_layer,
    elements_by_proof_status,
    lookup,
    lookup_char,
    lookup_unicode,
    periodic_table,
    proven_elements,
)

# ── Registry completeness ────────────────────────────────────────────


class TestRegistryCompleteness:
    """AEU_REGISTRY must contain exactly 39 entries covering all Arabic elements."""

    # 28 consonants / semi-vowels (Table 1: AE_001..AE_028)
    CONSONANT_IDS = [f"AE_{i:03d}" for i in range(1, 29)]
    # 10 diacritics / marks (Table 2: AE_029..AE_038)
    MARK_IDS = [f"AE_{i:03d}" for i in range(29, 39)]
    # 1 long vowel letter (Table 3: AE_039)
    LONG_VOWEL_IDS = ["AE_039"]

    def test_all_consonant_ids_present(self):
        for eid in self.CONSONANT_IDS:
            assert eid in AEU_REGISTRY, f"Missing element {eid}"

    def test_all_mark_ids_present(self):
        for eid in self.MARK_IDS:
            assert eid in AEU_REGISTRY, f"Missing element {eid}"

    def test_long_vowel_id_present(self):
        assert "AE_039" in AEU_REGISTRY

    def test_total_entry_count(self):
        expected = len(self.CONSONANT_IDS) + len(self.MARK_IDS) + len(self.LONG_VOWEL_IDS)
        assert len(AEU_REGISTRY) == expected

    def test_secondary_index_matches_registry(self):
        assert len(AEU_BY_UNICODE) == len(AEU_REGISTRY)
        for a in AEU_REGISTRY.values():
            assert AEU_BY_UNICODE[a.unicode_codepoint] is a


# ── AEU dataclass invariants (AMU = R, B, N, G, E) ───────────────────


class TestAEUContract:
    """Every AEU entry must satisfy the full 16-field AMU contract."""

    def test_all_element_ids_match_key(self):
        for eid, a in AEU_REGISTRY.items():
            assert a.element_id == eid

    def test_all_names_non_empty(self):
        for eid, a in AEU_REGISTRY.items():
            assert a.element_name, f"{eid} has empty element_name"

    def test_all_classes_are_valid_enum(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.element_class, ElementClass), f"{eid}"

    def test_all_functions_are_valid_enum(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.element_function, ElementFunction), f"{eid}"

    def test_all_referents_non_empty(self):
        """R — Referent must be present for every element."""
        for eid, a in AEU_REGISTRY.items():
            assert a.referent, f"{eid} has empty referent"

    def test_all_boundaries_non_empty(self):
        """B — Boundary must be present for every element."""
        for eid, a in AEU_REGISTRY.items():
            assert a.boundary, f"{eid} has empty boundary"

    def test_all_necessities_non_empty(self):
        """N — Necessity must be present for every element."""
        for eid, a in AEU_REGISTRY.items():
            assert a.necessity, f"{eid} has empty necessity"

    def test_all_governing_roles_non_empty(self):
        """G — Governing Role must be present for every element."""
        for eid, a in AEU_REGISTRY.items():
            assert a.governing_role, f"{eid} has empty governing_role"

    def test_all_unicode_codepoints_positive(self):
        """E — Encoding identity: codepoint must be a positive integer."""
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.unicode_codepoint, int), f"{eid}"
            assert a.unicode_codepoint > 0, f"{eid} has zero codepoint"

    def test_all_layers_are_valid_enum(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.layer, ElementLayer), f"{eid}"

    def test_all_combination_types_are_valid_enum(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.combination_type, CombinationType), f"{eid}"

    def test_all_unicode_profiles_are_valid_enum(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.unicode_profile, UnicodeProfileType), f"{eid}"

    def test_all_proof_statuses_are_valid_enum(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.proof_status, ProofStatus), f"{eid}"

    def test_all_depends_on_are_tuples_of_strings(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.depends_on, tuple), f"{eid}"
            for dep in a.depends_on:
                assert isinstance(dep, str), f"{eid} depends_on has non-string item"

    def test_all_depends_on_non_empty(self):
        for eid, a in AEU_REGISTRY.items():
            assert len(a.depends_on) >= 1, f"{eid} has empty depends_on"

    def test_all_unlocks_are_tuples_of_strings(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.unlocks, tuple), f"{eid}"
            for u in a.unlocks:
                assert isinstance(u, str), f"{eid} unlocks has non-string item"

    def test_all_unlocks_non_empty(self):
        for eid, a in AEU_REGISTRY.items():
            assert len(a.unlocks) >= 1, f"{eid} has empty unlocks"

    def test_frozen(self):
        a = AEU_REGISTRY["AE_002"]
        with pytest.raises((AttributeError, TypeError)):
            a.element_name = "modified"  # type: ignore[misc]

    def test_is_aeu_instance(self):
        for a in AEU_REGISTRY.values():
            assert isinstance(a, AEU)


# ── math_form vector ─────────────────────────────────────────────────


class TestMathForm:
    """Math_Form must be an 8-bit binary vector in {0,1}⁸."""

    def test_all_math_forms_are_tuples(self):
        for eid, a in AEU_REGISTRY.items():
            assert isinstance(a.math_form, tuple), f"{eid}"

    def test_all_math_forms_have_length_8(self):
        for eid, a in AEU_REGISTRY.items():
            assert len(a.math_form) == 8, f"{eid} has math_form length {len(a.math_form)}"

    def test_all_math_form_values_are_binary(self):
        for eid, a in AEU_REGISTRY.items():
            for i, bit in enumerate(a.math_form):
                assert bit in (0, 1), f"{eid} math_form[{i}] = {bit}"

    def test_math_vector_property_returns_8_tuple(self):
        for eid, a in AEU_REGISTRY.items():
            v = a.math_vector
            assert len(v) == 8
            assert all(x in (0, 1) for x in v)

    def test_fatha_math_form(self):
        """Fatha: vowel_marker=1, short=1; all others 0."""
        a = AEU_REGISTRY["AE_029"]  # َ  Fatha
        assert a.math_form == (0, 1, 1, 0, 0, 0, 0, 0)

    def test_shadda_math_form(self):
        """Shadda: gemination=1, special_mark=1."""
        a = AEU_REGISTRY["AE_032"]  # ّ  Shadda
        assert a.math_form == (0, 0, 0, 0, 0, 1, 0, 1)

    def test_sukun_math_form(self):
        """Sukun: closure=1, special_mark=1."""
        a = AEU_REGISTRY["AE_033"]  # ْ  Sukun
        assert a.math_form == (0, 0, 0, 0, 1, 0, 0, 1)

    def test_tanwin_math_form(self):
        """All three tanwin: vowel_marker=1, short=1, indefiniteness=1."""
        for eid in ("AE_034", "AE_035", "AE_036"):
            a = AEU_REGISTRY[eid]
            assert a.math_form[1] == 1, f"{eid} vowel_marker should be 1"
            assert a.math_form[2] == 1, f"{eid} short should be 1"
            assert a.math_form[6] == 1, f"{eid} indefiniteness should be 1"

    def test_base_consonants_math_form(self):
        """Regular consonants: base_letter=1, all others 0."""
        for eid in ("AE_002", "AE_003", "AE_004", "AE_008"):
            a = AEU_REGISTRY[eid]
            assert a.math_form == (1, 0, 0, 0, 0, 0, 0, 0)

    def test_semi_vowels_math_form(self):
        """Waw and Ya carry long-vowel feature: base_letter=1, long=1."""
        for eid in ("AE_027", "AE_028"):
            a = AEU_REGISTRY[eid]
            assert a.math_form[0] == 1, f"{eid} base_letter should be 1"
            assert a.math_form[3] == 1, f"{eid} long should be 1"

    def test_alef_math_form(self):
        """Alef: base_letter=1, long=1."""
        a = AEU_REGISTRY["AE_039"]
        assert a.math_form[0] == 1
        assert a.math_form[3] == 1


# ── Specific element spot-checks ─────────────────────────────────────


class TestSpecificElements:
    """Spot-check key elements against the reference spec."""

    def test_hamza_is_composite_decision_unit(self):
        a = AEU_REGISTRY["AE_001"]
        assert a.element_class is ElementClass.COMPOSITE_DECISION_UNIT
        assert a.element_function is ElementFunction.ENCODING_BEARING
        assert a.unicode_codepoint == 0x0621
        assert a.unicode_profile is UnicodeProfileType.CONTEXTUAL_RENDERING
        assert a.proof_status is ProofStatus.PENDING
        assert "PR_010" in a.depends_on

    def test_ba_base_letter(self):
        a = AEU_REGISTRY["AE_002"]
        assert a.element_class is ElementClass.BASE_LETTER
        assert a.element_function is ElementFunction.IDENTITY_BEARING
        assert a.unicode_codepoint == 0x0628
        assert a.unicode_profile is UnicodeProfileType.SINGLE_CODE_POINT
        assert a.proof_status is ProofStatus.PROVEN

    def test_fatha_vowel_marker(self):
        a = AEU_REGISTRY["AE_029"]
        assert a.element_class is ElementClass.VOWEL_MARKER
        assert a.element_function is ElementFunction.MOTION_BEARING
        assert a.unicode_codepoint == 0x064E
        assert a.unicode_profile is UnicodeProfileType.COMBINING_MARK
        assert a.combination_type is CombinationType.ATTACHES_TO_BASE
        assert "PR_008" in a.depends_on

    def test_damma_vowel_marker(self):
        a = AEU_REGISTRY["AE_030"]
        assert a.element_class is ElementClass.VOWEL_MARKER
        assert a.unicode_codepoint == 0x064F

    def test_kasra_vowel_marker(self):
        a = AEU_REGISTRY["AE_031"]
        assert a.element_class is ElementClass.VOWEL_MARKER
        assert a.unicode_codepoint == 0x0650

    def test_shadda_structural_marker(self):
        a = AEU_REGISTRY["AE_032"]
        assert a.element_class is ElementClass.STRUCTURAL_MARKER
        assert a.element_function is ElementFunction.DUPLICATION_BEARING
        assert a.unicode_codepoint == 0x0651
        assert a.combination_type is CombinationType.CLUSTER_INTERNAL
        assert "PR_009" in a.depends_on

    def test_sukun_structural_marker(self):
        a = AEU_REGISTRY["AE_033"]
        assert a.element_class is ElementClass.STRUCTURAL_MARKER
        assert a.element_function is ElementFunction.CLOSURE_BEARING
        assert a.unicode_codepoint == 0x0652

    def test_tanwin_fath_indefiniteness(self):
        a = AEU_REGISTRY["AE_034"]
        assert a.element_class is ElementClass.STRUCTURAL_MARKER
        assert a.element_function is ElementFunction.INDEFINITENESS_BEARING
        assert a.unicode_codepoint == 0x064B
        assert a.proof_status is ProofStatus.PENDING
        assert "PR_011" in a.depends_on

    def test_tanwin_damm_indefiniteness(self):
        a = AEU_REGISTRY["AE_035"]
        assert a.element_function is ElementFunction.INDEFINITENESS_BEARING
        assert a.unicode_codepoint == 0x064C

    def test_tanwin_kasr_indefiniteness(self):
        a = AEU_REGISTRY["AE_036"]
        assert a.element_function is ElementFunction.INDEFINITENESS_BEARING
        assert a.unicode_codepoint == 0x064D

    def test_madda_composite(self):
        a = AEU_REGISTRY["AE_037"]
        assert a.element_class is ElementClass.STRUCTURAL_MARKER
        assert a.element_function is ElementFunction.ENCODING_BEARING
        assert a.unicode_codepoint == 0x0653
        assert a.proof_status is ProofStatus.COMPOSITE
        assert "PR_010" in a.depends_on
        assert "PR_012" in a.depends_on

    def test_superscript_alef_carrier(self):
        a = AEU_REGISTRY["AE_038"]
        assert a.element_class is ElementClass.CARRIER_RELATED_UNIT
        assert a.element_function is ElementFunction.LENGTH_BEARING
        assert a.unicode_codepoint == 0x0670
        assert a.proof_status is ProofStatus.PENDING

    def test_alef_long_vowel(self):
        a = AEU_REGISTRY["AE_039"]
        assert a.element_class is ElementClass.BASE_LETTER
        assert a.element_function is ElementFunction.LENGTH_BEARING
        assert a.unicode_codepoint == 0x0627
        assert a.proof_status is ProofStatus.PROVEN

    def test_waw_semi_vowel_long(self):
        a = AEU_REGISTRY["AE_027"]
        assert a.element_class is ElementClass.BASE_LETTER
        assert a.element_function is ElementFunction.LENGTH_BEARING
        assert a.unicode_codepoint == 0x0648

    def test_ya_semi_vowel_long(self):
        a = AEU_REGISTRY["AE_028"]
        assert a.element_class is ElementClass.BASE_LETTER
        assert a.element_function is ElementFunction.LENGTH_BEARING
        assert a.unicode_codepoint == 0x064A

    def test_lam_identity_bearing(self):
        a = AEU_REGISTRY["AE_023"]  # ل
        assert a.element_class is ElementClass.BASE_LETTER
        assert a.element_function is ElementFunction.IDENTITY_BEARING
        assert a.unicode_codepoint == 0x0644

    def test_nun_identity_bearing(self):
        a = AEU_REGISTRY["AE_025"]  # ن
        assert a.element_class is ElementClass.BASE_LETTER
        assert a.element_function is ElementFunction.IDENTITY_BEARING
        assert a.unicode_codepoint == 0x0646


# ── Char property ────────────────────────────────────────────────────


class TestCharProperty:
    """AEU.char must return the Unicode character for each element."""

    def test_hamza_char(self):
        assert AEU_REGISTRY["AE_001"].char == "ء"

    def test_ba_char(self):
        assert AEU_REGISTRY["AE_002"].char == "ب"

    def test_fatha_char(self):
        assert AEU_REGISTRY["AE_029"].char == "َ"

    def test_alef_char(self):
        assert AEU_REGISTRY["AE_039"].char == "ا"


# ── to_row() / periodic_table() ─────────────────────────────────────


class TestPeriodicTable:
    """periodic_table() must return one row per element with all 16 columns."""

    REQUIRED_COLUMNS = {
        "Element_ID", "Name", "Class", "Function", "Referent",
        "Boundary", "Necessity", "Governing_Role", "Layer",
        "Combination_Type", "Math_Form", "Unicode_Codepoint",
        "Unicode_Profile", "Depends_On", "Unlocks", "Proof_Status",
    }

    def test_periodic_table_has_39_rows(self):
        table = periodic_table()
        assert len(table) == 39

    def test_all_rows_have_required_columns(self):
        for row in periodic_table():
            assert self.REQUIRED_COLUMNS == set(row.keys()), (
                f"Row {row.get('Element_ID')} missing columns"
            )

    def test_unicode_codepoint_format(self):
        for row in periodic_table():
            cp = row["Unicode_Codepoint"]
            assert cp.startswith("U+"), f"{row['Element_ID']}: bad format {cp}"

    def test_rows_sorted_by_element_id(self):
        table = periodic_table()
        ids = [row["Element_ID"] for row in table]
        assert ids == sorted(ids)

    def test_to_row_matches_periodic_table(self):
        table = periodic_table()
        for row in table:
            eid = row["Element_ID"]
            a = AEU_REGISTRY[eid]
            assert a.to_row() == row

    def test_proof_status_values_are_strings(self):
        for row in periodic_table():
            assert isinstance(row["Proof_Status"], str)


# ── Public API functions ─────────────────────────────────────────────


class TestPublicAPI:
    """Tests for the module-level query functions."""

    def test_lookup_returns_aeu(self):
        a = lookup("AE_002")
        assert isinstance(a, AEU)
        assert a.element_id == "AE_002"

    def test_lookup_unknown_returns_none(self):
        assert lookup("AE_999") is None

    def test_lookup_unicode_ba(self):
        a = lookup_unicode(0x0628)
        assert a is not None
        assert a.element_id == "AE_002"

    def test_lookup_unicode_unknown_returns_none(self):
        assert lookup_unicode(0x0041) is None  # 'A' not Arabic

    def test_lookup_char_ba(self):
        a = lookup_char("ب")
        assert a is not None
        assert a.unicode_codepoint == 0x0628

    def test_lookup_char_empty_returns_none(self):
        assert lookup_char("") is None

    def test_elements_by_class_base_letters(self):
        base = elements_by_class(ElementClass.BASE_LETTER)
        # 26 consonants (AE_001 counted as COMPOSITE, not BASE) +
        # 2 semi-vowels + 1 alef = varies; check subset
        unicodes = {a.unicode_codepoint for a in base}
        assert 0x0628 in unicodes  # ب
        assert 0x0644 in unicodes  # ل
        assert 0x0627 in unicodes  # ا

    def test_elements_by_class_vowel_markers(self):
        vowels = elements_by_class(ElementClass.VOWEL_MARKER)
        assert len(vowels) == 3  # فتحة ضمة كسرة
        unicodes = {a.unicode_codepoint for a in vowels}
        assert 0x064E in unicodes  # َ
        assert 0x064F in unicodes  # ُ
        assert 0x0650 in unicodes  # ِ

    def test_elements_by_class_structural_markers(self):
        markers = elements_by_class(ElementClass.STRUCTURAL_MARKER)
        # شدة + سكون + 3 تنوين + مدة = 6
        assert len(markers) == 6
        unicodes = {a.unicode_codepoint for a in markers}
        assert 0x0651 in unicodes  # ّ
        assert 0x0652 in unicodes  # ْ
        assert 0x064B in unicodes  # ً
        assert 0x0653 in unicodes  # ٓ

    def test_elements_by_class_composite_decision_unit(self):
        composites = elements_by_class(ElementClass.COMPOSITE_DECISION_UNIT)
        assert len(composites) == 1
        assert composites[0].unicode_codepoint == 0x0621  # ء

    def test_elements_by_class_carrier_related(self):
        carriers = elements_by_class(ElementClass.CARRIER_RELATED_UNIT)
        assert len(carriers) == 1
        assert carriers[0].unicode_codepoint == 0x0670  # ٰ

    def test_elements_by_layer_phonological(self):
        phon = elements_by_layer(ElementLayer.PHONOLOGICAL)
        unicodes = {a.unicode_codepoint for a in phon}
        assert 0x0628 in unicodes  # ب consonant
        assert 0x0627 in unicodes  # ا alef

    def test_elements_by_layer_orthographic(self):
        orth = elements_by_layer(ElementLayer.ORTHOGRAPHIC)
        unicodes = {a.unicode_codepoint for a in orth}
        # Short vowel diacritics are orthographic
        assert 0x064E in unicodes  # َ
        assert 0x064F in unicodes  # ُ

    def test_elements_by_function_identity_bearing(self):
        ib = elements_by_function(ElementFunction.IDENTITY_BEARING)
        # All regular consonants except Hamza, Waw, Ya
        assert len(ib) >= 24
        unicodes = {a.unicode_codepoint for a in ib}
        assert 0x0628 in unicodes  # ب

    def test_elements_by_function_motion_bearing(self):
        mb = elements_by_function(ElementFunction.MOTION_BEARING)
        assert len(mb) == 3  # فتحة ضمة كسرة

    def test_elements_by_function_closure_bearing(self):
        cb = elements_by_function(ElementFunction.CLOSURE_BEARING)
        assert len(cb) == 1
        assert cb[0].unicode_codepoint == 0x0652  # ْ

    def test_elements_by_function_duplication_bearing(self):
        db = elements_by_function(ElementFunction.DUPLICATION_BEARING)
        assert len(db) == 1
        assert db[0].unicode_codepoint == 0x0651  # ّ

    def test_elements_by_function_indefiniteness_bearing(self):
        ib = elements_by_function(ElementFunction.INDEFINITENESS_BEARING)
        assert len(ib) == 3  # تنوين فتح ضم كسر
        unicodes = {a.unicode_codepoint for a in ib}
        assert 0x064B in unicodes
        assert 0x064C in unicodes
        assert 0x064D in unicodes

    def test_elements_by_function_length_bearing(self):
        lb = elements_by_function(ElementFunction.LENGTH_BEARING)
        unicodes = {a.unicode_codepoint for a in lb}
        assert 0x0627 in unicodes  # ا
        assert 0x0648 in unicodes  # و
        assert 0x064A in unicodes  # ي
        assert 0x0670 in unicodes  # ٰ

    def test_elements_by_proof_status_proven(self):
        proven = elements_by_proof_status(ProofStatus.PROVEN)
        assert len(proven) >= 30
        unicodes = {a.unicode_codepoint for a in proven}
        assert 0x0628 in unicodes

    def test_elements_by_proof_status_pending(self):
        pending = elements_by_proof_status(ProofStatus.PENDING)
        unicodes = {a.unicode_codepoint for a in pending}
        assert 0x0621 in unicodes  # ء  Hamza
        assert 0x064B in unicodes  # ً  tanwin

    def test_elements_by_combination_type_standalone(self):
        standalone = elements_by_combination_type(CombinationType.STANDALONE)
        # All base letters
        unicodes = {a.unicode_codepoint for a in standalone}
        assert 0x0628 in unicodes

    def test_elements_by_combination_type_attaches_to_base(self):
        attaches = elements_by_combination_type(CombinationType.ATTACHES_TO_BASE)
        unicodes = {a.unicode_codepoint for a in attaches}
        assert 0x064E in unicodes  # َ
        assert 0x0652 in unicodes  # ْ

    def test_proven_elements_helper(self):
        proven = proven_elements()
        assert len(proven) == len(elements_by_proof_status(ProofStatus.PROVEN))

    def test_is_proven_property(self):
        assert AEU_REGISTRY["AE_002"].is_proven() is True  # ب
        assert AEU_REGISTRY["AE_001"].is_proven() is False  # ء


# ── Unique codepoints ────────────────────────────────────────────────


class TestUniqueness:
    """Every element must map to a distinct Unicode code-point."""

    def test_all_codepoints_unique(self):
        codepoints = [a.unicode_codepoint for a in AEU_REGISTRY.values()]
        assert len(codepoints) == len(set(codepoints))

    def test_all_element_ids_unique(self):
        ids = list(AEU_REGISTRY.keys())
        assert len(ids) == len(set(ids))


# ── Unicode profile consistency ──────────────────────────────────────


class TestUnicodeProfileConsistency:
    """Base letters use SINGLE_CODE_POINT; diacritics use COMBINING_MARK."""

    def test_base_letters_have_single_codepoint_profile(self):
        for a in elements_by_class(ElementClass.BASE_LETTER):
            assert a.unicode_profile is UnicodeProfileType.SINGLE_CODE_POINT, (
                f"{a.element_id} ({a.element_name}) should be SINGLE_CODE_POINT"
            )

    def test_vowel_markers_have_combining_mark_profile(self):
        for a in elements_by_class(ElementClass.VOWEL_MARKER):
            assert a.unicode_profile is UnicodeProfileType.COMBINING_MARK, (
                f"{a.element_id} ({a.element_name}) should be COMBINING_MARK"
            )

    def test_structural_markers_have_combining_mark_profile(self):
        for a in elements_by_class(ElementClass.STRUCTURAL_MARKER):
            assert a.unicode_profile is UnicodeProfileType.COMBINING_MARK, (
                f"{a.element_id} ({a.element_name}) should be COMBINING_MARK"
            )

    def test_hamza_has_contextual_rendering_profile(self):
        a = AEU_REGISTRY["AE_001"]
        assert a.unicode_profile is UnicodeProfileType.CONTEXTUAL_RENDERING
