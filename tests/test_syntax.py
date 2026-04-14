"""Comprehensive tests for arabic_engine.syntax.syntax module."""

from __future__ import annotations

import pytest

from arabic_engine.core.enums import POS, IrabCase, IrabRole
from arabic_engine.core.types import LexicalClosure, SyntaxNode
from arabic_engine.syntax.syntax import _assign_case_and_role, analyse


# ── helpers ─────────────────────────────────────────────────────────


def _make_closure(surface: str, lemma: str, pos: POS) -> LexicalClosure:
    """Build a minimal LexicalClosure for testing."""
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=("ك", "ت", "ب"),
        pattern="فَعَلَ",
        pos=pos,
    )


# ── _assign_case_and_role ───────────────────────────────────────────


class TestAssignCaseAndRole:
    """Unit tests for the heuristic case/role assignment helper."""

    # 1. Verb → SUKUN / FI3L
    def test_verb_assignment(self):
        cl = _make_closure("كَتَبَ", "كتب", POS.FI3L)
        node = _assign_case_and_role(cl, 0, verb_seen=False, subject_seen=False)

        assert node.token == "كَتَبَ"
        assert node.lemma == "كتب"
        assert node.pos == POS.FI3L
        assert node.case == IrabCase.SUKUN
        assert node.role == IrabRole.FI3L

    # 2. Adverb → NASB / ZARF
    def test_adverb_assignment(self):
        cl = _make_closure("أَمْسِ", "أمس", POS.ZARF)
        node = _assign_case_and_role(cl, 1, verb_seen=True, subject_seen=False)

        assert node.case == IrabCase.NASB
        assert node.role == IrabRole.ZARF

    # 3. First ISM after verb → RAF3 / FA3IL
    def test_first_noun_after_verb_is_fa3il(self):
        cl = _make_closure("الطَّالِبُ", "طالب", POS.ISM)
        node = _assign_case_and_role(cl, 1, verb_seen=True, subject_seen=False)

        assert node.case == IrabCase.RAF3
        assert node.role == IrabRole.FA3IL

    # 4. Second ISM after verb → NASB / MAF3UL_BIH
    def test_second_noun_after_verb_is_maf3ul(self):
        cl = _make_closure("الكِتَابَ", "كتاب", POS.ISM)
        node = _assign_case_and_role(cl, 2, verb_seen=True, subject_seen=True)

        assert node.case == IrabCase.NASB
        assert node.role == IrabRole.MAF3UL_BIH

    # 5. ISM with no verb → RAF3 / MUBTADA (nominal sentence)
    def test_nominal_sentence_mubtada(self):
        cl = _make_closure("العِلْمُ", "علم", POS.ISM)
        node = _assign_case_and_role(cl, 0, verb_seen=False, subject_seen=False)

        assert node.case == IrabCase.RAF3
        assert node.role == IrabRole.MUBTADA

    # 6. Fallback — unknown POS → UNKNOWN / UNKNOWN
    def test_fallback_unknown_pos(self):
        cl = _make_closure("وَ", "و", POS.HARF)
        node = _assign_case_and_role(cl, 0, verb_seen=False, subject_seen=False)

        assert node.case == IrabCase.UNKNOWN
        assert node.role == IrabRole.UNKNOWN

    def test_fallback_damir(self):
        cl = _make_closure("هُوَ", "هو", POS.DAMIR)
        node = _assign_case_and_role(cl, 0, verb_seen=False, subject_seen=False)

        assert node.case == IrabCase.UNKNOWN
        assert node.role == IrabRole.UNKNOWN

    # Verify node preserves surface / lemma / pos for every branch
    def test_node_fields_for_zarf(self):
        cl = _make_closure("صَبَاحًا", "صباح", POS.ZARF)
        node = _assign_case_and_role(cl, 0, verb_seen=False, subject_seen=False)

        assert node.token == "صَبَاحًا"
        assert node.lemma == "صباح"
        assert node.pos == POS.ZARF

    # Verb flags should not affect FI3L assignment
    def test_verb_ignores_flags(self):
        cl = _make_closure("ذَهَبَ", "ذهب", POS.FI3L)
        node = _assign_case_and_role(cl, 3, verb_seen=True, subject_seen=True)

        assert node.case == IrabCase.SUKUN
        assert node.role == IrabRole.FI3L


# ── analyse ─────────────────────────────────────────────────────────


class TestAnalyse:
    """Integration tests for the full analyse() pipeline."""

    # 7. Verb-subject-object sentence  (كتب الطالب الدرس)
    def test_verb_subject_object(self):
        closures = [
            _make_closure("كَتَبَ", "كتب", POS.FI3L),
            _make_closure("الطَّالِبُ", "طالب", POS.ISM),
            _make_closure("الدَّرْسَ", "درس", POS.ISM),
        ]
        nodes = analyse(closures)

        assert len(nodes) == 3

        verb, subj, obj = nodes
        assert verb.role == IrabRole.FI3L
        assert verb.case == IrabCase.SUKUN

        assert subj.role == IrabRole.FA3IL
        assert subj.case == IrabCase.RAF3

        assert obj.role == IrabRole.MAF3UL_BIH
        assert obj.case == IrabCase.NASB

    # 8. Nominal sentence  (العلم نور)
    def test_nominal_sentence(self):
        closures = [
            _make_closure("العِلْمُ", "علم", POS.ISM),
            _make_closure("نُورٌ", "نور", POS.ISM),
        ]
        nodes = analyse(closures)

        assert len(nodes) == 2
        assert nodes[0].role == IrabRole.MUBTADA
        assert nodes[0].case == IrabCase.RAF3
        # Second ISM with no verb → still MUBTADA (no verb_seen)
        assert nodes[1].role == IrabRole.MUBTADA
        assert nodes[1].case == IrabCase.RAF3

    # 9. Adverbs depending on verb  (ذهب صباحًا)
    def test_adverb_depends_on_verb(self):
        closures = [
            _make_closure("ذَهَبَ", "ذهب", POS.FI3L),
            _make_closure("صَبَاحًا", "صباح", POS.ZARF),
        ]
        nodes = analyse(closures)

        verb, adv = nodes
        assert adv.role == IrabRole.ZARF
        assert adv.case == IrabCase.NASB
        assert adv.governor == "ذهب"
        assert "صباح" in verb.dependents

    # 10. Empty input
    def test_empty_input(self):
        assert analyse([]) == []

    # 11. Verb-only input
    def test_verb_only(self):
        closures = [_make_closure("جَاءَ", "جاء", POS.FI3L)]
        nodes = analyse(closures)

        assert len(nodes) == 1
        assert nodes[0].role == IrabRole.FI3L
        assert nodes[0].case == IrabCase.SUKUN
        assert nodes[0].governor is None
        assert nodes[0].dependents == []

    # 12. Multiple ISM tokens after verb
    def test_multiple_ism_after_verb(self):
        closures = [
            _make_closure("أَعْطَى", "أعطى", POS.FI3L),
            _make_closure("المُعَلِّمُ", "معلم", POS.ISM),
            _make_closure("الطَّالِبَ", "طالب", POS.ISM),
            _make_closure("الكِتَابَ", "كتاب", POS.ISM),
        ]
        nodes = analyse(closures)

        assert nodes[1].role == IrabRole.FA3IL
        assert nodes[2].role == IrabRole.MAF3UL_BIH
        # Third ISM — subject already seen → still MAF3UL_BIH
        assert nodes[3].role == IrabRole.MAF3UL_BIH
        assert nodes[3].case == IrabCase.NASB

    # 13. Governor / dependent relationships
    def test_governor_dependents(self):
        closures = [
            _make_closure("كَتَبَ", "كتب", POS.FI3L),
            _make_closure("الطَّالِبُ", "طالب", POS.ISM),
            _make_closure("الدَّرْسَ", "درس", POS.ISM),
        ]
        nodes = analyse(closures)

        verb, subj, obj = nodes
        # Verb is the governor of both subject and object
        assert subj.governor == "كتب"
        assert obj.governor == "كتب"
        assert verb.governor is None

        # Verb lists both as dependents
        assert "طالب" in verb.dependents
        assert "درس" in verb.dependents
        assert len(verb.dependents) == 2

    def test_adverb_without_preceding_verb_has_no_governor(self):
        closures = [_make_closure("صَبَاحًا", "صباح", POS.ZARF)]
        nodes = analyse(closures)

        assert len(nodes) == 1
        assert nodes[0].role == IrabRole.ZARF
        assert nodes[0].governor is None

    def test_mixed_verb_zarf_ism(self):
        closures = [
            _make_closure("ذَهَبَ", "ذهب", POS.FI3L),
            _make_closure("أَمْسِ", "أمس", POS.ZARF),
            _make_closure("الوَلَدُ", "ولد", POS.ISM),
        ]
        nodes = analyse(closures)

        verb, adv, subj = nodes
        assert adv.governor == "ذهب"
        assert subj.governor == "ذهب"
        assert subj.role == IrabRole.FA3IL
        assert set(verb.dependents) == {"أمس", "ولد"}

    def test_harf_in_sentence_gets_unknown(self):
        closures = [
            _make_closure("كَتَبَ", "كتب", POS.FI3L),
            _make_closure("فِي", "في", POS.HARF),
        ]
        nodes = analyse(closures)

        assert nodes[1].case == IrabCase.UNKNOWN
        assert nodes[1].role == IrabRole.UNKNOWN
        assert nodes[1].governor is None

    def test_output_order_matches_input(self):
        closures = [
            _make_closure("كَتَبَ", "كتب", POS.FI3L),
            _make_closure("الطَّالِبُ", "طالب", POS.ISM),
        ]
        nodes = analyse(closures)

        assert [n.token for n in nodes] == ["كَتَبَ", "الطَّالِبُ"]
