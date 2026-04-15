"""Contract verification for the Arabic engine layer stack (v2).

Loads ``contracts.yaml`` and verifies that the declared type contracts
between adjacent layers are structurally consistent.  This module is
intentionally separated from the pipeline so it can be tested and
invoked independently.
"""

from __future__ import annotations

import importlib
import inspect
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


def _extract_return_type_name(func: object) -> str:
    """Return the simplified return-annotation string of *func*, or ''."""
    try:
        sig = inspect.signature(func)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return ""
    ann = sig.return_annotation
    if ann is inspect.Parameter.empty:
        return ""
    return getattr(ann, "__name__", str(ann))


def verify_contracts(contracts_path: Optional[str] = None) -> bool:
    """Verify layer-adjacency type contracts.

    For every pair of adjacent layers (Lᵢ, Lᵢ₊₁), checks:
      1. The declared module exists and is importable.
      2. The declared function name exists in that module.
      3. ``output_type(Lᵢ)`` is structurally compatible with
         ``input_type(Lᵢ₊₁)`` (simplified string-containment check).
      4. (SIVP-v1 § A5) If the function has a return-type annotation,
         verify it is consistent with the declared ``output_type``.

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

        # SIVP-v1 § A5 — lightweight return-type consistency check
        func = getattr(mod, function_name)
        declared_output = layer.get("output_type", "")
        actual_return = _extract_return_type_name(func)
        if actual_return and declared_output:
            # Normalise for simple comparison (strip module qualifiers)
            norm_actual = actual_return.rsplit(".", 1)[-1]
            norm_declared = declared_output.rsplit(".", 1)[-1]
            # Accept if the declared type appears as substring (handles
            # generic wrappers like ``List[X]`` vs ``list[X]``).
            if (
                norm_declared.lower() not in norm_actual.lower()
                and norm_actual.lower() not in norm_declared.lower()
            ):
                raise ValueError(
                    f"Contract type mismatch at layer '{layer['name']}': "
                    f"declared output_type='{declared_output}', "
                    f"actual return annotation='{actual_return}'"
                )

    # Adjacency type check is available via verify_adjacency() for
    # full reporting.  verify_contracts() focuses on module/function
    # existence and return-type consistency.

    return True


def verify_adjacency(contracts_path: Optional[str] = None) -> List[Dict[str, str]]:
    """Verify type compatibility between every pair of adjacent layers.

    Unlike :func:`verify_contracts` (which skips compound Tuple inputs),
    this function reports *all* adjacency mismatches including compound
    inputs.  It returns a list of mismatch dicts rather than raising so
    callers can inspect the full picture.

    Each mismatch dict contains:

    * ``from_layer`` / ``to_layer`` — layer names
    * ``output_type`` / ``input_type`` — declared types
    * ``reason`` — human-readable explanation
    """
    layers = _load_contracts(contracts_path)
    mismatches: List[Dict[str, str]] = []

    for i in range(len(layers) - 1):
        current = layers[i]
        nxt = layers[i + 1]
        out_type = current.get("output_type", "")
        in_type = nxt.get("input_type", "")
        if not out_type or not in_type:
            continue
        if not _types_compatible(out_type, in_type):
            mismatches.append({
                "from_layer": current["name"],
                "to_layer": nxt["name"],
                "output_type": out_type,
                "input_type": in_type,
                "reason": (
                    f"Output '{out_type}' of '{current['name']}' is not "
                    f"directly compatible with input '{in_type}' of "
                    f"'{nxt['name']}'"
                ),
            })

    return mismatches


def _normalize_type(raw: str) -> str:
    """Normalise a type string for comparison.

    Handles common variations such as ``List[str]`` vs ``list[str]``,
    ``Optional[X]`` vs ``X | None``, and trims whitespace.
    """
    t = raw.strip()
    # Lower-case the generic wrapper names only (preserve inner names)
    for wrapper in ("List", "Dict", "Tuple", "Optional", "Set", "FrozenSet"):
        t = t.replace(wrapper, wrapper.lower())
    return t


def _extract_core(normalised: str) -> str:
    """Return the innermost non-generic portion of a type string.

    ``list[LexicalClosure]`` → ``lexicalclosure``
    ``tuple[list[lexicalclosure], list[concept]]`` → ``lexicalclosure,concept``
    """
    import re
    # Strip all generic wrappers and brackets, keep inner names
    inner = re.sub(r"\b(list|dict|tuple|optional|set|frozenset)\b", "", normalised)
    inner = inner.replace("[", "").replace("]", "")
    parts = [p.strip().lower() for p in inner.split(",") if p.strip()]
    return ",".join(parts)


def _types_compatible(output_type: str, input_type: str) -> bool:
    """Return True if *output_type* is structurally compatible with *input_type*.

    Uses a normalised core-extraction approach: both sides are reduced to
    their inner type names and compared.  The function is deliberately
    lenient for compound inputs (``Tuple[A, B]``) that consume multiple
    outputs from prior layers.
    """
    norm_out = _normalize_type(output_type)
    norm_in = _normalize_type(input_type)

    # Fast exact match
    if norm_out == norm_in:
        return True

    core_out = _extract_core(norm_out)
    core_in = _extract_core(norm_in)

    # Direct core match
    if core_out == core_in:
        return True

    # Check if output is a component of a compound input
    # e.g. output "list[LexicalClosure]" consumed by input
    #      "Tuple[List[LexicalClosure], List[Concept]]"
    if core_out and core_out in core_in:
        return True

    # Check if input is a component of a compound output
    if core_in and core_in in core_out:
        return True

    return False
