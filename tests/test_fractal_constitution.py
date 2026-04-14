"""Tests for Fractal Core Constitution v1 and Fractal Representation Spec v1.

Invariants tested
-----------------
Constitution (FCC-v1):
  1. ConstitutionLayer enum has exactly 10 members in ascending value order.
  2. ConstitutionConstraint enum has exactly 6 members.
  3. DERIVED_SPECS contains at least FRS-v1 and KS-v1.
  4. ConstitutionReport is a frozen dataclass.
  5. validate_constitution() returns a valid report (all derived modules importable).
  6. ConstitutionValidator().validate() returns the same report.

Representation Spec (FRS-v1):
  7. FractalOrigin is frozen and immutable.
  8. validate_fractal_origin accepts valid origins.
  9. validate_fractal_origin rejects invalid origins (each field individually).
  10. LayerTrace.from_sequence builds correctly.
  11. build_fractal_representation raises ValueError on invalid origin.
  12. build_fractal_representation returns a FractalRepresentation with sha256.
  13. to_int_vector() returns a tuple of non-negative ints.
  14. Two distinct origins produce different sha256 digests.
  15. RepresentationMode and RepresentationFormat have expected members.
  16. Public API is re-exported from arabic_engine.representation.
"""

from __future__ import annotations

import pytest

from arabic_engine.core.fractal_constitution import (
    DERIVED_SPECS,
    ConstitutionConstraint,
    ConstitutionLayer,
    ConstitutionReport,
    ConstitutionValidator,
    DerivedSpec,
    validate_constitution,
)
from arabic_engine.representation.fractal_rep_spec import (
    FractalOrigin,
    FractalRepresentation,
    LayerTrace,
    OriginValidationResult,
    RepresentationFormat,
    RepresentationMode,
    build_fractal_representation,
    validate_fractal_origin,
)

# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

_FULL_LAYER_NAMES = [
    "SIGNAL", "MORPHOLOGY", "PHONOLOGY", "SYNTAX",
    "CONCEPT", "DALALA", "JUDGEMENT",
    "ANCHORING", "EVALUATION", "INFERENCE",
]

_VALID_ORIGIN = FractalOrigin(
    existence=0x0643,
    prior_knowledge_key="U+0643",
    function_mask=0b10000001,
    initial_class="consonant",
)

_FULL_TRACE = LayerTrace.from_sequence(_FULL_LAYER_NAMES, gate_passed=True)


# ═════════════════════════════════════════════════════════════════════
# Constitution — enum completeness
# ═════════════════════════════════════════════════════════════════════


class TestConstitutionEnums:
    """ConstitutionLayer and ConstitutionConstraint membership tests."""

    def test_constitution_layer_count(self):
        assert len(ConstitutionLayer) == 10

    def test_constitution_layer_ascending_values(self):
        values = [layer.value for layer in ConstitutionLayer]
        assert values == sorted(values), "Layer values must be strictly ascending"
        assert values[0] == 0
        assert values[-1] == 9

    def test_constitution_layer_names(self):
        names = {layer.name for layer in ConstitutionLayer}
        for expected in _FULL_LAYER_NAMES:
            assert expected in names, f"{expected!r} missing from ConstitutionLayer"

    def test_constitution_constraint_count(self):
        assert len(ConstitutionConstraint) == 6

    def test_constitution_constraint_names(self):
        expected = {
            "SINGLE_FRACTAL_ORIGIN",
            "KERNEL_14_CLOSED",
            "STRICT_LAYER_SEQUENCE",
            "COMPUTATIONAL_DETERMINISM",
            "NO_DUPLICATE_CONTENT",
            "SINGLE_REFERENCE_AUTHORITY",
        }
        assert {c.name for c in ConstitutionConstraint} == expected


# ═════════════════════════════════════════════════════════════════════
# Constitution — derived specs catalogue
# ═════════════════════════════════════════════════════════════════════


class TestDerivedSpecsCatalogue:
    """DERIVED_SPECS catalogue checks."""

    def test_derived_specs_is_tuple(self):
        assert isinstance(DERIVED_SPECS, tuple)

    def test_derived_specs_minimum_count(self):
        assert len(DERIVED_SPECS) >= 5

    def test_derived_spec_frs_present(self):
        codes = {s.code for s in DERIVED_SPECS}
        assert "FRS-v1" in codes

    def test_derived_spec_ks_present(self):
        codes = {s.code for s in DERIVED_SPECS}
        assert "KS-v1" in codes

    def test_derived_spec_is_frozen(self):
        spec = DERIVED_SPECS[0]
        with pytest.raises(AttributeError):
            spec.code = "CHANGED"  # type: ignore[misc]

    def test_derived_spec_fields(self):
        for spec in DERIVED_SPECS:
            assert isinstance(spec, DerivedSpec)
            assert spec.code and isinstance(spec.code, str)
            assert spec.title and isinstance(spec.title, str)
            assert spec.doc_path and isinstance(spec.doc_path, str)
            assert spec.module and isinstance(spec.module, str)


# ═════════════════════════════════════════════════════════════════════
# Constitution — validation
# ═════════════════════════════════════════════════════════════════════


class TestConstitutionValidation:
    """validate_constitution() and ConstitutionValidator tests."""

    def test_validate_constitution_returns_report(self):
        report = validate_constitution()
        assert isinstance(report, ConstitutionReport)

    def test_validate_constitution_is_valid(self):
        report = validate_constitution()
        assert report.valid is True, f"Errors: {report.errors}"
        assert report.errors == ()

    def test_validate_constitution_checked_layers(self):
        report = validate_constitution()
        assert len(report.checked_layers) == 10
        for name in _FULL_LAYER_NAMES:
            assert name in report.checked_layers

    def test_validate_constitution_checked_specs(self):
        report = validate_constitution()
        assert "FRS-v1" in report.checked_specs
        assert report.missing_specs == ()

    def test_constitution_validator_valid(self):
        validator = ConstitutionValidator()
        report = validator.validate()
        assert report.valid is True

    def test_constitution_validator_with_missing_spec(self):
        bad_spec = DerivedSpec(
            code="NONEXISTENT",
            title="No such module",
            doc_path="docs/no_such.md",
            module="arabic_engine.nonexistent_module_xyz",
        )
        validator = ConstitutionValidator(specs=[bad_spec])
        report = validator.validate()
        assert report.valid is False
        assert "NONEXISTENT" in report.missing_specs
        assert any("nonexistent_module_xyz" in e for e in report.errors)

    def test_constitution_report_is_frozen(self):
        report = ConstitutionReport(valid=True)
        with pytest.raises(AttributeError):
            report.valid = False  # type: ignore[misc]


# ═════════════════════════════════════════════════════════════════════
# Representation Spec — FractalOrigin
# ═════════════════════════════════════════════════════════════════════


class TestFractalOrigin:
    """FractalOrigin immutability and validation tests."""

    def test_fractal_origin_is_frozen(self):
        with pytest.raises(AttributeError):
            _VALID_ORIGIN.existence = 0  # type: ignore[misc]

    def test_validate_origin_accepts_valid(self):
        result = validate_fractal_origin(_VALID_ORIGIN)
        assert isinstance(result, OriginValidationResult)
        assert result.valid is True
        assert result.errors == ()

    def test_validate_origin_rejects_negative_existence(self):
        bad = FractalOrigin(
            existence=-1,
            prior_knowledge_key="K",
            function_mask=0,
            initial_class="consonant",
        )
        result = validate_fractal_origin(bad)
        assert result.valid is False
        assert any("E(u)" in e for e in result.errors)

    def test_validate_origin_rejects_empty_prior_knowledge(self):
        bad = FractalOrigin(
            existence=65,
            prior_knowledge_key="",
            function_mask=0,
            initial_class="consonant",
        )
        result = validate_fractal_origin(bad)
        assert result.valid is False
        assert any("K(u)" in e for e in result.errors)

    def test_validate_origin_rejects_negative_function_mask(self):
        bad = FractalOrigin(
            existence=65,
            prior_knowledge_key="K",
            function_mask=-5,
            initial_class="consonant",
        )
        result = validate_fractal_origin(bad)
        assert result.valid is False
        assert any("F(u)" in e for e in result.errors)

    def test_validate_origin_rejects_empty_initial_class(self):
        bad = FractalOrigin(
            existence=65,
            prior_knowledge_key="K",
            function_mask=0,
            initial_class="",
        )
        result = validate_fractal_origin(bad)
        assert result.valid is False
        assert any("C(u)" in e for e in result.errors)


# ═════════════════════════════════════════════════════════════════════
# Representation Spec — LayerTrace
# ═════════════════════════════════════════════════════════════════════


class TestLayerTrace:
    """LayerTrace construction and immutability tests."""

    def test_from_sequence_builds_correctly(self):
        trace = LayerTrace.from_sequence(["SIGNAL", "MORPHOLOGY"], gate_passed=True)
        assert trace.layers == ("SIGNAL", "MORPHOLOGY")
        assert trace.final_layer == "MORPHOLOGY"
        assert trace.gate_passed is True

    def test_from_sequence_gate_not_passed(self):
        trace = LayerTrace.from_sequence(["SIGNAL"], gate_passed=False)
        assert trace.gate_passed is False

    def test_from_sequence_empty(self):
        trace = LayerTrace.from_sequence([], gate_passed=True)
        assert trace.layers == ()
        assert trace.final_layer == ""

    def test_layer_trace_is_frozen(self):
        with pytest.raises(AttributeError):
            _FULL_TRACE.gate_passed = False  # type: ignore[misc]

    def test_full_trace_layer_count(self):
        assert len(_FULL_TRACE.layers) == 10
        assert _FULL_TRACE.final_layer == "INFERENCE"


# ═════════════════════════════════════════════════════════════════════
# Representation Spec — RepresentationMode and RepresentationFormat
# ═════════════════════════════════════════════════════════════════════


class TestRepresentationEnums:
    """RepresentationMode and RepresentationFormat membership tests."""

    def test_representation_mode_members(self):
        names = {m.name for m in RepresentationMode}
        assert {"TEXT", "NUMERIC", "GRAPH", "HYBRID"} == names

    def test_representation_format_members(self):
        names = {f.name for f in RepresentationFormat}
        assert {"TUPLE", "JSON", "YAML", "CYPHER"} == names


# ═════════════════════════════════════════════════════════════════════
# Representation Spec — build_fractal_representation
# ═════════════════════════════════════════════════════════════════════


class TestBuildFractalRepresentation:
    """build_fractal_representation() tests."""

    def test_build_returns_fractal_representation(self):
        rep = build_fractal_representation(
            "U+0643", _VALID_ORIGIN, _FULL_TRACE,
        )
        assert isinstance(rep, FractalRepresentation)

    def test_build_sets_element_id(self):
        rep = build_fractal_representation(
            "U+0643", _VALID_ORIGIN, _FULL_TRACE,
        )
        assert rep.element_id == "U+0643"

    def test_build_sets_sha256(self):
        rep = build_fractal_representation(
            "U+0643", _VALID_ORIGIN, _FULL_TRACE,
        )
        assert isinstance(rep.sha256, str)
        assert len(rep.sha256) == 64  # SHA-256 hex digest

    def test_build_default_mode_and_format(self):
        rep = build_fractal_representation(
            "U+0643", _VALID_ORIGIN, _FULL_TRACE,
        )
        assert rep.mode == RepresentationMode.NUMERIC
        assert rep.format == RepresentationFormat.TUPLE

    def test_build_custom_mode_and_format(self):
        rep = build_fractal_representation(
            "U+0643", _VALID_ORIGIN, _FULL_TRACE,
            mode=RepresentationMode.GRAPH,
            format=RepresentationFormat.JSON,
        )
        assert rep.mode == RepresentationMode.GRAPH
        assert rep.format == RepresentationFormat.JSON

    def test_build_with_confidence_vector(self):
        cv = (1.0, 0.95, 0.90, 0.85, 0.80, 0.75, 0.85, 0.90, 0.88, 0.88)
        rep = build_fractal_representation(
            "U+0643", _VALID_ORIGIN, _FULL_TRACE,
            confidence_vector=cv,
        )
        assert rep.confidence_vector == cv

    def test_build_raises_on_invalid_origin(self):
        bad = FractalOrigin(
            existence=-1,
            prior_knowledge_key="",
            function_mask=0,
            initial_class="",
        )
        with pytest.raises(ValueError, match="FCC-v1"):
            build_fractal_representation("bad", bad, _FULL_TRACE)

    def test_representation_is_frozen(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        with pytest.raises(AttributeError):
            rep.element_id = "changed"  # type: ignore[misc]


# ═════════════════════════════════════════════════════════════════════
# Representation Spec — to_int_vector
# ═════════════════════════════════════════════════════════════════════


class TestToIntVector:
    """FractalRepresentation.to_int_vector() tests."""

    def test_to_int_vector_returns_tuple(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        vec = rep.to_int_vector()
        assert isinstance(vec, tuple)

    def test_to_int_vector_length(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        assert len(rep.to_int_vector()) == 6

    def test_to_int_vector_all_non_negative(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        assert all(isinstance(x, int) and x >= 0 for x in rep.to_int_vector())

    def test_to_int_vector_existence_matches(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        assert rep.to_int_vector()[0] == _VALID_ORIGIN.existence

    def test_to_int_vector_function_mask_matches(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        assert rep.to_int_vector()[1] == _VALID_ORIGIN.function_mask

    def test_to_int_vector_layer_count_matches(self):
        rep = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        assert rep.to_int_vector()[4] == len(_FULL_TRACE.layers)


# ═════════════════════════════════════════════════════════════════════
# Representation Spec — sha256 uniqueness
# ═════════════════════════════════════════════════════════════════════


class TestSha256Uniqueness:
    """Different origins or traces must produce different sha256 digests."""

    def test_different_existence_different_sha256(self):
        origin_a = FractalOrigin(
            existence=0x0643,
            prior_knowledge_key="U+0643",
            function_mask=1,
            initial_class="consonant",
        )
        origin_b = FractalOrigin(
            existence=0x0644,
            prior_knowledge_key="U+0644",
            function_mask=1,
            initial_class="consonant",
        )
        rep_a = build_fractal_representation("a", origin_a, _FULL_TRACE)
        rep_b = build_fractal_representation("b", origin_b, _FULL_TRACE)
        assert rep_a.sha256 != rep_b.sha256

    def test_different_traces_different_sha256(self):
        trace_short = LayerTrace.from_sequence(["SIGNAL", "MORPHOLOGY"], gate_passed=True)
        rep_full = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        rep_short = build_fractal_representation("U+0643", _VALID_ORIGIN, trace_short)
        assert rep_full.sha256 != rep_short.sha256

    def test_same_inputs_same_sha256(self):
        rep_a = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        rep_b = build_fractal_representation("U+0643", _VALID_ORIGIN, _FULL_TRACE)
        assert rep_a.sha256 == rep_b.sha256


# ═════════════════════════════════════════════════════════════════════
# Public API re-exports
# ═════════════════════════════════════════════════════════════════════


class TestPublicAPIReExports:
    """All public names are accessible from arabic_engine.representation."""

    def test_re_exports(self):
        import arabic_engine.representation as rep_pkg  # noqa: PLC0415
        for name in [
            "FractalOrigin",
            "FractalRepresentation",
            "LayerTrace",
            "RepresentationFormat",
            "RepresentationMode",
            "build_fractal_representation",
            "validate_fractal_origin",
        ]:
            assert hasattr(rep_pkg, name), f"{name!r} not re-exported"
