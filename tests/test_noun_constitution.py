"""Tests for noun constitution (classify_noun & validate_noun_completeness).

Covers all 12 facets with representative Arabic examples.
"""

from __future__ import annotations

from arabic_engine.core.enums import (
    POS,
    CompoundType,
    Definiteness,
    DerivationStatus,
    Gender,
    GenderBasis,
    NounKind,
    NounNumber,
    ProperNounType,
    SemanticType,
    UniversalParticular,
)
from arabic_engine.core.types import Concept, LexicalClosure, NounNode
from arabic_engine.noun.constitution import classify_noun, validate_noun_completeness


def _closure(
    surface: str,
    lemma: str,
    root: tuple = (),
    pattern: str = "",
    **kw,
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface, lemma=lemma, root=root, pattern=pattern,
        pos=POS.ISM, **kw,
    )


def _concept(label: str, **props) -> Concept:
    return Concept(
        concept_id=0, label=label, semantic_type=SemanticType.ENTITY,
        properties=props,
    )


# ── Entity nouns ────────────────────────────────────────────────────


class TestEntityNouns:
    def test_basic_entity(self):
        cl = _closure("حَجَر", "حجر", ("ح", "ج", "ر"), "فَعَل")
        node = classify_noun(cl)
        assert node.noun_kind in (NounKind.ENTITY, NounKind.INDIVIDUAL)
        assert node.gender == Gender.MASCULINE
        # حجر is in the genus-noun list so number is GENUS_NOUN
        assert node.number in (NounNumber.SINGULAR, NounNumber.GENUS_NOUN)

    def test_tree_feminine(self):
        cl = _closure("شجرة", "شجرة", ("ش", "ج", "ر"), "فَعْلَة")
        node = classify_noun(cl)
        assert node.gender == Gender.FEMININE
        assert node.number == NounNumber.SINGULAR

    def test_city(self):
        cl = _closure("مدينة", "مدينة", ("م", "د", "ن"), "فعيلة")
        co = _concept("مدينة")
        node = classify_noun(cl, co)
        assert node.gender == Gender.FEMININE


# ── Proper nouns ────────────────────────────────────────────────────


class TestProperNouns:
    def test_personal_proper(self):
        cl = _closure("زَيْدٌ", "زَيْد", ("ز", "ي", "د"), "فَعْل")
        co = _concept("زَيْد", proper_noun=True)
        node = classify_noun(cl, co)
        assert node.proper_type == ProperNounType.PERSONAL
        assert node.universality == UniversalParticular.PARTICULAR
        assert node.definiteness == Definiteness.DEFINITE_PROPER

    def test_place_proper(self):
        cl = _closure("دمشق", "دمشق", ("د", "م", "ش", "ق"), "")
        node = classify_noun(cl)
        assert node.proper_type == ProperNounType.PLACE

    def test_time_proper(self):
        cl = _closure("رمضان", "رمضان", ("ر", "م", "ض"), "")
        node = classify_noun(cl)
        assert node.proper_type == ProperNounType.TIME


# ── Attribute nouns ─────────────────────────────────────────────────


class TestAttributeNouns:
    def test_active_participle(self):
        cl = _closure("كاتب", "كاتب", ("ك", "ت", "ب"), "فاعل")
        node = classify_noun(cl)
        assert node.derivation == DerivationStatus.DERIVED

    def test_superlative(self):
        cl = _closure("أكبر", "أكبر", ("ك", "ب", "ر"), "أفعل")
        node = classify_noun(cl)
        assert node.derivation == DerivationStatus.DERIVED

    def test_known_adjective(self):
        cl = _closure("طويل", "طويل", ("ط", "و", "ل"), "فعيل")
        node = classify_noun(cl)
        assert node.derivation == DerivationStatus.DERIVED


# ── Number ──────────────────────────────────────────────────────────


class TestNumber:
    def test_singular(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = classify_noun(cl)
        assert node.number == NounNumber.SINGULAR

    def test_dual(self):
        cl = _closure("كتابان", "كتابان", ("ك", "ت", "ب"), "")
        node = classify_noun(cl)
        assert node.number == NounNumber.DUAL

    def test_sound_masc_plural(self):
        cl = _closure("معلمون", "معلم", ("ع", "ل", "م"), "مُفَعِّل")
        node = classify_noun(cl)
        assert node.number == NounNumber.SOUND_MASC_PLURAL

    def test_sound_fem_plural(self):
        cl = _closure("معلمات", "معلمة", ("ع", "ل", "م"), "")
        node = classify_noun(cl)
        assert node.number == NounNumber.SOUND_FEM_PLURAL

    def test_broken_plural(self):
        cl = _closure("كُتُب", "كُتُب", ("ك", "ت", "ب"), "فُعُل")
        node = classify_noun(cl)
        assert node.number == NounNumber.BROKEN_PLURAL

    def test_numeral(self):
        cl = _closure("ثلاثة", "ثلاثة", ("ث", "ل", "ث"), "")
        node = classify_noun(cl)
        assert node.number == NounNumber.NUMERAL


# ── Definiteness ────────────────────────────────────────────────────


class TestDefiniteness:
    def test_article(self):
        cl = _closure("الكتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = classify_noun(cl)
        assert node.definiteness == Definiteness.DEFINITE_ARTICLE

    def test_indefinite(self):
        cl = _closure("كتابٌ", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = classify_noun(cl)
        assert node.definiteness == Definiteness.INDEFINITE

    def test_proper_definiteness(self):
        cl = _closure("محمد", "محمد", ("ح", "م", "د"), "")
        node = classify_noun(cl)
        assert node.definiteness == Definiteness.DEFINITE_PROPER


# ── Gender ──────────────────────────────────────────────────────────


class TestGender:
    def test_masculine(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = classify_noun(cl)
        assert node.gender == Gender.MASCULINE

    def test_feminine_taa_marbuta(self):
        cl = _closure("مدرسة", "مدرسة", ("د", "ر", "س"), "مَفْعَلَة")
        node = classify_noun(cl)
        assert node.gender == Gender.FEMININE

    def test_feminine_semantic(self):
        cl = _closure("شمس", "شمس", ("ش", "م", "س"), "فَعْل")
        node = classify_noun(cl)
        assert node.gender == Gender.FEMININE
        assert node.gender_basis == GenderBasis.SEMANTIC


# ── Compound nouns ──────────────────────────────────────────────────


class TestCompound:
    def test_blend_compound(self):
        cl = _closure("بعلبك", "بعلبك", (), "")
        node = classify_noun(cl)
        assert node.compound_type == CompoundType.BLEND

    def test_annexation_compound(self):
        t1 = _closure("عبد", "عبد", ("ع", "ب", "د"), "فَعْل")
        t2 = _closure("الله", "الله", (), "")
        tokens = [t1, t2]
        node = classify_noun(t1, all_tokens=tokens, token_index=0)
        assert node.compound_type == CompoundType.ANNEXATION


# ── Borrowed nouns ──────────────────────────────────────────────────


class TestBorrowed:
    def test_borrowed_noun(self):
        cl = _closure("كمبيوتر", "كمبيوتر", (), "")
        node = classify_noun(cl)
        assert node.is_borrowed is True
        assert node.source_language == "English"
        assert node.noun_kind == NounKind.BORROWED

    def test_arabic_noun_not_borrowed(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = classify_noun(cl)
        assert node.is_borrowed is False


# ── Universality ────────────────────────────────────────────────────


class TestUniversality:
    def test_universal_definite_article(self):
        cl = _closure("الإنسان", "إنسان", ("ا", "ن", "س"), "")
        co = _concept("إنسان")
        node = classify_noun(cl, co)
        assert node.universality == UniversalParticular.UNIVERSAL

    def test_particular_proper(self):
        cl = _closure("زيد", "زَيْد", ("ز", "ي", "د"), "فَعْل")
        co = _concept("زَيْد", proper_noun=True)
        node = classify_noun(cl, co)
        assert node.universality == UniversalParticular.PARTICULAR


# ── Completeness validation ─────────────────────────────────────────


class TestValidateCompleteness:
    def test_complete_noun(self):
        cl = _closure("كتاب", "كتاب", ("ك", "ت", "ب"), "فِعال")
        node = classify_noun(cl)
        assert validate_noun_completeness(node) is True

    def test_incomplete_no_surface(self):
        node = NounNode(
            surface="", lemma="test", root=("ت",), pattern="",
            noun_kind=NounKind.ENTITY,
            universality=UniversalParticular.PARTICULAR,
            gender=Gender.MASCULINE, gender_basis=GenderBasis.LEXICAL,
            number=NounNumber.SINGULAR, definiteness=Definiteness.INDEFINITE,
            derivation=DerivationStatus.RIGID,
        )
        assert validate_noun_completeness(node) is False

    def test_incomplete_no_lemma(self):
        node = NounNode(
            surface="test", lemma="", root=("ت",), pattern="",
            noun_kind=NounKind.ENTITY,
            universality=UniversalParticular.PARTICULAR,
            gender=Gender.MASCULINE, gender_basis=GenderBasis.LEXICAL,
            number=NounNumber.SINGULAR, definiteness=Definiteness.INDEFINITE,
            derivation=DerivationStatus.RIGID,
        )
        assert validate_noun_completeness(node) is False

    def test_borrowed_without_root_is_valid(self):
        node = NounNode(
            surface="كمبيوتر", lemma="كمبيوتر", root=(), pattern="",
            noun_kind=NounKind.BORROWED,
            universality=UniversalParticular.PARTICULAR,
            gender=Gender.MASCULINE, gender_basis=GenderBasis.LEXICAL,
            number=NounNumber.SINGULAR, definiteness=Definiteness.INDEFINITE,
            derivation=DerivationStatus.RIGID,
            is_borrowed=True, source_language="English",
        )
        assert validate_noun_completeness(node) is True


# ── Pipeline integration ────────────────────────────────────────────


class TestPipelineIntegration:
    def test_pipeline_attaches_noun_nodes(self):
        from arabic_engine.pipeline import run
        result = run("كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ")
        noun_closures = [c for c in result.closures if c.noun_node is not None]
        assert len(noun_closures) >= 2  # زَيْد and رِسَالَة

    def test_pipeline_noun_has_correct_kind(self):
        from arabic_engine.pipeline import run
        result = run("كَتَبَ زَيْدٌ الرِّسَالَةَ أَمْسَ")
        for cl in result.closures:
            if cl.noun_node is not None:
                assert cl.noun_node.noun_kind is not None
                assert cl.noun_node.gender is not None
                assert cl.noun_node.number is not None
                assert cl.noun_node.definiteness is not None
