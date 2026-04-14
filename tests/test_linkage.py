"""Comprehensive tests for arabic_engine.linkage (dalala + semantic_roles)."""

from __future__ import annotations

from arabic_engine.core.enums import (
    POS,
    DalalaType,
    IrabCase,
    IrabRole,
    SemanticType,
    SpaceRef,
    TimeRef,
)
from arabic_engine.core.types import Concept, DalalaLink, LexicalClosure, SyntaxNode
from arabic_engine.linkage.dalala import (
    build_isnad_links,
    full_validation,
    validate_link,
)
from arabic_engine.linkage.semantic_roles import derive_semantic_roles

# ── helpers ─────────────────────────────────────────────────────────

def _closure(
    surface: str = "كتب",
    lemma: str = "كتب",
    root: tuple = ("ك", "ت", "ب"),
    pos: POS = POS.ISM,
    *,
    pattern: str = "فَعَلَ",
    temporal: TimeRef = TimeRef.UNSPECIFIED,
    spatial: SpaceRef = SpaceRef.UNSPECIFIED,
    syntax_role: IrabRole = IrabRole.UNKNOWN,
) -> LexicalClosure:
    return LexicalClosure(
        surface=surface,
        lemma=lemma,
        root=root,
        pattern=pattern,
        pos=pos,
        temporal=temporal,
        spatial=spatial,
        syntax_role=syntax_role,
    )


def _concept(
    concept_id: int = 1,
    label: str = "كتب",
    semantic_type: SemanticType = SemanticType.ENTITY,
) -> Concept:
    return Concept(concept_id=concept_id, label=label, semantic_type=semantic_type)


def _syntax_node(
    token: str = "كتب",
    lemma: str = "كتب",
    pos: POS = POS.FI3L,
    case: IrabCase = IrabCase.UNKNOWN,
    role: IrabRole = IrabRole.FI3L,
) -> SyntaxNode:
    return SyntaxNode(token=token, lemma=lemma, pos=pos, case=case, role=role)


# ════════════════════════════════════════════════════════════════════
# validate_link
# ════════════════════════════════════════════════════════════════════

class TestValidateLink:
    """Tests for dalala.validate_link (mutābaqa / taḍammun / iltizām)."""

    # ── mutābaqa branch ────────────────────────────────────────────

    def test_mutabaqa_exact_match(self):
        link = validate_link(_closure(lemma="كتاب"), _concept(label="كتاب"))
        assert link.dalala_type == DalalaType.MUTABAQA
        assert link.confidence == 1.0
        assert link.accepted is True

    def test_mutabaqa_preserves_source_and_target(self):
        link = validate_link(
            _closure(lemma="علم"), _concept(concept_id=42, label="علم")
        )
        assert link.source_lemma == "علم"
        assert link.target_concept_id == 42

    # ── taḍammun branch ────────────────────────────────────────────

    def test_tadammun_root_in_label(self):
        """Root radical appears inside the concept label."""
        link = validate_link(
            _closure(lemma="كاتب", root=("ك", "ت", "ب")),
            _concept(label="مكتبة"),  # contains ك, ت, ب
        )
        assert link.dalala_type == DalalaType.TADAMMUN
        assert link.confidence == 0.75
        assert link.accepted is True

    def test_tadammun_partial_root_match(self):
        """Even one root radical in label triggers taḍammun."""
        link = validate_link(
            _closure(lemma="ضارب", root=("ض", "ر", "ب")),
            _concept(label="ضوء"),  # contains ض
        )
        assert link.dalala_type == DalalaType.TADAMMUN
        assert link.confidence == 0.75

    # ── iltizām branch ─────────────────────────────────────────────

    def test_iltizam_fallback(self):
        """No lemma match, no root overlap → iltizām."""
        link = validate_link(
            _closure(lemma="ذهب", root=("ذ", "ه", "ب")),
            _concept(label="مدرسة"),
        )
        assert link.dalala_type == DalalaType.ILTIZAM
        assert link.confidence == 0.5
        assert link.accepted is True

    def test_iltizam_empty_root(self):
        """Empty root tuple can never match → fallback to iltizām."""
        link = validate_link(
            _closure(lemma="من", root=()),
            _concept(label="شيء"),
        )
        assert link.dalala_type == DalalaType.ILTIZAM
        assert link.confidence == 0.5

    # ── return type ────────────────────────────────────────────────

    def test_returns_dalala_link_instance(self):
        link = validate_link(_closure(), _concept())
        assert isinstance(link, DalalaLink)


# ════════════════════════════════════════════════════════════════════
# build_isnad_links
# ════════════════════════════════════════════════════════════════════

class TestBuildIsnadLinks:
    """Tests for dalala.build_isnad_links (verb-subject-object predication)."""

    def test_single_verb_single_noun(self):
        closures = [
            _closure(surface="كتب", lemma="كتب", pos=POS.FI3L),
            _closure(surface="الطالب", lemma="طالب", pos=POS.ISM),
        ]
        concepts = [
            _concept(concept_id=1, label="كتب", semantic_type=SemanticType.EVENT),
            _concept(concept_id=2, label="طالب"),
        ]
        links = build_isnad_links(closures, concepts)
        assert len(links) >= 1
        isnad = [lk for lk in links if lk.dalala_type == DalalaType.ISNAD]
        assert len(isnad) >= 1
        assert isnad[0].confidence == 0.95
        assert isnad[0].accepted is True

    def test_verb_followed_by_two_nouns(self):
        closures = [
            _closure(surface="قرأ", lemma="قرأ", pos=POS.FI3L),
            _closure(surface="الطالب", lemma="طالب", pos=POS.ISM),
            _closure(surface="الكتاب", lemma="كتاب", pos=POS.ISM),
        ]
        concepts = [
            _concept(concept_id=1, label="قرأ", semantic_type=SemanticType.EVENT),
            _concept(concept_id=2, label="طالب"),
            _concept(concept_id=3, label="كتاب"),
        ]
        links = build_isnad_links(closures, concepts)
        assert len(links) >= 2

    def test_no_verb_returns_empty(self):
        closures = [
            _closure(surface="الكتاب", lemma="كتاب", pos=POS.ISM),
            _closure(surface="الجديد", lemma="جديد", pos=POS.SIFA),
        ]
        concepts = [_concept(concept_id=i) for i in range(len(closures))]
        links = build_isnad_links(closures, concepts)
        assert links == []

    def test_empty_lists(self):
        assert build_isnad_links([], []) == []

    def test_verb_only_no_nouns(self):
        closures = [_closure(surface="جلس", lemma="جلس", pos=POS.FI3L)]
        concepts = [_concept(concept_id=1, label="جلس", semantic_type=SemanticType.EVENT)]
        links = build_isnad_links(closures, concepts)
        assert links == []

    def test_nouns_before_verb_not_linked(self):
        """ISM tokens appearing *before* the first verb should not get ISNAD links."""
        closures = [
            _closure(surface="الولد", lemma="ولد", pos=POS.ISM),
            _closure(surface="ذهب", lemma="ذهب", pos=POS.FI3L),
        ]
        concepts = [
            _concept(concept_id=1, label="ولد"),
            _concept(concept_id=2, label="ذهب", semantic_type=SemanticType.EVENT),
        ]
        links = build_isnad_links(closures, concepts)
        # The noun before the verb should not produce an ISNAD link
        assert all(lk.source_lemma != "ولد" for lk in links)

    def test_multiple_verbs_updates_predicate(self):
        """Each verb becomes the active predicate for subsequent nouns."""
        closures = [
            _closure(surface="كتب", lemma="كتب", pos=POS.FI3L),
            _closure(surface="الطالب", lemma="طالب", pos=POS.ISM),
            _closure(surface="قرأ", lemma="قرأ", pos=POS.FI3L),
            _closure(surface="الكتاب", lemma="كتاب", pos=POS.ISM),
        ]
        concepts = [
            _concept(concept_id=1, label="كتب", semantic_type=SemanticType.EVENT),
            _concept(concept_id=2, label="طالب"),
            _concept(concept_id=3, label="قرأ", semantic_type=SemanticType.EVENT),
            _concept(concept_id=4, label="كتاب"),
        ]
        links = build_isnad_links(closures, concepts)
        isnad = [lk for lk in links if lk.dalala_type == DalalaType.ISNAD]
        assert len(isnad) == 2
        # First noun linked to first verb
        assert isnad[0].source_lemma == "طالب"
        assert isnad[0].target_concept_id == 1
        # Second noun linked to second verb
        assert isnad[1].source_lemma == "كتاب"
        assert isnad[1].target_concept_id == 3

    def test_isnad_link_fields(self):
        closures = [
            _closure(surface="فتح", lemma="فتح", pos=POS.FI3L),
            _closure(surface="الباب", lemma="باب", pos=POS.ISM),
        ]
        concepts = [
            _concept(concept_id=10, label="فتح", semantic_type=SemanticType.EVENT),
            _concept(concept_id=20, label="باب"),
        ]
        links = build_isnad_links(closures, concepts)
        link = links[0]
        assert link.dalala_type == DalalaType.ISNAD
        assert link.confidence == 0.95
        assert link.accepted is True


# ════════════════════════════════════════════════════════════════════
# full_validation
# ════════════════════════════════════════════════════════════════════

class TestFullValidation:
    """Tests for dalala.full_validation (validate_link + build_isnad_links)."""

    def test_combines_per_token_and_isnad(self):
        closures = [
            _closure(surface="كتب", lemma="كتب", pos=POS.FI3L),
            _closure(surface="الطالب", lemma="طالب", pos=POS.ISM),
        ]
        concepts = [
            _concept(concept_id=1, label="كتب", semantic_type=SemanticType.EVENT),
            _concept(concept_id=2, label="طالب"),
        ]
        links = full_validation(closures, concepts)
        types = {lk.dalala_type for lk in links}
        # Should include per-token links AND structural ISNAD links
        assert DalalaType.ISNAD in types
        # Per-token validate_link should produce at least MUTABAQA for matching lemma
        assert DalalaType.MUTABAQA in types

    def test_empty_input(self):
        assert full_validation([], []) == []

    def test_count_at_least_token_count(self):
        closures = [
            _closure(surface="ذهب", lemma="ذهب", pos=POS.FI3L),
            _closure(surface="أحمد", lemma="أحمد", pos=POS.ISM),
        ]
        concepts = [
            _concept(concept_id=1, label="ذهب", semantic_type=SemanticType.EVENT),
            _concept(concept_id=2, label="أحمد"),
        ]
        links = full_validation(closures, concepts)
        # At minimum one link per token from validate_link
        assert len(links) >= len(closures)

    def test_no_verb_only_per_token(self):
        closures = [
            _closure(surface="كتاب", lemma="كتاب", pos=POS.ISM),
        ]
        concepts = [_concept(concept_id=1, label="كتاب")]
        links = full_validation(closures, concepts)
        # With no verb, no ISNAD links expected
        assert all(lk.dalala_type != DalalaType.ISNAD for lk in links)
        assert len(links) == 1


# ════════════════════════════════════════════════════════════════════
# derive_semantic_roles
# ════════════════════════════════════════════════════════════════════

class TestDeriveSemanticRoles:
    """Tests for semantic_roles.derive_semantic_roles."""

    def test_full_sentence(self):
        closures = [
            _closure(surface="كتب", lemma="كتب", pos=POS.FI3L),
            _closure(surface="الطالب", lemma="طالب", pos=POS.ISM),
            _closure(surface="الدرس", lemma="درس", pos=POS.ISM),
        ]
        nodes = [
            _syntax_node(token="كتب", lemma="كتب", pos=POS.FI3L, role=IrabRole.FI3L),
            _syntax_node(token="الطالب", lemma="طالب", pos=POS.ISM,
                         case=IrabCase.RAF3, role=IrabRole.FA3IL),
            _syntax_node(token="الدرس", lemma="درس", pos=POS.ISM,
                         case=IrabCase.NASB, role=IrabRole.MAF3UL_BIH),
        ]
        roles = derive_semantic_roles(closures, nodes)
        assert roles["event"] == "كتب"
        assert roles["agent"] == "طالب"
        assert roles["patient"] == "درس"

    def test_temporal_zarf(self):
        closures = [
            _closure(surface="صباحاً", lemma="صباح", pos=POS.ZARF,
                     temporal=TimeRef.PRESENT),
        ]
        nodes = [
            _syntax_node(token="صباحاً", lemma="صباح", pos=POS.ZARF,
                         role=IrabRole.ZARF),
        ]
        roles = derive_semantic_roles(closures, nodes)
        assert roles["time"] == "صباحاً"

    def test_spatial_zarf(self):
        closures = [
            _closure(surface="هنا", lemma="هنا", pos=POS.ZARF,
                     spatial=SpaceRef.HERE),
        ]
        nodes = [
            _syntax_node(token="هنا", lemma="هنا", pos=POS.ZARF,
                         role=IrabRole.ZARF),
        ]
        roles = derive_semantic_roles(closures, nodes)
        assert roles["place"] == "هنا"

    def test_empty_inputs(self):
        roles = derive_semantic_roles([], [])
        assert roles == {"event": "", "agent": "", "patient": "", "time": "", "place": ""}

    def test_no_verb_event_stays_empty(self):
        closures = [_closure(surface="كتاب", lemma="كتاب", pos=POS.ISM)]
        nodes = [_syntax_node(token="كتاب", lemma="كتاب", pos=POS.ISM,
                              role=IrabRole.MUBTADA)]
        roles = derive_semantic_roles(closures, nodes)
        assert roles["event"] == ""

    def test_unspecified_temporal_not_set(self):
        closures = [
            _closure(surface="مكان", lemma="مكان", pos=POS.ZARF,
                     temporal=TimeRef.UNSPECIFIED, spatial=SpaceRef.UNSPECIFIED),
        ]
        nodes = [
            _syntax_node(token="مكان", lemma="مكان", pos=POS.ZARF,
                         role=IrabRole.ZARF),
        ]
        roles = derive_semantic_roles(closures, nodes)
        assert roles["time"] == ""
        assert roles["place"] == ""

    def test_all_keys_present(self):
        roles = derive_semantic_roles([], [])
        for key in ("event", "agent", "patient", "time", "place"):
            assert key in roles
