"""Contract adjacency tests — verifies type compatibility checking.

Tests the type normalisation and compatibility logic used to verify
that ``output_type(Lᵢ)`` is structurally compatible with
``input_type(Lᵢ₊₁)`` for adjacent layers.
"""

from __future__ import annotations

from arabic_engine.core.contracts import (
    _extract_core,
    _normalize_type,
    _types_compatible,
    verify_adjacency,
)


# ── Type normalisation ──────────────────────────────────────────────


class TestNormalizeType:
    """_normalize_type lowers generic wrappers consistently."""

    def test_list_lowered(self):
        assert _normalize_type("List[str]") == "list[str]"

    def test_dict_lowered(self):
        assert _normalize_type("Dict[str, int]") == "dict[str, int]"

    def test_tuple_lowered(self):
        assert _normalize_type("Tuple[int, str]") == "tuple[int, str]"

    def test_optional_lowered(self):
        assert _normalize_type("Optional[str]") == "optional[str]"

    def test_inner_names_preserved(self):
        assert _normalize_type("List[LexicalClosure]") == "list[LexicalClosure]"

    def test_whitespace_stripped(self):
        assert _normalize_type("  str  ") == "str"


# ── Core extraction ─────────────────────────────────────────────────


class TestExtractCore:
    """_extract_core strips generics and returns lowercase inner names."""

    def test_simple_type(self):
        assert _extract_core("str") == "str"

    def test_list_type(self):
        assert _extract_core("list[LexicalClosure]") == "lexicalclosure"

    def test_tuple_type(self):
        core = _extract_core("tuple[list[LexicalClosure], list[Concept]]")
        assert "lexicalclosure" in core
        assert "concept" in core

    def test_nested_generics(self):
        core = _extract_core("list[list[str]]")
        assert core == "str"


# ── Type compatibility ──────────────────────────────────────────────


class TestTypesCompatible:
    """_types_compatible correctly identifies compatible type pairs."""

    def test_exact_match(self):
        assert _types_compatible("str", "str") is True

    def test_case_insensitive_generic(self):
        assert _types_compatible("List[str]", "list[str]") is True

    def test_simple_mismatch(self):
        assert _types_compatible("int", "str") is False

    def test_list_element_match(self):
        assert _types_compatible("List[str]", "List[str]") is True

    def test_list_element_mismatch(self):
        assert _types_compatible("List[int]", "List[str]") is False

    def test_output_as_component_of_tuple_input(self):
        """Output is consumed as part of a compound Tuple input."""
        assert _types_compatible(
            "List[LexicalClosure]",
            "Tuple[List[LexicalClosure], List[Concept]]",
        ) is True

    def test_completely_unrelated_types(self):
        assert _types_compatible("float", "List[Proposition]") is False

    def test_str_to_str(self):
        assert _types_compatible("str", "str") is True

    def test_str_to_list_str(self):
        # str is a component of list[str] via core extraction
        assert _types_compatible("str", "List[str]") is True


# ── Full adjacency report ───────────────────────────────────────────


class TestVerifyAdjacency:
    """verify_adjacency reports mismatches from the real contracts.yaml."""

    def test_returns_list(self):
        result = verify_adjacency()
        assert isinstance(result, list)

    def test_mismatches_have_required_keys(self):
        for m in verify_adjacency():
            assert "from_layer" in m
            assert "to_layer" in m
            assert "output_type" in m
            assert "input_type" in m
            assert "reason" in m

    def test_known_direct_pairs_are_compatible(self):
        """Known direct-flow pairs should NOT appear in mismatches."""
        mismatches = verify_adjacency()
        mismatch_pairs = {(m["from_layer"], m["to_layer"]) for m in mismatches}
        # normalize → tokenize is str → str (direct flow)
        assert ("normalize", "tokenize") not in mismatch_pairs
        # tokenize → lexical_closure is List[str] → List[str]
        assert ("tokenize", "lexical_closure") not in mismatch_pairs

    def test_known_indirect_pairs_reported(self):
        """Pairs that route through non-adjacent layers appear as mismatches."""
        mismatches = verify_adjacency()
        mismatch_pairs = {(m["from_layer"], m["to_layer"]) for m in mismatches}
        # syntax outputs List[SyntaxNode] but ontology expects List[LexicalClosure]
        assert ("syntax", "ontology") in mismatch_pairs
