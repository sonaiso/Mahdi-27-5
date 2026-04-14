"""Comprehensive tests for arabic_engine.core.contracts."""

from __future__ import annotations

import os
import textwrap

import pytest

from arabic_engine.core.contracts import _load_contracts, verify_contracts

# ── helpers ──────────────────────────────────────────────────────────────

def _write_yaml(directory, content: str, filename: str = "contracts.yaml") -> str:
    """Write *content* to a YAML file inside *directory* and return its path."""
    path = os.path.join(str(directory), filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content))
    return path


_VALID_LAYER_YAML = """\
layers:
  - name: dummy
    module: json
    function: dumps
    input_type: Any
    output_type: str
"""

_TWO_LAYER_YAML = """\
layers:
  - name: first
    module: json
    function: dumps
    input_type: Any
    output_type: str
  - name: second
    module: json
    function: loads
    input_type: str
    output_type: Any
"""

_BAD_MODULE_YAML = """\
layers:
  - name: bad_mod
    module: totally.nonexistent.module
    function: foo
    input_type: str
    output_type: str
"""

_BAD_FUNCTION_YAML = """\
layers:
  - name: bad_fn
    module: json
    function: this_function_does_not_exist
    input_type: str
    output_type: str
"""

_CLASS_METHOD_YAML = """\
layers:
  - name: class_method_layer
    module: json
    function: JSONDecoder.decode
    input_type: str
    output_type: Any
"""

_EMPTY_LAYERS_YAML = """\
layers: []
"""

_MISSING_OUTPUT_TYPE_YAML = """\
layers:
  - name: a
    module: json
    function: dumps
    input_type: Any
  - name: b
    module: json
    function: loads
    input_type: str
    output_type: Any
"""


# ── TestLoadContracts ────────────────────────────────────────────────────

class TestLoadContracts:
    """Tests for _load_contracts()."""

    def test_default_path_loads_list(self):
        """Default (no argument) loads the real contracts.yaml and returns a list."""
        layers = _load_contracts()
        assert isinstance(layers, list)

    def test_default_path_layers_non_empty(self):
        """The real contracts.yaml must contain at least one layer."""
        layers = _load_contracts()
        assert len(layers) > 0

    def test_default_layers_have_required_keys(self):
        """Every layer from the real YAML must have required keys."""
        required = {"name", "module", "function", "input_type", "output_type"}
        for layer in _load_contracts():
            assert required.issubset(layer.keys()), (
                f"Layer '{layer.get('name', '?')}' is missing keys: "
                f"{required - layer.keys()}"
            )

    def test_explicit_path(self, tmp_path):
        """_load_contracts with an explicit path reads that file."""
        path = _write_yaml(tmp_path, _VALID_LAYER_YAML)
        layers = _load_contracts(path)
        assert len(layers) == 1
        assert layers[0]["name"] == "dummy"

    def test_explicit_path_two_layers(self, tmp_path):
        """Explicit YAML with two layers returns both."""
        path = _write_yaml(tmp_path, _TWO_LAYER_YAML)
        layers = _load_contracts(path)
        assert len(layers) == 2
        assert layers[0]["function"] == "dumps"
        assert layers[1]["function"] == "loads"

    def test_empty_layers(self, tmp_path):
        """An empty layers list is valid and returns []."""
        path = _write_yaml(tmp_path, _EMPTY_LAYERS_YAML)
        layers = _load_contracts(path)
        assert layers == []


# ── TestVerifyContracts ──────────────────────────────────────────────────

class TestVerifyContracts:
    """Tests for verify_contracts()."""

    def test_real_contracts_pass(self):
        """Integration: verify_contracts with real contracts.yaml returns True."""
        assert verify_contracts() is True

    def test_valid_custom_yaml(self, tmp_path):
        """A minimal well-formed YAML passes verification."""
        path = _write_yaml(tmp_path, _VALID_LAYER_YAML)
        assert verify_contracts(path) is True

    def test_bad_module_raises(self, tmp_path):
        """A YAML with an un-importable module raises ValueError."""
        path = _write_yaml(tmp_path, _BAD_MODULE_YAML)
        with pytest.raises(ValueError, match="cannot be imported"):
            verify_contracts(path)

    def test_bad_function_raises(self, tmp_path):
        """A YAML with a missing function raises ValueError."""
        path = _write_yaml(tmp_path, _BAD_FUNCTION_YAML)
        with pytest.raises(ValueError, match="not found in module"):
            verify_contracts(path)

    def test_empty_layers_returns_true(self, tmp_path):
        """Empty layers list should pass verification."""
        path = _write_yaml(tmp_path, _EMPTY_LAYERS_YAML)
        assert verify_contracts(path) is True

    def test_class_method_skipped(self, tmp_path):
        """Functions containing '.' (class methods) are skipped entirely."""
        path = _write_yaml(tmp_path, _CLASS_METHOD_YAML)
        assert verify_contracts(path) is True

    def test_adjacency_missing_output_type_raises(self, tmp_path):
        """Adjacency check accesses output_type; missing key should raise."""
        path = _write_yaml(tmp_path, _MISSING_OUTPUT_TYPE_YAML)
        with pytest.raises(KeyError):
            verify_contracts(path)
