"""tests/test_reception_constitution.py — Epistemic Reception Constitution v1.

Covers:
* Enum completeness (SubjectGenre, ReceptionRank, ReceptionLayer, CarryingStatus)
* Constitutional matrix structure (4 genres × 6 ranks = 24 cells)
* Carrying status per the governing matrix
* Structural properties (primary entry, closure rank, layers)
* Validation (correct and incorrect claims)
* SemanticType → SubjectGenre mapping
"""

from __future__ import annotations

import pytest

from arabic_engine.cognition.reception_constitution import (
    CONSTITUTIONAL_MATRIX,
    RECEPTION_RANK_DEFINITIONS,
    SUBJECT_GENRE_DEFINITIONS,
    assess_subject,
    build_constitutional_matrix,
    classify_carrying,
    get_closure_rank,
    get_layer,
    get_primary_entry,
    get_reception_ranks_for_layer,
    map_semantic_type_to_genre,
    validate_carrying_claim,
)
from arabic_engine.core.enums import (
    CarryingStatus,
    ReceptionLayer,
    ReceptionRank,
    SemanticType,
    SubjectGenre,
)
from arabic_engine.core.types import (
    CarryingCell,
    ReceptionConstitutionMatrix,
    ReceptionConstitutionRecord,
    ReceptionRankDefinition,
    SubjectGenreDefinition,
)

# ── 5.1 Enum tests ─────────────────────────────────────────────────


class TestSubjectGenreEnum:
    """All 4 SubjectGenre members exist and are distinct."""

    def test_member_count(self) -> None:
        assert len(SubjectGenre) == 4

    @pytest.mark.parametrize("name", ["WUJUD", "SIFA", "HADATH", "NISBA"])
    def test_member_exists(self, name: str) -> None:
        assert hasattr(SubjectGenre, name)

    def test_members_distinct(self) -> None:
        values = [m.value for m in SubjectGenre]
        assert len(values) == len(set(values))


class TestReceptionRankEnum:
    """All 6 ReceptionRank members exist and are distinct."""

    def test_member_count(self) -> None:
        assert len(ReceptionRank) == 6

    @pytest.mark.parametrize(
        "name", ["HISS", "SHUUR", "FIKR", "NIYYA", "KHIYAR", "IRADA"]
    )
    def test_member_exists(self, name: str) -> None:
        assert hasattr(ReceptionRank, name)

    def test_members_distinct(self) -> None:
        values = [m.value for m in ReceptionRank]
        assert len(values) == len(set(values))


class TestReceptionLayerEnum:
    """All 3 ReceptionLayer members exist and are distinct."""

    def test_member_count(self) -> None:
        assert len(ReceptionLayer) == 3

    @pytest.mark.parametrize(
        "name", ["ISTIQBAL", "MUALAJA_MARIFIYYA", "TAWJIH"]
    )
    def test_member_exists(self, name: str) -> None:
        assert hasattr(ReceptionLayer, name)

    def test_members_distinct(self) -> None:
        values = [m.value for m in ReceptionLayer]
        assert len(values) == len(set(values))


class TestCarryingStatusEnum:
    """All 3 CarryingStatus members exist and are distinct."""

    def test_member_count(self) -> None:
        assert len(CarryingStatus) == 3

    @pytest.mark.parametrize("name", ["ASIL", "TABA3I", "MUMTANI3"])
    def test_member_exists(self, name: str) -> None:
        assert hasattr(CarryingStatus, name)

    def test_members_distinct(self) -> None:
        values = [m.value for m in CarryingStatus]
        assert len(values) == len(set(values))


# ── 5.2 Matrix structure tests ─────────────────────────────────────


class TestMatrixStructure:
    """The 4×6 matrix has exactly 24 cells with correct coverage."""

    def test_constant_has_24_cells(self) -> None:
        assert len(CONSTITUTIONAL_MATRIX) == 24

    def test_build_returns_24_cells(self) -> None:
        m = build_constitutional_matrix()
        assert isinstance(m, ReceptionConstitutionMatrix)
        assert len(m.cells) == 24
        assert m.version == "v1"

    def test_each_genre_has_6_cells(self) -> None:
        for genre in SubjectGenre:
            cells = [c for c in CONSTITUTIONAL_MATRIX if c.genre == genre]
            assert len(cells) == 6, f"{genre.name} has {len(cells)} cells"

    def test_each_rank_has_4_cells(self) -> None:
        for rank in ReceptionRank:
            cells = [c for c in CONSTITUTIONAL_MATRIX if c.rank == rank]
            assert len(cells) == 4, f"{rank.name} has {len(cells)} cells"

    def test_no_duplicate_cells(self) -> None:
        keys = [(c.genre, c.rank) for c in CONSTITUTIONAL_MATRIX]
        assert len(keys) == len(set(keys))

    def test_all_cells_are_carrying_cell_instances(self) -> None:
        for cell in CONSTITUTIONAL_MATRIX:
            assert isinstance(cell, CarryingCell)


# ── 5.3 Carrying status tests (per the governing matrix) ──────────


class TestWujudCarrying:
    """الوجود — existence carrying statuses."""

    def test_hiss_asil(self) -> None:
        c = classify_carrying(SubjectGenre.WUJUD, ReceptionRank.HISS)
        assert c.status == CarryingStatus.ASIL

    def test_shuur_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.WUJUD, ReceptionRank.SHUUR)
        assert c.status == CarryingStatus.TABA3I

    def test_fikr_asil(self) -> None:
        c = classify_carrying(SubjectGenre.WUJUD, ReceptionRank.FIKR)
        assert c.status == CarryingStatus.ASIL

    def test_niyya_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.WUJUD, ReceptionRank.NIYYA)
        assert c.status == CarryingStatus.TABA3I

    def test_khiyar_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.WUJUD, ReceptionRank.KHIYAR)
        assert c.status == CarryingStatus.TABA3I

    def test_irada_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.WUJUD, ReceptionRank.IRADA)
        assert c.status == CarryingStatus.TABA3I


class TestSifaCarrying:
    """الصفة — attribute carrying statuses."""

    def test_hiss_asil(self) -> None:
        c = classify_carrying(SubjectGenre.SIFA, ReceptionRank.HISS)
        assert c.status == CarryingStatus.ASIL
        assert "المحسوس" in c.qualification

    def test_shuur_asil(self) -> None:
        c = classify_carrying(SubjectGenre.SIFA, ReceptionRank.SHUUR)
        assert c.status == CarryingStatus.ASIL

    def test_fikr_asil(self) -> None:
        c = classify_carrying(SubjectGenre.SIFA, ReceptionRank.FIKR)
        assert c.status == CarryingStatus.ASIL

    def test_niyya_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.SIFA, ReceptionRank.NIYYA)
        assert c.status == CarryingStatus.TABA3I

    def test_khiyar_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.SIFA, ReceptionRank.KHIYAR)
        assert c.status == CarryingStatus.TABA3I

    def test_irada_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.SIFA, ReceptionRank.IRADA)
        assert c.status == CarryingStatus.TABA3I


class TestHadathCarrying:
    """الحدث — event carrying statuses."""

    def test_hiss_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.HADATH, ReceptionRank.HISS)
        assert c.status == CarryingStatus.TABA3I

    def test_shuur_asil(self) -> None:
        c = classify_carrying(SubjectGenre.HADATH, ReceptionRank.SHUUR)
        assert c.status == CarryingStatus.ASIL

    def test_fikr_asil(self) -> None:
        c = classify_carrying(SubjectGenre.HADATH, ReceptionRank.FIKR)
        assert c.status == CarryingStatus.ASIL

    def test_niyya_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.HADATH, ReceptionRank.NIYYA)
        assert c.status == CarryingStatus.TABA3I

    def test_khiyar_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.HADATH, ReceptionRank.KHIYAR)
        assert c.status == CarryingStatus.TABA3I

    def test_irada_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.HADATH, ReceptionRank.IRADA)
        assert c.status == CarryingStatus.TABA3I


class TestNisbaCarrying:
    """النسبة — relation carrying statuses."""

    def test_hiss_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.NISBA, ReceptionRank.HISS)
        assert c.status == CarryingStatus.TABA3I
        assert "ممتنع" in c.qualification  # pure abstract → impossible

    def test_shuur_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.NISBA, ReceptionRank.SHUUR)
        assert c.status == CarryingStatus.TABA3I

    def test_fikr_asil(self) -> None:
        c = classify_carrying(SubjectGenre.NISBA, ReceptionRank.FIKR)
        assert c.status == CarryingStatus.ASIL

    def test_niyya_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.NISBA, ReceptionRank.NIYYA)
        assert c.status == CarryingStatus.TABA3I

    def test_khiyar_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.NISBA, ReceptionRank.KHIYAR)
        assert c.status == CarryingStatus.TABA3I

    def test_irada_taba3i(self) -> None:
        c = classify_carrying(SubjectGenre.NISBA, ReceptionRank.IRADA)
        assert c.status == CarryingStatus.TABA3I


class TestDirectionRanksTaba3i:
    """All genres in NIYYA / KHIYAR / IRADA are تبعي."""

    @pytest.mark.parametrize("genre", list(SubjectGenre))
    @pytest.mark.parametrize(
        "rank",
        [ReceptionRank.NIYYA, ReceptionRank.KHIYAR, ReceptionRank.IRADA],
    )
    def test_always_taba3i(
        self, genre: SubjectGenre, rank: ReceptionRank
    ) -> None:
        c = classify_carrying(genre, rank)
        assert c.status == CarryingStatus.TABA3I


# ── 5.4 Structural property tests ─────────────────────────────────


class TestStructuralProperties:
    """Primary entry, closure rank, and layer assignments."""

    def test_primary_entry_wujud(self) -> None:
        assert get_primary_entry(SubjectGenre.WUJUD) == ReceptionRank.HISS

    def test_primary_entry_sifa(self) -> None:
        assert get_primary_entry(SubjectGenre.SIFA) == ReceptionRank.HISS

    def test_primary_entry_hadath(self) -> None:
        assert get_primary_entry(SubjectGenre.HADATH) == ReceptionRank.SHUUR

    def test_primary_entry_nisba(self) -> None:
        assert get_primary_entry(SubjectGenre.NISBA) == ReceptionRank.FIKR

    @pytest.mark.parametrize("genre", list(SubjectGenre))
    def test_closure_rank_always_fikr(self, genre: SubjectGenre) -> None:
        assert get_closure_rank(genre) == ReceptionRank.FIKR

    def test_layer_hiss(self) -> None:
        assert get_layer(ReceptionRank.HISS) == ReceptionLayer.ISTIQBAL

    def test_layer_shuur(self) -> None:
        assert get_layer(ReceptionRank.SHUUR) == ReceptionLayer.ISTIQBAL

    def test_layer_fikr(self) -> None:
        assert get_layer(ReceptionRank.FIKR) == ReceptionLayer.MUALAJA_MARIFIYYA

    def test_layer_niyya(self) -> None:
        assert get_layer(ReceptionRank.NIYYA) == ReceptionLayer.TAWJIH

    def test_layer_khiyar(self) -> None:
        assert get_layer(ReceptionRank.KHIYAR) == ReceptionLayer.TAWJIH

    def test_layer_irada(self) -> None:
        assert get_layer(ReceptionRank.IRADA) == ReceptionLayer.TAWJIH

    def test_ranks_for_istiqbal(self) -> None:
        ranks = get_reception_ranks_for_layer(ReceptionLayer.ISTIQBAL)
        assert ranks == (ReceptionRank.HISS, ReceptionRank.SHUUR)

    def test_ranks_for_mualaja(self) -> None:
        ranks = get_reception_ranks_for_layer(ReceptionLayer.MUALAJA_MARIFIYYA)
        assert ranks == (ReceptionRank.FIKR,)

    def test_ranks_for_tawjih(self) -> None:
        ranks = get_reception_ranks_for_layer(ReceptionLayer.TAWJIH)
        assert ranks == (
            ReceptionRank.NIYYA,
            ReceptionRank.KHIYAR,
            ReceptionRank.IRADA,
        )


# ── 5.5 Validation tests ──────────────────────────────────────────


class TestValidateCarryingClaim:
    """Correct claims pass, incorrect claims fail with rationale."""

    def test_correct_claim_passes(self) -> None:
        ok, rationale = validate_carrying_claim(
            SubjectGenre.WUJUD, ReceptionRank.HISS, CarryingStatus.ASIL
        )
        assert ok is True
        assert len(rationale) > 0

    def test_incorrect_claim_fails(self) -> None:
        ok, rationale = validate_carrying_claim(
            SubjectGenre.WUJUD, ReceptionRank.HISS, CarryingStatus.MUMTANI3
        )
        assert ok is False
        assert "ASIL" in rationale
        assert "MUMTANI3" in rationale

    def test_taba3i_correct(self) -> None:
        ok, _ = validate_carrying_claim(
            SubjectGenre.WUJUD, ReceptionRank.SHUUR, CarryingStatus.TABA3I
        )
        assert ok is True

    def test_taba3i_wrong(self) -> None:
        ok, rationale = validate_carrying_claim(
            SubjectGenre.WUJUD, ReceptionRank.SHUUR, CarryingStatus.ASIL
        )
        assert ok is False
        assert "TABA3I" in rationale


# ── 5.6 Integration tests ─────────────────────────────────────────


class TestAssessSubject:
    """assess_subject builds a full record."""

    @pytest.mark.parametrize("genre", list(SubjectGenre))
    def test_assess_returns_record(self, genre: SubjectGenre) -> None:
        record = assess_subject(genre)
        assert isinstance(record, ReceptionConstitutionRecord)
        assert record.subject_genre == genre
        assert len(record.carrying_cells) == 6
        assert record.epistemic_closure_rank == ReceptionRank.FIKR

    def test_assess_wujud_primary_entry(self) -> None:
        record = assess_subject(SubjectGenre.WUJUD)
        assert record.primary_entry_rank == ReceptionRank.HISS


class TestSemanticTypeMapping:
    """map_semantic_type_to_genre covers all known types."""

    def test_entity_to_wujud(self) -> None:
        assert map_semantic_type_to_genre(SemanticType.ENTITY) == SubjectGenre.WUJUD

    def test_attribute_to_sifa(self) -> None:
        assert map_semantic_type_to_genre(SemanticType.ATTRIBUTE) == SubjectGenre.SIFA

    def test_event_to_hadath(self) -> None:
        assert map_semantic_type_to_genre(SemanticType.EVENT) == SubjectGenre.HADATH

    def test_nominalized_event_to_hadath(self) -> None:
        assert (
            map_semantic_type_to_genre(SemanticType.NOMINALIZED_EVENT)
            == SubjectGenre.HADATH
        )

    def test_event_concept_to_hadath(self) -> None:
        assert (
            map_semantic_type_to_genre(SemanticType.EVENT_CONCEPT)
            == SubjectGenre.HADATH
        )

    def test_relation_to_nisba(self) -> None:
        assert map_semantic_type_to_genre(SemanticType.RELATION) == SubjectGenre.NISBA

    def test_norm_returns_none(self) -> None:
        assert map_semantic_type_to_genre(SemanticType.NORM) is None


class TestDefinitionConstants:
    """Subject genre and reception rank definition constants."""

    def test_subject_genre_definitions_count(self) -> None:
        assert len(SUBJECT_GENRE_DEFINITIONS) == 4

    def test_reception_rank_definitions_count(self) -> None:
        assert len(RECEPTION_RANK_DEFINITIONS) == 6

    def test_all_genres_have_definition(self) -> None:
        genres = {d.genre for d in SUBJECT_GENRE_DEFINITIONS}
        assert genres == set(SubjectGenre)

    def test_all_ranks_have_definition(self) -> None:
        ranks = {d.rank for d in RECEPTION_RANK_DEFINITIONS}
        assert ranks == set(ReceptionRank)

    def test_definitions_are_frozen(self) -> None:
        for d in SUBJECT_GENRE_DEFINITIONS:
            assert isinstance(d, SubjectGenreDefinition)
        for d in RECEPTION_RANK_DEFINITIONS:
            assert isinstance(d, ReceptionRankDefinition)
