"""Tests for the Masdar Fractal Constitution v1.

Covers:
  * Masdar extraction from root/pattern/bab and from surface form
  * Derivation from masdar (participles, time/place/manner/instrument nouns)
  * Interpreted masdar (مصدر مؤوّل) recognition
  * D_min completeness validation (8 conditions)
  * Fractal law cycle (6 phases)
  * KawnBridge between existential and transformational being
  * Pipeline integration (lexicon, hypothesis, time/space, contracts)
"""

from __future__ import annotations

import json
import pathlib

import pytest

from arabic_engine.core.enums import (
    POS,
    CellType,
    DalalaType,
    DerivationTarget,
    KawnType,
    MasdarBab,
    MasdarType,
    SemanticType,
    SpaceRef,
    TimeRef,
)
from arabic_engine.core.masdar_fractal import (
    assign,
    judge,
    link,
    preserve,
    return_to_source,
    run_fractal_cycle,
    transition,
    validate_dmin_masdar,
)
from arabic_engine.core.types import (
    Concept,
    FractalMasdarNode,
    LexicalClosure,
    MasdarDerivation,
    MasdarRecord,
)
from arabic_engine.linkage.masdar_bridge import (
    build_bridge,
    trace_fractal_path,
    validate_masdar_link,
)
from arabic_engine.signifier.masdar import (
    build_fractal_node,
    derive_from_masdar,
    extract_masdar,
    extract_masdar_from_surface,
    interpret_masdar,
    validate_completeness,
)

# ── Helpers ─────────────────────────────────────────────────────────


def _make_concept(cid: str, label: str, stype: SemanticType = SemanticType.EVENT) -> Concept:
    return Concept(concept_id=cid, label=label, semantic_type=stype)


def _make_closure(
    surface: str,
    lemma: str,
    root: tuple = (),
    pattern: str = "",
    pos: POS = POS.ISM,
) -> LexicalClosure:
    return LexicalClosure(surface=surface, lemma=lemma, root=root, pattern=pattern, pos=pos)


# ═══════════════════════════════════════════════════════════════════
#  PHASE 1 — Enum extensions
# ═══════════════════════════════════════════════════════════════════


class TestEnumExtensions:
    """Verify all masdar-related enum extensions are present."""

    def test_pos_has_masdar_sarih(self):
        assert POS.MASDAR_SARIH is not None

    def test_pos_has_masdar_muawwal(self):
        assert POS.MASDAR_MUAWWAL is not None

    def test_semantic_type_nominalized_event(self):
        assert SemanticType.NOMINALIZED_EVENT is not None

    def test_semantic_type_event_concept(self):
        assert SemanticType.EVENT_CONCEPT is not None

    def test_dalala_type_masdar_bridge(self):
        assert DalalaType.MASDAR_BRIDGE is not None

    def test_cell_type_masdar_explicit(self):
        assert CellType.CELL_MASDAR_EXPLICIT is not None

    def test_cell_type_masdar_interpreted(self):
        assert CellType.CELL_MASDAR_INTERPRETED is not None

    def test_cell_type_masdar_bridge(self):
        assert CellType.CELL_MASDAR_BRIDGE is not None

    def test_masdar_type_members(self):
        expected = {"ORIGINAL", "MIMI", "INDUSTRIAL", "MARRAH", "HAY2A", "MUAWWAL"}
        assert {m.name for m in MasdarType} == expected

    def test_masdar_bab_has_15_members(self):
        assert len(MasdarBab) == 15

    def test_derivation_target_has_9_members(self):
        assert len(DerivationTarget) == 9

    def test_kawn_type_members(self):
        expected = {"WUJUDI", "TAHAWWULI", "MASDAR_BRIDGE"}
        assert {k.name for k in KawnType} == expected

    def test_time_ref_masdar_potential(self):
        assert TimeRef.MASDAR_POTENTIAL is not None

    def test_space_ref_masdar_potential(self):
        assert SpaceRef.MASDAR_POTENTIAL is not None


# ═══════════════════════════════════════════════════════════════════
#  PHASE 2 — Dataclass instantiation
# ═══════════════════════════════════════════════════════════════════


class TestDataclasses:
    """Verify masdar dataclasses are constructible."""

    def test_masdar_record_creation(self):
        m = MasdarRecord(
            masdar_id="MSDR_TEST",
            surface="كِتابة",
            root=("ك", "ت", "ب"),
            pattern="فِعالة",
            masdar_type=MasdarType.ORIGINAL,
            masdar_bab=MasdarBab.FI3ALA,
            verb_form="كَتَبَ",
        )
        assert m.masdar_id == "MSDR_TEST"
        assert m.kawn_type == KawnType.MASDAR_BRIDGE

    def test_masdar_derivation_creation(self):
        d = MasdarDerivation(
            source_masdar_id="MSDR_TEST",
            target_type=DerivationTarget.ISM_FA3IL,
            target_surface="كاتِب",
            target_pattern="فاعِل",
        )
        assert d.source_masdar_id == "MSDR_TEST"

    def test_fractal_masdar_node_creation(self):
        m = MasdarRecord(
            masdar_id="MSDR_TEST",
            surface="كِتابة",
            root=("ك", "ت", "ب"),
            pattern="فِعالة",
            masdar_type=MasdarType.ORIGINAL,
            masdar_bab=MasdarBab.FI3ALA,
            verb_form="كَتَبَ",
        )
        node = FractalMasdarNode(node_id="FN_TEST", masdar=m)
        assert node.fractal_depth == 0
        assert node.completeness_score == 0.0


# ═══════════════════════════════════════════════════════════════════
#  PHASE 3 — Masdar extraction engine
# ═══════════════════════════════════════════════════════════════════


class TestExtractMasdar:
    """Test extract_masdar from root/pattern/bab."""

    @pytest.mark.parametrize(
        "root,bab,expected_pattern",
        [
            (("ض", "ر", "ب"), MasdarBab.FA3L, "فَعْل"),
            (("ك", "ت", "ب"), MasdarBab.FI3ALA, "فِعالة"),
            (("خ", "ر", "ج"), MasdarBab.FU3UL, "فُعول"),
            (("ط", "ل", "ب"), MasdarBab.FA3AL, "فَعَل"),
            (("ر", "ح", "ل"), MasdarBab.FA3IL, "فَعيل"),
            (("ك", "ر", "م"), MasdarBab.IF3AL, "إفعال"),
            (("ع", "ل", "م"), MasdarBab.TAF3IL, "تفعيل"),
            (("غ", "ف", "ر"), MasdarBab.ISTIF3AL, "استفعال"),
        ],
    )
    def test_extract_masdar_by_bab(self, root, bab, expected_pattern):
        m = extract_masdar(root, "فَعَلَ", bab)
        assert m.pattern == expected_pattern
        assert m.kawn_type == KawnType.MASDAR_BRIDGE
        assert m.root == root

    def test_extract_masdar_surface(self):
        m = extract_masdar(
            ("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة"
        )
        assert m.surface == "كِتابة"

    def test_extract_masdar_has_derivation_capacity(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA)
        assert len(m.derivation_capacity) >= 7

    def test_extract_masdar_id_format(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA)
        assert m.masdar_id.startswith("MSDR_")


class TestExtractMasdarFromSurface:
    """Test lexicon-based masdar extraction."""

    @pytest.mark.parametrize(
        "surface,expected_bab",
        [
            ("كِتابة", MasdarBab.FI3ALA),
            ("كتابة", MasdarBab.FI3ALA),
            ("خُروج", MasdarBab.FU3UL),
            ("خروج", MasdarBab.FU3UL),
            ("تَعليم", MasdarBab.TAF3IL),
            ("تعليم", MasdarBab.TAF3IL),
            ("استغفار", MasdarBab.ISTIF3AL),
            ("ضَرْب", MasdarBab.FA3L),
            ("ضرب", MasdarBab.FA3L),
            ("إكرام", MasdarBab.IF3AL),
            ("انكسار", MasdarBab.INFI3AL),
            ("اجتماع", MasdarBab.IFTI3AL),
        ],
    )
    def test_known_masdar(self, surface, expected_bab):
        m = extract_masdar_from_surface(surface)
        assert m is not None
        assert m.masdar_bab == expected_bab
        assert m.masdar_type == MasdarType.ORIGINAL

    def test_unknown_masdar_returns_none(self):
        assert extract_masdar_from_surface("شجرة") is None


class TestDeriveFromMasdar:
    """Test derivation from masdar."""

    @pytest.fixture
    def kitaba_masdar(self):
        return extract_masdar(
            ("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة"
        )

    @pytest.mark.parametrize(
        "target,expected_pattern",
        [
            (DerivationTarget.ISM_FA3IL, "فاعِل"),
            (DerivationTarget.ISM_MAF3UL, "مَفْعول"),
            (DerivationTarget.ISM_ZAMAN, "مَفْعَل"),
            (DerivationTarget.ISM_MAKAN, "مَفْعَل"),
            (DerivationTarget.ISM_HAY2A, "فِعْلة"),
            (DerivationTarget.ISM_ALA, "مِفْعَل"),
            (DerivationTarget.FI3L, "فَعَلَ"),
        ],
    )
    def test_derive_target(self, kitaba_masdar, target, expected_pattern):
        d = derive_from_masdar(kitaba_masdar, target)
        assert d.target_pattern == expected_pattern
        assert d.source_masdar_id == kitaba_masdar.masdar_id


class TestInterpretMasdar:
    """Test interpreted masdar (مصدر مؤوّل)."""

    def test_an_plus_verb(self):
        closures = [
            _make_closure("أن", "أن", pos=POS.HARF),
            _make_closure("يكتب", "كَتَبَ", root=("ك", "ت", "ب"), pattern="يَفْعِلُ", pos=POS.FI3L),
        ]
        m = interpret_masdar(closures)
        assert m is not None
        assert m.masdar_type == MasdarType.MUAWWAL
        assert m.root == ("ك", "ت", "ب")

    def test_no_an_returns_none(self):
        closures = [
            _make_closure("كتب", "كَتَبَ", root=("ك", "ت", "ب"), pos=POS.FI3L),
        ]
        assert interpret_masdar(closures) is None

    def test_an_without_verb_returns_none(self):
        closures = [
            _make_closure("أن", "أن", pos=POS.HARF),
            _make_closure("زيد", "زَيْد", pos=POS.ISM),
        ]
        assert interpret_masdar(closures) is None


# ═══════════════════════════════════════════════════════════════════
#  PHASE 4 — Masdar bridge
# ═══════════════════════════════════════════════════════════════════


class TestBuildFractalNode:
    """Test fractal node construction."""

    def test_build_produces_derivations(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")
        node = build_fractal_node(m, existential_link="JAMID_KTB")
        assert len(node.transformational_links) == len(m.derivation_capacity)
        assert node.existential_link == "JAMID_KTB"
        assert node.fractal_depth == 1

    def test_completeness_is_one_for_full_masdar(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")
        node = build_fractal_node(m)
        assert node.completeness_score == 1.0


class TestKawnBridge:
    """Test KawnBridge between existential and transformational."""

    def test_build_bridge(self):
        jamid = _make_concept("C_BOOK", "كتاب", SemanticType.ENTITY)
        fi3l = _make_concept("C_WRITE", "كَتَبَ", SemanticType.EVENT)
        masdar = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")

        bridge = build_bridge(jamid, masdar, fi3l)
        assert bridge.is_complete
        assert bridge.bridge_kawn_type == KawnType.MASDAR_BRIDGE
        assert len(bridge.links) == 2

    def test_bridge_links_are_masdar_bridge_type(self):
        jamid = _make_concept("C_BOOK", "كتاب", SemanticType.ENTITY)
        fi3l = _make_concept("C_WRITE", "كَتَبَ", SemanticType.EVENT)
        masdar = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")

        bridge = build_bridge(jamid, masdar, fi3l)
        for dl in bridge.links:
            assert dl.dalala_type == DalalaType.MASDAR_BRIDGE
            assert dl.accepted is True

    def test_trace_fractal_path(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")
        node = build_fractal_node(m)
        path = trace_fractal_path(node, "ISM_FA3IL")
        assert len(path) == 1
        assert path[0].target_type == DerivationTarget.ISM_FA3IL

    def test_validate_masdar_link(self):
        masdar = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")
        concept = _make_concept("C_WRITE", "كتابة", SemanticType.NOMINALIZED_EVENT)
        dl = validate_masdar_link(masdar, concept)
        assert dl.dalala_type == DalalaType.MASDAR_BRIDGE
        assert dl.confidence >= 0.5


# ═══════════════════════════════════════════════════════════════════
#  PHASE 5 — Fractal law cycle
# ═══════════════════════════════════════════════════════════════════


class TestFractalLawCycle:
    """Test the six-phase fractal law cycle."""

    @pytest.fixture
    def kitaba(self):
        return extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")

    def test_assign(self, kitaba):
        result = assign(kitaba)
        assert result["masdar_id"] == kitaba.masdar_id
        assert result["bab"] == "FI3ALA"
        assert result["event_core"] == "كتب"

    def test_preserve(self, kitaba):
        result = preserve(kitaba)
        assert result["preserved"] is True
        assert result["event_core"] == "كتب"
        assert result["kawn_type"] == "MASDAR_BRIDGE"

    def test_link(self, kitaba):
        result = link(kitaba, "JAMID_1", "FI3L_1", ["DERIV_1", "DERIV_2"])
        assert result["existential_link"] == "JAMID_1"
        assert result["transformational_link"] == "FI3L_1"
        assert len(result["derivative_links"]) == 2

    def test_judge(self, kitaba):
        result = judge(kitaba)
        assert result["bab"] == "FI3ALA"
        assert result["productivity"] >= 7
        assert result["confidence"] == 1.0

    def test_transition(self, kitaba):
        derivations = transition(kitaba)
        assert len(derivations) == len(kitaba.derivation_capacity)
        targets = {d.target_type for d in derivations}
        assert DerivationTarget.ISM_FA3IL in targets
        assert DerivationTarget.ISM_MAF3UL in targets

    def test_return_to_source(self, kitaba):
        derivations = transition(kitaba)
        result = return_to_source(derivations, kitaba)
        assert result["all_return"] is True
        assert result["derivation_count"] == len(derivations)

    def test_full_cycle(self, kitaba):
        result = run_fractal_cycle(kitaba, "JAMID_KTB", "FI3L_KTB")
        assert result["completeness_score"] == 1.0
        assert result["return_record"]["all_return"] is True
        assert len(result["derivations"]) >= 7


class TestDminMasdarValidation:
    """Test the 8-condition D_min validation."""

    def test_full_masdar_scores_1(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")
        node = build_fractal_node(m)
        result = validate_dmin_masdar(node)
        assert result["score"] == 1.0
        assert result["met_count"] == 8

    def test_all_conditions_named(self):
        m = extract_masdar(("ك", "ت", "ب"), "فَعَلَ", MasdarBab.FI3ALA, surface="كِتابة")
        node = build_fractal_node(m)
        result = validate_dmin_masdar(node)
        names = {c["name"] for c in result["conditions"]}
        expected = {"thubut", "hadd", "imtidad", "muqawwim", "alaqa", "intizam", "wahda", "taayin"}
        assert names == expected

    def test_empty_surface_reduces_score(self):
        m = MasdarRecord(
            masdar_id="MSDR_TEST",
            surface="",
            root=("ك", "ت", "ب"),
            pattern="فِعالة",
            masdar_type=MasdarType.ORIGINAL,
            masdar_bab=MasdarBab.FI3ALA,
            verb_form="كَتَبَ",
        )
        node = FractalMasdarNode(node_id="FN_TEST", masdar=m)
        score = validate_completeness(node)
        # Missing surface → thubut fails, and taayin still passes for non-MUAWWAL
        assert score < 1.0


# ═══════════════════════════════════════════════════════════════════
#  PHASE 6 — Pipeline integration
# ═══════════════════════════════════════════════════════════════════


class TestLexiconMasdarEntries:
    """Test masdar entries in the root_pattern lexicon."""

    def test_kitaba_in_lexicon(self):
        from arabic_engine.signifier.root_pattern import lexical_closure
        cl = lexical_closure("كِتابة")
        assert cl.pos == POS.MASDAR_SARIH
        assert cl.root == ("ك", "ت", "ب")
        assert cl.pattern == "فِعالة"

    def test_khuruj_in_lexicon(self):
        from arabic_engine.signifier.root_pattern import lexical_closure
        cl = lexical_closure("خُروج")
        assert cl.pos == POS.MASDAR_SARIH

    def test_talim_in_lexicon(self):
        from arabic_engine.signifier.root_pattern import lexical_closure
        cl = lexical_closure("تعليم")
        assert cl.pos == POS.MASDAR_SARIH

    def test_istighfar_in_lexicon(self):
        from arabic_engine.signifier.root_pattern import lexical_closure
        cl = lexical_closure("استغفار")
        assert cl.pos == POS.MASDAR_SARIH


class TestTimeSpaceMasdarPotential:
    """Test that masdar-typed closures produce MASDAR_POTENTIAL time/space."""

    def test_masdar_gives_temporal_potential(self):
        from arabic_engine.cognition.time_space import detect_time
        closures = [
            _make_closure("كِتابة", "كِتابة", root=("ك", "ت", "ب"),
                          pattern="فِعالة", pos=POS.MASDAR_SARIH),
        ]
        ref, detail = detect_time(closures)
        assert ref == TimeRef.MASDAR_POTENTIAL

    def test_masdar_gives_spatial_potential(self):
        from arabic_engine.cognition.time_space import detect_space
        closures = [
            _make_closure("كِتابة", "كِتابة", root=("ك", "ت", "ب"),
                          pattern="فِعالة", pos=POS.MASDAR_SARIH),
        ]
        ref, detail = detect_space(closures)
        assert ref == SpaceRef.MASDAR_POTENTIAL

    def test_explicit_adverb_takes_priority_over_masdar(self):
        from arabic_engine.cognition.time_space import detect_time
        closures = [
            _make_closure("كِتابة", "كِتابة", pos=POS.MASDAR_SARIH),
            _make_closure("أَمْسَ", "أَمْس", pos=POS.ZARF),
        ]
        ref, _ = detect_time(closures)
        assert ref == TimeRef.PAST  # adverb takes priority


class TestMasdarPatternsJson:
    """Test that masdar_patterns.json data file is valid."""

    def _patterns_path(self):
        return (
            pathlib.Path(__file__).resolve().parent.parent
            / "arabic_engine" / "data" / "masdar_patterns.json"
        )

    def test_file_loads(self):
        with open(self._patterns_path()) as f:
            data = json.load(f)
        assert "patterns" in data
        assert "thulathi_mujarrad" in data["patterns"]
        assert "thulathi_mazeed" in data["patterns"]

    def test_has_all_base_babs(self):
        with open(self._patterns_path()) as f:
            data = json.load(f)
        base_entries = data["patterns"]["thulathi_mujarrad"]["entries"]
        babs = {e["bab"] for e in base_entries}
        assert babs == {"FA3L", "FI3ALA", "FU3UL", "FA3AL", "FA3IL", "FU3AL"}


class TestTransitionsMasdar:
    """Test masdar transitions in transitions_seed_v1.json."""

    def test_masdar_transitions_loaded(self):
        from arabic_engine.signifier.functional_transition import load_seed_dataset
        records = load_seed_dataset()
        masdar_ids = {r.transition_id for r in records if int(r.transition_id.split("_")[1]) >= 34}
        assert len(masdar_ids) == 8

    def test_masdar_explicit_transition_exists(self):
        from arabic_engine.signifier.functional_transition import load_seed_dataset
        records = load_seed_dataset()
        tr034 = [r for r in records if r.transition_id == "TR_034"]
        assert len(tr034) == 1
        assert tr034[0].source_cell == CellType.CELL_EVENT_SOURCE
        assert tr034[0].target_cell == CellType.CELL_MASDAR_EXPLICIT


class TestContractsMasdarLayer:
    """Test that contracts.yaml includes masdar_analysis layer."""

    def test_masdar_layer_in_contracts(self):
        import yaml
        path = pathlib.Path(__file__).resolve().parent.parent / "arabic_engine" / "contracts.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        layer_names = [layer["name"] for layer in data["layers"]]
        assert "masdar_analysis" in layer_names
