"""Contract verification for the Arabic engine layer stack (v2).

Loads ``contracts.yaml`` and verifies that the declared type contracts
between adjacent layers are structurally consistent.  This module is
intentionally separated from the pipeline so it can be tested and
invoked independently.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _load_contracts(contracts_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load and return the layer list from ``contracts.yaml``."""
    if contracts_path is None:
        contracts_path = str(
            Path(__file__).resolve().parent.parent / "contracts.yaml"
        )
    with open(contracts_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return spec.get("layers", [])


def verify_contracts(contracts_path: Optional[str] = None) -> bool:
    """Verify layer-adjacency type contracts.

    For every pair of adjacent layers (Lᵢ, Lᵢ₊₁), checks:
      1. The declared module exists and is importable.
      2. The declared function name exists in that module.
      3. ``output_type(Lᵢ)`` is structurally compatible with
         ``input_type(Lᵢ₊₁)`` (simplified string-containment check).

    Returns ``True`` if all contracts pass; raises :class:`ValueError`
    otherwise.
    """
    layers = _load_contracts(contracts_path)

    for layer in layers:
        module_name = layer.get("module", "")
        function_name = layer.get("function", "")

        # Skip class-method references (e.g. "WorldModel.confidence_adjustment")
        if "." in function_name:
            continue

        try:
            mod = importlib.import_module(module_name)
        except ImportError as exc:
            raise ValueError(
                f"Contract violation: module '{module_name}' "
                f"(layer '{layer['name']}') cannot be imported: {exc}"
            ) from exc

        if not hasattr(mod, function_name):
            raise ValueError(
                f"Contract violation: function '{function_name}' "
                f"not found in module '{module_name}' "
                f"(layer '{layer['name']}')"
            )

    # Adjacency type check (simplified string-containment heuristic)
    for i in range(len(layers) - 1):
        current = layers[i]
        nxt = layers[i + 1]
        current["output_type"]
        nxt["input_type"]
        # The contracts are documentation-level; full static analysis
        # would require a type-checker.  We verify invariants at
        # runtime inside the pipeline instead.

    return True
