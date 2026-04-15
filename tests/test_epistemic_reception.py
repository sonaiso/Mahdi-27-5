"""tests/test_epistemic_reception.py — comprehensive tests for epistemic_reception.

Covers:
* Subject classification into four genres (Arts. 5–10)
* Reception rank → layer mapping (Art. 14)
* Full 4×6 constitutional matrix (Art. 40)
* Carrying-mode validation (Arts. 36–38)
* Full reception validation (Arts. 10–46)
* Sense articles (Arts. 16–20)
* Feeling articles (Arts. 21–25)
* Thought articles (Arts. 26–30)
* Direction ranks (Arts. 31–35)
* Batch validation
"""

from __future__ import annotations

import pytest

from arabic_engine.cognition.epistemic_reception import (
    CONSTITUTIONAL_MATRIX,
    build_reception_path,
    classify_subject,
    get_reception_layer,
    lookup_carrying_mode,
    validate_carrying_claim,
    validate_reception,
    validate_reception_batch,
)
from arabic_engine.core.enums import (
    CarryingMode,
    ReceptionDecisionCode,
    ReceptionLayer,
    ReceptionRank,
    ReceptionValidationOutcome,
    SubjectGenre,
)
from arabic_engine.core.types import (
    CarryingAssignment,
    EpistemicReceptionInput,
    SubjectClassification,
)

# ── Helpers ─────────────────────────────────────────────────────────────────


def _subject(
    genre: SubjectGenre = SubjectGenre.WUJUD,
    *,
    is_closed: bool = True,
    cid: str = "SC_TEST",
) -> SubjectClassification:
    return SubjectClassification(
        classification_id=cid,
        genre=genre,
        description="test subject",
        is_closed=is_closed,
    )


def _full_input(
    *,
    subject: SubjectClassification | None = None,
    sense: bool = True,
    feeling: bool = True,
    thought: bool = True,
    intention: bool = True,
    choice: bool = True,
    will: bool = True,
    claimed: tuple[CarryingAssignment, ...] = (),
    rid: str = "REC_TEST",
) -> EpistemicReceptionInput:
    if subject is None:
        subject = _subject()
    return EpistemicReceptionInput(
        reception_id=rid,
        subject=subject,
        sense_present=sense,
        feeling_present=feeling,
        thought_present=thought,
        intention_present=intention,
        choice_present=choice,
        will_present=will,
        claimed_assignments=claimed,
    )


# ═════════════════════════════════════════════════════════════════════════════
# 5.1 — TestSubjectClassification
# ═════════════════════════════════════════════════════════════════════════════


class TestSubjectClassification:
    """Test subject classification into the four genres (Arts. 5–10)."""

    def test_classify_existence_by_hint(self) -> None:
        sc = classify_subject("something", hints=["existence"])
        assert sc.genre == SubjectGenre.WUJUD
        assert sc.is_closed is True

    def test_classify_attribute_by_hint(self) -> None:
        sc = classify_subject("something", hints=["attribute"])
        assert sc.genre == SubjectGenre.SIFA
        assert sc.is_closed is True

    def test_classify_event_by_hint(self) -> None:
        sc = classify_subject("something", hints=["event"])
        assert sc.genre == SubjectGenre.HADATH
        assert sc.is_closed is True

    def test_classify_relation_by_hint(self) -> None:
        sc = classify_subject("something", hints=["relation"])
        assert sc.genre == SubjectGenre.NISBA
        assert sc.is_closed is True

    def test_classify_by_arabic_hint(self) -> None:
        sc = classify_subject("something", hints=["وجود"])
        assert sc.genre == SubjectGenre.WUJUD

    def test_classify_by_description_keyword(self) -> None:
        sc = classify_subject("an entity appeared")
        assert sc.genre == SubjectGenre.WUJUD
        assert sc.is_closed is True

    def test_unclosed_material(self) -> None:
        """Art. 10: If no genre is resolved, is_closed is False."""
        sc = classify_subject("xyzzy unknown stuff")
        assert sc.is_closed is False

    def test_exhaustiveness_proof(self) -> None:
        """Art. 10: Every recognisable subject fits one of the four genres."""
        assert len(SubjectGenre) == 4
        for genre in SubjectGenre:
            assert genre in (
                SubjectGenre.WUJUD,
                SubjectGenre.SIFA,
                SubjectGenre.HADATH,
                SubjectGenre.NISBA,
            )

    def test_classification_id_custom(self) -> None:
        sc = classify_subject("entity", hints=["existence"], classification_id="MY_ID")
        assert sc.classification_id == "MY_ID"


# ═════════════════════════════════════════════════════════════════════════════
# 5.2 — TestReceptionLayers
# ═════════════════════════════════════════════════════════════════════════════


class TestReceptionLayers:
    """Test rank-to-layer mapping (Art. 14)."""

    @pytest.mark.parametrize(
        ("rank", "expected_layer"),
        [
            (ReceptionRank.HISS, ReceptionLayer.ISTIQBAL),
            (ReceptionRank.SHUUUR, ReceptionLayer.ISTIQBAL),
            (ReceptionRank.FIKR, ReceptionLayer.MUALAJA_MARIFIYYA),
            (ReceptionRank.NIYYA, ReceptionLayer.TAWJIH),
            (ReceptionRank.KHIYAR, ReceptionLayer.TAWJIH),
            (ReceptionRank.IRADA, ReceptionLayer.TAWJIH),
        ],
    )
    def test_rank_to_layer(
        self, rank: ReceptionRank, expected_layer: ReceptionLayer
    ) -> None:
        assert get_reception_layer(rank) == expected_layer

    def test_all_six_ranks_mapped(self) -> None:
        assert len(ReceptionRank) == 6
        for rank in ReceptionRank:
            layer = get_reception_layer(rank)
            assert isinstance(layer, ReceptionLayer)


# ═════════════════════════════════════════════════════════════════════════════
# 5.3 — TestConstitutionalMatrix
# ═════════════════════════════════════════════════════════════════════════════


class TestConstitutionalMatrix:
    """Test all 24 cells of the 4×6 carrying matrix (Art. 40)."""

    def test_matrix_has_24_cells(self) -> None:
        assert len(CONSTITUTIONAL_MATRIX) == 24

    # ── Existence row (Art. 41) ──

    def test_existence_sense_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.WUJUD, ReceptionRank.HISS)
        assert a.mode == CarryingMode.ASIL

    def test_existence_feeling_tabi(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.WUJUD, ReceptionRank.SHUUUR)
        assert a.mode == CarryingMode.TABI

    def test_existence_thought_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.WUJUD, ReceptionRank.FIKR)
        assert a.mode == CarryingMode.ASIL

    @pytest.mark.parametrize(
        "rank",
        [ReceptionRank.NIYYA, ReceptionRank.KHIYAR, ReceptionRank.IRADA],
    )
    def test_existence_direction_tabi(self, rank: ReceptionRank) -> None:
        a = lookup_carrying_mode(SubjectGenre.WUJUD, rank)
        assert a.mode == CarryingMode.TABI

    # ── Attribute row (Art. 42) ──

    def test_attribute_sense_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.SIFA, ReceptionRank.HISS)
        assert a.mode == CarryingMode.ASIL
        assert "محسوس" in a.qualification

    def test_attribute_feeling_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.SIFA, ReceptionRank.SHUUUR)
        assert a.mode == CarryingMode.ASIL

    def test_attribute_thought_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.SIFA, ReceptionRank.FIKR)
        assert a.mode == CarryingMode.ASIL

    # ── Event row (Art. 43) ──

    def test_event_sense_tabi(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.HADATH, ReceptionRank.HISS)
        assert a.mode == CarryingMode.TABI

    def test_event_feeling_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.HADATH, ReceptionRank.SHUUUR)
        assert a.mode == CarryingMode.ASIL

    def test_event_thought_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.HADATH, ReceptionRank.FIKR)
        assert a.mode == CarryingMode.ASIL

    # ── Relation row (Art. 44) ──

    def test_relation_sense_tabi(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.NISBA, ReceptionRank.HISS)
        assert a.mode == CarryingMode.TABI

    def test_relation_feeling_tabi(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.NISBA, ReceptionRank.SHUUUR)
        assert a.mode == CarryingMode.TABI

    def test_relation_thought_asil(self) -> None:
        a = lookup_carrying_mode(SubjectGenre.NISBA, ReceptionRank.FIKR)
        assert a.mode == CarryingMode.ASIL

    def test_qualification_strings_present(self) -> None:
        """Key cells should have non-empty qualification strings."""
        a = lookup_carrying_mode(SubjectGenre.WUJUD, ReceptionRank.HISS)
        assert a.qualification != ""

    def test_thought_always_asil(self) -> None:
        """Art. 29: Thought carries all four genres originally."""
        for genre in SubjectGenre:
            a = lookup_carrying_mode(genre, ReceptionRank.FIKR)
            assert a.mode == CarryingMode.ASIL

    def test_direction_ranks_always_tabi(self) -> None:
        """Arts. 31–35: Direction ranks never carry originally."""
        for genre in SubjectGenre:
            for rank in (ReceptionRank.NIYYA, ReceptionRank.KHIYAR, ReceptionRank.IRADA):
                a = lookup_carrying_mode(genre, rank)
                assert a.mode == CarryingMode.TABI


# ═════════════════════════════════════════════════════════════════════════════
# 5.4 — TestCarryingValidation
# ═════════════════════════════════════════════════════════════════════════════


class TestCarryingValidation:
    """Test carrying-claim validation (Arts. 36–38)."""

    def test_asil_claim_accepted(self) -> None:
        claim = CarryingAssignment(
            genre=SubjectGenre.WUJUD,
            rank=ReceptionRank.HISS,
            mode=CarryingMode.ASIL,
            qualification="",
        )
        valid, codes = validate_carrying_claim(claim)
        assert valid is True
        assert codes == []

    def test_tabi_claim_accepted(self) -> None:
        claim = CarryingAssignment(
            genre=SubjectGenre.WUJUD,
            rank=ReceptionRank.SHUUUR,
            mode=CarryingMode.TABI,
            qualification="",
        )
        valid, codes = validate_carrying_claim(claim)
        assert valid is True
        assert codes == []

    def test_wrong_mode_rejected(self) -> None:
        """Claiming ASIL where the matrix says TABI → violation."""
        claim = CarryingAssignment(
            genre=SubjectGenre.WUJUD,
            rank=ReceptionRank.SHUUUR,
            mode=CarryingMode.ASIL,  # matrix says TABI
            qualification="",
        )
        valid, codes = validate_carrying_claim(claim)
        assert valid is False
        assert ReceptionDecisionCode.REC007_CARRYING_VIOLATION in codes

    def test_mumtani_claim_rejected(self) -> None:
        """Claiming ASIL where it would be prohibited → violation."""
        claim = CarryingAssignment(
            genre=SubjectGenre.NISBA,
            rank=ReceptionRank.HISS,
            mode=CarryingMode.ASIL,  # matrix says TABI
            qualification="",
        )
        valid, codes = validate_carrying_claim(claim)
        assert valid is False
        assert ReceptionDecisionCode.REC007_CARRYING_VIOLATION in codes


# ═════════════════════════════════════════════════════════════════════════════
# 5.5 — TestReceptionValidation
# ═════════════════════════════════════════════════════════════════════════════


class TestReceptionValidation:
    """Test full reception validation (Arts. 10–46)."""

    def test_valid_complete_reception(self) -> None:
        result = validate_reception(_full_input())
        assert result.outcome == ReceptionValidationOutcome.ACCEPTED
        assert result.codes == ()

    def test_missing_subject(self) -> None:
        inp = EpistemicReceptionInput(
            reception_id="R1",
            subject=None,
            sense_present=True,
            feeling_present=True,
            thought_present=True,
        )
        result = validate_reception(inp)
        assert result.outcome == ReceptionValidationOutcome.REJECTED_CONSTITUTIONALLY
        assert ReceptionDecisionCode.REC001_SUBJECT_GENRE_UNRESOLVED in result.codes

    def test_unclosed_subject(self) -> None:
        sub = _subject(is_closed=False)
        result = validate_reception(_full_input(subject=sub))
        assert result.outcome == ReceptionValidationOutcome.REJECTED_CONSTITUTIONALLY
        assert ReceptionDecisionCode.REC001_SUBJECT_GENRE_UNRESOLVED in result.codes

    def test_feeling_as_judgment(self) -> None:
        """Art. 24: feeling + no thought + direction ranks → REC004."""
        result = validate_reception(
            _full_input(sense=True, feeling=True, thought=False, intention=True)
        )
        assert ReceptionDecisionCode.REC004_FEELING_AS_JUDGMENT in result.codes

    def test_intention_as_reception(self) -> None:
        """Art. 31: intention with no sense/feeling → REC005."""
        result = validate_reception(
            _full_input(
                sense=False,
                feeling=False,
                thought=True,
                intention=True,
                choice=False,
                will=False,
            )
        )
        assert ReceptionDecisionCode.REC005_INTENTION_AS_RECEPTION in result.codes

    def test_will_as_determination(self) -> None:
        """Art. 33: will with no thought → REC006."""
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=True,
                thought=False,
                intention=False,
                choice=False,
                will=True,
            )
        )
        assert ReceptionDecisionCode.REC006_WILL_AS_DETERMINATION in result.codes

    def test_rank_order_violation(self) -> None:
        """Art. 15: sense + thought but no feeling → REC008."""
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=False,
                thought=True,
                intention=False,
                choice=False,
                will=False,
            )
        )
        assert ReceptionDecisionCode.REC008_RANK_ORDER_VIOLATION in result.codes

    def test_carrying_claim_violation_in_full_validation(self) -> None:
        """Wrong carrying claim → gets corrected + REC007 code."""
        bad_claim = CarryingAssignment(
            genre=SubjectGenre.WUJUD,
            rank=ReceptionRank.SHUUUR,
            mode=CarryingMode.ASIL,  # should be TABI
            qualification="",
        )
        result = validate_reception(_full_input(claimed=(bad_claim,)))
        assert ReceptionDecisionCode.REC007_CARRYING_VIOLATION in result.codes
        # Corrected assignments should have the right mode.
        assert result.corrected_assignments[0].mode == CarryingMode.TABI

    def test_accepted_has_path(self) -> None:
        result = validate_reception(_full_input())
        assert result.path is not None
        assert result.path.current_rank == ReceptionRank.IRADA

    def test_acceptance_criteria_art45(self) -> None:
        """Art. 45: All criteria met → ACCEPTED."""
        result = validate_reception(_full_input())
        assert result.outcome == ReceptionValidationOutcome.ACCEPTED

    def test_rejection_criteria_art46(self) -> None:
        """Art. 46: Any violation → REJECTED_CONSTITUTIONALLY."""
        result = validate_reception(
            _full_input(sense=True, feeling=False, thought=True)
        )
        assert result.outcome == ReceptionValidationOutcome.REJECTED_CONSTITUTIONALLY

    def test_axis_confusion(self) -> None:
        """Art. 11: Claiming ASIL for a direction rank is an axis confusion
        because direction ranks (intention, choice, will) are never the original
        carriers of any genre — confusing subject-carrying with reception-directing.
        """
        bad_claim = CarryingAssignment(
            genre=SubjectGenre.WUJUD,
            rank=ReceptionRank.NIYYA,
            mode=CarryingMode.ASIL,  # should be TABI — direction ranks never ASIL
            qualification="",
        )
        result = validate_reception(_full_input(claimed=(bad_claim,)))
        assert ReceptionDecisionCode.REC002_AXIS_CONFUSION in result.codes
        assert ReceptionDecisionCode.REC007_CARRYING_VIOLATION in result.codes


# ═════════════════════════════════════════════════════════════════════════════
# 5.6 — TestSenseArticles
# ═════════════════════════════════════════════════════════════════════════════


class TestSenseArticles:
    """Arts. 16–20: Sense as first input."""

    def test_sense_carries_existence_originally(self) -> None:
        """Art. 18: Sense carries existence (WUJUD) as ASIL."""
        a = lookup_carrying_mode(SubjectGenre.WUJUD, ReceptionRank.HISS)
        assert a.mode == CarryingMode.ASIL

    def test_sense_does_not_carry_relation_originally(self) -> None:
        """Art. 19: Sense does not carry abstract relation (NISBA) as ASIL."""
        a = lookup_carrying_mode(SubjectGenre.NISBA, ReceptionRank.HISS)
        assert a.mode != CarryingMode.ASIL

    def test_sense_overreach_detected(self) -> None:
        """Art. 19: Sense + direction ranks without thought → overreach."""
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=False,
                thought=False,
                intention=True,
                choice=False,
                will=False,
            )
        )
        assert ReceptionDecisionCode.REC003_SENSE_OVERREACH in result.codes

    def test_sense_alone_is_not_overreach(self) -> None:
        """Sense alone (no direction ranks) should not trigger overreach."""
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=False,
                thought=False,
                intention=False,
                choice=False,
                will=False,
            )
        )
        assert ReceptionDecisionCode.REC003_SENSE_OVERREACH not in result.codes


# ═════════════════════════════════════════════════════════════════════════════
# 5.7 — TestFeelingArticles
# ═════════════════════════════════════════════════════════════════════════════


class TestFeelingArticles:
    """Arts. 21–25: Feeling as internal effect."""

    def test_feeling_carries_attribute_originally(self) -> None:
        """Art. 23: Feeling carries attribute effect originally."""
        a = lookup_carrying_mode(SubjectGenre.SIFA, ReceptionRank.SHUUUR)
        assert a.mode == CarryingMode.ASIL

    def test_feeling_does_not_carry_complete_determination(self) -> None:
        """Art. 24: Feeling does not carry complete rational determination.

        Feeling + direction ranks without thought → REC004.
        """
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=True,
                thought=False,
                intention=True,
                choice=True,
                will=False,
            )
        )
        assert ReceptionDecisionCode.REC004_FEELING_AS_JUDGMENT in result.codes

    def test_feeling_with_thought_no_violation(self) -> None:
        """Feeling + thought → no judgment violation."""
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=True,
                thought=True,
                intention=True,
                choice=True,
                will=True,
            )
        )
        assert ReceptionDecisionCode.REC004_FEELING_AS_JUDGMENT not in result.codes


# ═════════════════════════════════════════════════════════════════════════════
# 5.8 — TestThoughtArticles
# ═════════════════════════════════════════════════════════════════════════════


class TestThoughtArticles:
    """Arts. 26–30: Thought as cognitive closure rank."""

    def test_thought_is_closure_rank(self) -> None:
        """Art. 28: Thought is original rank for cognitive closure."""
        assert get_reception_layer(ReceptionRank.FIKR) == ReceptionLayer.MUALAJA_MARIFIYYA

    def test_thought_carries_all_four_genres(self) -> None:
        """Art. 29: Thought carries all four genres originally."""
        for genre in SubjectGenre:
            a = lookup_carrying_mode(genre, ReceptionRank.FIKR)
            assert a.mode == CarryingMode.ASIL, (
                f"Thought should carry {genre.name} originally"
            )

    def test_thought_qualification_strings(self) -> None:
        """Art. 29: Each genre has a qualification at the thought rank."""
        for genre in SubjectGenre:
            a = lookup_carrying_mode(genre, ReceptionRank.FIKR)
            assert a.qualification != ""


# ═════════════════════════════════════════════════════════════════════════════
# 5.9 — TestDirectionRanks
# ═════════════════════════════════════════════════════════════════════════════


class TestDirectionRanks:
    """Arts. 31–35: Intention, Choice, Will are post-thought direction."""

    def test_direction_ranks_in_tawjih_layer(self) -> None:
        for rank in (ReceptionRank.NIYYA, ReceptionRank.KHIYAR, ReceptionRank.IRADA):
            assert get_reception_layer(rank) == ReceptionLayer.TAWJIH

    def test_direction_ranks_do_not_carry_originally(self) -> None:
        """Arts. 31–35: Direction ranks are always TABI, never ASIL."""
        for genre in SubjectGenre:
            for rank in (ReceptionRank.NIYYA, ReceptionRank.KHIYAR, ReceptionRank.IRADA):
                a = lookup_carrying_mode(genre, rank)
                assert a.mode == CarryingMode.TABI

    def test_intention_without_reception_flagged(self) -> None:
        """Art. 31: Intention present without sense/feeling → REC005."""
        result = validate_reception(
            _full_input(
                sense=False,
                feeling=False,
                thought=True,
                intention=True,
                choice=False,
                will=False,
            )
        )
        assert ReceptionDecisionCode.REC005_INTENTION_AS_RECEPTION in result.codes

    def test_will_without_thought_flagged(self) -> None:
        """Art. 33: Will present without thought → REC006."""
        result = validate_reception(
            _full_input(
                sense=True,
                feeling=True,
                thought=False,
                intention=False,
                choice=False,
                will=True,
            )
        )
        assert ReceptionDecisionCode.REC006_WILL_AS_DETERMINATION in result.codes


# ═════════════════════════════════════════════════════════════════════════════
# 5.10 — TestBatchValidation
# ═════════════════════════════════════════════════════════════════════════════


class TestBatchValidation:
    """Test batch validation of multiple reception inputs."""

    def test_batch_returns_tuple(self) -> None:
        results = validate_reception_batch([_full_input(), _full_input(rid="R2")])
        assert isinstance(results, tuple)
        assert len(results) == 2

    def test_batch_preserves_order(self) -> None:
        inp1 = _full_input(rid="FIRST")
        inp2 = _full_input(rid="SECOND")
        results = validate_reception_batch([inp1, inp2])
        assert results[0].reception_id == "FIRST"
        assert results[1].reception_id == "SECOND"

    def test_batch_mixed_outcomes(self) -> None:
        good = _full_input(rid="GOOD")
        bad = EpistemicReceptionInput(
            reception_id="BAD",
            subject=None,
            sense_present=True,
        )
        results = validate_reception_batch([good, bad])
        assert results[0].outcome == ReceptionValidationOutcome.ACCEPTED
        assert results[1].outcome == ReceptionValidationOutcome.REJECTED_CONSTITUTIONALLY

    def test_empty_batch(self) -> None:
        results = validate_reception_batch([])
        assert results == ()


# ═════════════════════════════════════════════════════════════════════════════
# Additional integration tests
# ═════════════════════════════════════════════════════════════════════════════


class TestReceptionPath:
    """Test build_reception_path construction."""

    def test_full_path(self) -> None:
        path = build_reception_path(
            _subject(SubjectGenre.WUJUD),
            sense=True,
            feeling=True,
            thought=True,
            intention=True,
            choice=True,
            will=True,
        )
        assert path.current_rank == ReceptionRank.IRADA
        assert len(path.assignments) == 6

    def test_partial_path(self) -> None:
        path = build_reception_path(
            _subject(SubjectGenre.HADATH),
            sense=True,
            feeling=True,
            thought=False,
        )
        assert path.current_rank == ReceptionRank.SHUUUR
        assert len(path.assignments) == 2

    def test_sense_only_path(self) -> None:
        path = build_reception_path(
            _subject(SubjectGenre.NISBA),
            sense=True,
        )
        assert path.current_rank == ReceptionRank.HISS
        assert len(path.assignments) == 1

    def test_empty_path(self) -> None:
        path = build_reception_path(_subject())
        assert path.current_rank == ReceptionRank.HISS
        assert len(path.assignments) == 0

    def test_path_id_derived_from_subject(self) -> None:
        sub = _subject(cid="MY_SUBJECT")
        path = build_reception_path(sub, sense=True)
        assert "MY_SUBJECT" in path.path_id

    def test_path_genre_matches_subject(self) -> None:
        sub = _subject(SubjectGenre.SIFA)
        path = build_reception_path(sub, sense=True, feeling=True)
        for a in path.assignments:
            assert a.genre == SubjectGenre.SIFA


class TestEnumCompleteness:
    """Verify enum counts and member names."""

    def test_subject_genre_count(self) -> None:
        assert len(SubjectGenre) == 4

    def test_reception_rank_count(self) -> None:
        assert len(ReceptionRank) == 6

    def test_reception_layer_count(self) -> None:
        assert len(ReceptionLayer) == 3

    def test_carrying_mode_count(self) -> None:
        assert len(CarryingMode) == 3

    def test_decision_code_count(self) -> None:
        assert len(ReceptionDecisionCode) == 8

    def test_validation_outcome_count(self) -> None:
        assert len(ReceptionValidationOutcome) == 3
