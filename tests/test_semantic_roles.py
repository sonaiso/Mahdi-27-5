"""Tests for arabic_engine/linkage/semantic_roles.py."""

from __future__ import annotations

from arabic_engine.core.enums import POS, IrabCase, IrabRole, SpaceRef, TimeRef
from arabic_engine.core.types import LexicalClosure, SyntaxNode
from arabic_engine.linkage.semantic_roles import derive_semantic_roles


def _closure(
    surface: str = "كتب",
    lemma: str = "كتب",
    pos: POS = POS.FI3L,
    temporal: TimeRef = TimeRef.UNSPECIFIED,
    spatial: SpaceRef = SpaceRef.UNSPECIFIED,
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=("ك", "ت", "ب"),
        pattern="فَعَلَ",
        pos=pos,
        temporal=temporal,
        spatial=spatial,
    )


def _syntax(
    token: str = "كتب",
    lemma: str = "كتب",
    role: IrabRole = IrabRole.FI3L,
    case: IrabCase = IrabCase.UNKNOWN,
    pos: POS = POS.FI3L,
) -> SyntaxNode:
    return SyntaxNode(
        token=token,
        lemma=lemma,
        pos=pos,
        case=case,
        role=role,
    )


def test_returns_dict_with_five_keys():
    result = derive_semantic_roles([], [])
    assert set(result.keys()) == {"event", "agent", "patient", "time", "place"}


def test_verb_maps_to_event():
    cl = _closure(surface="كتب", lemma="كتب", pos=POS.FI3L)
    sn = _syntax(token="كتب", lemma="كتب", role=IrabRole.FI3L)
    result = derive_semantic_roles([cl], [sn])
    assert result["event"] == "كتب"


def test_noun_subject_maps_to_agent():
    cl = _closure(surface="الطالب", lemma="طالب", pos=POS.ISM)
    sn = _syntax(token="الطالب", lemma="طالب", role=IrabRole.FA3IL, pos=POS.ISM)
    result = derive_semantic_roles([cl], [sn])
    assert result["agent"] == "طالب"


def test_noun_object_maps_to_patient():
    cl = _closure(surface="الكتاب", lemma="كتاب", pos=POS.ISM)
    sn = _syntax(token="الكتاب", lemma="كتاب", role=IrabRole.MAF3UL_BIH, pos=POS.ISM)
    result = derive_semantic_roles([cl], [sn])
    assert result["patient"] == "كتاب"


def test_zarf_temporal_maps_to_time():
    cl = _closure(surface="أمس", lemma="أمس", pos=POS.ZARF, temporal=TimeRef.PAST)
    sn = _syntax(token="أمس", lemma="أمس", role=IrabRole.ZARF, pos=POS.ZARF)
    result = derive_semantic_roles([cl], [sn])
    assert result["time"] == "أمس"


def test_zarf_spatial_maps_to_place():
    cl = _closure(surface="هنا", lemma="هنا", pos=POS.ZARF, spatial=SpaceRef.HERE)
    sn = _syntax(token="هنا", lemma="هنا", role=IrabRole.ZARF, pos=POS.ZARF)
    result = derive_semantic_roles([cl], [sn])
    assert result["place"] == "هنا"


def test_empty_input():
    result = derive_semantic_roles([], [])
    assert all(v == "" for v in result.values())


def test_first_verb_wins():
    cl1 = _closure(surface="كتب", lemma="كتب")
    cl2 = _closure(surface="قرأ", lemma="قرأ")
    sn1 = _syntax(token="كتب", lemma="كتب", role=IrabRole.FI3L)
    sn2 = _syntax(token="قرأ", lemma="قرأ", role=IrabRole.FI3L)
    result = derive_semantic_roles([cl1, cl2], [sn1, sn2])
    assert result["event"] == "كتب"


def test_first_agent_wins():
    cl1 = _closure(surface="الطالب", lemma="طالب", pos=POS.ISM)
    cl2 = _closure(surface="المعلم", lemma="معلم", pos=POS.ISM)
    sn1 = _syntax(token="الطالب", lemma="طالب", role=IrabRole.FA3IL, pos=POS.ISM)
    sn2 = _syntax(token="المعلم", lemma="معلم", role=IrabRole.FA3IL, pos=POS.ISM)
    result = derive_semantic_roles([cl1, cl2], [sn1, sn2])
    assert result["agent"] == "طالب"


def test_no_verb_event_empty():
    cl = _closure(surface="الكتاب", lemma="كتاب", pos=POS.ISM)
    sn = _syntax(token="الكتاب", lemma="كتاب", role=IrabRole.FA3IL, pos=POS.ISM)
    result = derive_semantic_roles([cl], [sn])
    assert result["event"] == ""


def test_mixed_sentence():
    cl_verb = _closure(surface="كتب", lemma="كتب", pos=POS.FI3L)
    cl_subj = _closure(surface="الطالب", lemma="طالب", pos=POS.ISM)
    cl_obj = _closure(surface="الدرس", lemma="درس", pos=POS.ISM)
    sn_verb = _syntax(token="كتب", lemma="كتب", role=IrabRole.FI3L)
    sn_subj = _syntax(token="الطالب", lemma="طالب", role=IrabRole.FA3IL, pos=POS.ISM)
    sn_obj = _syntax(token="الدرس", lemma="درس", role=IrabRole.MAF3UL_BIH, pos=POS.ISM)
    result = derive_semantic_roles(
        [cl_verb, cl_subj, cl_obj],
        [sn_verb, sn_subj, sn_obj],
    )
    assert result["event"] == "كتب"
    assert result["agent"] == "طالب"
    assert result["patient"] == "درس"
